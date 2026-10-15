#!/bin/bash
# vary.sh NEW BASE "#define P_X 1\n#define P_Y 2"  (copies all of src, replaces the listed switches, builds)
set -e; cd /home/user/ws
NEW=$1; BASE=$2; DEFS=$3
rm -rf "bots/$NEW"; mkdir -p "bots/$NEW"; cp -r "bots/$BASE/src" "bots/$NEW/"
for n in $(printf "%b\n" "$DEFS" | awk '/#define/{print $2}'); do sed -i "/#define $n\b/d" "bots/$NEW/src/params.h"; done
printf "%b\n" "$DEFS" >> "bots/$NEW/src/params.h"
CAMBC_NO_UPDATE_CHECK=1 cambc build "bots/$NEW" 2>&1 | tail -1
