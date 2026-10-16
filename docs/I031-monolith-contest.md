# I031 Monolith-only maps (contest)

**Hypothesis:** on `contest` the bot scores 0 gems (online 1-43, almost always 0-0 at round 2000, lost on the gold
tiebreak). Fixing it takes contest to 1000 gems against bots that leave the monolith alone; no other map changes.
Source: thread "Revisión del testeo local" (16 Oct).

**Why it was 0:** contest has two monoliths (20,000 hp, 200 strength, 200 gems + 300 gold, respawn 150) and ten gold
clusters; nothing else gives gems. `choose_target` dropped the monolith (`squad_needed` > roster: no team survives it
in one go) and `P_NOGOLD` dropped every gold cluster, so every champion stood at spawn for 2000 rounds with 0 gold.
At round 2000 the tiebreak is gold earned, so even the 0-0 games were losses.

**How the top teams play it** (replay 18c6cc61, Sneaky Bush Campers, rank 1, 1000 gems at round 1057): gold clusters
and items for ~600 rounds (Ren 900 -> 1900 hp), then all six bodies on one monolith (~45 rounds, the monolith hits one
champion for ~126 a round and they rotate the tank), one champion captures and carries the 200 gems, then the other
monolith, alternating with the respawns. A monolith's damage stays while nobody is in range (18,101 hp unchanged for
60 rounds), so it can be worn down over several trips.

**Change:** switch `P_MONO 1` (new, `main.cpp`). At init `mono_only` = the map has a monolith with gems and no other
group with gems. Only when `mono_only`: gold clusters are valid targets (gold = items and the tiebreak), and the
monolith is a target for the whole roster (needed capped at the roster, share cap = roster, no "too-strong" drop).
Files: `bots/study27-economy/src/main.cpp`.

## Local tests

| test | result |
|---|---|
| contest vs base (online bot), both sides | 0-0 r2000 -> 1000-0 at r1543 / r1606 |
| contest vs v30, study25, spar11, spar12, spar16, both sides | 10 of 10 won, 1000 gems at r1436-1670; base: 0-0 in 8, lost both to spar12 |
| same game as base, unlimited fuel (`--fuel 100000000`) | 276 of 277 maps identical on both sides (17 site + hold60 + dev200); only contest differs |
| same game as base, normal fuel | 7 of 34 site-map sides differ, exactly as many as a `P_MONO 0` build: fuel noise from moving code |
| `gate.py --kind farm` | safety clean (faults 0, fuel 91 vs 102); fresh 15-8 p=0.21 = undecided (fuel noise, see above) |
| `gate.py --kind fight` | PASS: fresh not against, panel flips 13 for / 5 against (contest), no veto |

Zip: `/mnt/project-files/bot/mybot_study27_economy_mono.zip`.

## Not covered
- Against a team that also goes for the monoliths, contest becomes a fight over them; untested locally.
- `stampede` and `eight` are not monolith maps (no monolith there); see the PR for what they are.
