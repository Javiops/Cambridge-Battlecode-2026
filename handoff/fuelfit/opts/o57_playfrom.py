# fuelfit o57 v2 (first playing round from a per-map table of measured start-up costs; v1 was the fitted model alone and
# played one round late on 9 maps: J2 +9.5 vs +11.3, reserve -2.8). v1 text: first playing round by a start-up cost model; replaces o08 v3's "<= 14 groups" rule). Start-up measured
# on the 40 maps with unlimited fuel (tools/heavy.py): cost_k ~ 68 + 18 * tiles/1000 + 5 * groups (least squares; worst
# residual +31k). Rounds the start-up needs: 1 if est <= 186k, else 1 + ceil((est - 186k) / 86k); the champion plays
# from the next round. Small maps (<= 14 groups and <= 3000 tiles, all measured <= 174k) keep round 2 as before. On
# big_world (373k) the old rule said round 3 while start-up really ended in round 4: the first moves then depended on
# the fuel (probe divergences at r11 on far maps).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
a="        s.play_from = s.groups.size() <= INIT_SMALL ? 2 : 3;\n"
assert s.count(a)==1
s=s.replace(a,"""        {  // fuelfit o57 v2: first playing round from the measured start-up cost of each map of the site pool (40 maps,
           // tools/heavy.py, unlimited fuel; key = tiles, groups, altars; cost in k, rounded up), +10k margin; an unknown
           // map falls back to the fitted model 68k + 18/tile + 5k/group + 20k. Rounds needed: 1 if <= 186k, then one
           // more per 86k; the champion plays from the next round.
            struct InitCost { int tiles, groups, altars, k; };
            static const InitCost table[] = {{{900, 6, 2, 118}, {900, 10, 2, 146}, {900, 14, 2, 163}, {900, 19, 2, 167}, {961, 8, 6, 138}, {961, 12, 1, 144}, {961, 15, 4, 153}, {1085, 34, 3, 235}, {1200, 28, 10, 263}, {1230, 8, 1, 142}, {1350, 22, 2, 207}, {1575, 32, 3, 249}, {1600, 14, 4, 163}, {1600, 21, 2, 217}, {1600, 22, 4, 200}, {1600, 51, 2, 337}, {1681, 20, 2, 196}, {2000, 17, 4, 212}, {2000, 18, 4, 202}, {2000, 28, 6, 260}, {2025, 21, 4, 228}, {2040, 12, 2, 189}, {2050, 31, 1, 279}, {2400, 18, 2, 192}, {2500, 9, 2, 177}, {2500, 14, 2, 173}, {2500, 16, 2, 194}, {2500, 20, 6, 222}, {2500, 29, 2, 238}, {2700, 42, 18, 298}, {3000, 13, 2, 195}, {3250, 23, 4, 251}, {3600, 46, 10, 324}, {3721, 11, 2, 212}, {4331, 28, 3, 299}, {5041, 30, 5, 269}, {6400, 14, 2, 258}, {6400, 24, 10, 272}, {10000, 12, 4, 289}, {10000, 24, 6, 383}}};
            const long tiles = static_cast<long>(bc::map::width()) * static_cast<long>(bc::map::height());
            long est = 68000 + 18 * tiles + 5000 * static_cast<long>(s.groups.size()) + 20000;
            for (const auto& e : table)
                if (e.tiles == tiles && e.groups == static_cast<int>(s.groups.size()) && e.altars == static_cast<int>(s.altars.size())) { est = 1000L * e.k + 10000; break; }
            const int rounds = est <= 186000 ? 1 : 1 + static_cast<int>((est - 186000 + 85999) / 86000);
            s.play_from = rounds + 1;
        }
""")
open(p,'w',newline='').write(s)
