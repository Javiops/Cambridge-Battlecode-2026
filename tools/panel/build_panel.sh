#!/bin/bash
# Build the specialist sparring panel (2026-10-16, analysis/local-judge/README.md part 2).
# Each specialist = the online bot (the zip recorded in online/data/versions.jsonl) + switches in params.h;
# sp_hunt also gets hunt.h (the P_HUNT patrol/chase mode, off by default so the online build is unchanged).
# usage: tools/panel/build_panel.sh [ONLINE_ZIP]   (from the repo root, after `cambc init --yes`)
set -e
cd "$(dirname "$0")/../.."
ZIP=${1:-$(python3 -c "import sys;sys.path.insert(0,'tools');import online_base as o;print(o.active()['zip'])")}
rm -rf bots/online/src && mkdir -p bots/online && unzip -q -o "$ZIP" -d bots/online
python3 tools/panel/patch_hunt.py bots/online/src
cambc build bots/online >/dev/null
TOP="#define P_FLEE_PCT 40\n#define P_UNI_FLEE 40\n#define P_LOWHP 0\n#define P_GA_AVOID_HP 42\n#define P_AVOID_DIST 2\n#define P_NOCHASE 0"
while IFS='|' read -r name defs; do
  [ -z "$name" ] && continue
  tools/variante.sh "$name" online "$(eval echo "\"$defs\"")" >/dev/null && echo "built bots/$name"
done < tools/panel/specialists.txt
