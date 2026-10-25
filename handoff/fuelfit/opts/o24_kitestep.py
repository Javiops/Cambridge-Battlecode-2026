# fuelfit o24 (pelea): fight::kite's step scores 8 tiles as -1000*threats + 300 + 100 (spell / attack range) minus
# chase and team terms (all >= 0), keeping a tile only above best + 0.5. A tile whose -1000*threats + 400 is not
# above that can never be kept, so its other terms are skipped; the threat count is computed once per tile. Exact.
import sys
d=sys.argv[1]; p=d+'/fight.h'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,a; s=s.replace(a,b)
rep("""        auto score = [&](vec2 t) {
            int thr = 0;
            for (std::size_t i = 0; i < near.size(); ++i)
                if (dist(t, near[i]->p) <= reaches[i]) ++thr;
            int df = dist(t, focus->p);""","""        auto thr_at = [&](vec2 t) {
            int thr = 0;
            for (std::size_t i = 0; i < near.size(); ++i)
                if (dist(t, near[i]->p) <= reaches[i]) ++thr;
            return thr;
        };
        auto score = [&](vec2 t, int thr) {
            int df = dist(t, focus->p);""")
rep("""        double bs = score(pos);
        std::optional<vec2> bt;
        for (int dx = -1; dx <= 1; ++dx)
            for (int dy = -1; dy <= 1; ++dy) {
                if (!dx && !dy) continue;
                vec2 t = pos + vec2(dx, dy);
                if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t)) continue;
                double sc = score(t);""","""        double bs = score(pos, thr_at(pos));
        std::optional<vec2> bt;
        for (int dx = -1; dx <= 1; ++dx)
            for (int dy = -1; dy <= 1; ++dy) {
                if (!dx && !dy) continue;
                vec2 t = pos + vec2(dx, dy);
                if (!bc::map::is_in_bounds(t)) continue;
                const int th = thr_at(t);
                if (-1000.0 * th + 400.0 <= bs + 0.5) continue;  // fuelfit o24: cannot win
                if (s.blocked.is_set(t)) continue;
                double sc = score(t, th);""")
open(p,'w',newline='').write(s)
