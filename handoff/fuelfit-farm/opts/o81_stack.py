# o81_stack.py SRCDIR [STACK_HP=0] [SHAREEXP=75] (farm thread; NOT EXACT: a decision change, judge by strength; over b35).
# Time budget of every champion in r1-300 (gem/contact.py on the replays + statistics JSON; top 10 = 40 online near games,
# us = near 80 panel): the top 10 spend 35% of their alive rounds within 4 tiles of an awake monster (16% at distance 3-4),
# we 26% (9%); they walk 42% of the time, we 51%; idle equal (17%); damage per round near a monster differs only 9%
# (63.8 vs 58.6). Monster damage by r300: 26726 vs 19198 (+39%) = +28% rounds near monsters x +9% per round. So the farm
# gap is champions STANDING AT THE SAME GROUP: the top 10 arrive 3-4 to a single-elk group (present at capture median 3,
# ours 2) and clear it fast; ours split up (one or two per group, the rest walking to a cluster). choose_target divides
# a group's value by team^e with e = 1.0 (full split) for groups under P_STACK_HP 3000 hp and P_SHAREEXP 0.75 above: a
# third champion sees a third of a 2640-hp elk group. o81 applies the stacking exponent to every monster group
# (P_STACK_HP -> STACK_HP, default 0) and optionally lowers it (SHAREEXP). Expected: champions per capture up, rounds near
# monsters up, walking down, gold-cluster trips down; watch deaths and far maps (e70s = exponent 0.40 on big groups only
# lost far 46 vs 48).
import sys
d=sys.argv[1]; hp=sys.argv[2] if len(sys.argv)>2 else '0'; e=sys.argv[3] if len(sys.argv)>3 else None
p=d+'/params.h'; s=open(p,newline='').read()
import re
m=re.search(r'#define P_STACK_HP (\d+)', s); assert m, 'P_STACK_HP'
s=s.replace(m.group(0), '#define P_STACK_HP %s  // o81: was %s; the stacking exponent applies to every monster group (top 10 arrive 3-4 to a single elk)' % (hp, m.group(1)))
if e:
    m=re.search(r'#define P_SHAREEXP (\d+)', s); assert m, 'P_SHAREEXP'
    s=s.replace(m.group(0), '#define P_SHAREEXP %s  // o81: was %s' % (e, m.group(1)))
open(p,'w',newline='').write(s)
