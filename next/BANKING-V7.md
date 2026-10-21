# Banking priority experiment: topdraft v7 / platform v85

V7 continues a healthy champion's existing banking trip before optional camp
planning, when no enemy is seen within eight tiles. It preserves altar choice,
trip hysteresis, starting-trip thresholds, model weights and initialization
reserve. There are no new map-name or opponent-name cases.

The uploaded bot compiled and was observed live as **platform v85**, submission
`656bbeb3-cda1-4c46-bf34-ca6ef406a5df`. Fran then requested a temporary teammate
handoff. **V82 was restored as selected**, and uploads, selection changes and
initiated matches are held until 23:10:20 UTC / 01:10:20 CEST, unless Fran releases
earlier. Offline work continues. Read `experiments/LIVE-HOLD.json` and
`experiments/CURRENT.json` for the current coordination state. Zero v85 unranked
groups were initiated before the hold; no v85 field result is claimed.

## Targeted development result

The frozen v6 parent reproduces the problem on official big-world against
starter: seat B banks zero, with Ren sampled at (26,84) carrying 15 gems from
round 225 through 1,975. V7 banks **105** in the same fixture. Seat A rises from
**121 to 316**. All four games finish with zero faults and zero fuel losses.
The same starter binary, official map bytes and release runtime are used.

Full log samples contain four long repeated-position banking sequences with
15 gems in v6 seat B (900–1,750-round spans). No sequence of at least 75 sampled
rounds remains with 12 or more gems in either v7 seat. Independent official-engine
snapshots at nine round boundaries per game corroborate the inventory/position
change and exactly reproduce terminal banks. Sampled positions do not establish
continuous immobility between samples, and one opponent fixture does not prove
the live Preyas case is solved.

**Remaining defect:** small loads can still stall late in the game. V7's early
trip continuation requires at least 12 gems, while the original late-game banking
policy starts trips with fewer. Ryth carries four gems at the same sampled position
in rounds 1,875–1,975 in both seats. Next test completing any already-started
healthy/quiet positive-cargo trip early, without changing when trips start.

## Broad screening and runtime

| Opponent | Games | Wins | Bot faults | Fuel-exhausted turns |
|---|---:|---:|---:|---:|
| Starter | 70 | 67 | 0 | 4 |
| Frozen v6 | 302 | 148 | 0 | 10 |

Coverage is 35 official maps and 116 generated development layouts, including
16 large geometries, always both seats. Mean deposits against v6 are 691.57
versus 684.19; the 148/302 result does not establish greater aggregate strength.
Fourteen fuel losses remain across 372 games, so this is not a zero-exhaustion
claim. The eight full-log canaries repeat fixtures from the screen and reproduce
their outcomes and champion statistics. An additional eight full-log parent
diagnostics reproduce v6 behavior. Do not count log repeats as independent games.

Existing tests: **139 passed**. The delivered source ZIP builds independently
to the identical local release WASM. The server-downloaded source ZIP matches
the upload exactly. Server live status verifies server compilation; no server
binary hash is claimed. V7 is an experiment, not a formal promotion. The trained
BC/PPO weights, Stage 1–7 certificates and all holdout locks remain unchanged.
Seventy new confirmation layouts still have zero games played.

## Identity and reproduction

- Source ZIP SHA256: `988b0ec7911e9573da47a5ed61fcd447b68770d194924e5777403986398a5ce2`.
- Local release WASM SHA256: `42650144a523cdd760b320efb067fc3325fb7a1e840b40deb16692a8bc0ba7ea`.
- Rules 1.0.1, official CLI 3.0.2; engine build
  `c3e9ffc8d98c106f86660c58344dc26ced9459a504e2f0d90d88b4c8594c7765`.

Restore archived sources/binaries and development maps from the validation ZIP.
Run `tools/topdraft_screen.py` against an isolated current official runtime using
`experiments/topdraft-v7/lab.toml`, `canary.toml` or `parent-canary.toml`.
Compact results and per-game JSONL are under `results/topdraft-v7-*`.
The package includes complete statistics/replays, native snapshots, test log,
source/build identities and a verified file-hash manifest. No new training is claimed.
