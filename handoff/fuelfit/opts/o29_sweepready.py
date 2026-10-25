# fuelfit o29 (pelea, pre-sweep): spell_sweep built its foe list (vision rebuild + 6 reads per foe) before knowing whether
# anything can be cast. Every cast in it (try_use, the 2+ foe area spell, cm_edge_aoe) needs a Targeted or Ground slot
# whose ability is ready: with none, it now returns before the list. The list also checks distance and enemy spawn
# before reading health / gems / channeling, so far foes cost one read. Engine reads have no side effects: exact.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,a; s=s.replace(a,b)
rep("""    if (!fuel_ok(6000)) return;
    vec2 pos = me.position();
    std::vector<Foe> foes;
    for (auto& c : vis_champions(*s.en))
        attempt([&] {
            if (!c.is_alive()) return false;
            Foe f{c, c.position(), c.health(), 0, 0, false};
            f.d = dist(f.p, pos);
            if (f.d > SPELL_RANGE || s.en_spawn.is_set(f.p)) return false;
""","""    if (!fuel_ok(6000)) return;
    {  // fuelfit o29: no ready Targeted / Ground ability, no cast below
        auto abs0 = me.abilities();
        bool any = false;
        for (int k = 0; k < 2 && !any; ++k)
            if ((s.slots[k] == Slot::Targeted || s.slots[k] == Slot::Ground) && abs0[k].is_ready()) any = true;
        if (!any) return;
    }
    vec2 pos = me.position();
    std::vector<Foe> foes;
    for (auto& c : vis_champions(*s.en))
        attempt([&] {
            if (!c.is_alive()) return false;
            const vec2 fp = c.position();
            const int fd = dist(fp, pos);
            if (fd > SPELL_RANGE || s.en_spawn.is_set(fp)) return false;  // fuelfit o29: before the other reads
            Foe f{c, fp, c.health(), 0, 0, false};
            f.d = fd;
""")
open(p,'w',newline='').write(s)
