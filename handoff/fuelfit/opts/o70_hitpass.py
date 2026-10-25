# fuelfit port of hitpass-v2 (copy-decisions thread, online +7 on c16 as hpb): a turn that ends with the attack unused
# takes a finishing blow (<= 2 of our hits) on an awake camp in reach, or a guardless cluster at <= 1 hit. Port rules:
# no fuel reads (the original gated on fuel_ok(9000)); the [hl] log is dropped. Cost: near_camps() only when the attack
# is still available after play_turn (most turns it is not).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
a="            play_turn(s);\n"
assert s.count(a)==1
s=s.replace(a,a+'''            if (P_HITLAST)  // hitpass-v2 port (fuelfit o70)
                attempt([&] {
                    bc::champion& me = bc::self();
                    if (!me.is_alive() || !me.can_attack()) return true;
                    const vec2 pos = me.position();
                    for (auto& c : near_camps(s, pos)) {
                        if (c.is_monolith() || c.is_golem() || c.health() <= 0) continue;
                        const vec2 cp = c.position();
                        if (dist(pos, cp) > me.attack_range()) continue;
                        const double hit = std::max(1.0, static_cast<double>(me.strength()));
                        bool ok = c.is_awake() && c.health() <= 2.0 * hit;
                        if (!ok && (c.is_gem_cluster() || c.is_gold_cluster()) && c.health() <= hit)
                            for (auto& g : s.groups)
                                if (g.mask.is_set(c.spawn_position())) { ok = g.str == 0 && !g.monolith; break; }
                        if (!ok) continue;
                        if (basic_attack(s, me, c, cp)) break;
                    }
                    return true;
                });
''')
open(p,'w',newline='').write(s)
p=d+'/params.h'; s=open(p,newline='').read()
assert 'P_HITLAST' not in s
s+="#ifndef P_HITLAST\n#define P_HITLAST 1      // hitpass-v2: an unused attack at the end of the turn takes a finishing blow on a camp in reach\n#endif\n"
open(p,'w',newline='').write(s)
