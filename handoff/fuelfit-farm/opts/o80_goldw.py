# o80_goldw.py SRCDIR [PCT=50] (farm thread; NOT EXACT: a decision change, judge by strength; over b35, independent of
# o70/o79). choose_target values a group at gems + gold_w x gold with gold_w = P_GOLD_W_EARLY / 100 = 1.0 before r600 (0.24
# after): 40 gold is worth 40 gems. Every candidate and pick of b35 + o70 printed on the near 80 panel (unlimited fuel,
# 7604 decisions r20-300): gold-only clusters are 30% of all picks (2317; ~2 per game per 100 rounds, flat over r0-300);
# when a single-elk group (>= 15 gems) is within 25 tiles we pick it 49% of the time, and in 448 decisions a gold-only
# cluster beats it on raw value / rounds: 40 gold in 21 rounds (7 tiles away) = 1.86 a round against 29 gems + 90 gold in
# 79 rounds = 0.81. Clean capture counts: top 10 2.0 gold-only cluster captures per game per 150-round window, we
# 4.1-4.6; single-elk groups top 10 1.4-1.9, we 0.5-0.8. o80 sets the early gold weight to PCT% (default 50: 40 gold = 20
# gems). Expected: fewer gold clusters, more elk and wolf+gem captures, less gold by r150-300 (watch shards bought,
# deaths, fights).
import sys
d=sys.argv[1]; pct=sys.argv[2] if len(sys.argv)>2 else '50'
p=d+'/params.h'; s=open(p,newline='').read()
a="#define P_GOLD_W_EARLY 100"; assert s.count(a)==1
s=s.replace(a,"#define P_GOLD_W_EARLY %s  // o80: was 100 (40 gold = 40 gems before r600); top 10 take half our gold-only clusters and 3x our single elks" % pct)
open(p,'w',newline='').write(s)
