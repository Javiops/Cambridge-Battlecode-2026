# fuelfit o17 (pelea, foes): a bc::champion is a heavy object (vtable, two ability views, one view per consumable), and
# the foes section copied each one several times a turn: Foe f{...} then push_back(f) plus vector growth, the same for
# the Seen list, and threat_of took the champion by value. The vectors are now reserved, Foe / Seen are built in place
# and threat_of takes a const reference. Same reads in the same order, same contents: exact.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,a; s=s.replace(a,b)
rep("inline Threat threat_of(bc::champion c, vec2 p, int atk_reach) {","inline Threat threat_of(const bc::champion& c, vec2 p, int atk_reach) {  // fuelfit o17: no copy")
rep("""    std::vector<Foe> foes;
    for (auto& c : vis_champions(*s.en)) {
        attempt([&] {
            if (!c.is_alive()) return false;
            Foe f{c, c.position(), c.health(), 0, 0, false};
            f.d = dist(f.p, pos);
            attempt([&] {
                f.gems = static_cast<int>(c.gem_count());
                return true;
            });
            attempt([&] {
                f.channeling = c.is_submitting_gems() || c.is_recalling();
                return true;
            });
            foes.push_back(f);
            return true;
        });
    }""","""    std::vector<Foe> foes;
    foes.reserve(vis_champions(*s.en).size());  // fuelfit o17: built in place, no champion copies
    for (auto& c : vis_champions(*s.en)) {
        attempt([&] {
            if (!c.is_alive()) return false;
            const vec2 fp = c.position();
            const float fhp = c.health();
            foes.emplace_back(c, fp, fhp, 0, 0, false);
            Foe& f = foes.back();
            f.d = dist(f.p, pos);
            attempt([&] {
                f.gems = static_cast<int>(c.gem_count());
                return true;
            });
            attempt([&] {
                f.channeling = c.is_submitting_gems() || c.is_recalling();
                return true;
            });
            return true;
        });
    }""")
rep("""        std::vector<Seen> now;
        for (auto& f : foes) {""","""        std::vector<Seen> now;
        now.reserve(foes.size());  // fuelfit o17
        for (auto& f : foes) {""")
rep("            now.push_back({f.c, f.p, until});","            now.emplace_back(f.c, f.p, until);")
open(p,'w',newline='').write(s)
