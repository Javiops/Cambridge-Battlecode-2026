void play_turn(State& s) {
    bc::champion& me = bc::self();
    FP(1, "init");
    if (!s.ready) {
        // P_FUELGUARD: start-up can eat most of the first turn's double budget on big maps; the turn then ends
        // cleanly on the spawn (start-up finishes next turn) rather than run out half way and play the rest late.
        if (!init(s, me)) {
            g_mode = "init-fuel";
            return;
        }
        s.ready = true;  // never retry a failing init every turn
        if (P_FUELGUARD && !fuel_ok(40000)) {
            g_mode = "init-fuel";
            return;
        }
    }
    const int round = static_cast<int>(bc::round_number());
    cf_observe(s, me, round);

    if (!me.is_alive()) {
        g_mode = "dead";
#if P_TRACK_LOG
        track::on_dead(round);
#endif
        shop(s, me);  // dead champions can still shop
        drop_target(s);
        return;
    }

    vec2 pos = me.position();
    const float mhp = me.max_health();
    int gems = static_cast<int>(me.gem_count());
    int gold = static_cast<int>(me.gold_count());
    bool on_spawn = s.my_spawn.is_set(pos);

    // Capture reward arrived while standing on our target's spawn tiles.
    if (s.target >= 0 && (gems > s.last_gems || gold > s.last_gold) && s.groups[s.target].mask.is_set(pos)) {
        Group& g = s.groups[s.target];
        ++s.cf_reward_gain_observed;
        g.next_ok = round + g.respawn - (P_RESPAWN ? 6 : 0);
        g.reward_seen = -1;
        broadcast_cooldown(s.target, g.next_ok);
        drop_target(s);
    }
    s.last_gems = gems;

    FP(2, "shop");
    if (P_SHOPFIX && !s.shop_done && fuel_ok(40000)) build_shop(s, me);  // init ran out of fuel before the item list was done
    if (gold >= 30) {
        shop(s, me);  // only succeeds on spawn / dead (or anywhere for Tavi)
        if (P_SHOPFIX && on_spawn && me.gold_count() >= 30 && static_cast<int>(me.gold_count()) == gold) s.shop_fail = round;
    }
    s.last_gold = static_cast<int>(me.gold_count());
    float hp = me.health();
    float hpr = hp / mhp;
    if (s.last_hp >= 0 && hp < s.last_hp - 1.0f) s.hit_round = round;
    s.last_hp = hp;

    if (PR.backhome) {
        bool sub = me.is_submitting_gems();
        if (s.sub_prev && !sub) s.trib_end = round;
        s.sub_prev = sub;
    }
    if (me.is_submitting_gems() || me.is_teleporting() || me.is_recalling()) {
        g_mode = "channel";
        return;
    }
    if (!fuel_ok(15000)) {
        g_mode = "low-fuel";
        return;
    }

    FP(3, "vision");
    if (X(pos) == s.still_x && Y(pos) == s.still_y) ++s.still_n;
    else { s.still_x = X(pos); s.still_y = Y(pos); s.still_n = 0; }
    s.blocked = s.static_block | bc::vision::champion_tiles() | bc::vision::camp_tiles();
    s.blocked.set(pos, false);
    attempt([&] {
        s.vis = me.visible_tiles();
        return true;
    });
    FP(4, "groups");
    if (P_MAPPLAN && P_MP_CHAINPLAN) s.self_pos = pos;
    refresh_groups(s, round);
    FP(5, "foes");

    std::vector<Foe> foes;
    for (auto& c : bc::vision::champions(*s.en)) {
        attempt([&] {
            if (!c.is_alive()) return false;
            Foe f{c, c.position(), c.health(), 0, 0, false};
            f.d = dist(f.p, pos);
            attempt([&] {
                f.gems = static_cast<int>(c.gem_count());
                return true;
            });
            attempt([&] {
                f.channeling = c.is_submitting_gems() || c.is_recalling();
                return true;
            });
            foes.push_back(f);
            return true;
        });
    }
    if (P_NOCHASE) {
        // Away: it stepped farther from where we stood, or toward its spawn without coming closer to us;
        // it stays "away" for 3 rounds unless it comes back within 2 of us.
        std::vector<Seen> now;
        for (auto& f : foes) {
            int until = -1;
            if (s.seen_r == round - 1)
                for (auto& o : s.seen)
                    if (o.c == f.c) {
                        until = o.away_until;
                        bool moved = !(o.p == f.p);
                        bool off = dist(f.p, s.seen_me) > dist(o.p, s.seen_me);
                        bool home = dist(f.p, s.en_center) < dist(o.p, s.en_center) && dist(f.p, pos) >= dist(o.p, pos);
                        if (moved && (off || home)) until = round + 3;
                        break;
                    }
            if (f.d <= 2) until = -1;
            f.away = until >= round;
            now.push_back({f.c, f.p, until});
        }
        s.seen = std::move(now);
        s.seen_r = round;
        s.seen_me = pos;
    }
    if (P_TRACK) track::update(s, me, foes, pos, round);
    if (P_DANGER) update_danger(s, foes, round);
    if (P_VOLLEY || P_FM >= 2) {  // the volley map of this round (step_towards reads it)
        s.thr.clear();
        for (auto& f : foes) {
            if (f.d > 10) continue;
            int ar = 1;
            attempt([&] {
                ar = static_cast<int>(f.c.attack_range());
                return true;
            });
            s.thr.push_back(threat_of(f.c, f.p, ar <= 1 ? 2 : ar + 1));
        }
        s.thr_r = round;
    }
    if (!foes.empty()) s.foe_r = round;
    FP(6, "camps");
    std::vector<bc::camp> camps = P_LEAN_CAMPS ? near_camps(s, pos) : bc::vision::camps();

    bool awake_camp_near = false;
    for (auto& c : camps)
        attempt([&] {
            if (dist(c.position(), pos) <= CAMP_RANGE + 1 && c.health() < c.max_health()) awake_camp_near = true;
            return true;
        });
    int nearest_foe = 99;
    for (auto& f : foes) nearest_foe = std::min(nearest_foe, f.d);
    if (P_TRACE) {
        g_nf = nearest_foe; g_nfoes = 0; g_nal = 0;
        for (auto& f : foes) if (f.d <= 8) ++g_nfoes;
        attempt([&] { for (auto& a : bc::vision::champions(*s.my)) if (!(a == me) && a.is_alive() && dist(a.position(), pos) <= 6) ++g_nal; return true; });
        g_rew = (s.target >= 0 && s.target < static_cast<int>(s.groups.size()) && s.groups[s.target].reward_seen == round) ? 1 : 0;
    }
    bool in_combat = nearest_foe <= 4 || awake_camp_near;
    bool safe = nearest_foe > 7 && !awake_camp_near;
    if (P_SAFE_RECALL) safe = safe && nearest_foe > 8 && round - s.hit_round > 2;
    // P_RECALL_NEAR: a recall only needs nobody to hit us while it channels, not an empty screen
    bool rsafe = safe || (s.rnear && nearest_foe >= s.rnear && round - s.hit_round >= 1 && !awake_camp_near);

    // Preserve a nearby cleared camp's loot, even if we were hit by its last
    // surviving monster on a recent turn. The recent-hit check in `safe` is
    // over-conservative after that monster has died. Only delay non-emergency
    // recalls, and only when we are the designated capturer, no enemies are
    // within 8 tiles, and no fighting camp is nearby. Very low HP still flees.
    bool capture_before_recall = false;
    if (P_CAPTURE_RECALL_FIX && hpr >= 0.20f && nearest_foe > 8 &&
        !awake_camp_near && s.target >= 0 &&
        s.target < static_cast<int>(s.groups.size()) && fuel_ok(18000)) {
        const Group& reward = s.groups[s.target];
        if (reward.reward_seen == round) {
            int nearest_tile = 99;
            for (auto tile : reward.tiles) nearest_tile = std::min(nearest_tile, dist(pos, tile));
            if (nearest_tile <= 2 && (!P_ONE_CAP || !other_captures(s, me, reward, s.target)))
                capture_before_recall = true;
        }
    }

    // P_CAPHOME: the reward of our camp waits within reach and we are its capturer.
    bool cap_home = false, cap_pend = false;
    if (PR.caphome && s.target >= 0 && s.target < static_cast<int>(s.groups.size()) && !awake_camp_near &&
        s.groups[s.target].reward_seen == round && fuel_ok(18000)) {
        const Group& rg = s.groups[s.target];
        int nt = 99;
        for (auto tile : rg.tiles) nt = std::min(nt, dist(pos, tile));
        if (nt <= PR.caphome && (!P_ONE_CAP || !other_captures(s, me, rg, s.target))) {
            cap_pend = PR.caphome_trib && nt <= 2;
            cap_home = PR.caphome_trib != 2 && hpr >= 0.1f && nearest_foe > (hpr * 100 < P.flee_pct ? 5 : 3) &&
                       (!PR.caphome_rsafe || rsafe);
        }
    }

    FP(7, "support");
    support_spells(s, me, in_combat);
    FP(8, "decide/flee");

    // Best enemy target: low health, channeling, or carrying gems; never on their spawn.
    Foe* tgt = nullptr;
    double tgt_score = 1e18;
    auto gone = [&](const Foe& f) {  // P_NOCHASE: walking away and out of reach: the fight with it is over
        return P_NOCHASE && f.away && f.d > me.attack_range() && f.gems < P_CHASE_GEMS && !f.channeling;
    };
    for (auto& f : foes) {
        if (f.d > 6 || s.en_spawn.is_set(f.p) || gone(f)) continue;
        double sc = f.hp - (f.channeling ? 300 : 0) - 5.0 * f.gems + 40.0 * f.d;
        if (sc < tgt_score) { tgt_score = sc; tgt = &f; }
    }

    // Stuck: same tile for many turns with nothing to hit. Bank or go home, give the target up.
    if (P_UNSTICK && s.still_n >= P_UNSTICK && !on_spawn && nearest_foe > 4 && !awake_camp_near &&
        (s.cap_start < 0 || round - s.cap_start > 10)) {
        g_mode = "unstick";
        if (s.target >= 0) {
            s.groups[s.target].bad_until = round + 30;
            drop_target(s);
        }
        if (gems > 0 && go_tribute(s, me, round)) return;
        if (hpr < 0.9f) {
            if (safe && attempt([&] {
                    me.recall();
                    return true;
                }))
                return;
            if (flee(s, me)) return;
        }
        s.still_n = 0;
    }

    if (PR.noleave && !awake_camp_near && hpr >= 0.15f && fuel_ok(25000)) {
        const bool carry = cap_rank(s.name, me.attack_range() > 1) <= 2;
        auto sm = read_sm();
        int gi = -1, gd = 99;
        for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
            const Group& g = s.groups[i];
            if (g.reward_seen != round || g.monolith) continue;
            int d = 99;
            for (auto tile : g.tiles) d = std::min(d, dist(pos, tile));
            if (d > PR.noleave || d >= gd) continue;
            if (i != s.target && count_claimers(s, sm, i) > 0) continue;  // another ally already went for it
            gi = i;
            gd = d;
        }
        bool skip = gi < 0;
        if (!skip && PR.cache && !carry) {  // tanks leave it to a carry: post it in the cache and move on
            bool carry_alive = false, carry_near = false;
            attempt([&] {
                for (auto& a : my_roster(s)) {
                    if (a == me || !a.is_alive()) continue;
                    bool ar = false;
                    try { ar = a.attack_range() > 1; } catch (...) {}
                    if (cap_rank(norm(bc::to_string(a.champion_name())), ar) > 2) continue;
                    carry_alive = true;
                    try { if (dist(a.position(), pos) <= 6) carry_near = true; } catch (...) {}
                }
                return true;
            });
            if (carry_alive && !(gd <= 1 && !carry_near)) {
                write_sm(SM_BC_GROUP, static_cast<std::uint8_t>(gi + 1));
                write_sm(SM_BC_READY, static_cast<std::uint8_t>(251 + ((round / 16) & 3)));
                if (s.target == gi) {
                    s.groups[gi].bad_until = round + 15;
                    drop_target(s);
                }
                skip = true;
            }
        }
        if (!skip) {
            Group& g = s.groups[gi];
            double dmg = s.thr_r == round ? danger_at(s.thr, pos) : 0.0;
            if (dmg * 3 < hp && (!P_ONE_CAP || !other_captures(s, me, g, gi))) {
                g_mode = "no-leave";
                if (s.target != gi) {
                    s.target = gi;
                    s.target_round = round;
                    s.cap_start = -1;
                    write_claim(s, gi);
                }
                if (!g.mask.is_set(pos)) step_towards(s, me, g.mask, true);
                if (g.mask.is_set(me.position())) {
                    if (s.cap_start < 0) s.cap_start = round;
                    bool want_home = hpr * 100 < P.recall_pct || (round - s.need_heal <= 2 && hpr < 0.8f);
                    if (want_home && rsafe && round - s.cap_start >= P_CAPRECALL_DELAY)
                        attempt([&] {
                            me.recall();
                            return true;
                        });
                }
                if (!me.is_recalling()) shoot_back(s, me, foes);
                return;
            }
        }
    }

    // 1. Healing on spawn.
    g_mode = "heal-spawn";
    if (on_spawn && hpr * 100 < P_GA_SPAWN_HEAL) {
        if (tgt) basic_attack(s, me, tgt->c, tgt->p);
        return;
    }

    if (cap_home && (hpr * 100 < P.recall_pct || (round - s.need_heal <= 2 && hpr < 0.8f))) {
        Group& g = s.groups[s.target];
        g_mode = "cap-home";  // capture and recall run together on the reward tiles
        if (!g.mask.is_set(pos)) step_towards(s, me, g.mask, true);
        if (g.mask.is_set(me.position())) {
            if (s.cap_start < 0) s.cap_start = round;
            attempt([&] {
                me.recall();
                return true;
            });
        }
        return;
    }

    // 2. Badly hurt: run, or recall if nobody can interrupt.
    g_mode = "flee/recall";
    // P_UNI_FLEE: with the caster draft, leave the fight earlier (the #1 walks away 58% of contact rounds below 30%
    // hp and 40% below 50%; v27 died in 20% of its contact rounds below 30%)
    if (!capture_before_recall &&
        hpr * 100 < ((P_UNI_FLEE && P_DRAFTUNI && s.casters) ? P_UNI_FLEE : P.flee_pct)) {
        if (gems > 0 && nearest_foe > 3) {
            auto a = best_altar(s, pos, round);
            if (a && dist(*a, pos) <= 1) {  // tribute is not interrupted by damage
                bool acted = go_tribute(s, me, round);
                if (acted || !P_U34_FAILED_CHANNELS) return;
            }
        }
        bool recalled = false;
        if (rsafe) recalled = attempt([&] {
            me.recall();
            return true;
        });
        if (!rsafe || (P_U34_FAILED_CHANNELS && !recalled)) {
            bool hit = P_HITFIRST && fight::hit_now(s, me, foes);
            flee(s, me);
            if (!hit) shoot_back(s, me, foes);
        }
        return;
    }

    if (!capture_before_recall && s.rnear && !safe && rsafe && !on_spawn &&
        dist(pos, s.spawn_center) > 6 && hpr * 100 < P.recall_pct) {
        g_mode = "near-recall";  // the #1: hurt, out of the fight by 4-6 tiles: recall now, come back whole
        if (attempt([&] {
                me.recall();
                return true;
            }))
            return;
    }

    bool fight_fav = false;  // P_CAMPFOE: step 3's verdict on the fight
    // 3. Enemy champions: back away from a stronger group, fight an even or weaker one.
    FP(9, "fight");
    g_mode = "fight";
    std::vector<vec2> allies;
    for (auto& a : bc::vision::champions(*s.my))
        attempt([&] {
            if (!(a == me) && a.is_alive()) allies.push_back(a.position());
            return true;
        });
    // Ally duty: a foe near an ally of ours (within 8 of us) becomes our target.
    if (P_ALLYDUTY && !tgt) {
        for (auto& f : foes) {
            if (f.d > 8 || s.en_spawn.is_set(f.p) || gone(f)) continue;
            for (auto& ap : allies)
                if (dist(ap, f.p) <= 3 && dist(ap, pos) <= 8) {
                    if (!tgt || f.hp < tgt->hp) tgt = &f;
                    break;
                }
        }
    }
    bool pv_fight = false;  // P_PV: the first-contact verdict, held for the engagement (verdict.h)
    if (P_PV) {
        int v = pv::verdict(s, me, foes, round, on_spawn);
        bool keep = false;
        if (P_PV_KEEPCAP && s.cap_start >= 0) {
            keep = true;
            for (auto& f : foes)
                if (f.d <= 3) keep = false;
        }
        if (v == 2 && !on_spawn && !foes.empty() && !keep) {
            g_mode = "pv-leave";
            fight::back_off(s, me, foes, round);
            return;
        }
        pv_fight = v == 1;
    }
    if (P_FM && !foes.empty() && !on_spawn && fight::fight_mode(s, me, foes, round)) {
        g_mode = s.fm == 1 ? "fm-engage" : "fm-retreat";
        return;
    }
    if (P_KITEFRONT == 1 && P_FRONT && !foes.empty() && !on_spawn && fight::front_line(s, me, foes, round)) {
        g_mode = "front";
        return;
    }
    if (P_KITE && s.casters && !foes.empty() && !on_spawn && (!s.melee || s.renkite) && fight::kite(s, me, foes, round)) {
        g_mode = "kite";
        return;
    }
    if (P_KITEFRONT != 1 && P_FRONT && !P_AVOIDFIRST && !foes.empty() && !on_spawn && fight::front_line(s, me, foes, round)) {
        g_mode = "front";
        return;
    }
    if (!foes.empty()) {
        if (P_CALLHELP && round - s.hit_round <= 1) fight::call_help(s, foes, round);
        if (PR.twin && !on_spawn && (s.cap_start < 0 || round - s.cap_start > 10) && fight::twin_guard(s, me, foes)) {
            g_mode = "twin";
            return;
        }
        double ours = hp, theirs = 0;
        for (auto& a : bc::vision::champions(*s.my))
            attempt([&] {
                if (!(a == me) && a.is_alive() && dist(a.position(), pos) <= 6) ours += a.health();
                return true;
            });
        for (auto& f : foes)
            if (f.d <= 8) theirs += f.hp;
        bool favourable = ours * 100.0 >= P_GA_FAV * theirs;
        if (P_ENGAGE2 && tgt) {
            int nb = 1, eb = 0;
            double oh = hp, eh = 0;
            for (auto& ap : allies)
                if (dist(ap, tgt->p) <= 8) ++nb;
            attempt([&] {
                for (auto& a : bc::vision::champions(*s.my))
                    if (!(a == me) && a.is_alive() && dist(a.position(), tgt->p) <= 8) oh += a.health();
                return true;
            });
            for (auto& f : foes)
                if (dist(f.p, tgt->p) <= 8) { ++eb; eh += f.hp; }
            favourable = nb >= eb && oh * 100.0 >= P_ENGAGE2 * eh;
        }
        if (P_TRACK && P_TRACK_FAV && tgt) favourable = track::favourable(me, tgt->p, round);
        bool helping = false;
        if (P_CALLHELP && hpr > 0.4f) {  // an ally named the foe hitting it: go and hit that one
            Foe* h = fight::help_target(s, foes, round);
            if (h && h->d <= P_HELP_R && !s.en_spawn.is_set(h->p) && !gone(*h)) {
                int nb = 1, eb = 0;
                for (auto& ap : allies) if (dist(ap, h->p) <= 6) ++nb;
                for (auto& f : foes) if (dist(f.p, h->p) <= 6) ++eb;
                if (nb >= eb) { tgt = h; favourable = true; helping = true; }
            }
        }
        // Top-10 habit: gang up on a lone foe that is hurt (< 65% hp) or carrying gems, with
        // P_GANG of us (me included) within 8 of it; never chase further than 8 tiles.
        if (P_GANG && !helping && hpr > 0.5f) {
            Foe* best = nullptr;
            for (auto& f : foes) {
                if (f.d > 8 || s.en_spawn.is_set(f.p) || gone(f)) continue;
                bool lone = true;
                for (auto& o : foes)
                    if (&o != &f && dist(o.p, f.p) <= 4) lone = false;
                if (!lone) continue;
                float mh = 0;
                attempt([&] {
                    mh = f.c.max_health();
                    return true;
                });
                if (!(f.channeling || f.gems >= 20 || (mh > 0 && f.hp < 0.65f * mh))) continue;
                int nb = 1;
                for (auto& ap : allies) if (dist(ap, f.p) <= 8) ++nb;
                if (nb < P_GANG) continue;
                if (!best || f.hp < best->hp) best = &f;
            }
            if (best) { tgt = best; favourable = true; helping = true; }
        }
        if (P_TRACK && P_TRACK_ISO && !helping && hpr > 0.4f) {  // a lone enemy the allies near it kill fast
            Foe* iso = track::isolated(s, me, foes, round, gone);
            if (iso) { tgt = iso; favourable = true; helping = true; }
        }
        bool pot_hold = false;
        if (P_POT && hpr > 0.3f)
            for (auto pa : s.pots)
                if (dist(pa, pos) <= 5) {
                    int nb6 = 1, eb6 = 0;
                    for (auto& ap : allies) if (dist(ap, pos) <= 6) ++nb6;
                    for (auto& f : foes) if (f.d <= 6) ++eb6;
                    if (eb6 < nb6 + 2) pot_hold = true;
                }
        if (pot_hold) favourable = true;
        if (pv_fight) favourable = true;
        g_ally_near_tgt = false;
        if (tgt)
            for (auto& ap : allies)
                if (dist(ap, tgt->p) <= 2) g_ally_near_tgt = true;
        fight_fav = favourable;
        bool killable = tgt && tgt->hp <= me.strength() * (P_GA_KILL_X / 10.0f);
        bool reachable = tgt && tgt->d <= me.attack_range() + 1;
        bool carrying = P_CARRY && gems >= P_CARRY;
        int low_pct = (P_CASSI_PCT && starts_with(s.name, "cassi")) ? P_CASSI_PCT : P_LOWHP;
        if (!killable && !on_spawn && !pot_hold && ((low_pct && hpr * 100 < low_pct && nearest_foe <= 6) ||
                                       (carrying && !favourable && nearest_foe <= 6))) {
            g_mode = "avoid";
            if (carrying) {
                auto a = best_altar(s, pos, round);
                if (a && dist(*a, pos) <= 1 && nearest_foe > 3) {
                    bool acted = go_tribute(s, me, round);
                    if (acted || !P_U34_FAILED_CHANNELS) return;
                }
            }
            fight::back_off(s, me, foes, round);
            return;
        }
        if (PR.outnum && !on_spawn && !(killable && reachable) && nearest_foe <= PR.outnum) {
            int nb = 1, eb = 0;
            attempt([&] {
                for (auto& a : bc::vision::champions(*s.my))
                    if (!(a == me) && a.is_alive() && !a.is_recalling() && dist(a.position(), pos) <= PR.outnum) ++nb;
                return true;
            });
            for (auto& f : foes)
                if (f.d <= PR.outnum && !s.en_spawn.is_set(f.p)) ++eb;
            if (eb >= nb + 2) {
                g_mode = "outnumbered";
                fight::back_off(s, me, foes, round);
                return;
            }
        }
        if (!favourable && !killable && (hpr * 100 < P_GA_AVOID_HP || nearest_foe <= P_AVOID_DIST) && !on_spawn) {
            g_mode = "avoid";
            fight::back_off(s, me, foes, round);
            return;
        }
        // P_AVOIDFIRST: the front line is taken only once the back-off checks above said stay
        if (P_AVOIDFIRST && P_KITEFRONT != 1 && P_FRONT && !on_spawn && fight::front_line(s, me, foes, round)) {
            g_mode = "front";
            return;
        }
        if (tgt && carrying && !killable && !tgt->channeling) tgt = nullptr;
        // P_NOCHASE2: a low or channelling foe is no reason to walk after it, unless it carries a big bag
        const bool close_enough = !PR.nochase2 || (tgt && (tgt->d <= me.attack_range() + 1 || tgt->gems >= P_CHASE_GEMS));
        if (tgt && (((killable || tgt->channeling) && close_enough) || (reachable && favourable) || helping ||
                    (P_ALLYDUTY && favourable && tgt->d <= 8 && g_ally_near_tgt))) {
            bool acted = engage(s, me, tgt->c, tgt->p, true, true);
            if (acted || !P_U34_ENGAGE_FALLBACK) return;
        }
    }

    // 4. Recall to heal / spend gold when safe; bank the bag first if an altar is close.
    FP(10, "recall/tribute");
    g_mode = "recall-shop";
    int home = dist(pos, s.spawn_center);
    bool want_recall = hpr * 100 < P.recall_pct || (gold >= P_SHOP_GOLD && hpr < 0.5f) ||
                       (round - s.need_heal <= 2 && hpr < 0.8f);
    bool shop_trip = P_SHOP_RECALL && gold >= P_SHOP_RECALL && !starts_with(s.name, "tavi") &&
                     (!P_SHOPFIX || round - s.shop_fail > 150) &&
                     s.cap_start < 0 && round - s.shop_recall > 40;
    want_recall = want_recall || shop_trip;
    // P_CAPRECALL: capture first and recall on the capture tiles, so the 5-round recall overlaps the 5-round
    // capture (procless on rows: it captures and arrives home healed in the same turn).
    // P_CAPRECALL 2: also take the free trip home whenever it heals or shops something (hp < 90%, 90+ gold).
    // Preserve normal healing/shop recalls. Only the extra capture opportunity
    // weighs the cost of returning to productive territory.
    bool cap_want = want_recall || (((s.de_map == v34de::Lanes) ? 1 : P_CAPRECALL) >= 2 &&
                                   cr_capture_extra(s, me, hpr, gold, round));
    if (((s.de_map == v34de::Lanes) ? 1 : P_CAPRECALL) && cap_want &&
        (safe || capture_before_recall) && s.target >= 0 && s.target < static_cast<int>(s.groups.size())) {
        Group& g = s.groups[s.target];
        if (g.reward_seen == round && !other_captures(s, me, g, s.target)) {
            if (g.mask.is_set(pos) && (P_CAPRECALL_DELAY == 0 || (s.cap_start >= 0 && round - s.cap_start >= P_CAPRECALL_DELAY))) {
                g_mode = "cap-recall";
                if (attempt([&] {
                        me.recall();
                        return true;
                    })) {
                    ++s.cr_started;
                    cr_trace(s, round);
                    if (shop_trip) s.shop_recall = round;
                }
                return;
            }
            want_recall = false;  // step on the tiles first
        }
    }
    if (PR.backhome && round - s.trib_end <= 2 && gems == 0 && home > 6) {
        s.trib_end = -1000;
        auto contested = [&](vec2 p) { return dist(p, s.spawn_center) - dist(p, s.en_center) >= -PR.backhome; };
        if (contested(pos)) {
            int t = s.target;
            if (can_choose(s)) t = choose_target(s, me, round);
            bool go = t < 0 || (contested(s.groups[t].center) && (round - s.foe_r <= 20 || hpr < 0.8f));
            if (go) {
                g_mode = "back-home";
                drop_target(s);
                if (rsafe && attempt([&] {
                        me.recall();
                        return true;
                    }))
                    return;
                if (flee(s, me)) return;
            } else if (t != s.target) {
                s.target = t;
                s.target_round = round;
                s.cap_start = -1;
                write_claim(s, t);
            }
        }
    }
    if (!capture_before_recall && rsafe && home > 6 && want_recall) {
        if (gems >= 10) {
            auto a = best_altar(s, pos, round);
            if (a && br_altar_distance(s, *a, pos, round) <= std::min(home, 12)) {
                g_mode = "tribute";
                bool acted = go_tribute(s, me, round);
                if (acted || !P_U34_FAILED_CHANNELS) return;
            }
        }
        bool recalled = attempt([&] {
            me.recall();
            return true;
        });
        if (recalled && shop_trip) s.shop_recall = round;
        if (recalled || !P_U34_FAILED_CHANNELS) return;
    }

    if (P_WALKHOME && !safe && home > 6 && hpr * 100 < P.recall_pct && nearest_foe > 2) {
        g_mode = "walk-home";
        if (gems >= 10) {
            auto a = best_altar(s, pos, round);
            if (a && br_altar_distance(s, *a, pos, round) <= std::min(home, 8) && go_tribute(s, me, round)) return;
        }
        if (flee(s, me)) return;
    }

    // 5. Bank gems.
    g_mode = "tribute";
    bool late = round >= P.late_round;
    if (gems > 0 && !(cap_pend && !late)) {
        auto a = best_altar(s, pos, round);
        int ad = a ? br_altar_distance(s, *a, pos, round) : 99;
        bool chain = false;
        const int chain_gems = mp_far_home(s) ? std::max(P_MP_CHAIN, (s.de_map == v34de::Rows) ? 60 : P_CHAIN) : ((s.de_map == v34de::Rows) ? 60 : P_CHAIN);
        if (chain_gems && gems < chain_gems && !late && ad > 2) {
            auto sm = read_sm();
            int gi = -1, gd = 99;
            for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
                Group& g = s.groups[i];
                if (g.gems <= 0 || g.monolith || g.next_ok > round || g.bad_until > round) continue;
                int d = dist(pos, g.center);
                if (d > (mp_far_home(s) ? P_MP_CHAIN_R : P_CHAIN_R) || d >= ad || d >= gd) continue;
                if (count_claimers(s, sm, i) > 0 && i != s.target) continue;
                if (squad_needed(g.hp, g.str, my_dps(s, me), std::max(1.0f, hp - mhp * 0.3f)) > 1) continue;
                gi = i;
                gd = d;
            }
            if (gi >= 0) {
                chain = true;
                if (s.target != gi) {
                    s.target = gi;
                    s.target_round = round;
                    s.cap_start = -1;
                    write_claim(s, gi);
                }
            }
        }
        // P_BAG: with no enemy seen for P_BAG_QUIET rounds, carry up to P_BAG gems before the trip
        // (rows winners bank 81 gems a trip; we banked 39).
        const int bag_q = mp_far_home(s) ? std::max(P_MP_BAG, (s.de_map == v34de::Rows) ? 48 : P_BAG) : ((s.de_map == v34de::Rows) ? 48 : P_BAG);
        int bag = (bag_q && round - s.foe_r > P_BAG_QUIET) ? std::max(P.tribute_gems, bag_q) : P.tribute_gems;
        if (!chain && (gems >= bag || late || (gems >= 10 && ad <= (s.de_map == v34de::Rows ? 4 : P_TRIBUTE_NEAR)) || (gems >= 5 && ad <= 2))) {
            // P_TELE: the walk to the altar is longer than recalling and walking from home: recall (heals and shops too).
            if (P_TELE && safe && s.tele_sa >= 0 && s.tele_va.is_set(pos) && !s.my_spawn.is_set(pos) &&
                static_cast<int>(s.tele_fa.get(pos)) > 5 + s.tele_sa + P_TELE) {
                g_mode = "tele-bank";
                if (attempt([&] {
                        me.recall();
                        return true;
                    }))
                    s.shop_recall = round;
                return;
            }
            bool acted = go_tribute(s, me, round);
            if (acted || !P_U34_FAILED_CHANNELS) return;
        }
    }

    // P_GROUP_R: keep the ball together. The leader is the first ally in draft order that is alive and not
    // channelling; followers come back to it, the leader waits for a straggler (ignoring anyone 15+ away).
    if (P_GROUP_R && grouped(s, round) && !awake_camp_near && s.cap_start < 0) {
        int li = -1, far = 0;
        vec2 lp{0, 0};
        std::vector<vec2> fol;
        attempt([&] {
            auto allies = my_roster(s);
            for (int k = 0; k < static_cast<int>(allies.size()); ++k) {
                auto& a = allies[k];
                try {
                    if (!a.is_alive() || a.is_recalling() || a.is_teleporting()) continue;
                    vec2 ap = a.position();
                    if (s.my_spawn.is_set(ap) && !(a == me)) continue;
                    if (li < 0) { li = k; lp = ap; continue; }
                    if (!(a == me)) fol.push_back(ap);
                } catch (...) {
                }
            }
            return true;
        });
        if (li >= 0 && li != s.ally_idx && dist(pos, lp) > P_GROUP_R) {
            g_mode = "group";
            bc::bitboard ring;
            ring.draw_chebyshev(lp, 2.0f);
            if (step_towards(s, me, ring, false)) {
                if (tgt && me.can_attack()) basic_attack(s, me, tgt->c, tgt->p);
                return;
            }
        }
        if (li == s.ally_idx)
            for (auto& f : fol) {
                int d = dist(f, pos);
                if (d <= 15) far = std::max(far, d);
            }
        if (li == s.ally_idx && far > 2 * P_GROUP_R) {
            g_mode = "group-wait";
            if (tgt && me.can_attack()) basic_attack(s, me, tgt->c, tgt->p);
            return;
        }
    }

    if (PR.campfoe && !on_spawn && !foes.empty()) {
        int live = 99;
        for (auto& f : foes)
            if (!s.en_spawn.is_set(f.p) && !gone(f)) live = std::min(live, f.d);
        bool capturing = s.target >= 0 && s.target < static_cast<int>(s.groups.size()) &&
                         s.groups[s.target].reward_seen == round && s.groups[s.target].mask.is_set(pos);
        if (!capturing && (live <= 3 || (live <= PR.campfoe && round - s.hit_round <= 2))) {
            g_mode = "campfoe";  // a fight: hit the rival or leave, never the camp
            if (tgt && fight_fav && tgt->d <= me.attack_range() + 1 && engage(s, me, tgt->c, tgt->p, true, false)) return;
            fight::back_off(s, me, foes, round);
            return;
        }
    }

    // 6. Farm camps.
    FP(11, "farm");
    g_mode = "farm";
    farm(s, me, round, camps);

    // Free hit on any enemy that ended up in reach.
    if (tgt && me.can_attack()) basic_attack(s, me, tgt->c, tgt->p);
}

