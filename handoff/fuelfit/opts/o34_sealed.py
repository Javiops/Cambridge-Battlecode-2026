# fuelfit o34 (recall/altares): altar_sealed (boss_battle/corners-type maps) is called 4-5 times per trip turn (every
# best_altar and br_altar_distance) and cost ~2.3k each (11-12k a bank turn on corners): two new boards, the ring's
# positions() (~770) and two is_set per ring tile. Now the boards are read into static ones and the "some ring tile
# in vision without a live camp" test is board algebra: vis &= ring; live &= vis; open = vis != live. Same reads,
# same exception path (visible_tiles_into/camp_tiles_into throw as the copies did), same answer.
# Measured: the hot part is the static set-up on each champion's first call (~11k, at its first trip). Moving it to
# a fixed early turn is NOT exact (boss_battle 2/2 replays differ: the camp tiles it reads change after r5), so it
# stays where it is; the turn cost is bounded (one pass over the group tiles).
# cr_return_walk: the one-off home field no longer waits for fuel_ok(22000) (with unlimited fuel it was always true).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""        bool open = false;
        attempt([&] {
            bc::bitboard vis = bc::vision::visible_tiles(), live = bc::vision::camp_tiles();
            for (auto p : ring.positions())
                if (vis.is_set(p) && !live.is_set(p)) { open = true; break; }
            return true;
        });
        return !open;""","""        bool open = false;
        attempt([&] {
            static bc::bitboard vis{ bc::uninitialized }, live{ bc::uninitialized };  // fuelfit o34
            bc::vision::visible_tiles_into(vis);
            bc::vision::camp_tiles_into(live);
            vis &= ring;
            live &= vis;
            open = !(vis == live);  // a ring tile in vision without a live camp
            return true;
        });
        return !open;""")
rep("""        s.cr_home_retry = round + 16;
        if (fuel_ok(22000)) {
            s.cr_home_ready = attempt([&] {
                bc::bitboard roots = s.my_spawn & ~s.static_block;
                s.cr_home_df.compute(s.static_block, roots, s.cr_home_seen, 200);
                return true;
            });
        }""","""        s.cr_home_retry = round + 16;
        s.cr_home_ready = attempt([&] {  // fuelfit o34: no fuel_ok(22000)
            bc::bitboard roots = s.my_spawn & ~s.static_block;
            s.cr_home_df.compute(s.static_block, roots, s.cr_home_seen, 200);
            return true;
        });""")
open(p,'w',newline='').write(s)
