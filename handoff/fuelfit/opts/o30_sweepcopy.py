# fuelfit o30 (pelea, pre-sweep; after o29): spell_sweep's foe list, like o17's: reserved, Foe built in place
# (a bc::champion copy is heavy: vtable, ability and consumable views). Same reads in the same order: exact.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
a="""    std::vector<Foe> foes;
    for (auto& c : vis_champions(*s.en))
        attempt([&] {
            if (!c.is_alive()) return false;
            const vec2 fp = c.position();
            const int fd = dist(fp, pos);
            if (fd > SPELL_RANGE || s.en_spawn.is_set(fp)) return false;  // fuelfit o29: before the other reads
            Foe f{c, fp, c.health(), 0, 0, false};
            f.d = fd;
            attempt([&] {
                f.gems = static_cast<int>(c.gem_count());
                f.channeling = c.is_submitting_gems() || c.is_recalling();
                return true;
            });
            foes.push_back(f);
            return true;
        });"""
assert s.count(a)==1
s=s.replace(a,"""    std::vector<Foe> foes;
    foes.reserve(vis_champions(*s.en).size());  // fuelfit o30
    for (auto& c : vis_champions(*s.en))
        attempt([&] {
            if (!c.is_alive()) return false;
            const vec2 fp = c.position();
            const int fd = dist(fp, pos);
            if (fd > SPELL_RANGE || s.en_spawn.is_set(fp)) return false;  // fuelfit o29: before the other reads
            const float fhp = c.health();
            foes.emplace_back(c, fp, fhp, 0, 0, false);  // fuelfit o30: in place
            Foe& f = foes.back();
            f.d = fd;
            attempt([&] {
                f.gems = static_cast<int>(c.gem_count());
                f.channeling = c.is_submitting_gems() || c.is_recalling();
                return true;
            });
            return true;
        });""")
open(p,'w',newline='').write(s)
