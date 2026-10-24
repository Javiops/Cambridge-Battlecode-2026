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

// lshop-v1 weights (Power folded into Bruiser of the same stat): late fill mix from P_LSHOP_R. Marcella: their late hit damage 278 vs our 197 (bcf thread); t10 Bruiser h 3134 / f 2093 / s 1632 + Power-s 878, ours all Bruiser-h.
CHAMP_HOOK bool late_mix(const State& s, std::vector<LateFill>& o) {
    if (!is(s.name)) return false;
    o = {{"bruiser", 'h', 3.1f}, {"bruiser", 's', 2.5f}, {"bruiser", 'f', 2.1f}};
    return true;
}

// mstick-v1 (play_turn, start of the fight step): Marcella next to a rival without the numbers gives ground.
// Top 10 Marcella before r150: 14% of PvP rounds adjacent to a rival, 43% outnumbering it by 2, trade 1.45;
// ours 31%, 19%, 1.08. Adjacent (<= 1) to a rival, hurt below P_MS_HP %, and 1 + allies within 3 - rivals within 3
// <= P_MS_NUM: back off, unless the rival dies to two hits. true = turn done.
int ms_n = 0;
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
        for (auto& a : bc::vision::champions(*s.my))
            if (!(a == me) && a.is_alive() && dist(a.position(), pos) <= 3) ++al;
        return true;
    });
    if (1 + al - fo > P_MS_NUM) return false;
    ++ms_n;
    if (ms_n <= 10 || ms_n % 50 == 0) std::printf("[ms] r%d n=%d hp=%.0f%% al=%d fo=%d\n", round, ms_n, hpr * 100, al, fo);
    fight::back_off(s, me, foes, round);
    return true;
}

}  // namespace marcella
