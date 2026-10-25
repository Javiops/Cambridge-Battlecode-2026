# fuelfit port of hitpass-v2 (copy-decisions thread, online +7 on c16 as hpb): a turn that ends with the attack unused
# v6: g_draft_sp does not survive the draft (globals reset for the game: v5 had hitpass off everywhere); g_tpc_path is the
# same walk sent through draft memory byte 29 and read in init_map (idlefix-v4).
# v5: reads g_draft_sp (farswap's draft BFS) instead of running pf_spawn_path in init: on big maps the start-up is already
# over budget and any extra init work shifts when play starts (v4: 12/56 far games changed vs b15).
# v4: the far gate is decided in the start-up turn (a pf_spawn_path() BFS at r2 shifted the fuel of big maps: 14/56 far games changed vs b15, probe 2/56).
# v3: off on far maps (spawn-to-spawn walk >= 60, the far definition of mapfeat40/farswap): PC b21hp vs b15 far -20, mid +4, near -2.
# v2: reuses the camps list play_turn built this round (near_camps is 5-97k) instead of a second near_camps call.
# takes a finishing blow (<= 2 of our hits) on an awake camp in reach, or a guardless cluster at <= 1 hit. Port rules:
# no fuel reads (the original gated on fuel_ok(9000)); the [hl] log is dropped. Cost: near_camps() only when the attack
# is still available after play_turn (most turns it is not).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
a="            play_turn(s);\n"
assert s.count(a)==1
s=s.replace(a,a+'''            if (P_HITLAST && !s.hp_far)  // hitpass-v2 port (fuelfit o70); v3: not on far maps
                attempt([&] {
                    bc::champion& me = bc::self();
                    if (!me.is_alive() || !me.can_attack()) return true;
                    const vec2 pos = me.position();
                    const std::vector<bc::camp>& hc = s.hp_camps_r == static_cast<int>(bc::round_number()) ? s.hp_camps : (s.hp_camps = near_camps(s, pos));
                    for (auto& c : hc) {
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
a="    std::vector<bc::camp> camps = near_camps(s, pos);\n"
assert s.count(a)==1
s=s.replace(a,"    s.hp_camps = near_camps(s, pos); s.hp_camps_r = round;  // fuelfit o70 v2: kept for the end-of-turn hit\n    std::vector<bc::camp>& camps = s.hp_camps;\n")
a="    bool ready = false;\n"
assert s.count(a)==1
s=s.replace(a,a+"    std::vector<bc::camp> hp_camps; int hp_camps_r = -1;  // fuelfit o70 v2\n    bool hp_far = true;  // fuelfit o70 v4: hitpass off on far maps, decided in the start-up turn\n")
a="        farm_warmup(s, 1000000);  // fuelfit o47/o48"
assert s.count(a)==1
s=s.replace(a,"        s.hp_far = P_HITLAST_FAR > 0 && !(g_tpc_path >= 0 && g_tpc_path < P_HITLAST_FAR);  // fuelfit o70 v6: the spawn walk the draft sent in draft-memory byte 29 (g_tpc_path, read in init_map); no BFS in the start-up turn\n"+a)
a="bool init(State& s, bc::champion& me) {\n"
assert s.count(a)==1
pass
open(p,'w',newline='').write(s)
p=d+'/params.h'; s=open(p,newline='').read()
assert 'P_HITLAST' not in s
s+="#ifndef P_HITLAST\n#define P_HITLAST 1      // hitpass-v2: an unused attack at the end of the turn takes a finishing blow on a camp in reach\n#endif\n#ifndef P_HITLAST_FAR\n#define P_HITLAST_FAR 60  // o70 v3: hitpass off when the spawn-to-spawn walk (pf_spawn_path, cached) is 60+ (far maps: PC 800 g lejanos -20, medios +4, cercanos -2)\n#endif\n"
open(p,'w',newline='').write(s)
