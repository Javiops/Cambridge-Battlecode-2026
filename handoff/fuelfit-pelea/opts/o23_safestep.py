# fuelfit o23 (pelea): fight::safe_step scores up to 25 dash tiles and 8 step tiles as threats*1000 + ally*10 + home
# distance and keeps a tile only if it beats the best by 500 (dash) or at all (step). All three terms are >= 0, so a
# tile is dropped as soon as the terms summed so far reach the bar: threats first (no engine call), then the blocked
# test (an engine call, ~50), then home distance, and the ally loop last. The map bounds test uses the map size read
# once (bc::map::is_in_bounds reads the layout on every call). Same tiles kept, same order, same scores. Exact.
import sys
d=sys.argv[1]; p=d+'/fight.h'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,a; s=s.replace(a,b)
rep("""    auto score = [&](vec2 t) {
        int ally = 30;
        for (auto a : allies) ally = std::min(ally, dist(t, a));
        return threats_at(t, foes, reaches) * 1000 + ally * 10 + dist(t, s.spawn_center);
    };""","""    auto score = [&](vec2 t) {
        int ally = 30;
        for (auto a : allies) ally = std::min(ally, dist(t, a));
        return threats_at(t, foes, reaches) * 1000 + ally * 10 + dist(t, s.spawn_center);
    };
    // fuelfit o23: the score of t if it is below lim, else lim (t cannot be kept); the terms are all >= 0
    static const int map_w = bc::map::width(), map_h = bc::map::height();
    auto score_below = [&](vec2 t, int lim) {
        if (X(t) < 0 || Y(t) < 0 || X(t) >= map_w || Y(t) >= map_h) return lim;
        int sc = threats_at(t, foes, reaches) * 1000;
        if (sc >= lim || s.blocked.is_set(t)) return lim;
        sc += dist(t, s.spawn_center);
        if (sc >= lim) return lim;
        int ally = 30;
        for (auto a : allies) ally = std::min(ally, dist(t, a));
        return sc + ally * 10;
    };""")
rep("""                    vec2 t = pos + vec2(dx, dy);
                    if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t)) continue;
                    int sc = score(t);
                    if (sc < bests - 500) { bests = sc; best = t; }""","""                    vec2 t = pos + vec2(dx, dy);
                    int sc = score_below(t, bests - 500);
                    if (sc < bests - 500) { bests = sc; best = t; }""")
rep("""                vec2 t = pos + vec2(dx, dy);
                if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t)) continue;
                int sc = score(t);
                if (sc < bests) { bests = sc; best = t; }
            }
        if (best && attempt([&] { return me.move_absolute(*best); })) moved = true;
    }
    return moved;""","""                vec2 t = pos + vec2(dx, dy);
                int sc = score_below(t, bests);
                if (sc < bests) { bests = sc; best = t; }
            }
        if (best && attempt([&] { return me.move_absolute(*best); })) moved = true;
    }
    return moved;""")
open(p,'w',newline='').write(s)
