# fuelfit o21 (pelea): fight::reach() reads the foe's attack range, its name and its abilities (about 700 fuel a call,
# 4-10 calls on a fight turn from safe_step, kite, front_line and spell_sweep). Nothing it reads changes during our turn
# (rivals only act on their own turns), so the value is kept per (round, champion). Exact: same inputs, same result.
import sys
d=sys.argv[1]; p=d+'/fight.h'; s=open(p,newline='').read()
a="inline int reach(const Foe& f) {\n"
assert s.count(a)==1
s=s.replace(a,"inline int reach_read(const Foe& f) {\n")
b="inline int threats_at(vec2 t, const std::vector<Foe>& foes, const std::vector<int>& reaches) {"
assert s.count(b)==1
s=s.replace(b,'''inline int reach(const Foe& f) {
    static int memo_r = -1, memo_n = 0;
    static std::uint32_t memo_h[10];
    static int memo_v[10];
    const int round = static_cast<int>(bc::round_number());
    if (round != memo_r) { memo_r = round; memo_n = 0; }
    const auto h = static_cast<std::uint32_t>(static_cast<bc::handle_champion_t>(f.c));
    for (int i = 0; i < memo_n; ++i)
        if (memo_h[i] == h) return memo_v[i];
    const int v = reach_read(f);
    if (memo_n < 10) { memo_h[memo_n] = h; memo_v[memo_n] = v; ++memo_n; }
    return v;
}

'''+b)
open(p,'w',newline='').write(s)
