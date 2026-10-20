# AGENTS.md: brief for anyone (person or agent) working in `next/`

`next/` is a fresh start, built separately from the rest of the repo, after CarsonBurke's method
(cb-bc, orbit-wars, kaggriculture). Nothing outside `next/` is used here. If it works, the team
moves to it.

## Constraints of the game (CAMBC 2026a)

- C++ compiled to WebAssembly. Each champion runs its own instance of the bot; allies share only
  `cambc::shared_memory` and the draft memory.
- A fuel budget per turn. A turn that runs out of fuel is lost (`fuelExhausted` in the stats).
  Always test with `--release`, which is how the platform runs bots; the lab does this for you.
- WASI randomness is always zero in matches. A bot that wants randomness seeds it from the map.
- Win: 1000 banked gems, or at round 2000 compare banked gems, lifetime gold, kills; a complete tie
  goes to team B.

## The loop

1. Read `results/REPORT.md`: leaderboard, win matrix, how each version plays, seat split, strategy coverage.
2. Pick one weakness of the champion and name the number that shows it.
3. Write the hypothesis as the changelog line on line 1 of `src/main.cpp`: `// next-v7: <change>, expect <number> to move`.
4. Edit the bot folder in place (one change), then `python3 -m lab freeze bots/<bot> <bot>-v<N>`.
5. `python3 -m lab league <bot>-v<N>` on the screen maps. Check the number you predicted.
6. If it looks better: `python3 -m lab gate <bot>-v<N>` on the confirm maps. Only a PASS can become champion
   (edit `champion` in `lab.toml`).
7. Write the outcome in `DECISIONS.md`, kept or rejected, with the numbers. Open questions go to `ROADMAP.md`.

### Live experimental versions (Fran's clarification, 20 October)

Do not require a promotion PASS before uploading or selecting a tested experimental
version for real-game learning. Fran explicitly accepts an initial aggregate win-rate
regression when a version fixes a targeted mistake. Freeze the source, reproduce the
release build, check functional/runtime behavior, record the hypothesis and retain a
rollback. Measure the targeted behavior as well as overall results and iterate in new
versions. Do not automatically revert solely for a lower win rate. The gate above still
applies to changing the **lab champion** or claiming proven strength; experimental live
selection does not make either claim. See `LIVE-EXPERIMENTS.md` for current selection.

## Rules

- **Version, don't mutate.** Frozen versions in `archive/` are never overwritten. The bot folder is edited in
  place so the GitHub diff shows exactly what changed.
- **One change per version.** Two changes at once cannot be told apart.
- **Settings live in `lab.toml`.** Map sets, panel, champion, gate thresholds. Not in the scripts.
- **Map sets have fixed jobs.** Tune on `screen`. `confirm` is only for the gate. Looking at confirm games while
  tuning makes them screening maps.
- **Always both sides.** Side B is favoured on these maps (see DECISIONS.md), so a one-sided result means nothing.
- **Fail loudly.** A game that does not finish is listed as a crash and fails the gate. Never skip it.
- **Tests first for the judge.** Any change to `lab/` keeps `python3 -m pytest -q tests` green and adds a test
  when it fixes a bug.
- **Below the noise floor is "no result".** The calibration bots tell us how big a difference the current maps
  can see (DECISIONS.md, 2026-10-17). A smaller gap is not evidence either way.

## Commands

```bash
cambc init --yes .                                  # once per machine: SDK, toolchain, maps
python3 -m lab freeze bots/dummy dummy-v1           # build (release) and keep a frozen version
python3 -m lab list
python3 -m lab league [VERSION ...] [--mirror]      # panel + champion + VERSIONs, screen maps, both sides
python3 -m lab gate VERSION                         # promotion gate on the confirm maps
python3 -m pytest -q tests
```
