#!/bin/bash
# usage: run_all.sh <WS dir name, e.g. ws2|ws3> <output dir>   (runs every q*.py with the loader pointed at $S/<WS>)
S=/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad
WS=$1; OUT=$2; mkdir -p $OUT; cd $OUT
for q in q1_territory q2_spread q3_actions q4_camps q5_maps q6_cycle q7_deaths q8_lanes q9_opening q10_determinism q11_rows q12_rowsgroups q13_stacking q14_idlecamp q15_rows_end; do
  WS=$WS python3 -I $S/ws2/scripts_positions/$q.py > $OUT/$q.out 2> $OUT/$q.err &
done
wait; echo RUN_DONE $WS $OUT
