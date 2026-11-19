#pragma once
// heart_of_ruin.h - Heart of Ruin (draft slot 1 on near/mid maps; Ren takes it on far maps, P_FAR_SWAP).
// Hooks: shop_plan (champions.h shop part 2), keeps_dash_for_attacks (step_towards), dash_strike (cast_offense).
// Shop part 1 (legacy) also has a horfocus layer for her, and champ::hp_share her health share (0.25).

namespace heart_of_ruin {

CHAMP_HOOK bool is(const std::string& n) { return starts_with(n, "heart"); }

// t10shop-v1: top-10 HoR build (45 top-10 games on 1.0.3, 10-22): Treasure first, Jungle-f, Bruiser-h, Durab-h,
// then Bruiser-f.
CHAMP_HOOK bool shop_plan(State& s) {
    if (!is(s.name)) return false;
    s.plan = {{"treasure", 'h', 1}, {"jungle", 'f', 1}, {"bruiser", 'h', 1}, {"durab", 'h', 1}, {"bruiser", 'h', 2}, {"bruiser", 'f', 99}};
    return true;
}

// horfocus-v1: HoR keeps the dash for attacks (never dashes to walk).
CHAMP_HOOK bool keeps_dash_for_attacks(const State& s) { return P_HORFOCUS && is(s.name); }

// horfocus-v1: the dash is her damage spell. Cast it onto the target, choosing the landing that hits the most
// units of the same encounter. Returns true when it was cast (cast_offense is done for this turn).
template <class U, class A>  // U: one copy per target kind (camp, champion), as when it was inside cast_offense
CHAMP_HOOK bool dash_strike(State& s, bc::champion& me, A& abs, const U& tgt, vec2 tpos, bool champ) {
    (void)tgt;
    if (P_HORFOCUS && s.dash_slot >= 0 && is(s.name) && abs[s.dash_slot].is_ready()) {
        // Previously tried r=3 from our tile (actual dash range is 2) and
        // scanned positions in arbitrary order, causing bad-destination SDK
        // errors and poor multi-target landings. Get the SDK range mask once;
        // filter terrain/occupancy, require the intended target in the radius-1
        // landing hitbox and score other visible units in the SAME encounter.
        auto& ab = abs[s.dash_slot];
        const vec2 origin = me.position();
        bc::bitboard in_range;
        const bc::bitboard* walls_p = nullptr;  // fuelfit o26: the map walls never change, read once per game
        const bool have_range = attempt([&] {
            in_range = ab.valid_tiles();
            static const bc::bitboard static_walls = bc::map::walls();
            walls_p = &static_walls;
            return true;
        });
        if (have_range && fuel_ok(19000)) {
            struct Landing { vec2 p; double score; };
            std::vector<Landing> choices;
            std::vector<vec2> others;
            // Stay away from unrelated camps: damaging them would wake them.
            if (champ) {
                for (auto& enemy : vis_champions(*s.en)) {
                    if (!fuel_ok(9500)) break;
                    attempt([&] {
                        if (enemy.is_alive() && enemy.is_visible() && enemy.position() != tpos)
                            others.push_back(enemy.position());
                        return true;
                    });
                }
            } else if (s.target >= 0 && s.target < static_cast<int>(s.groups.size())) {
                const auto& group = s.groups[s.target];
                for (auto& other : bc::vision::camps()) {
                    if (!fuel_ok(9500)) break;
                    attempt([&] {
                        if (other.health() > 0 && group.mask.is_set(other.spawn_position()) && other.position() != tpos)
                            others.push_back(other.position());
                        return true;
                    });
                }
            }
            const int dash_range = 2;  // the patched Heart of Ruin kit
            const float my_hp = me.health();  // fuelfit o26: read once
            for (int dx = -dash_range; dx <= dash_range; ++dx)
                for (int dy = -dash_range; dy <= dash_range; ++dy) {
                    vec2 p = origin + vec2(dx,dy);
                    if (!bc::map::is_in_bounds(p)) continue;
                    if (!patch_v1::dash_landing_geometry(X(origin),Y(origin),X(p),Y(p),X(tpos),Y(tpos))) continue;
                    if (s.blocked.is_set(p) || !in_range.is_set(p)) continue;
                    // A two-step dash must have at least one legal intermediate
                    // step not crossing a wall. Holes may be crossed by dash.
                    if (dist(origin,p) == 2) {
                        bool path = false;
                        for (int x=-1; x<=1 && !path; ++x)
                            for (int y=-1; y<=1 && !path; ++y) {
                                vec2 mid=origin+vec2(x,y);
                                if ((x || y) && dist(mid,p)==1 &&
                                    bc::map::is_in_bounds(mid) && !walls_p->is_set(mid)) path = true;
                            }
                        if (!path) continue;
                    }
                    int hits = 1;
                    for (auto other : others) if (dist(other,p) <= 1) ++hits;
                    // In PvP don't dash into extreme fire merely to hit one.
                    const double exposure = champ ? danger_at(s.thr,p) : 0.0;
                    const double score = patch_v1::dash_score(hits,exposure,my_hp,dist(origin,p),champ);
                    choices.push_back({p,score});
                }
            std::sort(choices.begin(),choices.end(),[](const Landing& a,const Landing& b){
                return a.score>b.score;
            });
            for (const auto& c : choices) {
                if (!fuel_ok(11000)) break;
                if (attempt([&] { return dm_use(ab).use(c.p); })) {
                    ++g_dash_corrected;
                    if (g_dash_corrected <= 8 || g_dash_corrected % 100 == 0)
                        std::printf("[patch-dash] who=%s r=%u casts=%d landing=(%d,%d) score=%.1f\n",
                                    s.name.c_str(), static_cast<unsigned>(bc::round_number()),g_dash_corrected,
                                    X(c.p),Y(c.p),c.score);
                    return true;
                }
            }
        }
    }
    return false;
}

// lshop-v1 weights (Power folded into Bruiser of the same stat): late fill mix from P_LSHOP_R. Heart of Ruin: t10 Bruiser h 1515 / f 1008 + Power-f 735, ours all Bruiser-f.
CHAMP_HOOK bool late_mix(const State& s, std::vector<LateFill>& o) {
    if (!is(s.name)) return false;
    o = {{"bruiser", 'h', 1.5f}, {"bruiser", 'f', 1.75f}};
    return true;
}

}  // namespace heart_of_ruin
