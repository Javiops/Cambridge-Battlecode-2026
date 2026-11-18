#!/bin/bash
# Checkpoint the structure GA (out/sga) to the shared folder every few minutes, so a container restart loses
# at most one generation. Usage: nohup tools/ga/island_sync.sh [DEST] &
DEST=${1:-/mnt/project-files/ga-farm/islands/structure}
mkdir -p "$DEST"
while true; do
  for f in out/sga/meta.json out/sga/template.wasm out/sga/*.json; do [ -e "$f" ] && cp -u "$f" "$DEST/"; done
  for d in out/sga/L*; do
    [ -d "$d" ] || continue
    n=$(basename "$d"); mkdir -p "$DEST/$n"
    for f in state.json log.md games.jsonl validate.txt run.log; do
      [ -e "$d/$f" ] && cp "$d/$f" "$DEST/$n/$f.tmp" && mv "$DEST/$n/$f.tmp" "$DEST/$n/$f"
    done
  done
  date -u +%FT%TZ > "$DEST/last_sync"
  sleep ${SYNC_EVERY:-300}
done
