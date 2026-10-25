# fuelfit o21 (recall/altares/campamentos): near_camps reads each group's camp list once (the seen test and the
# push used two camps() calls; same turn, same handles) and reserves the output; the awake-camp test stops at the
# first awake camp in reach (the flag only goes true; health() has no side effect); the bank chain loop computes
# my_dps once (engine reads of our own champion, unchanged inside the loop). Exact: same decisions, same order.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""    std::vector<bc::camp> out;
    bc::bitboard tv;  // the engine's own "effective vision", the one state() checks""","""    std::vector<bc::camp> out;
    out.reserve(24);  // fuelfit o21
    bc::bitboard tv;  // the engine's own "effective vision", the one state() checks""")
rep("""        bool seen = false;  // the engine refuses group queries when no camp spawn tile is in vision
        for (auto& c : g.obj->camps())
            if (tv.is_set(c.spawn_position())) { seen = true; break; }""","""        bool seen = false;  // the engine refuses group queries when no camp spawn tile is in vision
        auto gcs = g.obj->camps();  // fuelfit o21: one list per group, reused for the push below
        for (auto& c : gcs)
            if (tv.is_set(c.spawn_position())) { seen = true; break; }""")
rep("""        attempt([&] {
            for (auto& c : g.obj->camps())
                if (c.is_visible()) out.push_back(c);
            return true;
        });
    }
    return out;""","""        attempt([&] {
            for (auto& c : gcs)
                if (c.is_visible()) out.push_back(c);
            return true;
        });
    }
    return out;""")
rep("""    bool awake_camp_near = false;
    for (auto& c : camps)
        attempt([&] {""","""    bool awake_camp_near = false;
    for (auto& c : camps) {
        if (awake_camp_near) break;  // fuelfit o21: the flag only goes true
        attempt([&] {""")
rep("""            if (dist(c.position(), pos) <= CAMP_RANGE + 1 && c.health() < c.max_health()) awake_camp_near = true;
#endif
            return true;
        });""","""            if (dist(c.position(), pos) <= CAMP_RANGE + 1 && c.health() < c.max_health()) awake_camp_near = true;
#endif
            return true;
        });
    }""")
rep("""            auto sm = read_sm();
            int gi = -1, gd = 99;""","""            auto sm = read_sm();
            int gi = -1, gd = 99;
            double md = -1;  // fuelfit o21: my_dps once""")
rep("""                if (squad_needed(g.hp, g.str, my_dps(s, me), std::max(1.0f, hp - mhp * 0.3f)) > 1) continue;""","""                if (md < 0) md = my_dps(s, me);
                if (squad_needed(g.hp, g.str, md, std::max(1.0f, hp - mhp * 0.3f)) > 1) continue;""")
open(p,'w',newline='').write(s)
