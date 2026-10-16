#!/usr/bin/env python3
"""Insert the P_HUNT hooks (tools/panel/hunt.h) into an online-bot src folder. Idempotent; P_HUNT 0 = unchanged bot."""
import os, shutil, sys
src = sys.argv[1]
p = os.path.join(src, 'main.cpp'); s = open(p).read()
if '#include "hunt.h"' in s:
    sys.exit(0)
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hunt.h'), os.path.join(src, 'hunt.h'))
FIGHT = '''#if P_HUNT
    // P_HUNT (sparring-only): hunters take any fight that is not hopeless; prey = the foe carrying most gems
    // (Univardisty 84%), ties to the nearest (Mite 85%). Never on their spawn.
    if (hunt::is_hunter(s, round) && !foes.empty() && !on_spawn) {
        Foe* prey = nullptr;
        for (auto& f : foes) {
            if (f.d > P_HUNT_SEE || s.en_spawn.is_set(f.p)) continue;
            if (!prey || f.gems > prey->gems || (f.gems == prey->gems && f.d < prey->d)) prey = &f;
        }
        if (prey) {
            int nb = 1, eb = 0;
            for (auto& a : bc::vision::champions(*s.my))
                attempt([&] {
                    if (!(a == me) && a.is_alive() && dist(a.position(), pos) <= 6) ++nb;
                    return true;
                });
            for (auto& f : foes) if (dist(f.p, prey->p) <= 4) ++eb;
            if (eb <= nb + P_HUNT_ODDS) {
                g_mode = "hunt-fight";
                if (engage(s, me, prey->c, prey->p, true, true)) return;
            }
        }
    }
#endif
'''
MOVE = '''#if P_HUNT
    if (hunt::is_hunter(s, round) && hunt::walk(s, me, round, foes)) {
        g_mode = "hunt";
        if (tgt && me.can_attack()) basic_attack(s, me, tgt->c, tgt->p);
        return;
    }
#endif
'''
A = '    // 3. Enemy champions: back away from a stronger group, fight an even or weaker one.\n'
B = '    // 6. Farm camps.\n'
C = 'void play_turn(State& s) {'
for k in (A, B, C):
    assert s.count(k) == 1, k
s = s.replace(A, FIGHT + A).replace(B, MOVE + B).replace(C, '#include "hunt.h"\n' + C)
open(p, 'w').write(s)
pp = os.path.join(src, 'params.h')
open(pp, 'a').write('\n#ifndef P_HUNT\n#define P_HUNT 0\n#endif\n')
