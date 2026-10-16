# I033 fuel guard (`P_FUELGUARD`, bots/study27-economy)

## The problem

A champion turn has 100k fuel (200k on its first turn). When a turn runs past it, the engine ends the turn
(replay step kind 26 instead of the normal end, kind 8), **suspends the bot where it stopped and resumes it there in
the champion's next turn** (GameRules, "When the budget runs out"). So the champion does nothing for the rest of
that round, and its next round is spent finishing the old turn on last round's data. That is the "we don't input
anything" seen in online games.

Measured with `tools/fuelscan.py` (counts kind-26 turn ends per team from replays):

| where | our bot before | rival / after |
| --- | --- | --- |
| 38 online unranked games, 16 Oct 05:00-06:48 UTC (online bot) | 10.3 a game: lanes 63, monolith 26, ambush 21, rushbait-v2 17, pilgrimage 10 | rivals 32 a game (one stampede rival 248) |
| local, 17 site maps vs v30, side A, `--release` | 11.5 a game (5.6 in rounds 1-3) | **1.1** with the guard |
| local, hold60 vs v30 | 5.9 a game (5.1 in rounds 1-3) | **0.1** |
| local, self-play on the 17 site maps | 11.5 a game | **1.2** |

## Where the fuel went (`P_FUELPROF 1`, debug build)

- **Start-up (rounds 1-2, every map):** `init` costs 120-185k of the first turn's 200k on big maps:
  `bc::map::camp_groups()` alone 20-26k, the camp-group loop 50-98k, one path search per altar (5 altars = 35k+),
  then the rest of the first turn ran out and the second turn finished it.
- **Capturing (three quarters of the mid-game overruns, mode farm/capture):** `other_captures` asked `position()` of every ally,
  and an ally out of vision throws: 27-35k a call. The reward-evacuation check scanned every visible camp
  (`bc::vision::camps()`, 5-10k per camp) and re-ran `choose_target` (15-39k: a path search plus two calls per
  camp tile) every turn while standing on the reward.
- **The low-fuel fallback step** (`step_towards` under 25k) called `move_towards`, which is one more path search
  (7-27k) at the worst moment.
- Costs measured with probes: one path search 5-8k, `distance_field::get` 56, `bitboard::is_set` 43, exporting a
  whole distance field 6-12k (dearer than ~100 reads), `std::pow` ~1.

## The fix (all behind `P_FUELGUARD`, on in params.h)

Cheaper, same result:
1. one path search from the spawn decides which altars are reachable, instead of one per altar;
2. `choose_target` keeps the walking distances to every camp group while the champion stands on the same tile;
3. `other_captures` skips allies out of vision before `position()` throws (they were skipped by the catch anyway);
4. the evacuation check reads the camps within 12 tiles (the list play_turn already has), not every visible camp.

When the turn cannot pay for it:
5. start-up runs in three parts (map and groups, walking distances, roles and shop); a part that does not fit
   waits for the next turn and the champion stays on its spawn meanwhile;
6. an optional camp re-choice (`choose_target` costs up to what the dearest one so far cost) waits for a later turn
   when the turn could not pay for it plus a step; the reward-evacuation check skips its re-choice the same way;
7. log lines are skipped when the turn is nearly out;
8. the low-fuel fallback step is a plain greedy step (no search) under 20k.

## Checks

- **Same decisions:** with unlimited fuel (`--fuel 100000000`) the candidate plays the identical game to the base on
  154 of 154 map sides (17 site maps + hold60, vs v30). Only the fuel-dependent choices change.
- **Stability:** a no-op rebuild (40 extra additions a turn, a few hundred fuel) changed 24 of 154 map sides of the
  base and 15 of 154 with the guard. Fuel-dependent branches (`fuel_ok` thresholds all over the bot) remain, so
  local A/B tests are still noisier than they look.
- **Gate vs main** (`tools/gate.py bots/study27-economy main`): safety clean (0 faults, fuel-exhausted turns on
  lanes/corners/collision 115 -> 17); fresh maps 59-54 won/lost on both sides (p=0.71, gems/100 rounds 168.1 vs
  167.5): as a farm change, undecided. On fresh maps fuel almost never ran out after round 2, so most of the gain is on
  the big site maps (lanes, corners, monolith, ambush), where it matters online.

## Tools

- `python3 tools/fuelscan.py REPLAY...` (local `.repl26a` or online bundle `.zip`; tries each engine version) and
  `python3 tools/fuelscan.py --play bots/A bots/B --maps 'maps/*.map26a'` (plays with `--release`, as on the site).
- Profiling: add `#define P_FUELPROF 1` at the top of params.h of a copy, run without `--release`, read the
  `[fuel]` (cumulative per section, every 100 rounds) and `[heavy]` (turns over 70k or cut off) lines in team-x.stdout.
- `cambc build --release` fails ("CMake did not generate compile_commands.json") on a folder never built in debug:
  run `cambc build BOT` once first.
