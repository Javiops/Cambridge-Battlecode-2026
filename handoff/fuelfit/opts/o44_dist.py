# fuelfit o44 (shared helper, farm section is its heaviest user): dist() in 32-bit arithmetic. vec2::chebyshev_distance
# promotes to int64 (max(abs(int64), abs(int64))): 50 fuel per call on wasm32 (bench b7: dist x1000 = 50015). The
# scoring loop of choose_target calls it ~6 times per group per turn, step_towards and the fight code call it in loops.
# Exact: map coordinates are small (|x|,|y| < 2^15), so int32 differences and abs never overflow and the max is the
# same value; the result was already truncated to int. No fuel_ok, no output.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""inline int dist(vec2 a, vec2 b) { return static_cast<int>(a.chebyshev_distance(b)); }""",
"""inline int dist(vec2 a, vec2 b) {  // fuelfit o44: 32-bit Chebyshev distance (same value as vec2::chebyshev_distance)
    const int dx = a.x > b.x ? a.x - b.x : b.x - a.x, dy = a.y > b.y ? a.y - b.y : b.y - a.y;
    return dx > dy ? dx : dy;
}""")
open(p,'w',newline='').write(s)
print("o44 ok")
