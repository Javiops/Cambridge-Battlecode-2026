#!/bin/bash
# Mechanism test of process-audit-1023 §3.5 (mandatory before panel17 / online): CAND vs pHuntF and rRushHunt (RIVS env), 40 site maps x 2 sides = 80 games each,
# judged vs $BASE (default nightpack-v2 = V18 since 10-23 10:56; t10shop-v2 = V17 and nightpack-v1 also have base results) on the result net + 6 side-effect gauges
# (gold@400, deaths, Vesper deaths, fuel cuts, first 20+ capture, clears@400) + the rule's counter.
# usage: runmech.sh WORKDIR CAND_ZIP_OR_SRC_DIR NAME ['COUNTER_REGEX'] [JOBS]
#   COUNTER_REGEX  regex of the status-line tag the new rule prints, e.g. '\[rally\]' (lines should carry r<round>)
# ~7 min with 4 jobs. Same toolchain/setup as runpanel17.sh (run that once, or let this do it).
set -e
W=$1; CAND=$2; NAME=$3; CTR=$4; J=${5:-4}; BASE=${BASE:-nightpack-v2}
L=/mnt/project-files/analysis/local-filter-1021; S=$L/scripts
mkdir -p "$W" && cd "$W"
[ -x cv/bin/cambc ] || { python3 -m venv cv && cv/bin/pip install -q /mnt/project-files/cambc-3.0.5-*.whl; }
C=/root/.cache/cambc; mkdir -p $C
[ -d $C/wasi-sdk-33 ] || { curl -sSL https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-33/wasi-sdk-33.0-x86_64-linux.tar.gz | tar xz -C $C && mv $C/wasi-sdk-33.0-x86_64-linux $C/wasi-sdk-33; }
[ -d $C/cmake-3.31.8-linux-x86_64 ] || curl -sSL https://github.com/Kitware/CMake/releases/download/v3.31.8/cmake-3.31.8-linux-x86_64.tar.gz | tar xz -C $C
[ -d $C/ninja-1.12.1-linux-x86_64 ] || { mkdir -p $C/ninja-1.12.1-linux-x86_64 && curl -sSL https://github.com/ninja-build/ninja/releases/download/v1.12.1/ninja-linux.zip -o /tmp/ninja.zip && unzip -oq /tmp/ninja.zip -d $C/ninja-1.12.1-linux-x86_64; }
if [ ! -f ws/cambc.toml ]; then
  mkdir -p ws && (cd ws && ../cv/bin/cambc init --yes . >/dev/null 2>&1 || true)
  mkdir -p ws/maps && find ws/maps -maxdepth 1 -name '*.map26a' -delete && cp /mnt/project-files/arena/maps/site40/*.map26a ws/maps/
fi
cd ws
[ $(ls maps/*.map26a | wc -l) -eq 40 ] || { echo "expected 40 maps in ws/maps"; exit 1; }
RIVS=${RIVS:-"pHuntF rRushHunt"}   # pHuntF = the farm/econ veto; rRushHunt = hard rival closest to the online band (t10shop wins 72%)
[ -d bots/pHuntF ] || { mkdir -p bots/pHuntF && cp -r $L/panel/pHuntF/src bots/pHuntF/; }
[ -d bots/rRushHunt ] || { mkdir -p bots/rRushHunt && cp -r $L/panel17/rRushHunt/src bots/rRushHunt/; }
rm -rf bots/$NAME; mkdir -p bots/$NAME
if [ -f "$CAND" ]; then (cd bots/$NAME && unzip -oq "$CAND"); else cp -r "$CAND"/src bots/$NAME/; fi
# guard: the candidate must be built on $BASE (10-23: a V17-based candidate judged vs the V18 default showed flips on maps where its rule never fires)
best=""; bestn=999999
for bs in $L/base-src/*/; do b=$(basename $bs); n=$(diff -r bots/$NAME/src $bs/src 2>/dev/null | grep -c '^[<>]'); echo "diff lines vs $b: $n"; [ $n -lt $bestn ] && { bestn=$n; best=$b; }; done
if [ "$best" != "$BASE" ] && [ -z "$FORCE_BASE" ]; then echo "STOP: $NAME is closest to $best ($bestn lines), not BASE=$BASE. Rerun with BASE=$best (or FORCE_BASE=1)."; exit 2; fi
M=man_m_$NAME.txt; : > $M
for R in $RIVS; do
  d=res/cal_${BASE}_$R; [ -f $d/A_ambush.json ] || { mkdir -p $d && cp $L/base-results-mech/cal_${BASE}_$R/* $d/; }
  d=res/cal_${NAME}_$R; mkdir -p $d
  for m in maps/*.map26a; do n=$(basename $m .map26a)
    [ -e $d/A_$n.json ] || echo "bots/$NAME bots/$R $m $d/A_$n.repl26a --statistics $d/A_$n.json --json" >> $M
    [ -e $d/B_$n.json ] || echo "bots/$R bots/$NAME $m $d/B_$n.repl26a --statistics $d/B_$n.json --json" >> $M
  done
done
../cv/bin/cambc run-batch $M --jobs $J --release --json > log_m_$NAME.txt 2>&1 || true
for R in $RIVS; do d=res/cal_${NAME}_$R
  [ -n "$CTR" ] && python3 $S/mechcount.py "$CTR" $d
  (cd res && python3 $S/compact.py cal_${NAME}_$R); find $d -name '*.repl26a' -delete
done
RIV="$RIVS" python3 $S/mechgate.py $BASE $NAME
python3 $S/likeness.py gate $BASE $NAME ${RIVS// /,}
