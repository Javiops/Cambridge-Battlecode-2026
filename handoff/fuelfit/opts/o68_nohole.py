# o68_nohole.py SRCDIR (farm thread; NOT EXACT: a decision change, judge by strength; over b29 = b28 + o66 + o67, also
# applies over b15 + o59 + o63 + o64). step_towards' mapplan rule 5 (mp_dash_hole_step: a dash champion plans its walk
# across holes it can dash) stood behind `fuel_ok(40000)`; with kvvl's real fuel it hardly ever ran in r2-r10 (init ate
# the budget), and in b15+ fuel_ok is a stub, so it runs every turn. On reverse_spiral (spawn-to-spawn path 1) Heart of
# Ruin and Vesper take the hole shortcut through the middle, alone, next to the enemy spawn, and die at r24-r27 in 8 of
# 8 local games (17 deaths <= r100; kvvl 0): the camp is cleared at r100+ instead of r74, 7 gems and 0 gold at r100 over
# 8 games (kvvl 366 / 1528). With the step off (b27): reverse_spiral 7/8 (b27 0/8, kvvl 7/8; net gems +2238 / -2770 /
# +887), rushbait_v2 7/8 (b27 5/8, kvvl 4/8; +2859 / +506 / +642).
# P_MP_HOLE: 0 = no hole routes at all (b31: near losers +8/72 but far -3/56); 1 = as before; 2 = a hole route only when it
# does not split the group: in farm mode, if an ally without a dash (by champion name) claims the same target group, walk
# with it (b32: farm 128 g: h2 97, h0 93, b29 88). P_MP_HOLE_SMALL (b33 = 2500): no hole routes on small maps either.
# No fuel read.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""    int tank_bits = -1;      // P_DPSFARM: bit k = ally k is a tank (-1 not known yet)""",
"""    int tank_bits = -1;      // P_DPSFARM: bit k = ally k is a tank (-1 not known yet)
    int dash_bits = -1;      // o68: bit k = ally k has a dash (by champion name; -1 not known yet)""")
rep("""int tank_bits(State& s) {
    if (s.tank_bits >= 0) return s.tank_bits;""",
"""// o68: allies with a dash ability, by champion name (ren, vesper, vendetta, heart of ruin); cached like tank_bits.
int dash_bits(State& s) {
    if (s.dash_bits >= 0) return s.dash_bits;
    int bits = 0;
    bool ok = attempt([&] {
        auto allies = my_roster(s);
        for (int k = 0; k < static_cast<int>(allies.size()) && k < 16; ++k) {
            std::string n = norm(bc::to_string(allies[k].champion_name()));
            if (n.find("ren") == 0 || n.find("vesper") == 0 || n.find("vendetta") == 0 || n.find("heart") == 0) bits |= 1 << k;
        }
        return true;
    });
    if (ok) s.dash_bits = bits;
    return bits;
}
// o68 (P_MP_HOLE == 2): true when a hole route would leave an ally behind: we are farming our target and an ally without
// a dash claims the same group.
bool hole_splits_group(State& s) {
    if (s.target < 0 || s.ally_idx < 0 || std::strcmp(g_mode, "farm") != 0) return false;
    auto sm = read_sm();
    const int db = dash_bits(s);
    for (int k = 0; k < claim_slots(s) && k < s.roster; ++k) {
        if (k == s.ally_idx) continue;
        const int claim = claim_value(s, sm, k);
        if (claim > 0 && claim - 1 == s.target && !((db >> k) & 1)) return true;
    }
    return false;
}
int tank_bits(State& s) {
    if (s.tank_bits >= 0) return s.tank_bits;""")
rep("""    if (use_dash && s.dash_slot >= 0 && !s.mp_dashholes.is_empty() && fuel_ok(40000)) {
        int r = mp_dash_hole_step(s, me, goals, vblock, pos);  // mapplan_game.h rule 5: plan across holes we can dash""",
"""    if (P_MP_HOLE && use_dash && s.dash_slot >= 0 && !s.mp_dashholes.is_empty() && fuel_ok(40000) &&
        (P_MP_HOLE_SMALL <= 0 || static_cast<long>(bc::map::width()) * static_cast<long>(bc::map::height()) >= P_MP_HOLE_SMALL) &&
        (P_MP_HOLE != 2 || !hole_splits_group(s))) {  // o68: 0 = no hole routes; 2 = not when it leaves a dash-less ally behind; off on maps < P_MP_HOLE_SMALL tiles
        int r = mp_dash_hole_step(s, me, goals, vblock, pos);  // mapplan_game.h rule 5: plan across holes we can dash""")
# hole_splits_group needs claim helpers and g_mode declared before step_towards: forward declarations
rep("""bool step_towards(State& s, bc::champion& me, const bc::bitboard& goals_in, bool use_dash) {""",
"""bool hole_splits_group(State& s);  // o68 (defined with tank_bits)
bool step_towards(State& s, bc::champion& me, const bc::bitboard& goals_in, bool use_dash) {""")
open(p,'w',newline='').write(s)
p=d+'/params.h'; s=open(p,newline='').read()
rep("""#ifndef P_HOLEFIX""","""#ifndef P_MP_HOLE
#define P_MP_HOLE 2  // o68: 1 = dash champions plan across crossable holes (mapplan rule 5); 0 = never; 2 = only when no dash-less ally shares the target
#endif
#ifndef P_MP_HOLE_SMALL
#define P_MP_HOLE_SMALL 0  // o68 v3: no hole routes at all on maps with fewer tiles than this (0 = no size rule); 2500 covers reverse_spiral (900) and rushbait_v2 (2400)
#endif
#ifndef P_HOLEFIX""")
open(p,'w',newline='').write(s)
