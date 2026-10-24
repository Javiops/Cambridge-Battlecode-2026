#!/bin/bash
# sub.sh N... : 52-game subset, replays kept
cd $(dirname $0)
for N in "$@"; do rm -rf res/$N; ./mk.sh $N | awk 'NR%6==1' > m_$N.txt; ../cv/bin/cambc run-batch m_$N.txt --jobs 4 --release --json > log_$N.txt 2>&1; tail -1 log_$N.txt; done
