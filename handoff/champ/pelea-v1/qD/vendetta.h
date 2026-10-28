#pragma once
// vendetta.h - Vendetta (draft slot 5, in Varg's place: P_DRAFT_SWAP3). Hooks: shop_plan (champions.h shop part 2).
// fight.h's enemy model also knows her dash (legacy name list "vend", replaced by the engine query, P_KINDFIX).

namespace vendetta {

CHAMP_HOOK bool is(const std::string& n) { return starts_with(n, "vendetta"); }

// t10shop-v1: top-10 Vendetta build: Treasure first, Jungle-s, Bruiser-h, Durab-h, then Bruiser-s.
CHAMP_HOOK bool shop_plan(State& s) {
    if (!is(s.name)) return false;
    s.plan = {{"treasure", 'h', 1}, {"jungle", 's', 1}, {"bruiser", 'h', 1}, {"durab", 'h', 1}, {"bruiser", 's', 99}};
    return true;
}

// lshop-v1 weights (Power folded into Bruiser of the same stat): late fill mix from P_LSHOP_R. Vendetta: t10 Bruiser s 1840 / h 1144 + Power-s 514, ours all Bruiser-s.
CHAMP_HOOK bool late_mix(const State& s, std::vector<LateFill>& o) {
    if (!is(s.name)) return false;
    o = {{"bruiser", 'h', 1.15f}, {"bruiser", 's', 2.35f}};
    return true;
}

}  // namespace vendetta
