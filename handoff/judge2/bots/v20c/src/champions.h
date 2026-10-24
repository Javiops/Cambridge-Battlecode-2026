#pragma once
// champions.h - the interface between the generic bot (main.cpp, fight.h, ...) and the per-champion files.
//
// Everything that only one champion does lives in <champion>.h (heart_of_ruin.h, vesper.h, marcella.h, ryth.h,
// vendetta.h, ren.h, and the legacy drafts' stellar.h, tavi.h, varg.h, prism.h, cassi_issac.h). main.cpp never
// names a champion: it calls the hooks below. Each hook falls back to the generic behaviour when the champion is
// not in our team (the draft varies: Ren replaces Heart of Ruin on far maps, P_FAR_SWAP).
//
// Rules for a new per-champion piece (see README_CHAMPIONS.md):
//   1. key it on the champion (X::is(name)), never on a draft slot or ally index;
//   2. put it in X.h; if no hook fits, add one here and a call at the one place in main.cpp where it acts;
//   3. a hook that runs every turn must stay cheap: fuel per turn changes decisions (fuel_ok), so the games.
//
// This file is included right after State. The champion files are included at the end of main.cpp, so they can
// use every generic helper (step_towards, cast_offense, fight::hit_now, ...); here they are only declared.
// The dispatch functions keep the exact order of the checks they replaced: the compiled bot is byte-identical
// to V20 (v139 v6d), so a refactor costs no fuel and changes no game.

#include <string>
#include <vector>

// A hook is inlined where it is called, exactly like the code it replaced (the compiled bot stays V20's).
#define CHAMP_HOOK inline __attribute__((always_inline))

// ---- per-champion declarations (definitions in <champion>.h) -------------------------------------------------
namespace heart_of_ruin {
CHAMP_HOOK bool is(const std::string& n);
CHAMP_HOOK bool shop_plan(State& s);
CHAMP_HOOK bool keeps_dash_for_attacks(const State& s);
template <class U, class A> CHAMP_HOOK bool dash_strike(State& s, bc::champion& me, A& abs, const U& tgt, vec2 tpos, bool champ);
}
namespace vesper {
CHAMP_HOOK bool is(const std::string& n);
}
namespace marcella {
CHAMP_HOOK bool is(const std::string& n);
CHAMP_HOOK bool shop_plan(State& s);
}
namespace ryth {
CHAMP_HOOK bool is(const std::string& n);
CHAMP_HOOK bool shop_plan(State& s);
}
namespace vendetta {
CHAMP_HOOK bool is(const std::string& n);
CHAMP_HOOK bool shop_plan(State& s);
}
namespace ren {
CHAMP_HOOK bool is(const std::string& n);
}
namespace stellar {
CHAMP_HOOK bool is(const std::string& n);
}
namespace prism {
CHAMP_HOOK bool is(const std::string& n);
}
namespace tavi {
CHAMP_HOOK bool is(const std::string& n);
CHAMP_HOOK bool shops_in_field(const State& s);
}
namespace varg {
CHAMP_HOOK bool is(const std::string& n);
CHAMP_HOOK bool splashes(const State& s);
constexpr double SPLASH = 1.5;
}
namespace cassi_issac {
CHAMP_HOOK bool is_cassi(const std::string& n);
CHAMP_HOOK bool is_issac(const std::string& n);
inline bool pair_ok(State& s, bc::champion& me);
inline bool twin_guard(State& s, bc::champion& me, const std::vector<Foe>& foes);
CHAMP_HOOK bool twin_farm(State& s, bc::champion& me, int round, vec2 pos);
}

// ---- hooks called by main.cpp ----------------------------------------------------------------------------------
namespace champ {

// Shop, part 1 (build_shop): the historical emblem layers, oldest first; the last layer that matches wins.
// For the V20 draft only two champions still take their plan from here: Vesper (the generic "durab/jungle/bruiser,
// then power-s" melee plan) and Ren (the casters' "power-f, durab-h, then power-f"). Heart of Ruin, Marcella, Ryth
// and Vendetta are overwritten by their own shop_plan() (part 2). Kept as it was: removing dead layers would change
// the start-up fuel. P_BRUISER_FILL then turns the last "power" quota of these plans into Bruiser.
CHAMP_HOOK void legacy_plan(State& s) {
    if (ryth::is(s.name)) {
        s.plan = {{"jungle", 'h', 1}, {"durab", 'h', 1}, {"monster", 'h', 1}, {"power", 'h', 99}};
    } else if (vesper::is(s.name)) {
        s.plan = {{"monster", 's', 1}, {"treasure", 's', 1}, {"jungle", 'h', 1}, {"power", 's', 99}};
    } else if (s.melee) {
        s.plan = {{"jungle", 'h', 1}, {"monster", 's', 1}, {"durab", 'h', 1}, {"power", 's', 99}};
    } else {
        s.plan = {{"monster", 's', 1}, {"jungle", 'h', 1}, {"power", 's', 99}};
    }
    // what the top teams buy: the monster emblem first, then power
    if (cassi_issac::is_cassi(s.name))
        s.plan = {{"monster", 'f', 1}, {"power", 'f', 99}};
    else if (ryth::is(s.name))
        s.plan = {{"monster", 's', 1}, {"power", 's', 2}, {"jungle", 'h', 1}, {"power", 's', 99}};
    else
        s.plan = {{"monster", 's', 1}, {"power", 's', 3}, {"jungle", 'h', 1}, {"power", 's', 99}};
    if (!cassi_issac::is_cassi(s.name))  // Mite's tank build: survive camps solo, then raw power
        s.plan = {{"durab", 's', 1}, {"jungle", 's', 1}, {"bruiser", 'h', 1}, {"power", 's', 99}};
    // what the top-10 winners buy (2026-10-14 study of 169 games)
    if (cassi_issac::is_issac(s.name))      // their Issac: 11 power-s shards a game, ours 5.5
        s.plan = {{"power", 's', 2}, {"jungle", 's', 1}, {"power", 's', 99}};
    else if (tavi::is(s.name))  // their Tavi buys focus; ours bought strength
        s.plan = {{"power", 'f', 1}, {"bruiser", 'f', 1}, {"power", 'f', 99}};
    else if (cassi_issac::is_cassi(s.name)) // little gold on Cassi: power-f and one durability-h
        s.plan = {{"power", 'f', 1}, {"durab", 'h', 1}, {"power", 'f', 99}};
    else if (stellar::is(s.name))  // top Stellar: power-f x10, durability-h
        s.plan = {{"power", 'f', 1}, {"durab", 'h', 1}, {"power", 'f', 99}};
    else if (ren::is(s.name))      // top Ren: power-s, some power-f (retaliation is focus)
        s.plan = {{"power", 's', 1}, {"bruiser", 'h', 1}, {"power", 'f', 1}, {"power", 's', 99}};


    if ((ren::is(s.name) || prism::is(s.name) || stellar::is(s.name)))
        s.plan = {{"power", 'f', 1}, {"durab", 'h', 1}, {"power", 'f', 99}};  // the #1's casters: 8-13 power-f a game
    // One offensive opening emblem, then the complete original melee core.
    // Preserve Jungle camp mitigation and Bruiser health for later farming.
    if (ryth::is(s.name) || varg::is(s.name) || vendetta::is(s.name))
        s.plan = {{"power", 's', 1}, {"durab", 's', 1}, {"jungle", 's', 1},
                  {"bruiser", 'h', 1}, {"power", 's', 99}};
    if (P_HORFOCUS && heart_of_ruin::is(s.name))  // horfocus-v1: rivals' HoR 71% focus shards (top 10 67%), ours 0%
        s.plan = {{"power", 'f', 1}, {"bruiser", 'f', 1}, {"power", 's', 1}, {"power", 'f', 99}};
}

// Shop, part 2 (end of build_shop): the champion's own plan, final (no bruiser fill, no opening replace).
// Order of the checks as in V20. A champion without one keeps part 1's plan.
CHAMP_HOOK void shop_plan(State& s) {
#if P_T10SHOP
    if (P_T10SHOP & 1)
        vendetta::shop_plan(s) || marcella::shop_plan(s) || ryth::shop_plan(s) || heart_of_ruin::shop_plan(s);
#endif
}

// Shop, every buy (shop()): true = the champion's own plan holds its health shards, so hp_pick is off.
CHAMP_HOOK bool own_plan(const State& s) {
    return P_T10SHOP && (vendetta::is(s.name) || marcella::is(s.name) || ryth::is(s.name) || heart_of_ruin::is(s.name));
}

// Shop, every buy (hp_pick): the share of shards that should be health, and the family to buy it in.
// 0 = no health rule for this champion. The first chain is legacy (P_HP_SHOP, 10-14), the second overrides it.
CHAMP_HOOK void hp_share(const State& s, float& share, const char*& fam) {
    if (cassi_issac::is_issac(s.name)) share = 0.16f;
    else if (varg::is(s.name)) share = 0.12f;
    else if (ryth::is(s.name)) { share = 0.34f; fam = "bruiser"; }
    else if (ren::is(s.name)) { share = 0.25f; fam = "bruiser"; }
    else if (tavi::is(s.name)) share = 0.06f;
    if (P_HPSHARE2) {  // engine-3 hp share of shop gold by r300, rivals' (51-75) in our losses: HoR 37%, Ren 53%, Ryth 52%, Varg 40%, Stellar 16%
        fam = "durab";
        if (heart_of_ruin::is(s.name)) share = P_HORFOCUS ? 0.25f : 0.40f;
        else if (varg::is(s.name)) share = 0.40f;
        else if (ryth::is(s.name)) { share = 0.50f; fam = "bruiser"; }
        else if (ren::is(s.name)) { share = 0.50f; fam = "bruiser"; }
        else if (stellar::is(s.name)) share = 0.20f;
    }
}

// init_roles: the team plays the caster mode (hold altar, kite, cast-first sweep, recall near foes, flee %) when
// one of these is in it. Called per ally; the name is read twice on purpose (V20's fuel).
CHAMP_HOOK bool caster_mode(const bc::champion& a) {
    return stellar::is(norm(bc::to_string(a.champion_name()))) ||
           (P_VESP_CASTER && vesper::is(norm(bc::to_string(a.champion_name()))));
}

// tank_bits: melee by name (legacy list; P_KINDFIX replaces it with the engine's attack range).
CHAMP_HOOK bool melee_by_name(const std::string& n) {
    return cassi_issac::is_issac(n) || starts_with(n, "vend") || varg::is(n) || ren::is(n) || marcella::is(n) ||
           vesper::is(n);
}

// P_CAPPRIO / shared rewards: capture priority by champion (lower first): Stellar, casters, Ren, tanks.
inline int cap_rank(const std::string& n, bool ranged) {
    if (stellar::is(n)) return 0;
    if (ranged) return 1;
    if (ren::is(n)) return 2;
    return 3;
}

}  // namespace champ
