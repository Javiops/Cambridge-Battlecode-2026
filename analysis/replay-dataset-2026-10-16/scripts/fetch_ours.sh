#!/bin/bash
# download (sequential, polite) then decode in parallel
cd "$1"
R=/home/user/cambridge-battlecode-2026/tools
for m in $(python3 -c "import json;[print(x['match']) for x in json.load(open('sel.json'))]"); do
  [ -s zips/$m.zip ] && continue
  if [ -s /mnt/project-files/online/data/replays/$m.zip ]; then cp /mnt/project-files/online/data/replays/$m.zip zips/; continue; fi
  curl -sSL -o zips/$m.zip.tmp "https://2026a.battlecode.co.uk/api/v1/matches/$m/bundle" && mv zips/$m.zip.tmp zips/$m.zip
  sleep 1
done
ls zips/*.zip | xargs -P 8 -I{} bash -c 'm=$(basename {} .zip); [ -s steps2/$m.c.jsonl ] || (node '$R'/replaydump.js {} --every-step --camps 2>/dev/null | python3 -I '$R'/compact.py /dev/stdin steps2/$m.c.jsonl)'
echo DONE $(ls steps2 | wc -l)
