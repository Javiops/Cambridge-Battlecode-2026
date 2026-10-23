#pragma once
// ryth.h - Ryth (draft slot 4). Hooks: shop_plan (champions.h shop part 2); champ::hp_share has her health share.

namespace ryth {

CHAMP_HOOK bool is(const std::string& n) { return starts_with(n, "ryth"); }

// t10shop-v1: top-10 Ryth build: Treasure first, Jungle-s, Bruiser-h, Durab-h, Bruiser-s, then Bruiser-h.
CHAMP_HOOK bool shop_plan(State& s) {
    if (!is(s.name)) return false;
    s.plan = {{"treasure", 'h', 1}, {"jungle", 's', 1}, {"bruiser", 'h', 1}, {"durab", 'h', 1}, {"bruiser", 's', 1}, {"bruiser", 'h', 99}};
    return true;
}

}  // namespace ryth
