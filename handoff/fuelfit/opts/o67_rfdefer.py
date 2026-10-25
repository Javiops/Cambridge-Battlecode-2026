# o67_rfdefer.py SRCDIR (fuelfit, farm thread; NOT EXACT: a decision change, judge by strength; over b15 + o59 + o63 +
# o64 (+ o66)). The periodic re-choice of the farm target (`refresh`: round - target_round >= P_E_RETARGET = 6) is the
# r8-r9 peak on 11 of the 14 far maps (ambush r8 77-95k, starvation r8 71-90k, big_world r9 86k, fracture/road r9
# 62-71k): the champion has moved since its first choice, the per-position cache misses and the groups' reverse fields
# (o54: one static field per cheap turn) are not all computed yet, so choose_target pays the full forward field again
# (13-30k) plus the read-out, and the first step to the new target adds the goal and hole searches (20-35k).
# With P_RF_DEFER = 1 the periodic refresh waits until the reverse fields are complete (farm_pd_done) or we stand on the
# tile the cached distances were measured at (the choice is then ~1.5k: one get per group). A missing target or an
# expired one still chooses at once, as before. Map feature: only on maps of P_RF_DEFER_AREA tiles or more (default 4096:
# the forward field costs 4-14k on 41x41, nothing to save, so near maps play exactly as before) and only while
# round < P_RF_DEFER_R (default 60: a cap in case the reverse fields never complete). Effect on the far maps (e67p vs
# e64pf, r2-r40): no choose_target >= 15k on r4-r12 (b15: 3-5 per map); max turn r4-r12 ambush 95k -> 86k, starvation
# 90k -> 80k, big_world 91k -> 88k, road 71k -> 62k, split 53k -> 41k; turns >= 77.5k r2-r40 ambush 27 -> 14,
# starvation 16 -> 6, big_world 23 -> 16. Replays (unlimited fuel) on ambush, big_world, starvation, expanse, corners:
# byte-identical to b15 on both sides (the deferred refresh confirms the same target): the fuel goes, the game stays.
# No fuel read.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""    bool refresh = !committed && round - s.target_round >= (ball_on(s, round) ? 3 : target_refresh);""",
"""    bool refresh = !committed && round - s.target_round >= (ball_on(s, round) ? 3 : target_refresh);
#if P_RF_DEFER
    // fuelfit o67: a periodic re-choice that would pay the full forward field (no reverse fields yet, position moved)
    // waits for the reverse fields; the r8-r9 peak on the far maps was this field.
    if (refresh && !farm_pd_done(s) && s.pd_pos != pos && round < P_RF_DEFER_R &&
        bc::map::width() * bc::map::height() >= P_RF_DEFER_AREA)
        refresh = false;
#endif""")
open(p,'w',newline='').write(s)
p=d+'/params.h'; s=open(p,newline='').read()
rep("""#ifndef P_HOLEFIX""","""#ifndef P_RF_DEFER
#define P_RF_DEFER 1  // fuelfit o67: the periodic target refresh waits until the reverse fields exist (1) or not (0 = b15)
#endif
#ifndef P_RF_DEFER_AREA
#define P_RF_DEFER_AREA 5000  // fuelfit o67: only on maps with at least this many tiles (the forward field is cheap below; fracture 61x71 = 4331 lost its first-target correction)
#endif
#ifndef P_RF_DEFER_R
#define P_RF_DEFER_R 60  // fuelfit o67: no deferral from this round on
#endif
#ifndef P_HOLEFIX""")
open(p,'w',newline='').write(s)
