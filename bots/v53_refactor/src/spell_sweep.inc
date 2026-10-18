#if defined(P_SWEEP_LOG) && P_SWEEP_LOG >= 2
int g_sw[6];  // turns with a foe within 4: total, can't cast, channel, gate skip, no ready spell, cast
void sweep_dbg(State& s) {
    bc::champion& me = bc::self();
    if (!s.ready || !me.is_alive()) return;
    bool near = false;
    attempt([&] {
        for (auto& c : bc::vision::champions(*s.en))
            if (c.is_alive() && dist(c.position(), me.position()) <= SPELL_RANGE && !s.en_spawn.is_set(c.position())) near = true;
        return true;
    });
    if (!near) return;
    ++g_sw[0];
    if (!me.can_cast()) ++g_sw[1];
    else if (me.is_submitting_gems() || me.is_teleporting() || me.is_recalling()) ++g_sw[2];
    else {
        bool ready = false;
        auto abs = me.abilities();
        for (int k = 0; k < 2; ++k)
            if ((s.slots[k] == Slot::Targeted || s.slots[k] == Slot::Ground) && abs[k].is_ready()) ready = true;
        if (!ready) ++g_sw[4];
    }
    int r = static_cast<int>(bc::round_number());
    if (r % 50 == 0) std::printf("[swdbg] r=%d %s near=%d cantcast=%d channel=%d gate=%d noready=%d cast=%d mode=%s\n", r, s.name.c_str(), g_sw[0], g_sw[1], g_sw[2], g_sw[3], g_sw[4], g_sw[5], g_mode);
}
#endif

// pre = before the turn's move (P_SWEEP >= 3). P_SWEEP 5: a spell that roots us for the round is cast before
// moving only when standing is safe (hp >= 50%, no foe within 2, not outnumbered within 5); other spells always.
void spell_sweep(State& s, bool pre = false, bool free_only = false) {
    bc::champion& me = bc::self();
#if defined(P_SWEEP_LOG) && P_SWEEP_LOG >= 2
    sweep_dbg(s);
#endif
    if (!s.ready || !me.is_alive() || !me.can_cast()) return;
    if (me.is_submitting_gems() || me.is_teleporting() || me.is_recalling()) return;
    if (!fuel_ok(6000)) return;
    vec2 pos = me.position();
    std::vector<Foe> foes;
    for (auto& c : bc::vision::champions(*s.en))
        attempt([&] {
            if (!c.is_alive()) return false;
            Foe f{c, c.position(), c.health(), 0, 0, false};
            f.d = dist(f.p, pos);
            if (f.d > SPELL_RANGE || s.en_spawn.is_set(f.p)) return false;
            attempt([&] {
                f.gems = static_cast<int>(c.gem_count());
                f.channeling = c.is_submitting_gems() || c.is_recalling();
                return true;
            });
            foes.push_back(f);
            return true;
        });
    if (foes.empty()) {
        const bool roots_allowed = !P_CASTSAFE && !P_UNI_STAND && P_SWEEP != 5;
        if (cm_edge_aoe(s, me, roots_allowed, false, free_only)) g_mode = "sweep";
        return;
    }
    bool stand_ok = true;
    if (P_SWEEP == 5 && pre) {
        int nf = 0, na = 1;
        attempt([&] {
            for (auto& c : bc::vision::champions(*s.en))
                if (c.is_alive() && dist(c.position(), pos) <= 5) ++nf;
            for (auto& a : bc::vision::champions(*s.my))
                if (!(a == me) && a.is_alive() && dist(a.position(), pos) <= 4) ++na;
            return true;
        });
        for (auto& f : foes)
            if (f.d <= 2) stand_ok = false;
        if (me.health() < 0.5f * me.max_health() || nf > na + P_SW5_OUT || na < P_SW5_ALLY) stand_ok = false;
    }
    // P_UNI_STAND: with the caster draft, a spell that roots us is cast before moving only when no melee foe can
    // reach us next round and we have P_UNI_STAND_HP% hp; else we step first (v27's Stellar died from 60%+ hp in
    // 50 of 83 deaths, rooted by its own casts while melee closed from 4 to 1 tiles; the #1's Stellar holds 4-5)
    bool guard = pre && (P_SWEEP == 5 || (P_UNI_STAND && s.casters));
    if (P_UNI_STAND && s.casters && pre) {
        if (me.health() < P_UNI_STAND_HP / 100.0f * me.max_health()) stand_ok = false;
        for (auto& c : bc::vision::champions(*s.en))
            attempt([&] {
                if (!c.is_alive() || s.en_spawn.is_set(c.position())) return false;
                Foe f{c, c.position(), c.health(), dist(c.position(), pos), 0, false};
                if (f.d <= 2 || (c.attack_range() <= 1 && f.d <= fight::reach(f))) stand_ok = false;
                return true;
            });
    }
    // P_CASTSAFE: should this turn escape instead of standing to cast a spell that roots us?
    bool escape = false;
    if (P_CASTSAFE && pre) {
        float hpr = me.health() / std::max(1.0f, me.max_health());
        if (hpr * 100 < ((P_UNI_FLEE && P_DRAFTUNI && s.casters) ? P_UNI_FLEE : P.flee_pct)) {
            escape = true;  // play_turn will run or recall this round: a rooting cast would cancel the step
        } else {
            std::vector<Threat> th;
            attempt([&] {
                for (auto& c : bc::vision::champions(*s.en)) {
                    if (!c.is_alive() || s.en_spawn.is_set(c.position())) continue;
                    int ar = static_cast<int>(c.attack_range());
                    th.push_back(threat_of(c, c.position(), ar <= 1 ? 2 : ar + 1));
                }
                return true;
            });
            double here = danger_at(th, pos), lim = me.health() * P_CASTSAFE / 100.0;
            if (here >= lim) {
                for (int dx = -1; dx <= 1 && !escape; ++dx)
                    for (int dy = -1; dy <= 1 && !escape; ++dy) {
                        vec2 t = pos + vec2(dx, dy);
                        if ((!dx && !dy) || !bc::map::is_in_bounds(t) || s.blocked.is_set(t)) continue;
                        if (danger_at(th, t) < std::min(lim, 0.7 * here)) escape = true;
                    }
            }
        }
    }
    auto kills = [&](int k, const Foe& t) {
        const SpellInfo& si = spells_of(me).k[k];
        double foc = 0;
        attempt([&] {
            foc = me.focus();
            return true;
        });
        return (si.kind == 2 || si.kind == 3) && si.mod * foc >= t.hp;
    };
    Foe* threat = nullptr;
    Foe* weak = nullptr;
    for (auto& f : foes) {
        if (f.d <= fight::reach(f) && (!threat || f.d < threat->d)) threat = &f;
        auto wsc = [&](const Foe& x) {  // P_SQUISHY: sparring only, prefer ranged targets (real caster teams hit our Stellar more)
            double v = x.hp - (x.channeling ? 300 : 0) - 5.0 * x.gems;
            if (P_SQUISHY) attempt([&] { if (x.c.attack_range() > 1) v -= P_SQUISHY; return true; });
            return v;
        };
        if (!weak || wsc(f) < wsc(*weak)) weak = &f;
    }
    if (P_SWEEP == 4) {  // before the turn: only when we were hit lately, a foe can reach us, or the foe is hurt / channeling
        const int round = static_cast<int>(bc::round_number());
        bool fighting = round - s.hit_round <= 3 || weak->channeling || threat;
        float mh = 0;
        attempt([&] {
            mh = weak->c.max_health();
            return true;
        });
        if (mh > 0 && weak->hp < 0.6f * mh) fighting = true;
        if (!fighting) return;
    }
    if (s.sweep == 2) {  // only in a fight: we were hit, we are in a fight mode, or the foe is hurt / channeling
        const int round = static_cast<int>(bc::round_number());
        std::string m = g_mode;
        bool fighting = round - s.hit_round <= 3 || weak->channeling ||
                        !(m == "farm" || m == "tribute" || m == "recall-shop" || m == "walk-home" || m == "unstick");
        float mh = 0;
        attempt([&] {
            mh = weak->c.max_health();
            return true;
        });
        if (mh > 0 && weak->hp < 0.6f * mh) fighting = true;
#if defined(P_SWEEP_LOG) && P_SWEEP_LOG >= 2
        if (!fighting) ++g_sw[3];
#endif
        if (!fighting) return;
    }
    auto abs = me.abilities();
    bool cast = false;
    auto try_use = [&](bool want_cc, Foe* t) {
        for (int k = 0; k < 2 && !cast; ++k) {
            auto& ab = abs[k];
            if (s.slots[k] != Slot::Targeted && s.slots[k] != Slot::Ground) continue;
            bool cc = attempt([&] { return ab.is_cc(); });
            if (cc != want_cc || !ab.is_ready()) continue;
            if (free_only && slot_exclusive(s, me, k)) continue;
            bool ex = guard && slot_exclusive(s, me, k);
            if (ex && pre && !stand_ok) continue;
            if (escape && slot_exclusive(s, me, k) && !kills(k, *t)) {
#ifdef P_FXLOG
                std::printf("[cs] r=%d %s skip slot%d hp=%.0f\n", static_cast<int>(bc::round_number()), s.name.c_str(), k, me.health());
#endif
                continue;
            }
#if defined(P_SWEEP_LOG) && P_SWEEP_LOG >= 3
            try {
                bool ok = s.slots[k] == Slot::Targeted ? ab.use(t->c) : ab.use(t->p);
                if (!ok) std::printf("[swfail] r=%d %s slot%d returned false d=%d\n", static_cast<int>(bc::round_number()), s.name.c_str(), k, t->d);
                cast = ok;
            } catch (const std::exception& e) {
                std::printf("[swfail] r=%d %s slot%d d=%d: %s\n", static_cast<int>(bc::round_number()), s.name.c_str(), k, t->d, e.what());
            }
            continue;
#endif
            if (s.slots[k] == Slot::Targeted) {
                if (!attempt([&] { return ab.can_target_enemies(); })) continue;
                cast = attempt([&] { return ab.use(t->c); });
            } else {
                vec2 c = P_AOE ? aoe_centre(s, me, k, t->p) : t->p;
                cast = attempt([&] { return ab.use(c); });
            }
            if (cast && ex && pre) s.rooted_r = static_cast<int>(bc::round_number());
        }
    };
    if (threat) try_use(true, threat);
    if (!cast && P_AOE >= 2) {  // an area spell that covers 2+ foes beats a single-target one
        for (int k = 0; k < 2 && !cast; ++k) {
            if (s.slots[k] != Slot::Ground || aoe_slot(me, k).radius <= 0 || !abs[k].is_ready()) continue;
            if (free_only && slot_exclusive(s, me, k)) continue;
            bool ex = guard && slot_exclusive(s, me, k);
            if (ex && pre && !stand_ok) continue;
            if (escape && slot_exclusive(s, me, k) && !kills(k, *weak)) continue;
            int hits = 0;
            vec2 c = aoe_centre(s, me, k, weak->p, &hits);
            if (hits < 2) continue;
            cast = attempt([&] { return abs[k].use(c); });
            if (cast && ex && pre) s.rooted_r = static_cast<int>(bc::round_number());
        }
    }
    if (!cast) try_use(false, weak);
    if (!cast) try_use(true, weak);
    if (!cast) cast = cm_edge_aoe(s, me, !guard || stand_ok, guard && pre, free_only, escape);
#ifdef P_SWEEP_LOG
    if (cast) std::printf("[sweep] r=%d %s mode=%s hit=%d tgt_d=%d canmove=%d canatk=%d\n", static_cast<int>(bc::round_number()), s.name.c_str(), g_mode,
                          static_cast<int>(bc::round_number()) - s.hit_round, weak->d, me.can_move() ? 1 : 0, me.can_attack() ? 1 : 0);
#endif
#if defined(P_SWEEP_LOG) && P_SWEEP_LOG >= 2
    if (cast) ++g_sw[5];
#endif
    if (cast) g_mode = "sweep";
}

// P_SWEEP 5: we cast a rooting spell this round, so the turn's steps failed: shoot the weakest foe in reach.
void shoot_rooted(State& s) {
    bc::champion& me = bc::self();
    if (!me.is_alive() || !me.can_attack()) return;
    vec2 pos = me.position();
    std::vector<Foe> foes;
    for (auto& c : bc::vision::champions(*s.en))
        attempt([&] {
            if (!c.is_alive() || s.en_spawn.is_set(c.position())) return false;
            foes.push_back(Foe{c, c.position(), c.health(), dist(c.position(), pos), 0, false});
            return true;
        });
    shoot_back(s, me, foes);
}

