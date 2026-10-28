#!/bin/bash
# decall.sh TAG [jobs]: decode every replay of rep/TAG to dec/TAG (rounds <= 700)
T=$1; J=${2:-2}; S=/tmp/claude-0/-home-user-cambridge-battlecode-2026/e55ba673-3a8a-54e4-bdf4-6d6b0c43fcdb/scratchpad
mkdir -p /tmp/claude-0/w/dec/$T
ls /tmp/claude-0/w/ws/rep/$T/*.repl26a | xargs -P $J -I{} sh -c 'b=$(basename {} .repl26a); [ -f /tmp/claude-0/w/dec/'$T'/$b.json.gz ] || MAXR=700 python3 -I '$S'/viewer/ext.py {} /tmp/claude-0/w/dec/'$T'/$b.json.gz > /dev/null 2>&1'
