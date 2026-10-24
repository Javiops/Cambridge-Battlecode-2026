# fuelfit o01: cache vision::champions per side, keyed by the side's champion tiles this round (exact)
import glob,sys
d=sys.argv[1]
m=open(d+'/main.cpp',newline='').read()
anchor="// Every SDK action can throw (cambc::error, out_of_range, ...)."
assert m.count(anchor)==1
fn='''// fuelfit-v1: the visible champions of a side, re-read only when that side's champion tiles changed this turn
// (the SDK rebuilds the list from the tiles on every call, ~3000 fuel with 4 in view, 6.5 calls on a heavy turn).
std::vector<bc::champion> vis_champions(bc::team side) {
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
}

'''
m=m.replace(anchor,fn+anchor); open(d+'/main.cpp','w',newline='').write(m)
for f in glob.glob(d+'/*.cpp')+glob.glob(d+'/*.h'):
    s=open(f,newline='').read(); s2=s.replace('bc::vision::champions(*s.','vis_champions(*s.')
    if s2!=s: open(f,'w',newline='').write(s2)
