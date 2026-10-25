#!/bin/bash
# far.sh NAME [FUEL] : 14 far maps x rTop1,rD x 2 sides = 56 games; results res/far_NAME (or res/far_NAME_qFUEL)
cd $(dirname $0); N=$1; Q=$2; OUT=far_$N; [ -n "$Q" ] && OUT=far_${N}_q$Q
FAR="islands rows lanes great_wall expanse split shortcut ambush pilgrimage big_world fracture concentrated_wealth starvation road_of_riches"
rm -rf res/$OUT; > m_$OUT.txt
for r in rTop1 rD; do mkdir -p res/$OUT/$r; for m in maps/*.map26a; do n=$(basename $m .map26a); b=${n:2}
 [[ " $FAR " == *" $b "* ]] || continue
 echo "bots/$N bots/$r $m res/$OUT/$r/A_$n.repl26a --statistics res/$OUT/$r/A_$n.json --json" >> m_$OUT.txt
 echo "bots/$r bots/$N $m res/$OUT/$r/B_$n.repl26a --statistics res/$OUT/$r/B_$n.json --json" >> m_$OUT.txt
done; done
EXTRA=""; [ -n "$Q" ] && EXTRA="--fuel-quantum $Q"
../cv/bin/cambc run-batch m_$OUT.txt --jobs 4 --release --json $EXTRA > log_$OUT.txt 2>&1; tail -1 log_$OUT.txt
