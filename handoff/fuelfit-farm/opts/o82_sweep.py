# o82_sweep.py SRCDIR [MAXSTR=60] (farm thread; NOT EXACT: a decision change, judge by strength; over b35).
# Who stands at the same monster group (gem/contact.py, group-rounds per game with 1/2/3/4+ own champions within 4 of an
# awake monster of the group, r1-300): top 10 116/63/32/22, b35 98/65/29/12. The 4+ engagements of the top 10 are on WEAK
# groups (total strength <= 60: a single elk or wolf): 8.0 / 4.8 / 6.4 group-rounds per game in r0-50 / 50-150 / 150-300
# against our 5.2 / 2.0 / 2.1; on 61-120 and 121+ groups both sides are below 1.5. The top 10 sweep weak groups with the
# whole team all game (a 4-5 champion kill of a 2640-hp elk group takes 8-10 rounds); we do it only in the opening, because
# choose_target splits the value of a group under P_STACK_HP evenly among the champions heading there (a fourth champion
# sees a quarter). o81 (team^0.75 / team^0.5 for every monster group) formed top-10-like trios but also on 2-3 elk groups and
# the far maps collapsed (40/56). o82: a weak monster group (0 < str <= MAXSTR, hp < P_STACK_HP) is not split at all from
# round P_SWEEP_R on (the team sweeps it together); other groups keep the base rule. Expected: 4+ engagements on weak groups
# up, group gems r0-300 up, deaths down; watch far maps and gold clusters.
import sys
d=sys.argv[1]; ms=sys.argv[2] if len(sys.argv)>2 else '60'
p=d+'/main.cpp'; s=open(p,newline='').read()
a="share_pow(team, (g.monolith || g.hp < P_STACK_HP || false) ? 100 : P_SHAREEXP)"
assert s.count(a)==1
s=s.replace(a,"((round >= P_SWEEP_R && g.str > 0 && g.str <= P_SWEEP_STR && g.hp < P_STACK_HP) ? 1.0 : share_pow(team, (g.monolith || g.hp < P_STACK_HP || false) ? 100 : P_SHAREEXP))")
b="// big camps (P_STACK_HP+): a joiner keeps more of the value, so champions stack there"; assert s.count(b)==1
s=s.replace(b,"// o82: weak monster groups are swept by the whole team (no value split); big camps (P_STACK_HP+): a joiner keeps more of the value")
open(p,'w',newline='').write(s)
p=d+'/params.h'; s=open(p,newline='').read()
a="#ifndef P_HOLEFIX"; assert s.count(a)==1
s=s.replace(a,"""#ifndef P_SWEEP_STR
#define P_SWEEP_STR %s  // o82: monster groups up to this total strength are not value-split among joiners (top 10 sweep single elks/wolves with 4+)
#endif
#ifndef P_SWEEP_R
#define P_SWEEP_R 50  // o82: from this round (the opening has its own rules)
#endif
#ifndef P_HOLEFIX""" % ms)
open(p,'w',newline='').write(s)
