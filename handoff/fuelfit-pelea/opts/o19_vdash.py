# fuelfit o19 (pelea, Vesper): kite_shoot_first's dash scan read four engine bitboards / bounds per tile of its 7x7
# square (~250 fuel a tile, ~12k a scan). A tile's score is at most -1000 * threats + 400 (the spawn term only
# subtracts), so a tile with that bound <= best + 500 can never be kept: the threat count (plain arithmetic) is
# computed first and such tiles skip the engine reads. Bounds use the static map size (same test as is_in_bounds).
# Same tiles, same order, same strict '>': exact.
import sys
d=sys.argv[1]; p=d+'/vesper.h'; s=open(p,newline='').read()
a="""                    int bs = sc(pos);
                    std::optional<vec2> bt;
                    for (int dx = -3; dx <= 3; ++dx)
                        for (int dy = -3; dy <= 3; ++dy) {
                            vec2 t = pos + vec2(dx, dy);
                            if ((!dx && !dy) || !bc::map::is_in_bounds(t) || !ok.is_set(t) || s.blocked.is_set(t)) continue;
                            int v = sc(t);
"""
assert s.count(a)==1
s=s.replace(a,"""                    int bs = sc(pos);
                    std::optional<vec2> bt;
                    static const int map_w = bc::map::width(), map_h = bc::map::height();  // fuelfit o19
                    for (int dx = -3; dx <= 3; ++dx)
                        for (int dy = -3; dy <= 3; ++dy) {
                            vec2 t = pos + vec2(dx, dy);
                            if (!dx && !dy) continue;
                            int th = 0;  // fuelfit o19: the best this tile can score, before any engine read
                            for (std::size_t i = 0; i < near.size(); ++i)
                                if (dist(t, near[i]->p) <= reaches[i]) ++th;
                            if (-1000 * th + 400 <= bs + 500) continue;
                            if (X(t) < 0 || Y(t) < 0 || X(t) >= map_w || Y(t) >= map_h || !ok.is_set(t) || s.blocked.is_set(t)) continue;
                            int v = sc(t);
""")
open(p,'w',newline='').write(s)
