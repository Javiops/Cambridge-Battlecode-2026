#pragma once
#ifndef P_R5_WARD
#define P_R5_WARD 0
#endif
#ifndef P_R5_LOCK
#define P_R5_LOCK 0
#endif
// 0 = original bush-only heuristic, 1 = camp/respawn intel, 2 = enemy approach intel.
#ifndef P_WARD_MODE
#define P_WARD_MODE 0
#endif
// Success-only placement logs for replay investigations (off during performance tests).
#ifndef P_WARD_LOG
#define P_WARD_LOG 0
#endif

// Optional personal scouting after the existing turn decisions. The only tile
// search is a 5x5 local window; no new vision board or distance field is built.
bool r5_personal_ward(State& s) {
    static int next_check = 0;
    if (!s.ready || !s.my || !fuel_ok(P_WARD_MODE != 0 ? 29000 : 9000)) return false;
    const int round = static_cast<int>(bc::round_number());
    if (round < next_check) return false;
    next_check = round + 4;
    return attempt([&] {
        bc::champion& me = bc::self();
        if (!me.is_alive() || me.is_recalling() || me.is_submitting_gems() ||
            me.is_teleporting() || me.ward_cooldown() > 0 ||
            me.restrictions().contains(bc::buff_restrictions::ward)) return false;
        const vec2 here = me.position();
        const auto& bushes = bc::map::bushes();
        const auto& walls = bc::map::walls();
        // Our current connected bush is already transparent to our own vision.
        if (P_WARD_MODE == 0 && bushes.is_set(here)) return false;
        vec2 goal = s.en_center;
        if (s.target >= 0 && s.target < static_cast<int>(s.groups.size()))
            goal = s.groups[s.target].center;
        if (static_cast<int>(me.gem_count()) >= P.tribute_gems) {
            int nearest = 1 << 20;
            for (std::size_t i = 0; i < s.altars.size(); ++i) {
                if (i < s.altar_ok.size() && !s.altar_ok[i]) continue;
                const int d = dist(here, s.altars[i]);
                if (d < nearest) { nearest = d; goal = s.altars[i]; }
            }
        }
        const auto current = me.ward_positions();
        if (P_WARD_MODE == 0 && !current.empty() && bushes.is_set(current.front()) &&
            dist(current.front(), goal) <= bc::constants::ward_vision_radius)
            return false;
        // One permanent, personal ward: do not casually erase remote camp
        // surveillance just because the champion walked to another lane.
        if (P_WARD_MODE != 0 && !current.empty() && dist(here, current.front()) > 10) {
            for (const auto& g : s.groups) {
                if (g.gems <= 0 || dist(g.center, here) <= 8) continue;
                if (dist(g.center, current.front()) <= bc::constants::ward_vision_radius)
                    return false;
            }
        }
        std::vector<const Group*> local_camps;
        if (P_WARD_MODE != 0) {
            local_camps.reserve(12);
            for (const auto& g : s.groups) {
                if (g.gems <= 0 || dist(g.center, here) > bc::constants::ward_vision_radius +
                        bc::constants::ward_placement_radius) continue;
                local_camps.push_back(&g);
                if (local_camps.size() == 12) break;
            }
        }
        struct Candidate { vec2 p{}; int rank = -1000; };
        std::array<Candidate, 3> best{};
        const int before = dist(here, goal);
        for (int dx = -2; dx <= 2; ++dx) for (int dy = -2; dy <= 2; ++dy) {
            if (P_WARD_MODE != 0 && !fuel_ok(21000)) break;
            const vec2 p = here + vec2(dx, dy);
            if (!bc::map::is_in_bounds(p) || p == here ||
                dist(here, p) > bc::constants::ward_placement_radius ||
                (P_WARD_MODE == 0 && !bushes.is_set(p)) ||
                s.static_block.is_set(p) || s.blocked.is_set(p) ||
                s.my_spawn.is_set(p) || s.en_spawn.is_set(p)) continue;
            if (!current.empty() && dist(current.front(), p) <= 2) continue;
            int rank = 3 * dist(here, p) + 2 * (before - dist(p, goal));
            if (P_WARD_MODE != 0) {
                const bool bush = bushes.is_set(p);
                // Sample eight unobstructed vision rays, counting tiles the
                // champion has not already seen. No full shadowcast per tile.
                // Bush-cluster transparency is approximated: a ward inside a
                // bush can look out, an outside ward stops at the first bush.
                int unseen = 0;
                for (int ux = -1; ux <= 1; ++ux) for (int uy = -1; uy <= 1; ++uy) {
                    if (!ux && !uy) continue;
                    for (int n = 1; n <= bc::constants::ward_vision_radius; ++n) {
                        vec2 q = p + vec2(ux*n, uy*n);
                        if (!bc::map::is_in_bounds(q) || walls.is_set(q)) break;
                        if (!s.vis.is_set(q) && !s.my_spawn.is_set(q) && !s.en_spawn.is_set(q)) ++unseen;
                        if (!bush && bushes.is_set(q)) break;
                    }
                }
                // Only give a big bonus to valuable camps the ward can
                // plausibly watch, particularly across fog/cover.
                int unseen_gem_camps = 0;
                int covered_gem_camps = 0;
                for (const Group* gp : local_camps) {
                    const auto& g = *gp;
                    if (dist(g.center, p) > bc::constants::ward_vision_radius) continue;
                    // Approximate LOS along the camp ray (8 or fewer steps).
                    int ddx = X(g.center)-X(p), ddy = Y(g.center)-Y(p);
                    int steps = std::max(std::abs(ddx),std::abs(ddy));
                    bool line = true;
                    for (int k = 1; k <= steps; ++k) {
                        vec2 q = p + vec2((ddx*k)/steps, (ddy*k)/steps);
                        if (walls.is_set(q) || (!bush && bushes.is_set(q))) {line = false; break;}
                    }
                    if (!line) continue;
                    ++covered_gem_camps;
                    if (!s.vis.is_set(g.center)) ++unseen_gem_camps;
                }
                const int ahead = before - dist(p, goal);
                if (P_WARD_MODE == 1) {
                    // Camp / respawn monitoring: prefer new gem camp vision,
                    // also give some weight to scouting hidden routes.
                    rank = 50*unseen_gem_camps + 8*covered_gem_camps +
                           2*unseen + (bush ? 14 : 0) + 4*ahead;
                } else {
                    // Counter-gank: more weight on hidden approach tiles and
                    // bushes; a nearby camp is still a useful secondary target.
                    const int towards_enemy = dist(here,s.en_center)-dist(p,s.en_center);
                    rank = 16*unseen_gem_camps + 2*covered_gem_camps +
                           4*unseen + (bush ? 25 : 0) +
                           10*towards_enemy + 3*ahead;
                }
                // Don't replace an existing ward for essentially no new view.
                if (unseen_gem_camps == 0 && unseen < 3) continue;
            }
            for (int i = 0; i < 3; ++i) {
                if (rank <= best[i].rank) continue;
                for (int j = 2; j > i; --j) best[j] = best[j - 1];
                best[i] = {p, rank};
                break;
            }
        }
        for (const auto& c : best) {
            if (c.rank == -1000 || !fuel_ok(6000)) break;
            if (bc::vision::has_champion(c.p) || bc::vision::has_camp(c.p) ||
                bc::vision::has_teleport(c.p) || bc::vision::has_ward(c.p, *s.my)) continue;
            if (attempt([&] { return me.place_ward(c.p); })) {
                next_check = round + 8;
#if P_WARD_LOG
                std::printf("[ward] r=%d mode=%d who=%d xy=%d,%d target=%d,%d rank=%d\n",
                            round, P_WARD_MODE, s.ally_idx, X(c.p), Y(c.p), X(goal), Y(goal), c.rank);
#endif
                return true;
            }
            if (me.ward_cooldown() > 0) break;
        }
        return false;
    });
}

// Buy only with the remainder left by ordinary shopping, then spend the lock
// on a nearby contested/enemy-side altar. No extra recall or movement is added.
bool r5_altar_lock(State& s) {
    if (!s.ready || !s.my || !fuel_ok(7000)) return false;
    return attempt([&] {
        bc::champion& me = bc::self();
        if (!me.is_alive() || me.is_recalling() || me.is_submitting_gems() ||
            me.is_teleporting() ||
            me.restrictions().contains(bc::buff_restrictions::consumable)) return false;
        const vec2 here = me.position();
        const auto kind = bc::consumable_type::altar_lock;
        const auto& lock = me.consumables()[kind];
        auto owned = lock.count();
        if (!owned && s.my_spawn.is_set(here)) {
            const auto gold = me.gold_count();
            if (gold >= kind.cost() && gold < 30 && me.can_buy(kind)) {
                me.buy(kind);
                owned = lock.count();
            }
        }
        if (!owned) return false;
        int best = -1, rank = 1 << 20;
        for (std::size_t i = 0; i < s.altars.size(); ++i) {
            const vec2 a = s.altars[i];
            if (dist(here, a) > 2 || dist(a, s.en_center) > dist(a, s.spawn_center) + 4) continue;
            if (bc::vision::has_altar_lock(a) && bc::vision::altar_lock_at(a).is_ally()) continue;
            const int score = dist(a, s.en_center);
            if (score < rank) { rank = score; best = static_cast<int>(i); }
        }
        return best >= 0 && fuel_ok(4000) && lock.use(s.altars[best]);
    });
}
