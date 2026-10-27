# aw "alerta temprana" (superiority thread 10-27). t5b 2.0.0 replays, E1 vs top 5, r151-300: we die 1.79/game (top 5
# 0.61); 85% by champions, 53% with no ally within 6, 51% outnumbered, 76% on our own half. r21-100: contacts start
# 2.1 of us vs 2.7 of them within 4, and nobody reinforces after the start. A champion that sees P_AW_N+ rivals within
# P_AW_R and has fewer allies around (within P_AW_AR, recalling ones not counted) leaves BEFORE the contact: toward the
# nearest visible ally within 12, else away (back_off). Not on spawn, not when the foe in reach dies to our hit.
import sys
p = sys.argv[1] + '/main.cpp'
s = open(p).read()
a = """    bool fight_fav = false;  // P_CAMPFOE: step 3's verdict on the fight"""
assert s.count(a) == 1
s = s.replace(a, """#ifndef P_AW
#define P_AW 1
#endif
#ifndef P_AW_FROM
#define P_AW_FROM 21
#endif
#ifndef P_AW_R
#define P_AW_R 8
#endif
#ifndef P_AW_AR
#define P_AW_AR 6
#endif
#ifndef P_AW_N
#define P_AW_N 2      // at least this many rivals
#endif
#ifndef P_AW_M
#define P_AW_M 1      // and at least this many more than us
#endif
#ifndef P_AW_NOAL4
#define P_AW_NOAL4 0  // 1: no retreat when an ally is already within 4 (same fight: keep shooting)
#endif
#ifndef P_AW_MIND
#define P_AW_MIND 0   // only before contact: nearest rival at least this far
#endif
#ifndef P_AW_OWN
#define P_AW_OWN 0    // 1: only on our half (nearer our spawn than theirs)
#endif
    if (P_AW && round >= P_AW_FROM && !on_spawn && nearest_foe <= P_AW_R && fuel_ok(12000) &&
        (!P_AW_OWN || dist(pos, s.spawn_center) < dist(pos, s.en_center)) && nearest_foe >= P_AW_MIND) {
        int eb = 0;
        const Foe* nf = nullptr;
        for (auto& f : foes)
            if (f.d <= P_AW_R && !s.en_spawn.is_set(f.p) && !gone(f)) { ++eb; if (!nf || f.d < nf->d) nf = &f; }
        if (eb >= P_AW_N) {
            int nb = 1, aw_al4 = 0;
            vec2 ap{0, 0};
            int apd = 99;
            attempt([&] {
                for (auto& a : vis_champions(*s.my)) {
                    if (a == me || !a.is_alive() || a.is_recalling()) continue;
                    const vec2 q = a.position();
                    const int d = dist(q, pos);
                    if (d <= P_AW_AR) ++nb;
                    if (d <= 4) ++aw_al4;
                    if (d < apd && !s.my_spawn.is_set(q)) { apd = d; ap = q; }
                }
                return true;
            });
            const bool kill = nf && nf->d <= static_cast<int>(me.attack_range()) && nf->hp <= me.strength() * (P_GA_KILL_X / 10.0f);
#ifndef P_AW_PERS
#define P_AW_PERS 1   // the condition must hold this many rounds in a row
#endif
            static int aw_last = -10, aw_run = 0;
            const bool aw_cond = eb >= nb + P_AW_M && !kill && !(P_AW_NOAL4 && aw_al4 > 0);
            if (aw_cond) { aw_run = (aw_last == round - 1) ? aw_run + 1 : 1; aw_last = round; }
            if (aw_cond && aw_run >= P_AW_PERS) {
                g_mode = "aw";
                ++g_aw;
                if (gems > 0 && nearest_foe > 3) {
                    auto al = best_altar(s, pos, round);
                    if (al && dist(*al, pos) <= 1 && go_tribute(s, me, round)) return;
                }
                bool hit = fight::hit_now(s, me, foes);
                bool moved = false;
                if (apd > P_AW_AR && apd <= 12 && me.can_move()) {
                    bc::bitboard ring;
                    ring.draw_chebyshev(ap, 1.0f);
                    moved = step_towards(s, me, ring & ~s.blocked, true);
                }
                if (!moved) { if (!fight::safe_step(s, me, foes)) flee(s, me); }
                if (!hit) shoot_back(s, me, foes);
                return;
            }
        }
    }
    bool fight_fav = false;  // P_CAMPFOE: step 3's verdict on the fight""")
a = "int g_wp = 0;"
assert s.count(a) == 1
s = s.replace(a, "int g_aw = 0;  // aw: early-warning leaves\nint g_wp = 0;")
import re
m = re.search(r'    std::printf\("\[fuelfit\][^\n]*\n', s)
s = s[:m.end()] + '    std::printf("[sup] aw%d own%d p%d d%d n4%d r%d R%d AR%d N%d M%d\\n", P_AW, P_AW_OWN, P_AW_PERS, P_AW_MIND, P_AW_NOAL4, P_AW_FROM, P_AW_R, P_AW_AR, P_AW_N, P_AW_M);\n' + s[m.end():]
open(p, 'w').write(s)
print('ok aw')
