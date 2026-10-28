#pragma once
// prism.h - Prism (slot 5 in the drdB draft, in Ryth's place). Hooks: shop_plan, late_mix (champions.h shop part 2).
// Her passive gives focus per carried gem; both spells are focus damage (targeted stun 1.5x, ground area 1.0x).

namespace prism {

CHAMP_HOOK bool is(const std::string& n) { return starts_with(n, "prism"); }

// t5b Prism build (150 top-5 games, 2.0.0): per game Bruiser-f 18.8 shards (3.5 emblems), Bruiser-h 10.2, Jungle-h 4.4,
// Durab-h 3.9, Home-h 3.4, Monster-h 2.9: about half health. Ours (power-f, durab-h, power-f) died 2.8 a game, 95 gems.
CHAMP_HOOK bool shop_plan(State& s) {
    if (!is(s.name)) return false;
    s.plan = {{"jungle", 'h', 1}, {"bruiser", 'f', 1}, {"durab", 'h', 1}, {"bruiser", 'h', 1}, {"bruiser", 'f', 99}};
    return true;
}

// late fill: their Bruiser f 18.8 / h 10.2 shards a game
CHAMP_HOOK bool late_mix(const State& s, std::vector<LateFill>& o) {
    if (!is(s.name)) return false;
    o = {{"bruiser", 'h', 1.0f}, {"bruiser", 'f', 1.85f}};
    return true;
}

}  // namespace prism
