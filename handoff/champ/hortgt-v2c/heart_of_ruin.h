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

// hortgt-v1: her farm targets. The top-10 HoR is the team's camp tank: 50 rounds next to a camp in r0-150 (ours 24),
// on guarded groups that carry gems (elk+gems, wolf+gems); ours also walks to gold-only clusters. Multiplies
// choose_target's score; 1.0 for any other champion.
CHAMP_HOOK double target_w(const State& s, const Group& g, bool needs_company) {
    static const bool me = is(s.name);
    if (!me) return 1.0;
    if (P_HOR_RMAX && static_cast<int>(bc::round_number()) >= P_HOR_RMAX) return 1.0;
    if (P_HOR_NEAR) {  // hortgt-v2: near maps only (spawn-to-spawn path < P_HOR_NEAR, Judge 2's "near"); read once
        static int sp = -2;
        if (sp == -2) {
            sp = -1;
            attempt([&] {
                bc::bitboard block = bc::map::walls() | bc::map::holes() | bc::map::altars();
                bc::distance_field da;
                bc::bitboard va;
                da.compute(block, bc::map::spawn_region(bc::team::ally), va);
                int ab = 1 << 30;
                for (auto p : bc::map::spawn_region(bc::team::enemy).positions())
                    if (va.is_set(p)) ab = std::min(ab, static_cast<int>(da.get(p)));
                if (ab < (1 << 30)) sp = ab;
                return true;
            });
            std::printf("[hortgt] spawn_path=%d on=%d\n", sp, (sp >= 0 && sp < P_HOR_NEAR) ? 1 : 0);
        }
        if (sp < 0 || sp >= P_HOR_NEAR) return 1.0;
    }
    if (g.monolith) return 1.0;
    if (g.gems <= 0) return P_HOR_GOLD_W / 100.0;
    if (g.str <= 0) return P_HOR_CLUSTER_W / 100.0;
    return (P_HOR_SOLO && needs_company ? P_HOR_GUARD_W / 70.0 : P_HOR_GUARD_W / 100.0);
}

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
        bc::bitboard in_range, walls;
        const bool have_range = attempt([&] {
            in_range = ab.valid_tiles();
            walls = bc::map::walls();
            return true;
        });
        if (have_range && fuel_ok(19000)) {
            struct Landing { vec2 p; double score; };
            std::vector<Landing> choices;
            std::vector<vec2> others;
            // Stay away from unrelated camps: damaging them would wake them.
            if (champ) {
                for (auto& enemy : bc::vision::champions(*s.en)) {
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
            for (int dx = -dash_range; dx <= dash_range; ++dx)
                for (int dy = -dash_range; dy <= dash_range; ++dy) {
                    vec2 p = origin + vec2(dx,dy);
                    if (!bc::map::is_in_bounds(p) || s.blocked.is_set(p) || !in_range.is_set(p)) continue;
                    if (!patch_v1::dash_landing_geometry(X(origin),Y(origin),X(p),Y(p),X(tpos),Y(tpos))) continue;
                    // A two-step dash must have at least one legal intermediate
                    // step not crossing a wall. Holes may be crossed by dash.
                    if (dist(origin,p) == 2) {
                        bool path = false;
                        for (int x=-1; x<=1 && !path; ++x)
                            for (int y=-1; y<=1 && !path; ++y) {
                                vec2 mid=origin+vec2(x,y);
                                if ((x || y) && dist(mid,p)==1 &&
                                    bc::map::is_in_bounds(mid) && !walls.is_set(mid)) path = true;
                            }
                        if (!path) continue;
                    }
                    int hits = 1;
                    for (auto other : others) if (dist(other,p) <= 1) ++hits;
                    // In PvP don't dash into extreme fire merely to hit one.
                    const double exposure = champ ? danger_at(s.thr,p) : 0.0;
                    const double score = patch_v1::dash_score(hits,exposure,me.health(),dist(origin,p),champ);
                    choices.push_back({p,score});
                }
            std::sort(choices.begin(),choices.end(),[](const Landing& a,const Landing& b){
                return a.score>b.score;
            });
            for (const auto& c : choices) {
                if (!fuel_ok(11000)) break;
                if (attempt([&] { return ab.use(c.p); })) {
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

}  // namespace heart_of_ruin
