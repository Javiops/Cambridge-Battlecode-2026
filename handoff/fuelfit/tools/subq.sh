#!/bin/bash
# subq.sh FUEL N... : 52-game subset with --fuel-quantum FUEL, results in res/N_qFUEL
cd $(dirname $0); Q=$1; shift
for N in "$@"; do R=${N}_q$Q; rm -rf res/$R; ./mk.sh $R | awk 'NR%6==1' | sed "s|bots/$R |bots/$N |g" > m_$R.txt
../cv/bin/cambc run-batch m_$R.txt --jobs 4 --release --json --fuel-quantum $Q > log_$R.txt 2>&1; tail -1 log_$R.txt; done
