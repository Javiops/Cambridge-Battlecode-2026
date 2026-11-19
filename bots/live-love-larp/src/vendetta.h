#pragma once
// vendetta.h - Vendetta (draft slot 5, in Varg's place: P_DRAFT_SWAP3). Hooks: shop_plan (champions.h shop part 2).
// fight.h's enemy model also knows her dash (legacy name list "vend", replaced by the engine query, P_KINDFIX).

namespace vendetta {

CHAMP_HOOK bool is(const std::string& n) { return starts_with(n, "vendetta"); }

// o95 cut: a damage champion leaves a contact before its health (minus the last 2 rounds' damage) drops under P_CUT_PCT %.
// Top 10: contacts with 10+ rounds and leaving below 40% health much rarer than ours (contacts.py).
CHAMP_HOOK bool cuts_contact(const State& s) { return P_CUT && is(s.name); }

// t10shop-v1: top-10 Vendetta build: Treasure first, Jungle-s, Bruiser-h, Durab-h, then Bruiser-s.
CHAMP_HOOK bool shop_plan(State& s) {
    if (!is(s.name)) return false;
    s.plan = {{"treasure", 's', 1}, {"jungle", 's', 1}, {"bruiser", 'h', 1}, {"bruiser", 's', 99}};  // o109: Strength first (top 10 Vendetta 8-9 Strength shards at r400, ours 2-3)
    return true;
}

// lshop-v1 weights (Power folded into Bruiser of the same stat): late fill mix from P_LSHOP_R. Vendetta: t10 Bruiser s 1840 / h 1144 + Power-s 514, ours all Bruiser-s.
CHAMP_HOOK bool late_mix(const State& s, std::vector<LateFill>& o) {
    if (!is(s.name)) return false;
    o = {{"bruiser", 'h', 1.15f}, {"bruiser", 's', 2.35f}};
    return true;
}

}  // namespace vendetta
