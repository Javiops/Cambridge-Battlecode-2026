#pragma once
#ifndef P_R5_WARD
#define P_R5_WARD 0
#endif
#ifndef P_R5_LOCK
#define P_R5_LOCK 0
#endif

// One permanent, opportunistic ward per champion.  Each champion chooses a
// useful nearby bush while travelling normally; warding never redirects its
// path or uses the shared-memory bytes reserved for team alerts.
#ifndef P_CF_ALL_PASSING_WARDS
#define P_CF_ALL_PASSING_WARDS 0
#endif
#ifndef P_CF_WARD_EVENT_LOG
#define P_CF_WARD_EVENT_LOG 0
#endif

bool cf_all_passing_wards(State& s) {
    if (!s.ready || !s.my || s.ally_idx < 0 || !fuel_ok(13000)) return false;
    // Use a separate throttle for each roster slot even if champion code runs
    // in one team VM.  Unlike the old draft plan, every slot can ward.
    static std::array<int, 16> retry_by_slot{};
    const int slot = std::min(s.ally_idx, 15);
    const int round = static_cast<int>(bc::round_number());
    if (round < 6 || round < retry_by_slot[slot]) return false;
    retry_by_slot[slot] = round + 5;

    return attempt([&] {
        bc::champion& me = bc::self();
        if (!me.is_alive() || me.is_recalling() || me.is_submitting_gems() ||
            me.is_teleporting() || me.ward_cooldown() > 0 ||
            me.restrictions().contains(bc::buff_restrictions::ward)) return false;
        // One active, permanent ward per champion. Never replace a good ward.
        if (!me.ward_positions().empty()) return false;
        const vec2 here = me.position();
        const auto& bushes = bc::map::bushes();

        // Use the draft-selected contested altar when present; otherwise the
        // two-spawn midpoint. This is a soft preference, NOT an exact waypoint.
        const vec2 center = draftplan::R.valid &&
                (draftplan::R.flags & draftplan::F_CENTRAL_ALTAR)
            ? draftplan::R.central
            : vec2((s.spawn_center.x + s.en_center.x) / 2,
                   (s.spawn_center.y + s.en_center.y) / 2);

        // Slot-dependent cross-lane preferences avoid a pile of wards all
        // pointing at the same altar. They never force extra travel.
        const int off[6] = {-7, 7, -3, 3, 0, 10};
        int vx = s.en_center.x - s.spawn_center.x;
        int vy = s.en_center.y - s.spawn_center.y;
        const vec2 across((vy > 0) - (vy < 0), (vx < 0) - (vx > 0));
        const vec2 preference(center.x + across.x * off[slot % 6],
                              center.y + across.y * off[slot % 6]);

        // Use teammates' already planted ward positions where the SDK exposes
        // them. No shared-memory writes, so this won't collide with alerts.
        std::vector<vec2> ally_wards;
        if (fuel_ok(18000)) {
            for (auto& ally : bc::champions(*s.my)) {
                if (ally == me) continue;
                try {
                    for (auto p : ally.ward_positions()) ally_wards.push_back(p);
                } catch (...) { /* Unavailable hidden teammate state. */ }
            }
        }

        struct Candidate { vec2 p{}; int score = -100000; bool bush = false; };
        std::array<Candidate, 4> best{};
        for (auto& c : best) c.score = -100000;
        for (int dx = -2; dx <= 2; ++dx) for (int dy = -2; dy <= 2; ++dy) {
            const vec2 p = here + vec2(dx, dy);
            if (p == here || !bc::map::is_in_bounds(p) ||
                dist(p, here) > bc::constants::ward_placement_radius ||
                s.static_block.is_set(p) || s.my_spawn.is_set(p) ||
                s.en_spawn.is_set(p)) continue;
            const bool in_bush = bushes.is_set(p);
            // If a champion never passes an appropriate bush, allow a late
            // non-bush placement near the central objectives, not at home.
            if (!in_bush && round < 130) continue;
            const int dh = dist(p, s.spawn_center);
            const int de = dist(p, s.en_center);
            const int dc = dist(p, center);
            if (dh < 7 || de < 5 || dc > 16) continue;
            if (round < 110 && std::abs(dh - de) > 20) continue;

            int sc = (in_bush ? 66 : 39) - 3 * dc;
            sc -= std::min(24, 2 * std::abs(dh - de));
            sc -= std::min(17, dist(p, preference));
            for (const vec2 a : s.altars)
                if (dist(p, a) <= bc::constants::ward_vision_radius) {
                    sc += 12;
                    break;
                }
            if (s.target >= 0 && s.target < static_cast<int>(s.groups.size()) &&
                dist(p, s.groups[s.target].center) <= bc::constants::ward_vision_radius)
                sc += 7;

            int nearby_ward = 999;
            for (const vec2 w : ally_wards)
                nearby_ward = std::min(nearby_ward, dist(p, w));
            if (nearby_ward <= 4) sc -= 65;
            else if (nearby_ward <= 8) sc -= 24;
            else if (nearby_ward <= 12) sc -= 10;
            // No incentive to ward beside ourselves if an equally useful bush
            // two tiles away would retain vision after we leave the area.
            sc += dist(p, here);
            if (sc < (in_bush ? 19 : 24)) continue;
            for (int i = 0; i < 4; ++i) {
                if (sc <= best[i].score) continue;
                for (int j = 3; j > i; --j) best[j] = best[j - 1];
                best[i] = {p, sc, in_bush};
                break;
            }
        }
        for (const auto& c : best) {
            if (c.score == -100000 || !fuel_ok(6500)) break;
            if (bc::vision::has_champion(c.p) || bc::vision::has_camp(c.p) ||
                bc::vision::has_teleport(c.p) ||
                bc::vision::has_ward(c.p, *s.my)) continue;
            if (attempt([&] { return me.place_ward(c.p); })) {
                if (P_CF_WARD_EVENT_LOG)
                    std::printf("[ward-place] slot=%d round=%d x=%d y=%d bush=%d score=%d\n",
                                s.ally_idx, round, c.p.x, c.p.y, c.bush ? 1 : 0, c.score);
                return true;
            }
            if (me.ward_cooldown() > 0) break;
        }
        return false;
    });
}

// Kept as the integration point for the existing end-of-turn call. Ward
// placement and sighting are separate: bc::vision already includes the
// champion's ward on subsequent turns, before combat/camp/altar decisions.
// Your teammate can add shared-memory alerts independently.
bool r5_personal_ward(State& s) {
    if (P_CF_ALL_PASSING_WARDS) return cf_all_passing_wards(s);
    static int next_check = 0;
    if (!s.ready || !s.my || !fuel_ok(9000)) return false;
    if (P_DP_WARDS && draftplan::R.valid &&
        (s.ally_idx < 0 || s.ally_idx >= P_DP_WARDERS || s.ally_idx >= draftplan::R.ward_n)) return false;
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
        if (bushes.is_set(here)) return false;
        vec2 goal = s.en_center;
        if (P_DP_WARDS && draftplan::R.valid) {
            goal = draftplan::R.ward[s.ally_idx];
            if (goal.x < 0 || dist(here, goal) > bc::constants::ward_placement_radius) return false;
        } else if (s.target >= 0 && s.target < static_cast<int>(s.groups.size()))
            goal = s.groups[s.target].center;
        if (!P_DP_WARDS && static_cast<int>(me.gem_count()) >= P.tribute_gems) {
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
            const int rank = P_DP_WARDS ? (100 - 10 * dist(p, goal) - dist(here, p))
                                        : (3 * dist(here, p) + 2 * (before - dist(p, goal)));
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
