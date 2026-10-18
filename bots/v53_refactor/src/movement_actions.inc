bool volley_mode(bc::champion& me) {
    if (!P_VOLLEY_FARM && (std::strcmp(g_mode, "farm") == 0 || std::strcmp(g_mode, "channel") == 0)) return false;
    if (P_VOLLEY_FIGHT >= 2 || (P_VOLLEY_FIGHT == 1 && me.attack_range() > 1)) return true;
    static const char* fights[] = {"fight", "front", "kite", "fm-engage", "twin"};
    for (auto* f : fights)
        if (std::strcmp(g_mode, f) == 0) return false;
    return true;
}

// P_FUELGUARD: one step to the free neighbour closest to `to` (straight line), no path search: the turn still moves
// when it has no fuel left for a search.
bool greedy_step(State& s, bc::champion& me, vec2 to) {
    if (!me.can_move()) return false;
    vec2 pos = me.position();
    int here = dist(pos, to), bd = here;
    std::optional<vec2> best;
    for (int dx = -1; dx <= 1; ++dx)
        for (int dy = -1; dy <= 1; ++dy) {
            if (!dx && !dy) continue;
            vec2 t = pos + vec2(dx, dy);
            if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t)) continue;
            int d = dist(t, to);
            if (d < bd) { bd = d; best = t; }
        }
    return best && attempt([&] { return me.move_absolute(*best); });
}

bc::bitboard mp_awake_camp_zone(State& s, vec2 pos);
int mp_dash_hole_step(State& s, bc::champion& me, const bc::bitboard& goals, const bc::bitboard& vblock, vec2 pos);
bool step_towards(State& s, bc::champion& me, const bc::bitboard& goals_in, bool use_dash) {
    FP_SCOPE(16, "step_towards");
    vec2 pos = me.position();
    bc::bitboard goals = goals_in & ~s.blocked;
    if (goals.is_empty() || goals.is_set(pos)) return false;
    if (!me.can_move() && !(use_dash && s.dash_slot >= 0)) return false;

    bc::bitboard vblock = s.blocked;  // P_VOLLEY: blocked plus lethal tiles
    bool vol_on = false;
    if (P_VOLLEY && !s.thr.empty() && s.thr_r == static_cast<int>(bc::round_number()) && volley_mode(me)) {
        double lim = me.health() * P_VOLLEY / 100.0;
        double here = danger_at(s.thr, pos);
        if (here >= lim) {  // standing in a ready volley: first get out, toward the goal on ties
            if (me.can_move()) {
                bool field = attempt([&] {
                    s.dest.clear();
                    s.dest.set(pos);
                    s.df.compute_to(s.blocked, goals, s.dest, s.visited);
                    return true;
                });
                std::vector<std::pair<double, vec2>> c;
                for (int dx = -1; dx <= 1; ++dx)
                    for (int dy = -1; dy <= 1; ++dy) {
                        if (!dx && !dy) continue;
                        vec2 t = pos + vec2(dx, dy);
                        if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t)) continue;
                        double dg = danger_at(s.thr, t);
                        if (dg >= here) continue;
                        double g = field && s.visited.is_set(t) ? s.df.get(t) : 999;
                        c.push_back({dg + 0.5 * g, t});
                    }
                std::sort(c.begin(), c.end(), [](auto& a, auto& b) { return a.first < b.first; });
                for (auto& [sc, t] : c)
                    if (attempt([&] { return me.move_absolute(t); })) return true;
            }
        } else {  // the ring around us is enough: next turn looks again
            for (int dx = -P_VOLLEY_R; dx <= P_VOLLEY_R; ++dx)
                for (int dy = -P_VOLLEY_R; dy <= P_VOLLEY_R; ++dy) {
                    vec2 t = pos + vec2(dx, dy);
                    if ((dx || dy) && bc::map::is_in_bounds(t) && !s.blocked.is_set(t) && danger_at(s.thr, t) >= lim) {
                        vblock.set(t);
                        vol_on = true;
                    }
                }
        }
    }

    if (!fuel_ok(25000)) {
        auto ps = goals.positions();
        if (ps.empty()) return false;
        vec2 best = ps[0];
        for (auto p : ps)
            if (dist(p, pos) < dist(best, pos)) best = p;
        if (P_FUELGUARD && !fuel_ok(14000)) return greedy_step(s, me, best);  // move_towards is one more path search
        return attempt([&] { return me.move_towards(best); });
    }

    s.dest.clear();
    s.dest.set(pos);
    auto fallback = [&] {
        auto ps = goals.positions();
        if (ps.empty() || !me.can_move()) return false;
        vec2 best = ps[0];
        for (auto p : ps)
            if (dist(p, pos) < dist(best, pos)) best = p;
        return attempt([&] { return me.move_towards(best); });
    };
    bool ok_field = false;
    if (P_MAPPLAN && P_MP_CAMPAVOID && fuel_ok(30000)) {  // mapplan_game.h rule 3: walk around awake camps we do not fight
        bc::bitboard avoid = mp_awake_camp_zone(s, pos);
        if (!avoid.is_empty())
            ok_field = attempt([&] {
                s.df.compute_to(vblock | (avoid & ~goals), goals, s.dest, s.visited);
                return s.visited.is_set(pos);
            });
    }
    if (!ok_field)
        ok_field = attempt([&] {
            s.df.compute_to(vblock, goals, s.dest, s.visited);
            return s.visited.is_set(pos);
        });
    if (!ok_field && vol_on) return false;  // every way runs through a ready volley: wait
    if (!ok_field && P_UNJAM) {  // corridor jammed by champions: plan through them
        ok_field = attempt([&] {
            bc::bitboard b2 = s.static_block | bc::vision::camp_tiles();
            b2.set(pos, false);
            s.df.compute_to(b2, goals_in & ~s.static_block, s.dest, s.visited);
            return s.visited.is_set(pos);
        });
    }
    if (!ok_field) return fallback();

    if (P_MAPPLAN && P_MP_DASHHOLE && use_dash && s.dash_slot >= 0 && !s.mp_dashholes.is_empty() && fuel_ok(40000)) {
        int r = mp_dash_hole_step(s, me, goals, vblock, pos);  // mapplan_game.h rule 5: plan across holes we can dash
        if (r) return r > 0;
    }
    bool moved = false;
    if (use_dash && s.dash_slot >= 0 && me.can_cast()) {
        auto ab = me.abilities()[s.dash_slot];
        int here = s.df.get(pos);
        if (here >= 3 && ab.is_ready()) {
            std::optional<vec2> best;
            int bestd = here - 1;  // only dash if it beats a plain step
            for (int dx = -2; dx <= 2; ++dx)
                for (int dy = -2; dy <= 2; ++dy) {
                    vec2 t = pos + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t) || !s.visited.is_set(t)) continue;
                    int d = s.df.get(t);
                    if (d < bestd) { bestd = d; best = t; }
                }
            if (best && attempt([&] { return ab.use(*best); })) {
                moved = true;
                pos = *best;
            }
        }
    }
    if (me.can_move()) {
        std::vector<vec2> steps;
        attempt([&] {
            steps = s.df.next_moves_from(pos);
            return true;
        });
        for (auto d : steps)
            if (attempt([&] { return me.move(d); })) { moved = true; break; }
        if (!moved && !steps.empty()) moved = fallback();
        if (steps.empty() && !moved) moved = fallback();
        if (P_UNJAM && !moved && me.can_move()) {  // still stuck: any free tile that is not farther
            int here = s.df.get(pos);
            for (int dx = -1; dx <= 1 && !moved; ++dx)
                for (int dy = -1; dy <= 1 && !moved; ++dy) {
                    if (!dx && !dy) continue;
                    vec2 t = pos + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t) || !s.visited.is_set(t)) continue;
                    if (s.df.get(t) > here + 1) continue;
                    moved = attempt([&] { return me.move_absolute(t); });
                }
        }
    }
    return moved;
}

bool flee(State& s, bc::champion& me) { return step_towards(s, me, s.my_spawn, true); }

// ---------------------------------------------------------------------------
// Combat helpers
// ---------------------------------------------------------------------------
// U34_UNDERLYING_HOOKS: fresh SDK visibility after our own actions.
// A visible handle collected earlier can become hidden or die after a cast,
// attack, knockback or our move. A dead record may remain visible, so health
// must also be positive. is_visible handles hidden/not-found normally.
template <class U>
bool u34_target_visible(const U& target) {
    return attempt([&] { return target.is_visible() && target.health() > 0; });
}

vec2 aoe_centre(State& s, bc::champion& me, int k, vec2 tp, int* hits = nullptr);  // P_AOE, defined below

template <class U>
bool cast_offense(State& s, bc::champion& me, const U& tgt, vec2 tpos, bool champ) {
    if (!me.can_cast() || dist(me.position(), tpos) > SPELL_RANGE) return false;
    auto abs = me.abilities();
    for (int k = 0; k < 2; ++k) {
        auto& ab = abs[k];
        // P_SAVECC: keep stuns for champions while enemies were seen in the last P_SAVECC rounds.
        if (P_SAVECC && !champ && s.foe_r > -1000 && static_cast<int>(bc::round_number()) - s.foe_r <= P_SAVECC &&
            attempt([&] { return ab.is_cc(); }))
            continue;
        if (s.slots[k] == Slot::Targeted) {
            if (!(champ ? ab.can_target_enemies() : ab.can_target_camps())) continue;
            if (ab.is_ready() && attempt([&] { return ab.use(tgt); })) return true;
        } else if (s.slots[k] == Slot::Ground) {
            if (!ab.is_ready()) continue;
            vec2 c = tpos;
            if (P_AOE && champ) c = aoe_centre(s, me, k, tpos);
            if (attempt([&] { return ab.use(c); })) return true;
        }
    }
    return false;
}

template <class U>
bool basic_attack(State& s, bc::champion& me, const U& tgt, vec2 tpos) {
    if (dist(me.position(), tpos) > me.attack_range() || !me.can_attack()) return false;
    if (P_U34_ATTACK_LIVE && !u34_target_visible(tgt)) return false;
    bool hit = attempt([&] {
        me.attack(tgt);
        return true;
    });
    // Preserve a reset cooldown when its only selected target disappeared.
    if (hit && s.reset_slot >= 0 && me.can_cast() &&
        // P_U34_RESET_LIVE 1: only on corners/interlock, spend the reset only if the target is still alive and
        // visible after the first hit; 2: the same check on every map (a dead target wastes the reset).
        (!(P_U34_RESET_LIVE >= 2 || (P_U34_RESET_LIVE && (s.de_map == v34de::Corners || s.de_map == v34de::Interlock))) ||
         u34_target_visible(tgt))) {
        auto ab = me.abilities()[s.reset_slot];
        if (ab.is_ready() && attempt([&] { return ab.use(); }))
            attempt([&] {
                me.attack(tgt);
                return true;
            });
    }
    return hit;
}

bool g_ally_near_tgt = false;
// Full engage on one target: spell, attack, close distance, attack again.
template <class U>
bool engage(State& s, bc::champion& me, const U& tgt, vec2 tpos, bool champ, bool dash) {
    FP_SCOPE(17, "engage");
    int d = dist(me.position(), tpos);
    int range = me.attack_range();
    bool acted = false;
    // Keep the exact action order; report whether any action really succeeded.
    if (d <= (s.melee ? range + 1 : 3)) acted = cast_offense(s, me, tgt, tpos, champ);
    if (basic_attack(s, me, tgt, tpos)) return true;
    if (dist(me.position(), tpos) > range) {
        bc::bitboard ring;
        ring.draw_chebyshev(tpos, static_cast<float>(range));
        acted = step_towards(s, me, ring, dash && (!P_NODASHIN || d <= 3 || g_ally_near_tgt)) || acted;
        acted = basic_attack(s, me, tgt, tpos) || acted;
    }
    return acted;
}

void support_spells(State& s, bc::champion& me, bool in_combat) {
    if (!me.can_cast()) return;
    auto abs = me.abilities();
    for (int k = 0; k < 2; ++k) {
        auto& ab = abs[k];
        if (s.slots[k] == Slot::Shield && in_combat && me.health() < 0.85f * me.max_health()) {
            if (ab.is_ready() && attempt([&] { return ab.use(); })) return;
        }
        if (s.slots[k] == Slot::Heal && ab.is_ready()) {
            for (auto& a : bc::vision::champions(*s.my)) {
                if (a == me) continue;
                bool done = attempt([&] {
                    if (!a.is_alive() || dist(a.position(), me.position()) > SPELL_RANGE) return false;
                    if (ab.heal_amount(a) < 0.5f * ab.heal_amount()) return false;
                    return ab.use(a);
                });
                if (done) return;
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Objectives
// ---------------------------------------------------------------------------
// Shared memory (8 bytes): bytes 0..4 = claim per ally index (group+1, 0 = none);
// bytes 5/6 = "group (byte5-1) respawns at round byte6*8", written by whoever saw it.
