#pragma once
// marcella.h - Marcella (draft slot 3, in Ren's place: P_DRAFT_SWAP).
// Hooks: shop_plan (champions.h shop part 2). Her damage work (build, spell use) goes here.

namespace marcella {

CHAMP_HOOK bool is(const std::string& n) { return starts_with(n, "marcella"); }

// t10shop-v1: top-10 Marcella build (45 top-10 games on 1.0.3, 10-22): Treasure first, Jungle-s, 2 Bruiser-h,
// Durab-h, 2 Bruiser-f, then Bruiser-h.
CHAMP_HOOK bool shop_plan(State& s) {
    if (!is(s.name)) return false;
    s.plan = {{"treasure", 'h', 1}, {"jungle", 's', 1}, {"bruiser", 'h', 2}, {"durab", 'h', 1}, {"bruiser", 'f', 2}, {"bruiser", 'h', 99}};
    return true;
}

// lshop-v1 weights (Power folded into Bruiser of the same stat): late fill mix from P_LSHOP_R. Marcella: their late hit damage 278 vs our 197 (bcf thread); t10 Bruiser h 3134 / f 2093 / s 1632 + Power-s 878, ours all Bruiser-h.
CHAMP_HOOK bool late_mix(const State& s, std::vector<LateFill>& o) {
    if (!is(s.name)) return false;
    o = {{"bruiser", 'h', 3.1f}, {"bruiser", 's', 2.5f}, {"bruiser", 'f', 2.1f}};
    return true;
}

}  // namespace marcella
