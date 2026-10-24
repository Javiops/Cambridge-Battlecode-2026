# fuelfit o02: vis_champions keyed by (round, my position, wards placed): during our turn nothing else moves, and our
# vision only changes when we move (walk, dash, crystal) or place a ward. Returned by const reference (no copy).
import sys,glob
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,a; s=s.replace(a,b)
rep("""std::vector<bc::champion> vis_champions(bc::team side) {
    static int r[2] = {-1, -1};
    static bc::bitboard key[2];
    static std::vector<bc::champion> val[2];
    const int i = side == bc::team::ally ? 0 : 1;
    const int round = static_cast<int>(bc::round_number());
    bc::bitboard t = bc::vision::champion_tiles(side);
    if (r[i] == round && t == key[i]) return val[i];
    std::vector<bc::champion> out;
    const auto ps = t.positions();
    out.reserve(ps.size());
    for (const auto p : ps) out.push_back(bc::vision::champion_at(p));
    r[i] = round;
    key[i] = std::move(t);
    val[i] = out;
    return out;
}""","""int g_ward_n = 0;
const std::vector<bc::champion>& vis_champions(bc::team side) {
    static int r[2] = {-1, -1}, kx[2], ky[2], kw[2];
    static std::vector<bc::champion> val[2];
    const int i = side == bc::team::ally ? 0 : 1;
    const int round = static_cast<int>(bc::round_number());
    const vec2 mp = bc::self().position();
    if (r[i] == round && kx[i] == X(mp) && ky[i] == Y(mp) && kw[i] == g_ward_n) return val[i];
    const auto ps = bc::vision::champion_tiles(side).positions();
    val[i].clear();
    val[i].reserve(ps.size());
    for (const auto p : ps) val[i].push_back(bc::vision::champion_at(p));
    r[i] = round; kx[i] = X(mp); ky[i] = Y(mp); kw[i] = g_ward_n;
    return val[i];
}""")
rep("int g_ward_n = 0;\nvoid ward_turn(State& s) {","void ward_turn(State& s) {")
open(p,'w',newline='').write(s)
