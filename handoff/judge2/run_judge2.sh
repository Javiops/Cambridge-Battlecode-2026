#!/usr/bin/env bash
# Juez 2: juega CAND contra los 10 rivales (6 del panel duro + 4 castigadores) en los 40 mapas, por los dos lados = 800 partidas,
# y da el veredicto frente a V20 (v6d) con las partidas base ya jugadas (base_v6d_outcomes.json).
# uso:  bash run_judge2.sh /ruta/al/bot_src_o_zip NOMBRE [JOBS]      (necesita `cambc` en el PATH; motor 1.0.3 / cambc 3.0.5)
# La carpeta del bot debe contener src/ (o ser un .zip con src/ dentro).
set -e
H=$(cd "$(dirname "$0")" && pwd); CAND=$1; NAME=$2; J=${3:-$(nproc)}
W=$H/work; mkdir -p $W/bots $W/res; cd $W
for r in rTop1 rD rF rHunt mV19 mV10d rPun5 rPun5b rPun5c rPun5d; do [ -d bots/$r ] || cp -r $H/bots/$r bots/; done
rm -rf bots/$NAME; mkdir -p bots/$NAME
if [ -f "$CAND" ]; then (cd bots/$NAME && unzip -oq "$CAND"); else cp -r "$CAND"/src bots/$NAME/; fi
M=man_$NAME.txt; : > $M
for r in rTop1 rD rF rHunt mV19 mV10d rPun5 rPun5b rPun5c rPun5d; do d=res/$NAME/$r; mkdir -p $d
  for m in $H/maps/*.map26a; do n=$(basename $m .map26a)
    [ -e $d/A_$n.json ] || echo "bots/$NAME bots/$r $m $d/A_$n.repl26a --statistics $d/A_$n.json --json" >> $M
    [ -e $d/B_$n.json ] || echo "bots/$r bots/$NAME $m $d/B_$n.repl26a --statistics $d/B_$n.json --json" >> $M
  done; done
[ -s $M ] && cambc run-batch $M --jobs $J --release --json > log_$NAME.txt 2>&1 || true
find res/$NAME -name '*.repl26a' -delete
python3 $H/judge2_local.py $W/res/$NAME
