# pkc: pkb + the follower walks back to its pack leader (in vision, off spawn, no foe within 6, not capturing)
import sys, subprocess
d = sys.argv[1]
subprocess.check_call(['python3', '/tmp/claude-0/w/opts/pkb.py', d])
p = d + '/main.cpp'
s = open(p).read()
a = """    // P_GROUP_R: keep the ball together. The leader is the first ally in draft order that is alive and not
    // channelling; followers come back to it, the leader waits for a straggler (ignoring anyone 15+ away).
    if (false) {"""
assert s.count(a) == 1
s = s.replace(a, """#ifndef P_PK_WALK
#define P_PK_WALK 5   // pkc: a follower farther than this from its pack leader walks back to within 2 of it
#endif
    if (P_PK_WALK && grouped(s, round) && !on_spawn && nearest_foe > 6 && !awake_camp_near && s.cap_start < 0 &&
        !(s.target >= 0 && s.target < static_cast<int>(s.groups.size()) && s.groups[s.target].reward_seen == round)) {
        const int li = pk_lead(s);
        vec2 lp{0, 0};
        bool ok = false;
        attempt([&] {
            auto& allies = my_roster(s);
            if (li < 0 || li >= static_cast<int>(allies.size())) return false;
            auto& a = allies[li];
            if (!a.is_alive() || a.is_recalling() || a.is_teleporting()) return false;
            lp = a.position();
            ok = !s.my_spawn.is_set(lp);
            return true;
        });
        if (ok && dist(pos, lp) > P_PK_WALK) {
            g_mode = "pack";
            bc::bitboard ring;
            ring.draw_chebyshev(lp, 2.0f);
            if (step_towards(s, me, ring & ~s.blocked, false)) return;
        }
    }
    // P_GROUP_R: keep the ball together. The leader is the first ally in draft order that is alive and not
    // channelling; followers come back to it, the leader waits for a straggler (ignoring anyone 15+ away).
    if (false) {""")
open(p, 'w').write(s)
print('ok pkc')
