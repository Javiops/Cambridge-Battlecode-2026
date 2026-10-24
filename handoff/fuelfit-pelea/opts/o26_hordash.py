# fuelfit o26 (pelea): heart_of_ruin::dash_strike scores up to 25 landing tiles. The landing geometry test is pure
# arithmetic, so it now runs before the two engine bitboard reads (blocked, valid tiles) instead of after; the map
# walls are static and read once per game; our health is read once per call instead of once per tile. Same tiles,
# same scores, same order. Exact.
import sys
d=sys.argv[1]; p=d+'/heart_of_ruin.h'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,a; s=s.replace(a,b)
rep("""        bc::bitboard in_range, walls;""","""        bc::bitboard in_range;
        const bc::bitboard* walls_p = nullptr;  // fuelfit o26: the map walls never change, read once per game""")
rep("""            in_range = ab.valid_tiles();
            walls = bc::map::walls();""","""            in_range = ab.valid_tiles();
            static const bc::bitboard static_walls = bc::map::walls();
            walls_p = &static_walls;""")
rep("bc::map::is_in_bounds(mid) && !walls.is_set(mid)) path = true;","bc::map::is_in_bounds(mid) && !walls_p->is_set(mid)) path = true;")
rep("""                    if (!bc::map::is_in_bounds(p) || s.blocked.is_set(p) || !in_range.is_set(p)) continue;
                    if (!patch_v1::dash_landing_geometry(X(origin),Y(origin),X(p),Y(p),X(tpos),Y(tpos))) continue;""","""                    if (!bc::map::is_in_bounds(p)) continue;
                    if (!patch_v1::dash_landing_geometry(X(origin),Y(origin),X(p),Y(p),X(tpos),Y(tpos))) continue;
                    if (s.blocked.is_set(p) || !in_range.is_set(p)) continue;""")
rep("""            const int dash_range = 2;  // the patched Heart of Ruin kit""","""            const int dash_range = 2;  // the patched Heart of Ruin kit
            const float my_hp = me.health();  // fuelfit o26: read once""")
rep("patch_v1::dash_score(hits,exposure,me.health(),dist(origin,p),champ)","patch_v1::dash_score(hits,exposure,my_hp,dist(origin,p),champ)")
open(p,'w',newline='').write(s)
