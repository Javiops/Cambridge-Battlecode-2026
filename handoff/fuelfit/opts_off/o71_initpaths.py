# fuelfit o71 (exact): init_paths computes the enemy-spawn distance field (25-30k on 100x100) only to decide the jackpot
# rule, which needs a non-monolith group holding half the map's gems with spawn_pd >= 0. When no group qualifies the
# field is never read: skip the compute. (Exporting the fields instead of per-tile reads was tried: +10%, exports are
# metered by size.)
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
a='''    attempt([&] {
            bc::bitboard wall = bc::map::walls() | bc::map::holes() | s.my_spawn;
            bc::distance_field fe;
            bc::bitboard ve;
            fe.compute(wall, s.en_spawn & ~wall, ve);
            int total = 0;
            for (auto& g : s.groups) total += g.gems;
'''
assert s.count(a)==1
s=s.replace(a,'''    attempt([&] {
            int total = 0;
            for (auto& g : s.groups) total += g.gems;
            bool any = false;  // fuelfit o71: the field is only read for jackpot candidates
            for (auto& g : s.groups) if (!(g.monolith || g.gems * 2 < total || g.spawn_pd < 0)) any = true;
            if (!any) return true;
            bc::bitboard wall = bc::map::walls() | bc::map::holes() | s.my_spawn;
            bc::distance_field fe;
            bc::bitboard ve;
            fe.compute(wall, s.en_spawn & ~wall, ve);
''')
open(p,'w',newline='').write(s)
