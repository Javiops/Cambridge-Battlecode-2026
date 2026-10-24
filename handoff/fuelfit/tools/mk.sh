#!/bin/bash
# mk.sh NAME [ROUNDS] -> manifest for NAME vs 6 rivals on non-far maps both sides
N=$1; R=${2:-400}; FAR="islands rows lanes great_wall expanse split shortcut ambush pilgrimage big_world fracture concentrated_wealth starvation road_of_riches"
for r in rTop1 rD rF rHunt mV19 mV10d; do mkdir -p res/$N/$r; for m in maps/*.map26a; do n=$(basename $m .map26a); b=${n:2}
 [[ " $FAR " == *" $b "* ]] && continue
 [ -e res/$N/$r/A_$n.json ] || echo "bots/$N bots/$r $m res/$N/$r/A_$n.repl26a --statistics res/$N/$r/A_$n.json --json"
 [ -e res/$N/$r/B_$n.json ] || echo "bots/$r bots/$N $m res/$N/$r/B_$n.repl26a --statistics res/$N/$r/B_$n.json --json"
done; done
