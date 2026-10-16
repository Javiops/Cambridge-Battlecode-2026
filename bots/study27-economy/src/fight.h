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

#ifndef P_HITFIRST
#define P_HITFIRST 0
#endif
#ifndef P_SAFESTEP
#define P_SAFESTEP 0
#endif
#ifndef P_CALLHELP
#define P_CALLHELP 0
#endif
#ifndef P_TWIN
#define P_TWIN 0
#endif
#ifndef P_HELP_R
#define P_HELP_R 6
#endif
// P_KITE 1: ranged casters fight like the top-10 caster teams (VeryGood, Univardisty): step to a tile no
// foe can reach next round while keeping the target within spell range, stun the foe that can reach us,
// spend damage spells on the weakest foe within 4, shoot at range 3. P_KITE_OUT: give the fight to the
// old rules when the foes here outnumber us by more than this many bodies.
#ifndef P_FRONT_STAND
#define P_FRONT_STAND 0
#endif
#ifndef P_KITE
#define P_KITE 0
#endif
#ifndef P_KITE_OUT
#define P_KITE_OUT 1
#endif
#ifndef P_KITE_ZONE
#define P_KITE_ZONE 0
#endif
#ifndef P_DASHFIX
#define P_DASHFIX 1
#endif
// P_KITEFRONT (2026-10-15 fix list): P_KITE ran before P_FRONT, so a caster that kited never used the front-line
// doctrine. 1 = P_FRONT runs first and kite only when the front line declines the turn; 2 = kite keeps the turn
// but shoots the team's focus (the foe closest to our group, P_FRONT's choice) instead of its own.
#ifndef P_KITEFRONT
#define P_KITEFRONT 0
#endif

namespace fight {

// P_NOCHASE: walking away from us and out of our attack range (and not a 150+ gem bag): that fight is over.
inline bool gone(const Foe& f, bc::champion& me) {
    return P_NOCHASE && f.away && f.d > me.attack_range() && f.gems < P_CHASE_GEMS && !f.channeling;
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
        auto roster = bc::champions(*s.en);
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
        auto roster = bc::champions(*s.en);
        if (idx >= static_cast<int>(roster.size())) return false;
        for (auto& f : foes)
            if (f.c == roster[idx]) out = &f;
        return true;
    });
    return out;
}


// Step 4: Cassi and Issac share one life. Returns true if this turn's move was used.
inline bool twin_guard(State& s, bc::champion& me, const std::vector<Foe>& foes) {
    bool cassi = starts_with(s.name, "cassi"), issac = starts_with(s.name, "issac");
    if (!cassi && !issac) return false;
    vec2 pos = me.position();
    std::optional<vec2> partner, nearest;
    int nd = 99;
    attempt([&] {
        for (auto& a : bc::vision::champions(*s.my)) {
            if (a == me || !a.is_alive()) continue;
            vec2 ap = a.position();
            if (dist(ap, pos) < nd) { nd = dist(ap, pos); nearest = ap; }
            std::string n = norm(bc::to_string(a.champion_name()));
            if ((issac && starts_with(n, "cassi")) || (cassi && starts_with(n, "issac"))) partner = ap;
        }
        return true;
    });
    if (cassi) {
        int fd = 99;
        for (auto& f : foes) if (!s.en_spawn.is_set(f.p)) fd = std::min(fd, f.d);
        if (fd > 8 || nd <= 3 || !nearest) return false;
        vec2 goal = partner && dist(*partner, pos) <= nd + 4 ? *partner : *nearest;
        bool hit = hit_now(s, me, foes);
        bc::bitboard ring;
        ring.draw_chebyshev(goal, 1.0f);
        bool moved = step_towards(s, me, ring, true);
        if (!hit) shoot_back(s, me, foes);
        return moved || hit;
    }
    if (!partner || dist(*partner, pos) <= 2) return false;
    int fd = 99;
    for (auto& f : foes) fd = std::min(fd, dist(f.p, *partner));
    if (fd > 8) return false;
    bool hit = hit_now(s, me, foes);
    bc::bitboard ring;
    ring.draw_chebyshev(*partner, 1.0f);
    bool moved = step_towards(s, me, ring, true);
    return moved || hit;
}

// Backing off: optionally hit first, then step (safe tile, retreat or flee), then hit if we have not yet.
inline void back_off(State& s, bc::champion& me, const std::vector<Foe>& foes, int round) {
    bool hit = P_HITFIRST && hit_now(s, me, foes);
#ifdef P_PROBE
    std::printf("[hf] r=%d %s range=%.0f hit=%d move=%d\n", round, s.name.c_str(), static_cast<double>(me.attack_range()), hit ? 1 : 0, me.can_move() ? 1 : 0);
#endif
    if (P_SAFESTEP) {
        if (!safe_step(s, me, foes)) flee(s, me);
    } else if (P_RETREAT) {
        retreat(s, me, foes);
    } else {
        flee(s, me);
    }
    if (!hit) shoot_back(s, me, foes);
    if (P_CALLHELP && round - s.hit_round <= 1) call_help(s, foes, round);
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
    if (P_FRONT_LOCAL) {  // a team fight only: someone of ours close, and not outnumbered right here
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

    if (P_FRONT_CAST && d <= SPELL_RANGE) cast_offense(s, me, focus->c, focus->p, true);  // stun it before it reaches us
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
    // P_FRONT_STAND: nobody can reach us next round and the focus is within spell range: stand and cast first
    // (Tavi's, Cassi's and Ryth's damage spells cannot be cast in a round we step), then shoot. The top 4's casters
    // stand still in 46-50% of the rounds an enemy is within 4; ours 33-39%, and step away in 36-47%.
    if (P_FRONT_STAND && !threatened && focus->d <= SPELL_RANGE && me.can_cast()) {
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
    if (P_FRONT_CAST && dist(pos, focus->p) <= SPELL_RANGE) cast_offense(s, me, focus->c, focus->p, true);
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
    if (P_KITE_ZONE && closest > P_KITE_ZONE && round - s.hit_round > 2) return false;
    if (P_NOCHASE && round - s.hit_round > 2) {  // the fight is over when everyone close is walking away
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
    if (fc > mc + P_KITE_OUT && tc > oc * 1.3) return false;
    std::vector<int> reaches;
    for (auto* f : near) reaches.push_back(reach(*f));

    Foe* focus = nullptr;
    double best = 1e18;
    for (auto* f : near) {
        if (f->d > SPELL_RANGE + 1 || gone(*f, me)) continue;
        double sc = f->hp - (f->channeling ? 300.0 : 0.0) + f->d * 20.0;
        if (P_SQUISHY) attempt([&] { if (f->c.attack_range() > 1) sc -= P_SQUISHY; return true; });
        if (sc < best) { best = sc; focus = f; }
    }
    if (P_KITEFRONT == 2 && focus) {  // the team's focus (P_FRONT's choice: the foe closest to our group) when in reach
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

    if (me.can_move()) {  // 1. step: out of every foe's reach, focus within spell range, near the team
        auto score = [&](vec2 t) {
            int thr = 0;
            for (std::size_t i = 0; i < near.size(); ++i)
                if (dist(t, near[i]->p) <= reaches[i]) ++thr;
            int df = dist(t, focus->p);
            double sc = -1000.0 * thr + (df <= SPELL_RANGE ? 300.0 : 0.0) + (df <= range ? 100.0 : 0.0);
            if (!P_NOCHASE || focus->gems >= P_CHASE_GEMS) sc -= 10.0 * std::max(0, df - SPELL_RANGE);  // walk after it
            if (!mates.empty()) {
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
                    vec2 c = P_AOE ? aoe_centre(s, me, k, t->p) : t->p;
                    cast = attempt([&] { return ab.use(c); });
                }
            }
        };
        if (threat) try_use(true, threat);
        if (!cast && P_AOE >= 2 && dist(pos, focus->p) <= SPELL_RANGE)  // an area spell that covers 2+ foes first
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
// P_FM: the fight mode (2026-10-14 "Rehacer la pelea"). Online the top 4 stand still in 46-50% of the
// rounds an enemy is within 4 and step closer in 22-26%; we stepped away in 36-47% and kept farming or
// backing off in 60% of those rounds. Damage spells of Tavi, Cassi and Ryth root the caster for the
// round (exclusive_with_movement), so a ranged champion that wants to cast must stand.
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

// Stuns first, then damage; rooting spells only when allowed.
inline bool cast_at(State& s, bc::champion& me, const Foe& t, bool allow_root, bool stun_only) {
    if (!me.can_cast() || dist(me.position(), t.p) > SPELL_RANGE) return false;
    auto abs = me.abilities();
    for (int pass = 0; pass < 2; ++pass)
        for (int k = 0; k < 2; ++k) {
            auto& ab = abs[k];
            if (s.slots[k] != Slot::Targeted && s.slots[k] != Slot::Ground) continue;
            if (!ab.is_ready()) continue;
            bool cc = attempt([&] { return ab.is_cc(); });
            if ((pass == 0) != cc || (stun_only && !cc)) continue;
            if (!allow_root && slot_exclusive(s, me, k)) continue;
            bool ok = false;
            if (s.slots[k] == Slot::Targeted) {
                if (!attempt([&] { return ab.can_target_enemies(); })) continue;
                ok = attempt([&] { return ab.use(t.c); });
            } else {
                ok = attempt([&] { return ab.use(t.p); });
            }
            if (ok) return true;
        }
    return false;
}

// P_FM 2: the volley model. Every damage spell of the casters we meet is exclusive_with_movement
// (probe 2026-10-14: Stellar 2.0 x focus and a radius-1 area 1.4 x focus, Tavi 2.2 x focus with a
// 1-round stun, Cassi 2.0 x focus; only Cassi's pure stun is free): a caster that steps cannot cast it
// that round. So a ready caster threatens only the tiles within its spell range of where it stands,
// and whoever walks into range eats the first volley (~550 from three). Enemy cooldowns are readable:
// hold just outside the range of ready casters, cast first when they walk in, step in when their
// spells are down.
// Rounds until our own damage or stun spell is ready (0 = ready now).
inline int my_spell_cd(State& s, bc::champion& me) {
    int best = 99;
    attempt([&] {
        auto abs = me.abilities();
        for (int k = 0; k < 2; ++k) {
            if (s.slots[k] != Slot::Targeted && s.slots[k] != Slot::Ground) continue;
            if (!attempt([&] { return abs[k].is_damage() || abs[k].is_aoe_damage() || abs[k].is_cc(); })) continue;
            best = std::min(best, static_cast<int>(abs[k].cooldown()));
        }
        return true;
    });
    return best;
}

// Move to the best of our tile and its neighbours (next best when a tile is taken). False if we stay.
template <class F>
inline bool step_best(State& s, bc::champion& me, F score) {
    if (!me.can_move()) return false;
    vec2 pos = me.position();
    double here = score(pos);
    std::vector<std::pair<double, vec2>> c;
    for (int dx = -1; dx <= 1; ++dx)
        for (int dy = -1; dy <= 1; ++dy) {
            if (!dx && !dy) continue;
            vec2 t = pos + vec2(dx, dy);
            if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t)) continue;
            double sc = score(t);
            if (sc > here) c.push_back({sc, t});
        }
    std::sort(c.begin(), c.end(), [](auto& a, auto& b) { return a.first > b.first; });
    for (auto& [sc, t] : c)
        if (attempt([&] { return me.move_absolute(t); })) return true;
    return false;
}

inline bool fight_mode(State& s, bc::champion& me, std::vector<Foe>& foes, int round) {
    vec2 pos = me.position();
    bool ranged = me.attack_range() > 1;
    int range = static_cast<int>(me.attack_range());
    std::vector<Foe*> near;
    int nearest = 99;
    for (auto& f : foes) {
        if (f.d > P_FM_R + 2 || s.en_spawn.is_set(f.p)) continue;
        near.push_back(&f);
        if (!gone(f, me)) nearest = std::min(nearest, f.d);
    }
    if (near.empty() || nearest > P_FM_R) {
        s.fm = 0;
        s.fm_hold = 0;
        return false;
    }
    // Our side: me and the allies within 5 that are not recalling.
    std::vector<Unit> us{{pos, me.health(), unit_dps(me)}};
    std::vector<Mate> mates;
    attempt([&] {
        for (auto& a : bc::vision::champions(*s.my)) {
            try {
                if (a == me || !a.is_alive() || a.is_recalling()) continue;
                vec2 p = a.position();
                if (dist(p, pos) > 5) continue;
                us.push_back({p, a.health(), unit_dps(a)});
                mates.push_back({p, a.attack_range() > 1});
            } catch (...) {
            }
        }
        return true;
    });
    double oh = 0, od = 0, th = 0, td = 0;
    long cx = 0, cy = 0;
    for (auto& u : us) { oh += u.hp; od += u.dps; cx += X(u.p); cy += Y(u.p); }
    vec2 centre(static_cast<std::int32_t>(cx / static_cast<long>(us.size())), static_cast<std::int32_t>(cy / static_cast<long>(us.size())));
    for (auto* f : near)
        if (f->d <= 6) { th += f->hp; td += unit_dps(f->c); }
    // P_FM 2: the threat of every foe close by, and the volley each side has ready.
    std::vector<Threat> thr;
    double their_ready = 0, our_ready = 0;
    if (P_FM >= 2) {
        for (auto* f : near) {
            thr.push_back(threat_of(f->c, f->p, reach(*f)));
            if (f->d <= 6) their_ready += thr.back().ready;
        }
        our_ready += threat_of(me, pos, 1).ready;
        attempt([&] {
            for (auto& a : bc::vision::champions(*s.my)) {
                try {
                    if (a == me || !a.is_alive() || a.is_recalling() || dist(a.position(), pos) > 5) continue;
                    our_ready += threat_of(a, a.position(), 1).ready;
                } catch (...) {
                }
            }
            return true;
        });
        if (P_FM_VR) {  // trade the volleys first, then Lanchester on what is left
            oh = std::max(0.3 * oh, oh - their_ready);
            th = std::max(0.3 * th, th - our_ready);
        }
    }
    double ratio = (oh * od) / std::max(1.0, th * td);  // Lanchester: health x damage
    float hpr = me.health() / std::max(1.0f, me.max_health());
    bool was = s.fm == 1 && round - s.fm_r <= 2;
    bool fight = ratio * 100.0 >= (was ? P_FM_STAY : P_FM_ENTER) && hpr * 100 >= P_FM_LOWHP;

    // One focus for everybody: low health, channelling or a big bag, near our group.
    Foe* focus = nullptr;
    double best = 1e18;
    for (auto* f : near) {
        if (gone(*f, me) || f->d > P_FM_R + 1) continue;
        double sc = f->hp - (f->channeling ? 300.0 : 0.0) - 3.0 * f->gems + 30.0 * dist(f->p, centre);
        if (f->gems >= P_CHASE_GEMS) sc -= 1000.0;
        if (sc < best) { best = sc; focus = f; }
    }
    if (!focus) {
        s.fm = 0;
        return false;
    }
    // Melee foes that can be on top of us next round.
    std::vector<Foe*> divers;
    for (auto* f : near)
        if (f->d <= 2 && reach(*f) <= 2) divers.push_back(f);

#ifdef P_FM_LOG
    std::printf("[fm] r=%d %s hp=%.0f ratio=%.2f their=%.0f our=%.0f here=%.0f near=%d fight=%d\n", round, s.name.c_str(), me.health(), ratio, their_ready,
                our_ready, P_FM >= 2 ? danger_at(thr, pos) : 0.0, nearest, fight ? 1 : 0);
#endif
    if (!fight) {  // retreat towards our allies, stun whoever follows, shoot back after the step
        s.fm = 2;
        s.fm_r = round;
        if (!divers.empty()) cast_at(s, me, *divers.front(), false, true);
        if (P_FM >= 2 && P_FM_RET) {  // out of the ready volleys first, then away and towards allies and home
            double myhp = me.health();
            bool moved = step_best(s, me, [&](vec2 t) {
                double dg = danger_at(thr, t);
                int nf = 9;
                for (auto* f : near) nf = std::min(nf, dist(t, f->p));
                int mate = 30;
                for (auto& m : mates) mate = std::min(mate, dist(t, m.p));
                return -dg - (dg >= myhp * P_FM_VOL / 100.0 ? 5000.0 : 0.0) + 40.0 * std::min(nf, 6) - 10.0 * std::max(0, mate - 3) -
                       5.0 * dist(t, s.spawn_center);
            });
            if (!moved && danger_at(thr, me.position()) <= 0) flee(s, me);
        } else if (!safe_step(s, me, foes)) flee(s, me);
        shoot_back(s, me, foes);
        Foe* close = nullptr;
        for (auto* f : near)
            if (!close || dist(me.position(), f->p) < dist(me.position(), close->p)) close = f;
        if (close) cast_at(s, me, *close, false, false);
        return true;
    }
    s.fm = 1;
    s.fm_r = round;

    if (!ranged) {  // melee: peel a foe on top of our ranged, else the focus
        Foe* tgt = focus;
        double pb = 1e18;
        for (auto* f : near)
            for (auto& m : mates)
                if (m.ranged && dist(f->p, m.p) <= 2 && f->d <= 3) {
                    double sc = dist(f->p, m.p) * 100.0 + f->hp / 100.0;
                    if (sc < pb) { pb = sc; tgt = f; }
                }
        if (tgt->d <= range) {
            cast_at(s, me, *tgt, true, false);
            basic_attack(s, me, tgt->c, tgt->p);
            return true;
        }
        if (P_FM >= 2 && me.can_move()) {  // do not walk alone into a ready volley
            double myhp = me.health();
            vec2 tp = tgt->p;
            std::optional<vec2> nxt;
            for (int dx = -1; dx <= 1; ++dx)
                for (int dy = -1; dy <= 1; ++dy) {
                    vec2 t = pos + vec2(dx, dy);
                    if ((dx || dy) && bc::map::is_in_bounds(t) && !s.blocked.is_set(t) && (!nxt || dist(t, tp) < dist(*nxt, tp))) nxt = t;
                }
            if (nxt && danger_at(thr, *nxt) >= myhp * P_FM_VOL / 100.0) {
                step_best(s, me, [&](vec2 t) {
                    double dg = danger_at(thr, t);
                    return -(dg >= myhp * P_FM_VOL / 100.0 ? 5000.0 : 0.0) - 0.1 * dg - 40.0 * dist(t, tp);
                });
                if (dist(me.position(), tp) <= range) basic_attack(s, me, tgt->c, tp);
                else hit_any(s, me, near);
                return true;
            }
        }
        engage(s, me, tgt->c, tgt->p, true, tgt->d <= 3);
        return true;
    }

    if (P_FM >= 2) {  // ranged with the volley model
        double myhp = me.health();
        auto lethal = [&](double dg) { return dg >= myhp * P_FM_VOL / 100.0; };
        int cd = me.can_cast() ? my_spell_cd(s, me) : 99;
        // 1. A foe within our spell range and our spell is up: stand and cast first, then shoot.
        Foe* inr = focus->d <= SPELL_RANGE ? focus : nullptr;
        for (auto* f : near)
            if (!inr && f->d <= SPELL_RANGE && !gone(*f, me)) inr = f;
        if (inr) s.fm_hold = 0;
        if (cd == 0 && inr && (!lethal(danger_at(thr, pos)) || !me.can_move())) {
            cast_at(s, me, *inr, true, false);
            if (dist(pos, focus->p) <= range) basic_attack(s, me, focus->c, focus->p);
            else hit_any(s, me, near);
            return true;
        }
        // 2. Waiting at the edge too long with nobody coming in: back to the old rules (farm).
        if (!inr && P_FM_HOLD > 0 && ++s.fm_hold > P_FM_HOLD && !lethal(danger_at(thr, pos))) return false;
        // 3. Pick the tile: never into a lethal volley, step in when theirs are down and ours is up.
        bool moved = step_best(s, me, [&](vec2 t) {
            double dg = danger_at(thr, t);
            double sc = -dg - (lethal(dg) ? 5000.0 : 0.0);
            int df = dist(t, focus->p);
            if (cd <= 1 && df <= SPELL_RANGE) sc += 250;
            if (df <= range) sc += 150;
            sc -= 15.0 * std::max(0, df - SPELL_RANGE);
            int mate = 30;
            for (auto& m : mates) mate = std::min(mate, dist(t, m.p));
            sc -= 20.0 * std::max(0, mate - 3);
            return sc;
        });
        pos = me.position();
        if (!moved) cast_at(s, me, *focus, true, false);
        cast_at(s, me, *focus, false, false);
        if (dist(pos, focus->p) <= range) basic_attack(s, me, focus->c, focus->p);
        else hit_any(s, me, near);
        return true;
    }

    // Ranged: a diver next to us: stun it without rooting, step out, then shoot.
    if (!divers.empty()) {
        cast_at(s, me, *divers.front(), false, true);
        if (me.can_move()) {
            auto score = [&](vec2 t) {
                int thr = 0;
                for (auto* f : divers)
                    if (dist(t, f->p) <= 2) ++thr;
                int df = dist(t, focus->p);
                int mate = 30;
                for (auto& m : mates) mate = std::min(mate, dist(t, m.p));
                return -1000 * thr + (df <= SPELL_RANGE ? 300 : 0) + (df <= range ? 100 : 0) - 20 * std::max(0, mate - 3);
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
        }
        pos = me.position();
        cast_at(s, me, *focus, false, false);
        if (dist(pos, focus->p) <= range) basic_attack(s, me, focus->c, focus->p);
        else hit_any(s, me, near);
        return true;
    }
    // Safe: stand and cast on the focus, then shoot.
    if (focus->d <= SPELL_RANGE) {
        cast_at(s, me, *focus, true, false);
        if (focus->d <= range) {
            basic_attack(s, me, focus->c, focus->p);
            return true;
        }
        if (!me.can_move()) {  // rooted by the spell: hit whatever is in reach
            hit_any(s, me, near);
            return true;
        }
    }
    // Close in to our range, but never next to a melee foe.
    if (me.can_move()) {
        bc::bitboard ring;
        ring.draw_chebyshev(focus->p, static_cast<float>(range));
        for (auto* f : near)
            if (reach(*f) <= 2) {
                bc::bitboard bad;
                bad.draw_chebyshev(f->p, 2.0f);
                ring = ring & ~bad;
            }
        step_towards(s, me, ring, false);
    }
    pos = me.position();
    cast_at(s, me, *focus, false, false);
    if (dist(pos, focus->p) <= range) basic_attack(s, me, focus->c, focus->p);
    else hit_any(s, me, near);
    return true;
}

}  // namespace fight
