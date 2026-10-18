bool g_cap_other_on = false;  // P_CAPPRIO: the ally that takes the reward already stands on it

// One capturer per reward: among the allies on the reward or claiming it within 4 tiles,
// the nearest one (lowest index on ties) captures; everybody else leaves.
bool other_captures_impl(State& s, bc::champion& me, const Group& g, int gi);
bool other_captures(State& s, bc::champion& me, const Group& g, int gi) {
    if (!P_OCMEMO) return other_captures_impl(s, me, g, gi);
    const int round = static_cast<int>(bc::round_number());
    vec2 p = me.position();
    if (s.oc_round == round && s.oc_group == gi && s.oc_x == X(p) && s.oc_y == Y(p)) {
        g_cap_other_on = s.oc_on;
        return s.oc_other;
    }
    bool o = other_captures_impl(s, me, g, gi);
    s.oc_round = round; s.oc_group = gi; s.oc_x = X(p); s.oc_y = Y(p);
    s.oc_other = o; s.oc_on = g_cap_other_on;
    return o;
}
bool other_captures_impl(State& s, bc::champion& me, const Group& g, int gi) {
    FP_SCOPE(24, "other_captures");
    auto mask_dist = [&](vec2 p) {
        int d = 99;
        for (auto t : g.tiles) d = std::min(d, dist(p, t));
        return d;
    };
    int mine = mask_dist(me.position());
    auto sm = read_sm();
    bool other = false;
    g_cap_other_on = false;
    if (i_am_tank(s)) return true;  // P_DPSFARM: a tank never takes a reward
    const int my_rank = PR.capprio ? cap_rank(s.name, me.attack_range() > 1) : 0;
    std::vector<bc::champion> seen;  // P_FUELGUARD: allies in vision (position() of any other one throws)
    if (P_FUELGUARD) attempt([&] { seen = bc::vision::champions(*s.my); return true; });
    attempt([&] {
    auto allies = my_roster(s);
    for (std::size_t k = 0; k < allies.size() && !other; ++k) {
        auto& a = allies[k];
        if (P_FUELGUARD && std::find(seen.begin(), seen.end(), a) == seen.end()) continue;
        // One ally per attempt: an ally out of our vision throws on position(), and with a
        // single attempt around the loop that aborted it, so nobody ever left the reward.
        try {
            if (a == me || !a.is_alive()) continue;
            if (PR.dpsfarm && ((tank_bits(s) >> k) & 1)) continue;  // tanks step off, they never capture
            int d = mask_dist(a.position());
            bool claims = k < static_cast<std::size_t>(claim_slots(s)) && claim_value(s, sm, static_cast<int>(k)) == gi + 1;
            if (PR.capprio) {
                if (a.is_recalling() || a.is_teleporting()) continue;
                int ar = cap_rank(norm(bc::to_string(a.champion_name())), a.attack_range() > 1);
                bool counts = ar == 0 && my_rank > 0 ? ((claims && d <= PR.capprio) || d <= 1) : ((claims && d <= 4) || d == 0);
                if (!counts) continue;
                if (ar < my_rank || (ar == my_rank && (d < mine || (d == mine && static_cast<int>(k) < s.ally_idx)))) {
                    other = true;
                    g_cap_other_on = d == 0;
                }
                continue;
            }
            // P_CAPCLAIM: only allies still claiming the group count. Allies that already chose to
            // leave stand on the tiles for one more turn, and counting them made everybody leave.
            if (P_CAPCLAIM ? !(claims && d <= 4) : !(d == 0 || (claims && d <= 4))) continue;
            if (P_CAPDPS) {  // the capture's gold goes to a ranged damage dealer first (top 4: Ryth/Stellar/Cassi earn it)
                int ka = (a.attack_range() > 1 ? 0 : 100) + d, km = (me.attack_range() > 1 ? 0 : 100) + mine;
                if (ka < km || (ka == km && static_cast<int>(k) < s.ally_idx)) other = true;
                continue;
            }
            if (d < mine || (d == mine && static_cast<int>(k) < s.ally_idx)) other = true;
        } catch (...) {
        }
    }
    return true;
    });
    return other;
}

void drop_target(State& s) {
    s.target = -1;
    s.cap_start = -1;
    write_claim(s, -1);
}


// Local-only diagnostics: these do not use the eight shared bytes.
// A death after a recent camp action is temporal evidence, not kill attribution.
void cf_observe(State& s, bc::champion& me, int round) {
    const bool alive = me.is_alive();
    if (!alive && s.cf_was_alive && round - s.cf_recent_camp <= 2) ++s.cf_death_after_camp;
    s.cf_was_alive = alive;
    if (round % 50 == 0 && s.cf_log_round != round) {
        s.cf_log_round = round;
        std::printf("[econ] who=%d r=%d cf_reach=%u cf_focus_wait=%u cf_focus_exit=%u cf_focus_hit=%u cf_evac=%u cf_reward_gain_observed=%u cf_death_after_camp=%u\n",
                    s.ally_idx, round, s.cf_reach, s.cf_focus_wait, s.cf_focus_exit, s.cf_focus_hit, s.cf_evac,
                    s.cf_reward_gain_observed, s.cf_death_after_camp);
    }
}

// True only for actual visible, healthy allies who can plausibly remain here.
// No claimed-but-absent champion contributes damage to the focus model.
bool cf_available(const bc::champion& a) {
    return a.is_visible() && a.is_alive() && a.health() > 0 &&
           a.health() >= 0.35 * a.max_health() && !a.is_recalling() &&
           !a.is_teleporting() && !a.is_submitting_gems();
}


// Leave only for an ally ALREADY occupying the reward. Merely approaching or
// claiming allies never justify emptying the region and resetting capture.
bool cf_evac_reward(State& s, bc::champion& me, Group& g, int round, const std::vector<bc::camp>* near = nullptr) {
    FP_SCOPE(26, "evac");
    const vec2 pos = me.position();
    if (!g.mask.is_set(pos) || !me.can_move() || !fuel_ok(28000)) return false;
    bool present = false;
    for (auto& a : bc::vision::champions(*s.my)) {
        attempt([&] {
            if (a == me || !cf_available(a) || !g.mask.is_set(a.position())) return false;
            // In particular do not rely on a recalling/teleporting ally remaining.
            present = true;
            return true;
        });
        if (present) break;
    }
    if (!present) return false;
    std::vector<std::pair<vec2, int>> monsters;
    // P_FUELGUARD: the camps within 12 (play_turn's list) are the only ones that can reach a tile next to us.
    for (const auto& c : (P_FUELGUARD && near) ? *near : bc::vision::camps()) {
        if (!fuel_ok(16000)) return false;
        bool observed = attempt([&] {
            // Camp wake/aggro is not exposed: avoid every visible damaging
            // monster's range, including an untouched member of an awake group.
            if (c.health() > 0 && c.strength() > 0)
                monsters.push_back({c.position(), c.attack_range()});
            return true;
        });
        if (!observed) return false; // An unknown visible hazard cannot authorize departure.
    }
    // Temporarily remove this target from scoring, without broadcasting a claim
    // or changing lifecycle memory. Failed/no-benefit moves restore all fields.
    const int old_target = s.target, old_bad = g.bad_until;
    g.bad_until = round + 1;
    int alternate = -1;
    if (can_choose(s)) attempt([&] { alternate = choose_target(s, me, round); return true; });
    g.bad_until = old_bad;
    if (!fuel_ok(16000)) return false;
    if (alternate < 0 || alternate == old_target) return false;
    const auto& next = s.groups[alternate];
    const int old_distance = dist(pos, next.center);
    const double current_danger = danger_at(s.thr, pos);
    std::optional<vec2> best;
    int best_distance = old_distance;
    for (int dx = -1; dx <= 1; ++dx)
        for (int dy = -1; dy <= 1; ++dy) {
            if (!dx && !dy) continue;
            vec2 p = pos + vec2(dx, dy);
            if (!bc::map::is_in_bounds(p) || s.blocked.is_set(p) || g.mask.is_set(p)) continue;
            if (danger_at(s.thr, p) > current_danger) continue;
            bool monster_safe = true;
            for (const auto& c : monsters) {
                if (dist(p, c.first) <= c.second) monster_safe = false;
                if (!monster_safe) break;
            }
            if (!monster_safe) continue;
            const int d = dist(p, next.center);
            if (d < best_distance) { best = p; best_distance = d; }
        }
    if (!best || !attempt([&] { return me.move_absolute(*best); })) return false;
    ++s.cf_evac;
    s.target = alternate;
    s.target_round = round;
    s.cap_start = -1;
    write_claim(s, alternate);
    g_farm = "reward-evac";
    return true;
}

void farm(State& s, bc::champion& me, int round, const std::vector<bc::camp>& camps) {
    vec2 pos = me.position();
    double hp = me.health();
    double mhp = std::max(1.0, static_cast<double>(me.max_health()));
    if (i_am_tank(s)) {  // P_DPSFARM: go where a DPS farms
        auto sm = read_sm();
        int best = -1, bd = 1 << 30, tb = tank_bits(s);
        bool issac = starts_with(s.name, "issac");
        attempt([&] {
            auto allies = my_roster(s);
            for (int k = 0; k < claim_slots(s) && k < static_cast<int>(allies.size()); ++k) {
                if (k == s.ally_idx || ((tb >> k) & 1) || !allies[k].is_alive()) continue;
                int c = static_cast<int>(claim_value(s, sm, k)) - 1;
                if (c < 0 || c >= static_cast<int>(s.groups.size()) || s.groups[c].bad_until > round) continue;
                int d = dist(pos, s.groups[c].center);
                if (issac && starts_with(norm(bc::to_string(allies[k].champion_name())), "cassi")) d -= 1000;
                if (d < bd) { bd = d; best = c; }
            }
            return true;
        });
        if (best >= 0 && best != s.target) {
            s.target = best;
            s.target_round = round;
            s.cap_start = -1;
            write_claim(s, best);
        }
        if (s.target >= 0 && s.groups[s.target].reward_seen == round) {  // the camp is dead: leave the loot to the DPS
            Group& g = s.groups[s.target];
            g_farm = "tank-off";
            write_sm(SM_BC_GROUP, static_cast<std::uint8_t>(s.target + 1));
            write_sm(SM_BC_READY, static_cast<std::uint8_t>(251 + ((round / 16) & 3)));
            g.bad_until = round + 10;
            drop_target(s);
            if (g.mask.is_set(pos)) {
                bc::bitboard r2;
                for (auto t : g.tiles) r2.draw_chebyshev(t, 2.0f);
                step_towards(s, me, r2 & ~g.mask, false);
            }
            return;
        }
        if (best >= 0) s.target_round = round;  // keep following: no periodic re-choice of our own
    }
    if (PR.twinfarm && starts_with(s.name, "issac")) {
        int ck = -1;
        std::optional<vec2> cp;
        attempt([&] {
            auto allies = my_roster(s);
            for (int k = 0; k < static_cast<int>(allies.size()); ++k) {
                if (!starts_with(norm(bc::to_string(allies[k].champion_name())), "cassi") || !allies[k].is_alive()) continue;
                ck = k;
                try { cp = allies[k].position(); } catch (...) {}
            }
            return true;
        });
        if (ck >= 0) {
            int claim = static_cast<int>(claim_value(s, read_sm(), ck)) - 1;
            if (claim >= 0 && claim < static_cast<int>(s.groups.size())) {
                if (claim != s.target) {
                    s.target = claim;
                    s.target_round = round;
                    s.cap_start = -1;
                    write_claim(s, claim);
                }
            } else if (cp && dist(*cp, pos) > PR.twinfarm && !s.my_spawn.is_set(*cp)) {
                g_farm = "twin-join";
                drop_target(s);
                bc::bitboard ring;
                ring.draw_chebyshev(*cp, 2.0f);
                step_towards(s, me, ring, false);
                return;
            }
        }
    }

    // Committed = a camp of our group is already damaged, or we are capturing.
    bool committed = false;
    if (s.target >= 0) {
        Group& g = s.groups[s.target];
        if (s.cap_start >= 0 && g.mask.is_set(pos)) committed = true;
        // A cleared camp awaiting capture is also committed. Otherwise the
        // retarget timer can redirect us between the final kill and the loot.
        if (P_CAPTURE_RECALL_FIX && g.reward_seen == round) committed = true;
        for (auto& c : camps)
            if (g.mask.is_set(c.spawn_position()) &&
                attempt([&] { return c.health() > 0 && c.health() < c.max_health(); }))
                committed = true;
    }
    bool expired = s.target >= 0 && (s.groups[s.target].bad_until > round ||
                                     s.groups[s.target].next_ok > round + (P_RESPAWN ? dist(pos, s.groups[s.target].center) + P_RESPAWN : 0));
    int target_refresh = 20;
#if defined(P_E_RETARGET) && P_E_RETARGET > 0
    target_refresh = P_E_RETARGET;
#endif
    // A damaged camp or active capture remains committed. Only travel plans
    // are reconsidered sooner when a more productive group becomes available.
    bool refresh = !committed && round - s.target_round >= (ball_on(s, round) ? 3 : target_refresh);
    if (P_FUELGUARD && (s.target < 0 || expired || refresh) && !can_choose(s)) {
        // Not enough fuel to choose and still act: a periodic re-choice waits for a later turn (we keep farming the
        // current target); with no usable target the turn ends here, cleanly, instead of being cut off half way
        // and finished one round late.
        if (s.target < 0 || expired) { g_farm = "fuel-wait"; return; }
        refresh = false;
    }
    if (s.target < 0 || expired || refresh) {
        int t = choose_target(s, me, round);
        if (t != s.target) s.cap_start = -1;
        s.target = t;
        s.target_round = round;
        write_claim(s, t);
    }
    g_farm = "travel";
    if (s.target < 0) {
        // Everything is on cooldown or claimed: wait out of reach of the respawning
        // group that frees up first (monsters hit at range 3; wait at 5).
        int wi = -1, wbest = 1 << 30;
        for (int i = 0; i < static_cast<int>(s.groups.size()); ++i) {
            Group& g = s.groups[i];
            if (g.gems + g.gold <= 0 || g.monolith || g.next_ok <= round || g.bad_until > round) continue;
            int w = g.next_ok - round + dist(pos, g.center) / 2;
            if (w < wbest) { wbest = w; wi = i; }
        }
        if (wi >= 0 && wbest < 120 && hp >= 0.6 * mhp) {
            g_farm = "wait";
            Group& g = s.groups[wi];
            bc::bitboard r5, r4;
            for (auto t : g.tiles) {
                r5.draw_chebyshev(t, 5.0f);
                r4.draw_chebyshev(t, 4.0f);
            }
            step_towards(s, me, r5 & ~r4, true);
            return;
        }
        g_farm = "no-target";
        if (!s.my_spawn.is_set(pos)) {
            if (hp < 0.9 * mhp && dist(pos, s.spawn_center) > 8) s.need_heal = round;
            else flee(s, me);
        }
        return;
    }
    Group& g = s.groups[s.target];
    attempt([&] {  // replay overlay: yellow line to the camp we are farming
        bc::debug::draw_line(pos, g.center, 0xFFD700);
        return true;
    });

    std::vector<const bc::camp*> live;
    for (auto& c : camps)
        if (g.mask.is_set(c.spawn_position()) && attempt([&] { return c.health() > 0; })) live.push_back(&c);

    if (!live.empty()) {
        s.cap_start = -1;
        s.probe_fail = 0;
        double rem = 0, str = 0;
        bool engaged = false;
        for (auto* c : live) {
            attempt([&] {
                rem += c->health();
                str += c->strength();
                if (c->health() < c->max_health()) engaged = true;
                return true;
            });
        }
        double dps = my_dps(s, me);
        double afford = std::max(1.0, hp - mhp * P_RESERVE_PCT / 100.0);
        int needed = squad_needed(rem, str, dps, afford);
        int here = 1 + allies_near(s, me, g.center, 7);
        int coming = 1 + count_claimers(s, read_sm(), s.target);
        const bool mono_go = (s.mono_only && g.monolith) || (P_JACKGO && g.jackpot && round >= P_JACKGO);
        if (mono_go) needed = std::min(needed, std::max(1, std::min(g.monolith ? s.roster : P_JACKN, s.roster)));
        if (!engaged && needed > here) {
            if (needed > std::max(coming, s.roster) || (!mono_go && needed > squad_needed(rem, str, dps, mhp * 0.75))) {
                g_farm = "too-strong";  // not even a full-health squad would do it
                g.bad_until = round + 60;
                drop_target(s);
                return;
            }
            if (PR.needheal) {  // a wait that no recall or ally will end: take another camp
                if (s.wait_group != s.target) { s.wait_group = s.target; s.wait_start = round; }
                bool recall_next = needed > coming && hp < 0.8 * mhp && dist(pos, s.spawn_center) > 6;
                if ((needed > coming && !recall_next) || round - s.wait_start > PR.needheal) {
                    g_farm = "wait-drop";
                    g.bad_until = round + 30;
                    s.wait_group = -1;
                    drop_target(s);
                    return;
                }
            }
            if (needed > coming) {
                g_farm = "need-heal";   // affordable with full health, not with this much
                s.need_heal = round;
                return;
            }
            g_farm = "rally";           // wait out of reach until the squad is here
            bc::bitboard r5, r4;
            for (auto* c : live) {
                r5.draw_chebyshev(c->position(), 5.0f);
                r4.draw_chebyshev(c->position(), 4.0f);
            }
            step_towards(s, me, r5 & ~r4, true);
            return;
        }
        g_farm = "fight-camp";
        s.wait_group = -1;
        if (hp < mhp * P_BAIL_PCT / 100.0) {
            g_farm = "bail";
            g.bad_until = round + 30;
            drop_target(s);
            bool awake_near = false;
            for (auto* c : live)
                if (dist(c->position(), pos) <= CAMP_RANGE && c->health() < c->max_health()) awake_near = true;
            if (awake_near) flee(s, me);
            return;
        }
        const bc::camp* tgt = live[0];
        for (auto* c : live)
            if (c->health() < tgt->health()) tgt = c;
        // Prefer a living camp already in basic range over walking to another
        // member of this same group. Keep the old choice if none is in range.
        if (P_U34_FARM_REACH && me.can_attack() && fuel_ok(12000)) {
            const int ar = static_cast<int>(me.attack_range());
            const bc::camp* local = nullptr;
            float lowest = 1e30f;
            int checked = 0;
            for (auto* c : live) {
                if (++checked > 8 || !fuel_ok(7000)) break;
                attempt([&] {
                    float health = c->health();
                    if (health > 0 && health < lowest && dist(pos, c->position()) <= ar) {
                        local = c;
                        lowest = health;
                    }
                    return true;
                });
            }
            if (local) { if (local != tgt) ++s.cf_reach; tgt = local; }
        }
        s.cf_recent_camp = round;
        engage(s, me, *tgt, tgt->position(), false, true);
        return;
    }

    // Nothing of this group is visible alive.
    if (g.reward_seen == round) {  // the engine says the reward is waiting: stand on it
        g_farm = "capture";
        if (P_ONE_CAP && other_captures(s, me, g, s.target)) {
            if (PR.capprio && g.mask.is_set(pos)) {
                if (!g_cap_other_on) return;  // keep the capture going until the champion that takes it arrives
                g_farm = "cap-handoff";
                g.bad_until = round + 12;
                drop_target(s);
                bc::bitboard r2;
                for (auto t : g.tiles) r2.draw_chebyshev(t, 2.0f);
                step_towards(s, me, r2 & ~g.mask, false);
                return;
            }
            if (cf_evac_reward(s, me, g, round, &camps)) return;
            if (g.mask.is_set(pos)) return; // retain capture if no safe purposeful step exists
            g_farm = "leave-reward";
            g.bad_until = round + 12;
            drop_target(s);
            if (P_STEPOFF && g.mask.is_set(pos)) {  // standing on the tiles would split the reward
                bc::bitboard r2;
                for (auto t : g.tiles) r2.draw_chebyshev(t, 2.0f);
                step_towards(s, me, r2 & ~g.mask, false);
            }
            return;
        }
        if (g.mask.is_set(pos)) {
            if (s.cap_start < 0) s.cap_start = round;
            if (round - s.cap_start > 12) {  // nothing came: someone else holds it
                g.next_ok = round + 20;
                drop_target(s);
            }
            return;
        }
        step_towards(s, me, g.mask, true);
        return;
    }
    if (g.next_ok > round) {  // refresh_groups saw it respawning
        if (P_RESPAWN && g.next_ok <= round + dist(pos, g.center) + P_RESPAWN) {
            g_farm = "wait-respawn";  // stand 2-3 tiles off its spawn tiles until it is back
            bc::bitboard r3, r1;
            for (auto t : g.tiles) {
                r3.draw_chebyshev(t, 3.0f);
                r1.draw_chebyshev(t, 1.0f);
            }
            bc::bitboard ring = r3 & ~r1;
            if (!ring.is_set(pos)) step_towards(s, me, ring, false);
            return;
        }
        drop_target(s);
        return;
    }
    // Alive but nothing visible: the monsters are hidden (bushes) or out of view.
    // Walk onto its spawn tiles; stepping into a hidden unit reveals it.
    g_farm = "approach";
    s.cap_start = -1;
    bc::bitboard goals = g.mask;
    if (g.mask.is_set(pos)) goals.set(pos, false);
    bool moved = step_towards(s, me, goals, true);
    if (!moved) {
        if (++s.probe_fail > 3) {
            g.bad_until = round + 25;
            drop_target(s);
            s.probe_fail = 0;
        }
    } else {
        s.probe_fail = 0;
    }
}

// ---------------------------------------------------------------------------
// One turn
// ---------------------------------------------------------------------------

// An AoE with cast range four and radius one can hit a visible champion five
// tiles away by aiming at a legal nearer centre. Ordinary targeted casts keep
// their existing scan/range; this is only a fallback when they did not cast.
