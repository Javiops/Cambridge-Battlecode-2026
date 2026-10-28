#!/bin/bash
# mkm.sh BOT OUT [EVERY] : manifest BOT vs 6 panel17 rivals on 26 non-far maps, both sides (every EVERY-th line; 6 -> 52 games)
S=/tmp/claude-0/-home-user-cambridge-battlecode-2026/76ec8910-3410-5095-ba5f-885fa2d39df3/scratchpad
cd $S/ws; N=$1; O=$2; E=${3:-1}
FAR="islands rows lanes great_wall expanse split shortcut ambush pilgrimage big_world fracture concentrated_wealth starvation road_of_riches"
for r in rTop1 rD rF rHunt mV19 mV10d; do mkdir -p res/$O/$r; for m in maps/*.map26a; do b=$(basename $m .map26a)
 [[ " $FAR " == *" $b "* ]] && continue
 echo "bots/$N bots/p17_$r $m res/$O/$r/A_$b.repl26a --statistics res/$O/$r/A_$b.json --json"
 echo "bots/p17_$r bots/$N $m res/$O/$r/B_$b.repl26a --statistics res/$O/$r/B_$b.json --json"
done; done | awk -v e=$E 'NR%e==1 || e==1'
