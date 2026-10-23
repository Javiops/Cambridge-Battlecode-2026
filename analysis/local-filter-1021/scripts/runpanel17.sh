#!/bin/bash
# Run CAND against the V17 panel (10 rivals on the t10shop-v2 brain: rA..rM drafts, rInv invader, rHunt hunter;
# 40 site maps x 2 sides = 800 games) and judge it vs $BASE (default t10shop-v2 = V17; t10draft-v2 and marc-bfill-v1 also have base results).
# usage: runpanel.sh WORKDIR CAND_ZIP_OR_SRC_DIR NAME [JOBS]
#   WORKDIR  any empty/scratch dir (re-used across runs); cal_* results go to WORKDIR/ws/res/cal_NAME_<rival>/
#   CAND     bundles/<x>.zip (with src/) or a directory holding src/
# Needs python3, node (gold400 decodes replays with online/tools/replaydump.js), curl.
# The panel base is NOT replayed: its compacted result JSONs are copied from base-results-v17/. Online scale = net x 120/800.
set -e
W=$1; CAND=$2; NAME=$3; J=${4:-4}; BASE=${BASE:-nightpack-v2}  # V18 since 10-23 10:56; t10shop-v2 (V17), t10draft-v2, marc-bfill-v1 also in base-results-v17/
L=/mnt/project-files/analysis/local-filter-1021; S=$L/scripts
mkdir -p "$W" && cd "$W"
[ -x cv/bin/cambc ] || { python3 -m venv cv && cv/bin/pip install -q /mnt/project-files/cambc-3.0.4-*.whl; }
# toolchain: cambc's own download fails on the proxy CA (rustls), so fetch it with curl once
C=/root/.cache/cambc; mkdir -p $C
[ -d $C/wasi-sdk-33 ] || { curl -sSL https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-33/wasi-sdk-33.0-x86_64-linux.tar.gz | tar xz -C $C && mv $C/wasi-sdk-33.0-x86_64-linux $C/wasi-sdk-33; }
[ -d $C/cmake-3.31.8-linux-x86_64 ] || curl -sSL https://github.com/Kitware/CMake/releases/download/v3.31.8/cmake-3.31.8-linux-x86_64.tar.gz | tar xz -C $C
[ -d $C/ninja-1.12.1-linux-x86_64 ] || { mkdir -p $C/ninja-1.12.1-linux-x86_64 && curl -sSL https://github.com/ninja-build/ninja/releases/download/v1.12.1/ninja-linux.zip -o /tmp/ninja.zip && unzip -oq /tmp/ninja.zip -d $C/ninja-1.12.1-linux-x86_64; }
if [ ! -f ws/cambc.toml ]; then
  mkdir -p ws && (cd ws && ../cv/bin/cambc init --yes . >/dev/null 2>&1 || true)
  # cambc init drops its own prefixed copies (00_x.map26a); keep only site40's names, which the base results use
  mkdir -p ws/maps && find ws/maps -maxdepth 1 -name '*.map26a' -delete && cp /mnt/project-files/arena/maps/site40/*.map26a ws/maps/
fi
cd ws
[ $(ls maps/*.map26a | wc -l) -eq 40 ] || { echo "expected 40 maps in ws/maps"; exit 1; }
for p in rA rB rC rD rF rE rG rM rInv rHunt; do [ -d bots/$p ] || { mkdir -p bots/$p && cp -r $L/panel17/$p/src bots/$p/; }; done
for d in $L/base-results-v17/cal_${BASE}_*; do n=$(basename $d); [ -f res/$n/A_ambush.json ] || { mkdir -p res/$n && cp $d/* res/$n/; }; done
rm -rf bots/$NAME; mkdir -p bots/$NAME
if [ -f "$CAND" ]; then (cd bots/$NAME && unzip -oq "$CAND"); else cp -r "$CAND"/src bots/$NAME/; fi
M=man_$NAME.txt; : > $M
for r in rA rB rC rD rF rE rG rM rInv rHunt; do mkdir -p res/cal_${NAME}_$r; for m in maps/*.map26a; do n=$(basename $m .map26a)
  [ -e res/cal_${NAME}_$r/A_$n.json ] || echo "bots/$NAME bots/$r $m res/cal_${NAME}_$r/A_$n.repl26a --statistics res/cal_${NAME}_$r/A_$n.json --json" >> $M
  [ -e res/cal_${NAME}_$r/B_$n.json ] || echo "bots/$r bots/$NAME $m res/cal_${NAME}_$r/B_$n.repl26a --statistics res/cal_${NAME}_$r/B_$n.json --json" >> $M
done; done
../cv/bin/cambc run-batch $M --jobs $J --release --json > log_$NAME.txt 2>&1 || true
tail -1 log_$NAME.txt
export PAN=rA,rB,rC,rD,rF,rE,rG,rM,rInv,rHunt
# stats 1 MB -> 25 KB a game; replays are not needed (gold@r400 comes from the timelines)
(cd res && python3 $S/compact.py $(for r in ${PAN//,/ }; do echo cal_${NAME}_$r; done)); find res -path "res/cal_${NAME}_r*" -name '*.repl26a' -delete
python3 $S/pair6.py $BASE $NAME | tail -1
python3 $S/gold400j.py $BASE $NAME
