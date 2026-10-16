#pragma once
#ifndef P_R5_WARD
#define P_R5_WARD 0
#endif
#ifndef P_R5_LOCK
#define P_R5_LOCK 0
#endif

// Optional personal scouting after the existing turn decisions. The only tile
// search is a 5x5 local window; no new vision board or distance field is built.
bool r5_personal_ward(State& s) {
    static int next_check = 0;
    if (!s.ready || !s.my || !fuel_ok(9000)) return false;
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
        // Our current connected bush is already transparent to our own vision.
        if (bushes.is_set(here)) return false;
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
        if (!current.empty() && bushes.is_set(current.front()) &&
            dist(current.front(), goal) <= bc::constants::ward_vision_radius)
            return false;
        struct Candidate { vec2 p{}; int rank = -1000; };
        std::array<Candidate, 3> best{};
        const int before = dist(here, goal);
        for (int dx = -2; dx <= 2; ++dx) for (int dy = -2; dy <= 2; ++dy) {
            const vec2 p = here + vec2(dx, dy);
            if (!bc::map::is_in_bounds(p) || p == here ||
                dist(here, p) > bc::constants::ward_placement_radius ||
                !bushes.is_set(p) || s.static_block.is_set(p) || s.blocked.is_set(p) ||
                s.my_spawn.is_set(p) || s.en_spawn.is_set(p)) continue;
            if (!current.empty() && dist(current.front(), p) <= 2) continue;
            const int rank = 3 * dist(here, p) + 2 * (before - dist(p, goal));
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
