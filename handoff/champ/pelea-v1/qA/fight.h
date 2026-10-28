// fight.h - what a champion does once enemy champions are close.
// Included by main.cpp after its helpers (State, Foe, basic_attack, cast_offense, flee, retreat,
// write_sm). Every rule has a P_* switch in params.h; with all of them at 0 nothing here runs.
//
//   P_HITFIRST  1: when backing off, hit the weakest foe in reach first, then step (step 1 of the plan)
//   P_SAFESTEP  1: back off to the neighbouring tile the fewest foes can reach, ties toward an ally (step 2)
//   P_TWIN      1: Cassi never alone near foes (walks to the nearest ally); Issac stays within 2 of
//               Cassi while foes are within 8 of her (step 4: one death kills both)
//   P_CALLHELP  1: a champion that is hit names its attacker in shared memory; allies within
//               P_HELP_R tiles of that foe attack it when they are not outnumbered (step 3)

// P_KITE 1: ranged casters fight like the top-10 caster teams (VeryGood, Univardisty): step to a tile no
// foe can reach next round while keeping the target within spell range, stun the foe that can reach us,
// spend damage spells on the weakest foe within 4, shoot at range 3. P_KITE_OUT: give the fight to the
// old rules when the foes here outnumber us by more than this many bodies.

namespace fight {

// P_NOCHASE: walking away from us and out of our attack range (and not a 150+ gem bag): that fight is over.
inline bool gone(const Foe& f, bc::champion& me) {
    if (P_TEAM_FIGHT && P_TF_GLOBAL) {  // a hurt rival is never a finished fight (all fight paths)
        float mh = 1;
        try { mh = f.c.max_health(); } catch (...) {}
        if (f.hp < 0.5f * mh) return false;
    }
    return f.away && f.d > me.attack_range() && f.gems < P_CHASE_GEMS && !f.channeling;
}

// Shared memory has 8 bytes (measured: shared_memory.size() == 8) and 0-6 are taken by the farming
// code, so the help call packs into byte 7: enemy roster index + 1 in the low 3 bits, round & 31 above.
constexpr std::size_t SM_HELP = 7;

// How far a foe can hit next round: melee 2 (3 with a dash), ranged its range + 1.

// Combat-moves experiment: cooldown uses owner turn-end ticks. Treat <=1 as
// potentially ready at the next opportunity rather than asserting an exact
// initiative forecast. Missing/unreadable metadata keeps the original reach.
inline bool combat_moves_dash_soon(const bc::champion& c) {
    try {
        bool found = false;
        for (const auto& ab : c.abilities()) {
            if (!ab.is_dash()) continue;
            found = true;
            if (ab.cooldown() <= 1) return true;
        }
        return !found;
    } catch (...) {
        return true;
    }
}

inline int reach(const Foe& f) {
    int r = 1;
    attempt([&] {
        r = static_cast<int>(f.c.attack_range());
        return true;
    });
    if (r <= 1) {
        std::string n;
        attempt([&] {
            n = norm(bc::to_string(f.c.champion_name()));
            return true;
        });
        // Melee champions with a dash: Vendetta, Issac and Ren (Cassi is ranged and has none; the old list said
        // "cassi", so Issac's dash was missed). P_DASHFIX 0 keeps the old list for measuring.
        bool dash = starts_with(n, "vend") || starts_with(n, P_DASHFIX ? "issac" : "cassi") || starts_with(n, "ren");
        if (P_KINDFIX) attempt([&] {  // any melee champion with a dash ability (Heart of Ruin has one), read from the engine
            bool d = false;
            for (const auto& ab : f.c.abilities())
                if (ab.is_dash()) d = true;
            dash = d;
            return true;
        });
        if (!dash) return 2;
        return combat_moves_dash_soon(f.c) ? 3 : 2;
    }
    return r + 1;
}

inline int threats_at(vec2 t, const std::vector<Foe>& foes, const std::vector<int>& reaches) {
    int n = 0;
    for (std::size_t i = 0; i < foes.size(); ++i)
        if (dist(t, foes[i].p) <= reaches[i]) ++n;
    return n;
}

// Step 1: hit the weakest foe that is in reach right now. Returns true if we attacked.
inline bool hit_now(State& s, bc::champion& me, const std::vector<Foe>& foes) {
    // Measured: a ranged champion that attacks can no longer move this turn (64 of 64 Cassi hits on
    // packs), so ranged champions step first and shoot after (shoot_back) unless they are stuck anyway.
    if (me.attack_range() > 1 && me.can_move()) return false;
    vec2 pos = me.position();
    const Foe* best = nullptr;
    for (auto& f : foes) {
        if (f.hp <= 0 || dist(pos, f.p) > me.attack_range()) continue;
        if (!best || f.hp < best->hp) best = &f;
    }
    if (!best) return false;
    cast_offense(s, me, best->c, best->p, true);
    return basic_attack(s, me, best->c, best->p);
}

// Step 2: move to the neighbour (or dash target) that the fewest foes can reach next round;
// ties go to the tile nearest a healthy ally, then nearest home.
inline bool safe_step(State& s, bc::champion& me, const std::vector<Foe>& foes) {
    vec2 pos = me.position();
    std::vector<int> reaches;
    reaches.reserve(foes.size());
    for (auto& f : foes) reaches.push_back(reach(f));
    std::vector<vec2> allies;
    attempt([&] {
        for (auto& a : bc::vision::champions(*s.my))
            if (!(a == me) && a.is_alive() && a.health() > 0.4f * a.max_health()) allies.push_back(a.position());
        return true;
    });
    if (true) track::remembered_allies(allies, static_cast<int>(bc::round_number()));
    auto score = [&](vec2 t) {
        int ally = 30;
        for (auto a : allies) ally = std::min(ally, dist(t, a));
        return threats_at(t, foes, reaches) * 1000 + ally * 10 + dist(t, s.spawn_center);
    };
    bool moved = false;
    int here = score(pos);
    if (here >= 1000 && s.dash_slot >= 0 && me.can_cast()) {  // in reach of someone: dash if it helps
        auto ab = me.abilities()[s.dash_slot];
        if (ab.is_ready()) {
            std::optional<vec2> best;
            int bests = here;
            for (int dx = -2; dx <= 2; ++dx)
                for (int dy = -2; dy <= 2; ++dy) {
                    vec2 t = pos + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t)) continue;
                    int sc = score(t);
                    if (sc < bests - 500) { bests = sc; best = t; }
                }
            if (best && attempt([&] { return ab.use(*best); })) {
                moved = true;
                pos = me.position();
                here = score(pos);
            }
        }
    }
    if (me.can_move()) {
        std::optional<vec2> best;
        int bests = here;
        for (int dx = -1; dx <= 1; ++dx)
            for (int dy = -1; dy <= 1; ++dy) {
                if (!dx && !dy) continue;
                vec2 t = pos + vec2(dx, dy);
                if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t)) continue;
                int sc = score(t);
                if (sc < bests) { bests = sc; best = t; }
            }
        if (best && attempt([&] { return me.move_absolute(*best); })) moved = true;
    }
    return moved;
}

// Step 3, sender: name the closest foe as the one hitting us.
inline void call_help(State& s, const std::vector<Foe>& foes, int round) {
    const Foe* near = nullptr;
    for (auto& f : foes)
        if (!near || f.d < near->d) near = &f;
    if (!near || near->d > 4) return;
    int idx = -1;
    attempt([&] {
        auto roster = en_roster(s);
        for (std::size_t k = 0; k < roster.size(); ++k)
            if (roster[k] == near->c) idx = static_cast<int>(k);
        return true;
    });
    if (idx < 0) return;
    if (idx > 6) return;
    write_sm(SM_HELP, static_cast<std::uint8_t>((idx + 1) | ((round & 31) << 3)));
}

// Step 3, receiver: the foe an ally asked for help against in the last 2 rounds, if we can see it.
inline Foe* help_target(State& s, std::vector<Foe>& foes, int round) {
    int b = read_sm()[SM_HELP];
    int idx = (b & 7) - 1, r = b >> 3;
    if (idx < 0 || ((round - r) & 31) > 2) return nullptr;
    Foe* out = nullptr;
    attempt([&] {
        auto roster = en_roster(s);
        if (idx >= static_cast<int>(roster.size())) return false;
        for (auto& f : foes)
            if (f.c == roster[idx]) out = &f;
        return true;
    });
    return out;
}


// Backing off: optionally hit first, then step (safe tile, retreat or flee), then hit if we have not yet.
inline void back_off(State& s, bc::champion& me, const std::vector<Foe>& foes, int round) {
    bool hit = hit_now(s, me, foes);
    if (!safe_step(s, me, foes)) flee(s, me);

    if (!hit) shoot_back(s, me, foes);
    if (false) call_help(s, foes, round);
}


// P_FRONT: the user's fight doctrine (2026-10-14). Front to back: everybody hits one target, the
// foe closest to our group (weakest first on ties); ranged champions hold their range behind the
// melee and step away only as far as keeps that target in range; melee peel foes that reach our
// ranged; nobody chases or walks back, except to chase a foe carrying P_CHASE_GEMS+ gems.
// Returns false when this is not our fight (nothing close, or badly outnumbered): the old rules decide.
struct Mate {
    vec2 p;
    bool ranged;
};

inline bool hit_any(State& s, bc::champion& me, const std::vector<Foe*>& near) {
    const Foe* best = nullptr;
    vec2 pos = me.position();
    for (auto* f : near)
        if (dist(pos, f->p) <= me.attack_range() && (!best || f->hp < best->hp)) best = f;
    if (!best) return false;
    cast_offense(s, me, best->c, best->p, true);
    return basic_attack(s, me, best->c, best->p);
}

inline bool front_line(State& s, bc::champion& me, std::vector<Foe>& foes, int round) {
    vec2 pos = me.position();
    bool ranged = me.attack_range() > 1;
    int range = static_cast<int>(me.attack_range());
    std::vector<Mate> mates;
    double ours = me.health();
    attempt([&] {
        for (auto& a : bc::vision::champions(*s.my)) {
            try {
                if (a == me || !a.is_alive()) continue;
                vec2 p = a.position();
                if (dist(p, pos) > 9) continue;
                mates.push_back({p, a.attack_range() > 1});
                ours += a.health();
            } catch (...) {
            }
        }
        return true;
    });
    std::vector<Foe*> near;
    int nearest = 99;
    double theirs = 0;
    for (auto& f : foes) {
        if (f.d > 8 || s.en_spawn.is_set(f.p)) continue;
        near.push_back(&f);
        theirs += f.hp;
        if (!gone(f, me)) nearest = std::min(nearest, f.d);
    }
    if (near.empty()) return false;
    bool fighting = nearest <= P_FRONT_ZONE || (nearest <= P_FRONT_ZONE + 3 && round - s.hit_round <= 2);
    if (!fighting) return false;
    if (theirs * 100.0 > ours * P_FRONT_OUT) return false;
    {  // a team fight only: someone of ours close, and not outnumbered right here
        int mc = 0, fc = 0;
        double oc = me.health(), tc = 0;
        for (auto& m : mates)
            if (dist(m.p, pos) <= 4) ++mc;
        for (auto* f : near)
            if (f->d <= 5) { ++fc; tc += f->hp; }
        if (mc == 0 || fc > mc + 1) return false;
        attempt([&] {
            for (auto& a : bc::vision::champions(*s.my))
                try {
                    if (!(a == me) && a.is_alive() && dist(a.position(), pos) <= 4) oc += a.health();
                } catch (...) {
                }
            return true;
        });
        if (tc * 100.0 > oc * P_FRONT_OUT) return false;
    }

    long sx = X(pos), sy = Y(pos);
    for (auto& m : mates) { sx += X(m.p); sy += Y(m.p); }
    long n = 1 + static_cast<long>(mates.size());
    vec2 anchor(static_cast<std::int32_t>(sx / n), static_cast<std::int32_t>(sy / n));

    Foe* focus = nullptr;
    double best = 1e18;
    for (auto* f : near)  // the one exception to "no chasing": a big bag
        if (f->gems >= P_CHASE_GEMS && f->d * 10.0 - f->gems < best) { best = f->d * 10.0 - f->gems; focus = f; }
    bool chase = focus != nullptr;
    if (!focus && !ranged)  // melee peel: a foe on top of one of our ranged
        for (auto* f : near)
            for (auto& m : mates)
                if (m.ranged && dist(f->p, m.p) <= 2 && f->d <= P_FRONT_ZONE + 1) {
                    double sc = dist(f->p, m.p) * 100.0 + f->d * 10.0 + f->hp / 100.0;
                    if (sc < best) { best = sc; focus = f; }
                }
    if (!focus)
        for (auto* f : near) {
            if (gone(*f, me)) continue;
            double sc = dist(f->p, anchor) * 100.0 + f->hp / 10.0 - (f->channeling ? 150.0 : 0.0);
            if (sc < best) { best = sc; focus = f; }
        }
    if (!focus) return false;
    int d = focus->d;

    if (false) cast_offense(s, me, focus->c, focus->p, true);  // stun it before it reaches us
    if (!ranged) {
        if (d <= range) {
            cast_offense(s, me, focus->c, focus->p, true);
            basic_attack(s, me, focus->c, focus->p);
            return true;
        }
        if ((d <= P_FRONT_ZONE && !gone(*focus, me)) || chase) {
            engage(s, me, focus->c, focus->p, true, d <= 3 || chase);
            return true;
        }
        hit_any(s, me, near);  // hold the line
        return true;
    }

    // Ranged: is a foe about to reach us?
    bool threatened = false;
    for (auto* f : near)
        if (dist(pos, f->p) <= reach(*f) - 1) threatened = true;
    if (false) {
        bool cast = false;
        auto abs = me.abilities();
        for (int k = 0; k < 2 && !cast; ++k) {
            auto& ab = abs[k];
            if ((s.slots[k] != Slot::Targeted && s.slots[k] != Slot::Ground) || !ab.is_ready()) continue;
            if (s.slots[k] == Slot::Targeted) {
                if (!attempt([&] { return ab.can_target_enemies(); })) continue;
                cast = attempt([&] { return ab.use(focus->c); });
            } else {
                cast = attempt([&] { return ab.use(focus->p); });
            }
        }
        if (cast) {
            if (!me.can_move() || dist(pos, focus->p) <= range) {
                if (dist(pos, focus->p) <= range) basic_attack(s, me, focus->c, focus->p);
                else hit_any(s, me, near);
                return true;
            }
        }
    }
    if (threatened && me.can_move()) {  // kite: the tile that keeps the focus in range, farthest from foes
        auto score = [&](vec2 t) {
            int close = 99;
            for (auto* f : near) close = std::min(close, dist(t, f->p));
            bool inr = dist(t, focus->p) <= range;
            return (inr ? 1000 : 0) + close * 10 - dist(t, anchor);
        };
        std::optional<vec2> bt;
        int bs = score(pos);
        for (int dx = -1; dx <= 1; ++dx)
            for (int dy = -1; dy <= 1; ++dy) {
                if (!dx && !dy) continue;
                vec2 t = pos + vec2(dx, dy);
                if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t)) continue;
                int sc = score(t);
                if (sc > bs) { bs = sc; bt = t; }
            }
        if (bt) attempt([&] { return me.move_absolute(*bt); });
        pos = me.position();
    }
    if (false) cast_offense(s, me, focus->c, focus->p, true);
    if (dist(pos, focus->p) <= range) {
        cast_offense(s, me, focus->c, focus->p, true);
        basic_attack(s, me, focus->c, focus->p);
        return true;
    }
    bool front = false;  // one of our melee is already on the focus: step up to our range behind it
    for (auto& m : mates)
        if (!m.ranged && dist(m.p, focus->p) <= range) front = true;
    if (!threatened && ((front && !gone(*focus, me)) || chase)) {
        bc::bitboard ring;
        ring.draw_chebyshev(focus->p, static_cast<float>(range));
        step_towards(s, me, ring, chase);
        if (dist(me.position(), focus->p) <= range) {
            cast_offense(s, me, focus->c, focus->p, true);
            basic_attack(s, me, focus->c, focus->p);
            return true;
        }
    }
    hit_any(s, me, near);
    return true;
}

inline bool kite(State& s, bc::champion& me, std::vector<Foe>& foes, int round) {
    vec2 pos = me.position();
    int range = static_cast<int>(me.attack_range());
    std::vector<Foe*> near;
    for (auto& f : foes)
        if (f.d <= 7 && !s.en_spawn.is_set(f.p)) near.push_back(&f);
    if (near.empty()) return false;
    int closest = 99;
    for (auto* f : near) closest = std::min(closest, f->d);
    // P_KITE_ZONE: nobody within this many tiles and we were not hit: keep farming (two caster balls
    // facing each other at 6-7 tiles otherwise stand still for the whole game).
    if (closest > P_KITE_ZONE && round - s.hit_round > 2) return false;
    if (round - s.hit_round > 2) {  // the fight is over when everyone close is walking away
        bool live = false;
        for (auto* f : near)
            if (!gone(*f, me) && f->d <= SPELL_RANGE + 1) live = true;
        if (!live) return false;
    }
    int mc = 1, fc = 0;
    double oc = me.health(), tc = 0;
    std::vector<vec2> mates;
    attempt([&] {
        for (auto& a : bc::vision::champions(*s.my))
            try {
                if (a == me || !a.is_alive()) continue;
                vec2 p = a.position();
                if (dist(p, pos) > 6) continue;
                ++mc;
                oc += a.health();
                mates.push_back(p);
            } catch (...) {
            }
        return true;
    });
    for (auto* f : near)
        if (f->d <= 6) { ++fc; tc += f->hp; }
    if (fc > mc + P_KITE_OUT && tc * 100.0 > oc * P_GA_KITE_HP) return false;
    if (PR.outnum && fc >= mc + champ::outnum_margin(s)) return false;  // outnumbered: the fight step backs off
    std::vector<vec2> pull;  // P_KITEALLY: allies we kite toward
    if (PR.kiteally)
        attempt([&] {
            for (auto& a : bc::vision::champions(*s.my))
                try {
                    if (a == me || !a.is_alive() || a.is_recalling()) continue;
                    vec2 p = a.position();
                    if (dist(p, pos) <= PR.kiteally && !s.my_spawn.is_set(p)) pull.push_back(p);
                } catch (...) {
                }
            return true;
        });
    std::vector<int> reaches;
    for (auto* f : near) reaches.push_back(reach(*f));

    Foe* focus = nullptr;
    double best = 1e18;
    for (auto* f : near) {
        if (f->d > SPELL_RANGE + 1 || gone(*f, me)) continue;
        double sc = f->hp - (f->channeling ? 300.0 : 0.0) + f->d * 20.0;
        if (sc < best) { best = sc; focus = f; }
    }
    if (false) {  // the team's focus (P_FRONT's choice: the foe closest to our group) when in reach
        long sx = X(pos), sy = Y(pos);
        for (auto& m : mates) { sx += X(m); sy += Y(m); }
        long n = 1 + static_cast<long>(mates.size());
        vec2 anchor(static_cast<std::int32_t>(sx / n), static_cast<std::int32_t>(sy / n));
        Foe* tf = nullptr;
        double tb = 1e18;
        for (auto* f : near) {
            if (f->d > SPELL_RANGE + 1 || gone(*f, me)) continue;
            double sc = dist(f->p, anchor) * 100.0 + f->hp / 10.0 - (f->channeling ? 150.0 : 0.0);
            if (sc < tb) { tb = sc; tf = f; }
        }
        if (tf) focus = tf;
    }
    if (!focus)
        for (auto* f : near)
            if (!focus || f->d < focus->d) focus = f;

    if (vesper::kite_shoot_first(s, me, near, reaches, focus, pos, range, round)) return true;  // vesper.h (vkite-v1)
    if (me.can_move()) {  // 1. step: out of every foe's reach, focus within spell range, near the team
        auto score = [&](vec2 t) {
            int thr = 0;
            for (std::size_t i = 0; i < near.size(); ++i)
                if (dist(t, near[i]->p) <= reaches[i]) ++thr;
            int df = dist(t, focus->p);
            double sc = -1000.0 * thr + (df <= SPELL_RANGE ? 300.0 : 0.0) + (df <= range ? 100.0 : 0.0);
            if (focus->gems >= P_CHASE_GEMS) sc -= 10.0 * std::max(0, df - SPELL_RANGE);  // walk after it
            if (PR.kiteally) {
                int ad = 99;
                for (auto& m : pull) ad = std::min(ad, dist(t, m));
                if (ad < 99 && ad > 2) sc -= 60.0 * (ad - 2);
            } else if (!mates.empty()) {
                int ad = 99;
                for (auto& m : mates) ad = std::min(ad, dist(t, m));
                if (ad > 4) sc -= 50.0 * (ad - 4);
            }
            return sc;
        };
        double bs = score(pos);
        std::optional<vec2> bt;
        for (int dx = -1; dx <= 1; ++dx)
            for (int dy = -1; dy <= 1; ++dy) {
                if (!dx && !dy) continue;
                vec2 t = pos + vec2(dx, dy);
                if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t)) continue;
                double sc = score(t);
                if (sc > bs + 0.5) { bs = sc; bt = t; }
            }
        if (bt) attempt([&] { return me.move_absolute(*bt); });
        pos = me.position();
    }

    if (me.can_cast()) {  // 2. spells: stun whoever can reach us, else damage the focus, else stun it
        auto abs = me.abilities();
        Foe* threat = nullptr;
        for (std::size_t i = 0; i < near.size(); ++i) {
            int dd = dist(pos, near[i]->p);
            if (dd <= reaches[i] && dd <= SPELL_RANGE && (!threat || dd < dist(pos, threat->p))) threat = near[i];
        }
        bool cast = false;
        auto try_use = [&](bool want_cc, Foe* t) {
            for (int k = 0; k < 2 && !cast; ++k) {
                auto& ab = abs[k];
                if (s.slots[k] != Slot::Targeted && s.slots[k] != Slot::Ground) continue;
                bool cc = attempt([&] { return ab.is_cc(); });
                if (cc != want_cc || !ab.is_ready()) continue;
                if (s.slots[k] == Slot::Targeted) {
                    if (!attempt([&] { return ab.can_target_enemies(); })) continue;
                    cast = attempt([&] { return ab.use(t->c); });
                } else {
                    vec2 c = aoe_centre(s, me, k, t->p);
                    cast = attempt([&] { return ab.use(c); });
                }
            }
        };
        if (threat) try_use(true, threat);
        if (!cast && dist(pos, focus->p) <= SPELL_RANGE)  // an area spell that covers 2+ foes first
            for (int k = 0; k < 2 && !cast; ++k) {
                if (s.slots[k] != Slot::Ground || aoe_slot(me, k).radius <= 0 || !abs[k].is_ready()) continue;
                int hits = 0;
                vec2 c = aoe_centre(s, me, k, focus->p, &hits);
                if (hits >= 2) cast = attempt([&] { return abs[k].use(c); });
            }
        if (!cast && dist(pos, focus->p) <= SPELL_RANGE) try_use(false, focus);
        if (!cast && dist(pos, focus->p) <= SPELL_RANGE) try_use(true, focus);
    }

    if (dist(pos, focus->p) <= range) basic_attack(s, me, focus->c, focus->p);  // 3. shoot
    else hit_any(s, me, near);
    return true;
}


// ---------------------------------------------------------------------------------------------------
struct Unit {
    vec2 p;
    double hp, dps;
};

inline double unit_dps(const bc::champion& c) {  // a basic attack a round plus about one spell per cooldown
    double str = 60, foc = 0;
    attempt([&] {
        str = c.strength();
        return true;
    });
    attempt([&] {
        foc = c.focus();
        return true;
    });
    return std::max(10.0, str + foc * 1.5 / 8.0);
}

}  // namespace fight
