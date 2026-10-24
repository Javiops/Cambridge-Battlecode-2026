#!/bin/bash
# HARD PANEL (judge since 10-23 20:00 for candidates on V20): rivals V19 wins <70% of (rTop1 rD rF rHunt) + two strong mirrors
# mV19 (pack-v1w) and mV10d (v10d); 80 games each (40 site maps x 2 sides) = 480 paired games vs $BASE (default v6d = V20).
# Validated on the chain-2 ladder (ladder_vs_panel_1023.md): matches online size, orders v9d > v10d like online; panel17 = side-effect veto.
# usage: runhard.sh WORKDIR CAND_ZIP NAME [JOBS]   -> net, bar 2*sqrt(changed), far/mid/near, kills/deaths/Vesper
S=/mnt/project-files/analysis/local-filter-1021/scripts; L=/mnt/project-files/analysis/local-filter-1021
W=$1; CAND=$2; NAME=$3; J=${4:-4}; BASE=${BASE:-v6d}; RIVS="${RIVS:-rTop1 rD rF rHunt mV19 mV10d}"
cd $W/ws || exit 1
for p in $RIVS; do [ -d bots/$p ] || { mkdir -p bots/$p && cp -r $L/panel17/$p/src bots/$p/; }; done
for p in $RIVS; do d=res/cal_${BASE}_$p; [ -f $d/A_ambush.json ] || { [ -d $L/base-results-hard/cal_${BASE}_$p ] && mkdir -p $d && cp $L/base-results-hard/cal_${BASE}_$p/* $d/; }; done
rm -rf bots/$NAME; mkdir -p bots/$NAME
if [ -f "$CAND" ]; then (cd bots/$NAME && unzip -oq "$CAND"); else cp -r "$CAND"/src bots/$NAME/; fi
M=man_hard_$NAME.txt; : > $M
for r in $RIVS; do mkdir -p res/cal_${NAME}_$r; for m in maps/*.map26a; do n=$(basename $m .map26a)
  [ -e res/cal_${NAME}_$r/A_$n.json ] || echo "bots/$NAME bots/$r $m res/cal_${NAME}_$r/A_$n.repl26a --statistics res/cal_${NAME}_$r/A_$n.json --json" >> $M
  [ -e res/cal_${NAME}_$r/B_$n.json ] || echo "bots/$r bots/$NAME $m res/cal_${NAME}_$r/B_$n.repl26a --statistics res/cal_${NAME}_$r/B_$n.json --json" >> $M
done; done
[ -s $M ] && { ../cv/bin/cambc run-batch $M --jobs $J --release --json > log_hard_$NAME.txt 2>&1 || true; tail -1 log_hard_$NAME.txt; }
(cd res && python3 $S/compact.py $(for r in $RIVS; do echo cal_${NAME}_$r; done)); find res -path "res/cal_${NAME}_*" -name '*.repl26a' -delete
PAN=${RIVS// /,} python3 $S/panelcls.py $BASE $NAME
PAN=${RIVS// /,} python3 $S/kd.py $BASE $NAME
