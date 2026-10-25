# o61 pA (pelea-v1, J2 +16.7 vs kvvl +10.4 on the old fuel-dependent base): vkite-v3 (vesper.h) + mstick-v1 (marcella.h).
# Decision change (not exact): judge by changed games / J2 against the deterministic base.
# - vkite-v3: with a rival that reaches Vesper standing at 1-2 tiles and no dash ready, she skips the shot (a shot costs
#   the step out) and lets fight::kite step and stun, unless the shot kills. Top 10 Vesper before r150: 9% of PvP
#   rounds at 1 tile, ours 14%.
# - mstick-v1: Marcella adjacent to a rival, below P_MS_HP (70) % hp and 1 + allies within 3 - rivals within 3 <=
#   P_MS_NUM (0) backs off (fight::back_off), unless that rival dies to two hits. Top 10 Marcella r<150: adjacent in 14%
#   of PvP rounds, ours 31%.
# Fuel rules: no fuel_ok, no new printf (the old [ms] line and status counters are dropped); loops bounded by the
# visible foes / allies (vis_champions, cached per turn by o01).
import sys
d=sys.argv[1]
def edit(fn, pairs):
    p=d+'/'+fn; s=open(p,newline='').read()
    for a,b in pairs:
        assert s.count(a)==1,(fn,a[:60],s.count(a)); s=s.replace(a,b)
    open(p,'w',newline='').write(s)
p=d+'/params.h'; s=open(p,newline='').read(); nl='\r\n' if '\r\n' in s else '\n'
s=s.rstrip('\r\n')+nl+nl.join(["","// pelea-v1 per champion (o61: vesper.h vkite-v3, marcella.h mstick-v1)",
"#ifndef P_VK3","#define P_VK3 1","#endif",
"#ifndef P_VK3_HP","#define P_VK3_HP 0     // 0 = hp does not matter; else keep shooting above this % hp","#endif",
"#ifndef P_MS","#define P_MS 1","#endif",
"#ifndef P_MS_HP","#define P_MS_HP 70","#endif",
"#ifndef P_MS_NUM","#define P_MS_NUM 0     // back off when 1 + allies - rivals (within 3) <= this","#endif"])+nl
open(p,'w',newline='').write(s)
edit('champions.h',[("""namespace marcella {
CHAMP_HOOK bool is(const std::string& n);
CHAMP_HOOK bool late_mix(const State& s, std::vector<LateFill>& o);
CHAMP_HOOK bool shop_plan(State& s);
}""","""namespace marcella {
CHAMP_HOOK bool is(const std::string& n);
CHAMP_HOOK bool late_mix(const State& s, std::vector<LateFill>& o);
CHAMP_HOOK bool shop_plan(State& s);
CHAMP_HOOK bool gives_ground(State& s, bc::champion& me, std::vector<Foe>& foes, vec2 pos, float hpr, bool on_spawn, int round);
}""")])
edit('marcella.h',[("""}  // namespace marcella""","""// mstick-v1 (o61, play_turn, start of the fight step): Marcella next to a rival without the numbers gives ground.
// Top 10 Marcella before r150: 14% of PvP rounds adjacent to a rival, 43% outnumbering it by 2, trade 1.45;
// ours 31%, 19%, 1.08. Adjacent (<= 1) to a rival, hurt below P_MS_HP %, and 1 + allies within 3 - rivals within 3
// <= P_MS_NUM: back off, unless the rival dies to two hits. true = turn done.
CHAMP_HOOK bool gives_ground(State& s, bc::champion& me, std::vector<Foe>& foes, vec2 pos, float hpr, bool on_spawn, int round) {
    if (!P_MS || on_spawn || foes.empty() || hpr * 100 >= P_MS_HP || !is(s.name)) return false;
    int adj = 0, fo = 0;
    bool kill = false;
    for (auto& f : foes) {
        if (s.en_spawn.is_set(f.p)) continue;
        if (f.d <= 3) ++fo;
        if (f.d <= 1) { ++adj; if (f.hp <= 2.0f * me.strength()) kill = true; }
    }
    if (!adj || kill) return false;
    int al = 0;
    attempt([&] {
        for (auto& a : vis_champions(*s.my))
            if (!(a == me) && a.is_alive() && dist(a.position(), pos) <= 3) ++al;
        return true;
    });
    if (1 + al - fo > P_MS_NUM) return false;
    fight::back_off(s, me, foes, round);
    return true;
}

}  // namespace marcella""")])
edit('vesper.h',[("""        if (!thr || dash || me.health() >= P_VKITE_HP / 100.0 * me.max_health()) {""","""#if P_VK3
        // vkite-v3 (o61): shoot from the edge of her range, then leave. With a rival that reaches her standing at 1-2
        // tiles and no dash, a shot costs the step out: step (fight::kite step 1) and stun it instead, unless the shot
        // kills. Top 10 Vesper before r150: 9% of PvP rounds at 1 tile, 1.5% hp lost a round; ours 14% and 2.5%.
        int td = 99;
        for (std::size_t i = 0; i < near.size(); ++i)
            if (dist(pos, near[i]->p) <= reaches[i]) td = std::min(td, dist(pos, near[i]->p));
        const bool kill = focus->hp <= me.strength();
        const bool shoot = !thr || dash || kill || td >= 3 || (P_VK3_HP && me.health() >= P_VK3_HP / 100.0 * me.max_health());
        if (!shoot) return false;
        if (shoot) {
#else
        if (!thr || dash || me.health() >= P_VKITE_HP / 100.0 * me.max_health()) {
#endif""")])
edit('main.cpp',[("""    FP(9, "fight");
    g_mode = "fight";
""","""    FP(9, "fight");
    g_mode = "fight";
    if (marcella::gives_ground(s, me, foes, pos, hpr, on_spawn, round)) { g_mode = "m-ground"; return; }  // o61 mstick-v1
""")])
