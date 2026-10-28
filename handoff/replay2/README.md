# Replay decoder for engine 2.0.0 (site since 2026-10-26, cambc 4.0.0)

`replaydump2.js` is `online/tools/replaydump.js` plus the 2.0.0 snapshot layout (189768 bytes). The layout comes from
the visualiser's PanelChrome chunk, which ships with the cambc 4.0.0 assets:
- Offsets from 7436 up move by +2688, and offsets from 133436 up move by +4688.
- Champion stride is 624 (items are now 84 words at +240), and group stride is 24 (captureDuration at +20).
- Field offsets inside champion, camp and group entries are unchanged: team, type, x, y, health, maxHealth, alive,
  gold, gems, group, awake, captureTeam.

The engine wasm is `v2_0_0-hWOQ1R8f.wasm`, a copy of the one `cambc view` downloads to `~/.cache/cambc/assets/`.

Usage:
- `node replaydump2.js REPLAY [--camps] [--every-step]`, with `CAMBC_VIS_WASM` set to the wasm in this folder.
- Python: `from dump2 import dump, cheb`, a drop-in for `capkind_light.dump` (camps on).

Checked on a local 2.0.0 game (b35 vs b35, 00contest, 1652 rounds) for these fields: champions, health and gems; camps
and group states; the step headers in --every-step.

KNOWN GAP: the final `statistics` block (Game_Statistics_GetChampion) is still read with the 1.0.3 layout, and its
numbers are wrong in 2.0.0 (damage 0, 42 items). Take statistics from run-batch `--statistics X.json`, or from
`cambc summary`, instead.

## Update (2026-10-27 17:50 UTC)
`replaydump_pc.js` is a copy of the PC's patched decoder (branch claude/pc-e1-assets, commit 16f4d0b, `pcassets/viewer/`).
On a local 2.0.0 game, its champion and camp rows are identical to `replaydump2.js` (0 differences in 1654 rounds), and
its final statistics block is correct (mine gives 0 damage). It also has --vis and --deltas. `dump2.py` now uses it.
