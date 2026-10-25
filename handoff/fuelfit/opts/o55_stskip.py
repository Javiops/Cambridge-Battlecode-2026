# o55_stskip.py SRCDIR (fuelfit, farm thread; EXACT). step_towards runs two path searches when the first fails: with
# the live blockers, then with static walls + camps only. Both have s.static_block inside their block set, so when a
# static wall (holes, walls, altars, enemy spawn) separates us from every goal both fail after visiting the whole
# reachable map (26-30k each on 100x100: big_world (71,80) after a dash over holes, ambush's moated room, islands),
# before isle_escape runs a third one. The mainland (tiles our spawn walks to over s.static_block) is computed once;
# standing off it with every goal on it, the two searches are skipped (nothing after them reads s.df / s.visited
# unless the search succeeded). The mainland is computed in the o54 warm-up slot (first), or by isle_escape as before.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""bool isle_escape(State& s, bc::champion& me, const bc::bitboard& goals) {
    if (s.dash_slot < 0) return false;
    vec2 pos = me.position();
    // The mainland: tiles our spawn walks to over walls, holes, altars and the enemy spawn (one search, on the first
    // call). On it there is nothing to escape, and that check is all the rule costs: a goal we cannot reach from the
    // mainland is the usual code's business (a full search there every such turn cost 30-90 run-outs on wall maps).
    static bc::bitboard mainland;
    static bool mainland_ok = false;
    if (!mainland_ok) {
        if (!attempt([&] {
                bc::distance_field mf;
                mf.compute(s.static_block, s.my_spawn & ~s.static_block, mainland);
                return true;
            }))
            return false;
        mainland_ok = true;
    }
    if (mainland.is_set(pos) || static_cast<int>(bc::round_number()) < g_isle_off) return false;""",
"""// The mainland: tiles our spawn walks to over walls, holes, altars and the enemy spawn (one search). fuelfit o55:
// shared by isle_escape and step_towards; computed by the first of the o54 warm-up slot or isle_escape.
bc::bitboard g_mainland;
bool g_mainland_ok = false;
bool mainland_ready(State& s) {
    if (g_mainland_ok) return true;
    if (!attempt([&] {
            bc::distance_field mf;
            mf.compute(s.static_block, s.my_spawn & ~s.static_block, g_mainland);
            return true;
        }))
        return false;
    g_mainland_ok = true;
    return true;
}
bool isle_escape(State& s, bc::champion& me, const bc::bitboard& goals) {
    if (s.dash_slot < 0) return false;
    vec2 pos = me.position();
    // On the mainland there is nothing to escape, and that check is all the rule costs: a goal we cannot reach from the
    // mainland is the usual code's business (a full search there every such turn cost 30-90 run-outs on wall maps).
    if (!mainland_ready(s)) return false;
    const bc::bitboard& mainland = g_mainland;
    if (mainland.is_set(pos) || static_cast<int>(bc::round_number()) < g_isle_off) return false;""")
rep("""    bool ok_field = false;
    if (false) {  // mapplan_game.h rule 3: walk around awake camps we do not fight""",
"""    // fuelfit o55: off the mainland with every goal on it, no search with a block set that contains s.static_block
    // can reach us: skip the two below (26-30k each on 100x100), straight to isle_escape / fallback.
    bool sep = false;
    if (P_ISLE && g_mainland_ok && !s.static_block.is_set(pos) && !g_mainland.is_set(pos))
        sep = (goals_in & ~s.static_block & ~g_mainland).is_empty();
    bool ok_field = false;
    if (false) {  // mapplan_game.h rule 3: walk around awake camps we do not fight""")
rep("""    if (!ok_field)
        ok_field = attempt([&] {
            s.df.compute_to(vblock, goals, s.dest, s.visited);
            return s.visited.is_set(pos);
        });
    if (!ok_field && vol_on) return false;  // every way runs through a ready volley: wait
    if (!ok_field) {  // corridor jammed by champions: plan through them""",
"""    if (!ok_field && !sep)
        ok_field = attempt([&] {
            s.df.compute_to(vblock, goals, s.dest, s.visited);
            return s.visited.is_set(pos);
        });
    if (!ok_field && vol_on) return false;  // every way runs through a ready volley: wait
    if (!ok_field && !sep) {  // corridor jammed by champions: plan through them""")
# o54 warm-up slot: the mainland first (isle_escape would compute it on its first off-mainland call anyway)
rep("""            std::strcmp(g_mode, "tribute") != 0 && s.pd_fwd_round != static_cast<int>(bc::round_number()))
            farm_pd_ready(s);""","""            std::strcmp(g_mode, "tribute") != 0 && s.pd_fwd_round != static_cast<int>(bc::round_number())) {
            if (P_ISLE && !g_mainland_ok) mainland_ready(s);  // fuelfit o55
            else farm_pd_ready(s);
        }""")
open(p,'w',newline='').write(s); print('o55 ok')
