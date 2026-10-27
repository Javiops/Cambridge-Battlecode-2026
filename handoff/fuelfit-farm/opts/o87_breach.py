# o87_breach.py SRCDIR (farm thread; NOT EXACT: a decision change on one map class; judge by gems submitted).
# Engine 2.0.0 map feature "altar ringed by camps" (02the_pack: the single altar sits in a free pocket inside a ring of
# 48 wolves, one group of 64800 hp). b35 and every bot of our lineage never submit a gem there in 2000 rounds (8/8 games):
# the bank route ignores live camps, so the move into the ring fails every round, and the ring group is dropped whole as
# "too-strong" although one wolf (1350 hp) opens the pocket. P_SEALED (boss_battle) only covers altars whose ring tiles
# ARE camp tiles; this covers altars whose free ring is unreachable because camps block the way.
#   - breach_blocked(s): once per game, from the spawn: an altar ring reachable without camps but not with camp tiles as
#     walls (and not a P_SEALED case) => g_breach_map = 1. Only such maps run any new code.
#   - breach_update(s): every P_BREACH_EVERY rounds: walls = static | camps assumed alive out of vision | live camps in
#     vision; if a ring tile is reached the pocket is open (normal tribute, dynamic route that avoids live camps);
#     else the gate = the camp tile next to the reached region nearest to an altar; its group becomes the target.
#   - fight-camp on the gate group counts only the gate camp (admission for one wolf, not 48) and walks to the gate.
#   - while blocked, best_altar() gives no altar and the trip block is skipped (farm on), as P_SEALED does.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a[:70],s.count(a))
    s=s.replace(a,b)
# 1. state fields
rep("    bool mono_only = false;  // P_MONO: every gem on the map sits in a monolith group\n",
    "    bool mono_only = false;  // P_MONO: every gem on the map sits in a monolith group\n"
    "    int breach_group = -1, breach_round = -1000; vec2 breach_tile; bool breach_open = false;  // o87 breach: gate camp / group\n")
# 2. globals + functions before best_altar
rep("std::optional<vec2> best_altar_impl(State& s, vec2 pos, int round);\nbool g_sealed_hit = false;",
r'''// o87 breach: an altar whose free ring can only be reached through live camps (02the_pack: a ring of 48 wolves)
int g_breach_map = -1;  // -1 not checked yet, 0 no such altar (old path, no extra work), 1 every usable altar is ringed by camps
bc::bitboard g_camp_static;  // every camp spawn tile of the map
bool breach_blocked(State& s) {
    if (!P_BREACH) return false;
    if (g_breach_map < 0) {
        if (s.groups.empty() || !s.raw_groups.empty() || s.altars.empty()) return false;  // groups still being read
        g_breach_map = 0;
        attempt([&] {
            for (auto& g : s.groups)
                for (auto t : g.tiles) g_camp_static.set(t);
            bc::bitboard roots = s.my_spawn & ~s.static_block, r0, r1;
            bc::distance_field f0, f1;
            f0.compute(s.static_block, roots, r0, 400);
            f1.compute(s.static_block | g_camp_static, roots, r1, 400);
            bool any = false, all_enclosed = true, free_ring = false;
            for (std::size_t i = 0; i < s.altars.size(); ++i) {
                if (!s.altar_ok[i]) continue;
                bc::bitboard ring;
                ring.draw_chebyshev(s.altars[i], 1.0f);
                ring &= ~s.static_block;
                if ((ring & r0).is_empty()) continue;  // not reachable at all: not ours to breach
                any = true;
                if (!(ring & r1 & ~g_camp_static).is_empty()) all_enclosed = false;
                if (!(ring & ~g_camp_static).is_empty()) free_ring = true;  // ring tiles that are camps are P_SEALED's case
            }
            if (any && all_enclosed && free_ring) g_breach_map = 1;
            std::printf("[breach] map=%d altars=%d\n", g_breach_map, static_cast<int>(s.altars.size()));
            return true;
        });
    }
    return g_breach_map == 1 && !s.breach_open;
}
// every P_BREACH_EVERY rounds: is the pocket open from here? else which camp is the gate?
void breach_update(State& s, vec2 pos, int round) {
    attempt([&] {
        static bc::bitboard vis{ bc::uninitialized }, live{ bc::uninitialized };
        bc::vision::visible_tiles_into(vis);
        bc::vision::camp_tiles_into(live);
        bc::bitboard block = s.static_block | (g_camp_static & ~vis) | (live & vis);
        block.set(pos, false);
        bc::bitboard roots, reached;
        roots.set(pos);
        bc::distance_field f;
        f.compute(block, roots, reached, 400);
        for (std::size_t i = 0; i < s.altars.size(); ++i) {
            if (!s.altar_ok[i]) continue;
            bc::bitboard ring;
            ring.draw_chebyshev(s.altars[i], 1.0f);
            if (!(ring & reached & ~block).is_empty()) {
                s.breach_open = true; s.breach_group = -1;
                std::printf("[breach] r%d %s pocket open\n", round, s.name.c_str());
                return true;
            }
        }
        int best = 1 << 30; vec2 bt;
        for (vec2 t : (g_camp_static & block).positions()) {
            bool adj = false;
            for (int dx = -1; dx <= 1 && !adj; ++dx)
                for (int dy = -1; dy <= 1 && !adj; ++dy) {
                    vec2 q = t + vec2(dx, dy);
                    if ((dx || dy) && bc::map::is_in_bounds(q) && reached.is_set(q)) adj = true;
                }
            if (!adj) continue;
            int da = 1 << 20;
            for (std::size_t i = 0; i < s.altars.size(); ++i)
                if (s.altar_ok[i]) da = std::min(da, dist(t, s.altars[i]));
            int expo = 0;  // camps within 3 of the gate: they wake and hit the breacher
            for (vec2 u : (g_camp_static & block).positions()) if (dist(u, t) <= 3) ++expo;
            const int cost = expo * 300 + da * 100 + dist(t, pos);
            if (cost < best) { best = cost; bt = t; }
        }
        s.breach_open = false;  // closed (again): the wolves respawn
        if (best < (1 << 30)) {
            int gi = -1;
            for (int i = 0; i < static_cast<int>(s.groups.size()); ++i)
                if (s.groups[i].mask.is_set(bt)) { gi = i; break; }
            if (s.breach_group != gi || !(s.breach_tile == bt))
                std::printf("[breach] r%d %s gate (%d,%d) group %d\n", round, s.name.c_str(), X(bt), Y(bt), gi);
            s.breach_tile = bt; s.breach_group = gi;
        } else s.breach_group = -1;
        return true;
    });
}

std::optional<vec2> best_altar_impl(State& s, vec2 pos, int round);
bool g_sealed_hit = false;''')
# 3. best_altar: no altar while blocked
rep("std::optional<vec2> best_altar(State& s, vec2 pos, int round) {\n    if (g_sealed_map == 0) return best_altar_impl(s, pos, round);",
    "std::optional<vec2> best_altar(State& s, vec2 pos, int round) {\n    if (breach_blocked(s)) return std::nullopt;  // o87: the ring is closed; farm and breach instead\n    if (g_sealed_map == 0) return best_altar_impl(s, pos, round);")
rep("bool br_plan(State& s, vec2 pos, int round) {\n", "extern int g_breach_map;  // o87\nbool br_plan(State& s, vec2 pos, int round) {\n")
# 4. route cache off on breach maps (the dynamic route uses s.blocked, which has the live camps)
rep("    if (s.altars.size() <= 64 && br_static_ready(s)) {\n        ++g_brc_n;",
    "    if (!(P_BREACH && g_breach_map == 1) && s.altars.size() <= 64 && br_static_ready(s)) {  // o87: live camps matter here\n        ++g_brc_n;")
# 5. trip block skipped while blocked (as on sealed maps)
rep("!(P_SEALED && g_sealed_map == 1 && !best_altar(s, pos, round) && g_sealed_hit)) {  // P_SEALED: sealed altar, farm on",
    "!((P_SEALED && g_sealed_map == 1 && !best_altar(s, pos, round) && g_sealed_hit) || breach_blocked(s))) {  // P_SEALED / o87: sealed or ringed altar, farm on")
# 6. farm(): the gate group is the target while blocked
rep("        s.target = t;\n        s.target_round = round;\n        write_claim(s, t);\n    }\n    g_farm = \"travel\";\n",
    "        s.target = t;\n        s.target_round = round;\n        write_claim(s, t);\n    }\n"
    "    if (breach_blocked(s) || g_breach_map == 1) {  // o87: open the pocket first (and notice when it closes again)\n"
    "        if (s.breach_group < 0 || round - s.breach_round >= P_BREACH_EVERY) { s.breach_round = round; breach_update(s, pos, round); }\n"
    "        if (!s.breach_open && s.breach_group >= 0 && s.target != s.breach_group) {\n"
    "            s.target = s.breach_group; s.target_round = round; s.cap_start = -1;\n"
    "            write_claim(s, s.breach_group);\n"
    "        }\n"
    "    }\n"
    "    g_farm = \"travel\";\n")
# 7. fight-camp: only the gate camp counts, and we walk to it
rep("    Group& g = s.groups[s.target];\n    attempt([&] {  // replay overlay: yellow line to the camp we are farming",
    "    Group& g = s.groups[s.target];\n    const bool breach_t = breach_blocked(s) && s.target == s.breach_group;  // o87\n    attempt([&] {  // replay overlay: yellow line to the camp we are farming")
rep("        double dps = my_dps(s, me);\n        double afford = std::max(1.0, hp - mhp * P_RESERVE_PCT / 100.0);\n        int needed = squad_needed(rem, str, dps, afford);",
    "        if (breach_t)  // o87: the gate's neighbours within 3 wake and hit the breacher as well\n"
    "            for (auto& c : camps)\n"
    "                if (g.mask.is_set(c.spawn_position()) && !(c.spawn_position() == s.breach_tile) && dist(c.spawn_position(), s.breach_tile) <= 3)\n"
    "                    attempt([&] { if (c.health() > 0) str += c.strength(); return true; });\n"
    "        double dps = my_dps(s, me);\n        double afford = std::max(1.0, hp - mhp * P_RESERVE_PCT / 100.0);\n        int needed = squad_needed(rem, str, dps, afford);")
rep("        if (g.mask.is_set(c.spawn_position()) && attempt([&] { return c.health() > 0; })) live.push_back(&c);",
    "        if (g.mask.is_set(c.spawn_position()) && !(breach_t && !(c.spawn_position() == s.breach_tile)) && attempt([&] { return c.health() > 0; })) live.push_back(&c);  // o87: the gate only")
rep("        if (!step_towards(s, me, g.mask, true) && me.can_move() && P_IDLE_NOSTEP) {",
    "        bc::bitboard breach_goal;  // o87\n        if (breach_t) breach_goal.set(s.breach_tile);\n        if (!step_towards(s, me, breach_t ? breach_goal : g.mask, true) && me.can_move() && P_IDLE_NOSTEP) {")
open(p,'w',newline='').write(s)
# params
q=d+'/params.h'; t=open(q,newline='').read()
assert 'P_BREACH' not in t
t+="#ifndef P_BREACH\n#define P_BREACH 1        // o87: an altar ringed by camps (02the_pack) is opened by killing the gate camp, not waited at\n#define P_BREACH_EVERY 10  // o87: rounds between gate recomputations per champion\n#endif\n"
open(q,'w',newline='').write(t)
print('o87 applied to',d)
