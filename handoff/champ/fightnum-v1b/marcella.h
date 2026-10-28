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

}  // namespace marcella
