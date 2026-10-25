# o81_stack.py SRCDIR [SHAREEXP=75] (farm thread; NOT EXACT: a decision change, judge by strength; over b35).
# Time budget of every champion in r1-300 (gem/contact.py on the replays + statistics JSON; top 10 = 40 online near games,
# us = near 80 panel): the top 10 spend 35% of their alive rounds within 4 tiles of an awake monster (16% at distance 3-4),
# we 26% (9%); they walk 42% of the time, we 51%; idle equal (17%); damage per round near a monster differs only 9%
# (63.8 vs 58.6). Monster damage by r300: 26726 vs 19198 (+39%) = +28% rounds near monsters x +9% per round. Trios (3+
# allies within 3, buddy thread's form.py g3): top 10 40 / 30 / 26% of rounds in r30-90 / 90-150 / 150-300, b35 30 / 19 /
# 15%. choose_target divides a group's value by team^e with e = 1.0 (full split) for groups under P_STACK_HP 3000 hp and
# P_SHAREEXP 0.75 above: a third champion sees a third of a 2640-hp single-elk group.
# v1 (P_STACK_HP 0: the exponent for EVERY group, clusters included): 0.75 near 61/80 vs 62, far 49/56 vs 48 (neutral);
# 0.50 near 53, far 41 (champions stacked on 120-hp clusters too). v2 (this file): the stacking exponent for MONSTER groups
# only (g.str > 0), clusters keep the even split. Expected: more champions per monster capture, more rounds near monsters
# and trios up, walking down; watch deaths and far maps.
import sys
d=sys.argv[1]; e=sys.argv[2] if len(sys.argv)>2 else None
p=d+'/main.cpp'; s=open(p,newline='').read()
a="share_pow(team, (g.monolith || g.hp < P_STACK_HP || false) ? 100 : P_SHAREEXP)"
assert s.count(a)==1
s=s.replace(a,"share_pow(team, (g.monolith || (g.str <= 0 && g.hp < P_STACK_HP) || false) ? 100 : P_SHAREEXP)")
b="// big camps (P_STACK_HP+): a joiner keeps more of the value, so champions stack there"; assert s.count(b)==1
s=s.replace(b,"// o81: every monster group stacks (top 10 arrive 3-4 to a single elk); clusters keep the even split")
open(p,'w',newline='').write(s)
if e:
    import re
    p=d+'/params.h'; s=open(p,newline='').read()
    m=re.search(r'#define P_SHAREEXP (\d+)', s); assert m
    s=s.replace(m.group(0), '#define P_SHAREEXP %s  // o81: was %s' % (e, m.group(1))); open(p,'w',newline='').write(s)
