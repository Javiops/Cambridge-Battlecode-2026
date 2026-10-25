# o76_warmdefer.py SRCDIR (NOT EXACT: start-up timing; judge by strength). Over b35 (o74). The farm warm-up (tile index
# lists + per-group constants, 20-26k on 13-22 group maps) is pure precomputation that farm_warmup_now() builds on first
# use, so it can leave turn 1. Measured start-up without it (idbg.py on b32, max champion): rushbait 146k, stampede 148k,
# collision 148k, gem_fields 152k, broken_curve 153k, swirl 158k, concentrated_wealth 159k, great_wall 164k, shortcut
# 167k; with the ~20k turn overhead all stay under the 200k cap with >= 13k margin (starfish, 169k start-up, reached 189k).
# Those nine maps played from r3 (start-up overflowed turn 1); o76 plays them from r2 with the warm-up paid in the first
# playing turn (r2 budget 100k, first play turn measured <= 60k). Rule: <= 22 groups, <= 3000 tiles, not (>= 2000 tiles
# and >= 20 groups) (monolith 172k, quadrants 176k, lost_world 175k, elk_arena 180k stay r3: too close to the cap).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:70],s.count(a)); s=s.replace(a,b)
rep("""    int dh_round = 0;        // o74: round in which the deferred dash-hole scan runs (0 = done in the start-up)
""","""    int dh_round = 0;        // o74: round in which the deferred dash-hole scan runs (0 = done in the start-up)
    bool fw_defer = false;   // o76: farm warm-up left out of turn 1 (farm_warmup_now builds it in the first playing turn)
""")
rep("""        farm_warmup(s, 1000000);  // fuelfit o47/o48: the farm tables (2.5k + 600 per group) in the start-up turn too
        {
            const long tiles = static_cast<long>(bc::map::width()) * static_cast<long>(bc::map::height());
            const std::size_t ng = s.groups.size();
            // fuelfit o74: the first turn holds the start-up (measured per pool map, fuelturns.py/idbg.py) and nothing else
            const int ts0 = s.roster;  // champions per team (init_map)
            if (tiles <= 1000 && (ng <= 8 || (ng <= 12 && ts0 <= 4))) s.play_from = 1;  // class A: start-up <= 118k, play fits too
            else if ((ng <= 16 && tiles <= 2500) || (ng <= 19 && tiles <= 1000)) s.play_from = 2;  // start-up <= 160k (turn 1 <= 190k measured): ends inside round 1
            else s.play_from = 3;  // the start-up overflows into round 2 (no action issued, nothing diverges)
        }
""","""        {
            const long tiles = static_cast<long>(bc::map::width()) * static_cast<long>(bc::map::height());
            const std::size_t ng = s.groups.size();
            // fuelfit o74: the first turn holds the start-up (measured per pool map, fuelturns.py/idbg.py) and nothing else
            const int ts0 = s.roster;  // champions per team (init_map)
            if (tiles <= 1000 && (ng <= 8 || (ng <= 12 && ts0 <= 4))) s.play_from = 1;  // class A: start-up <= 118k, play fits too
            else if ((ng <= 16 && tiles <= 2500) || (ng <= 19 && tiles <= 1000)) s.play_from = 2;  // start-up <= 160k (turn 1 <= 190k measured): ends inside round 1
            else if (ng <= 22 && tiles <= 3000 && !(tiles >= 2000 && ng >= 20)) { s.play_from = 2; s.fw_defer = true; }  // o76: start-up without the warm-up <= 167k
            else s.play_from = 3;  // the start-up overflows into round 2 (no action issued, nothing diverges)
            if (!s.fw_defer) farm_warmup(s, 1000000);  // fuelfit o47/o48: the farm tables (2.5k + 600 per group) in the start-up turn too
        }
""")
rep("""[fuelfit] b37 o74 o75 det""","""[fuelfit] b38 o74 o76 det""") if '[fuelfit] b37' in s else rep("""    std::printf("[init] %s melee=""","""    std::printf("[fuelfit] b38 o74 o76 det\\n");
    std::printf("[init] %s melee=""")
open(p,'w',newline='').write(s)
print('ok')
