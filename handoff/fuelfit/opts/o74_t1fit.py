# o74_t1fit.py SRCDIR (NOT EXACT: start-up timing; judge by strength). Over b32 (o72 + o68). Measured with the replay
# bundles' team-x.fuel files (fuelturns.py) and a per-step debug build (idbg.py) on the 40 pool maps, unlimited fuel:
# the first turn's total is the start-up (map 14-56k, groups ~2k each, paths 7-40k, roles+shop 42-55k, dash holes 7-13k,
# farm warm-up 11-49k) + ~33k (engine 14k + logs) and the cap is 200k. o72's class B added the idle round's fields
# (29-37k) to turn 1 and overflowed it on reverse_spiral (HoR/Vesper 210k/206k), gemfight (all four) and gold_rush;
# class A overflowed on elkring (5 champions); the dash-hole scan tipped corridors/rushbait/starfish/collision over.
# An overflowed turn 1 eats round 2 (the program resumes there and ends its turn), so the champion acts first in r3.
# In b15-b32, 124 of 234 champions in the 52 near games overflowed turn 1.
# o74: (1) never run init_wait in turn 1 (the fields come from the static queue, o64); (2) class A (play in turn 1) only
# with <= 8 groups, or <= 12 groups and <= 4 champions, on maps <= 1000 tiles; (3) the dash-hole scan leaves turn 1 on
# maps with >= 12 groups and <= 2500 tiles and runs in round P_DH_ROUND (6; rushbait r4 reached 94k) instead (resumable scan, no fuel read);
# (4) the first playing round is 2 when the start-up fits (<= 16 groups on maps <= 2500 tiles, or <= 20 groups on
# maps <= 1000 tiles: turn 1 <= 190k measured; collision 196k stays r3), else 3. Adds r2 play on gold_rush, starfish, gemfight, collision.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:70],s.count(a)); s=s.replace(a,b)
rep("""        if (s.dash_slot >= 0) mp_find_dashholes(s);  // mapplan_game.h rule 5 (o06: one bitboard pass)
""","""        {
            const long tiles0 = static_cast<long>(bc::map::width()) * static_cast<long>(bc::map::height());
            if (s.dash_slot >= 0 && !(s.groups.size() >= 12 && tiles0 <= 2500)) mp_find_dashholes(s);  // mapplan_game.h rule 5 (o06); o74: on 12+ group near maps the scan runs in round P_DH_ROUND
            else if (s.dash_slot >= 0) s.dh_round = P_DH_ROUND;
        }
""")
rep("""            if (ng <= 12 && tiles <= 1000) s.play_from = 1;  // fuelfit o72 class A
            else if (ng <= 19 && tiles <= 1000) { s.play_from = 2; s.wait_in_r1 = true; }  // class B
            else s.play_from = ng <= INIT_SMALL ? 2 : 3;
""","""            // fuelfit o74: the first turn holds the start-up (measured per pool map, fuelturns.py/idbg.py) and nothing else
            const int ts0 = s.roster;  // champions per team (init_map)
            if (tiles <= 1000 && (ng <= 8 || (ng <= 12 && ts0 <= 4))) s.play_from = 1;  // class A: start-up <= 118k, play fits too
            else if ((ng <= 16 && tiles <= 2500) || (ng <= 19 && tiles <= 1000)) s.play_from = 2;  // start-up <= 160k (turn 1 <= 190k measured): ends inside round 1
            else s.play_from = 3;  // the start-up overflows into round 2 (no action issued, nothing diverges)
""")
rep("""            if (s.wait_in_r1) init_wait(s);  // class B: the idle round's work, here
""","""            // o74: no idle-round work in turn 1 (o72's class B overflowed it); the static queue computes the fields
""")
rep("""    if (s.dash_slot >= 0 && s.dh_stage < 2 && fuel_ok(P_DHFUEL_NEED)) mp_find_dashholes(s);  // t10draft-fx-v1: finish the scan
""","""    if (s.dash_slot >= 0 && s.dh_stage < 2 && s.dh_round > 0 && round >= s.dh_round) mp_find_dashholes(s);  // o74: the scan deferred from turn 1, in a fixed round (no fuel read)
""")
rep("""    int dh_stage = 0;
""","""    int dh_stage = 0;
    int dh_round = 0;        // o74: round in which the deferred dash-hole scan runs (0 = done in the start-up)
""")
open(p,'w',newline='').write(s)
p=d+'/params.h'; s=open(p,newline='').read()
rep("""#ifndef P_MP_HOLE
""","""#ifndef P_DH_ROUND
#define P_DH_ROUND 6  // o74: round of the dash-hole scan on 12+ group near maps (out of the start-up turn)
#endif
#ifndef P_MP_HOLE
""")
open(p,'w',newline='').write(s)
