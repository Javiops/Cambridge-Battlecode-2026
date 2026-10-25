# fuelfit o13 (exact): ward_turn's fixed part (chebyshev draw, bitboard ops, vision query, placement tiles, positions)
# cost 5-9k on every even round with the cooldown over, even with no bush anywhere near. Now a static list of the map's
# bush tiles (read once) is scanned in C++ first (~10 instructions per bush); the boards are only built when a bush
# lies within P_WARD_R, which is exactly the case where `dark` could be non-empty.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:70],s.count(a)); s=s.replace(a,b)
rep("""    vec2 pos = me.position();
    if (s.my_spawn.is_set(pos)) return;
    static const bc::bitboard bushes = bc::map::bushes();  // fuelfit o04: static map data
    bc::bitboard dark;""","""    vec2 pos = me.position();
    if (s.my_spawn.is_set(pos)) return;
    static const bc::bitboard bushes = bc::map::bushes();  // fuelfit o04: static map data
    static const std::vector<vec2> bush_list = bushes.positions();  // fuelfit o13: read once
    {
        bool near = false;
        for (const auto b : bush_list)
            if (std::abs(X(b) - X(pos)) <= P_WARD_R && std::abs(Y(b) - Y(pos)) <= P_WARD_R) { near = true; break; }
        if (!near) return;  // fuelfit o13: `dark` would be empty
    }
    bc::bitboard dark;""")
open(p,'w',newline='').write(s)
