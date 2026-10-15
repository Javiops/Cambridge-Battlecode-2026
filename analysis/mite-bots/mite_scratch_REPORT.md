# mite_scratch — a from-scratch imitation of ladder #1 "Mite"

Bot: `bots/mite_scratch/src/main.cpp` (~1400 lines, one file; every section is tagged with the Mite rule it implements:
[DRAFT] [SHOP] [OPEN] [MAP] [TRIB] [RECALL] [FIGHT] [TARGET] [SPELL]).
Build: `CAMBC_NO_UPDATE_CHECK=1 cambc build bots/mite_scratch`.
Faults / fuel overruns: 0 in all 904 measured games (9 official + 44 generated + 60 hold-out maps, both sides, 4 opponents).

## 1. What was implemented (Mite rule -> code)

| Rule (report) | Status | Where / how |
|---|---|---|
| [DRAFT] fixed draft by team size: 3 picks Varg,Ryth,C&I when the spawn-to-spawn path <= 45 else Ren,Stellar,C&I; 4: Varg,Ryth,C&I,Ren; 5: Varg,Stellar,C&I,Ryth,Ren, Tavi for Ryth on long maps with many altars | done | `run_draft()`; the path is a BFS in the draft turn; team size, path and the Ryth/Ren focus flag go into draft memory |
| [SHOP] alive on spawn only, spend everything: jungle(main) x5 -> durability(main) x5 -> bruiser health x5 -> power(main); main = strength Varg/Issac, focus Cassi/Stellar/Tavi, Ryth/Ren focus on 5-pick maps else strength | done | `shop()`; Tavi shops anywhere |
| [SHOP] altar lock about every other trip, placed before tributing | done | lock bought on even shop trips; `maybe_place_lock()` places it on contested altars right before `submit_gems` |
| [OPEN] whole team to the nearest camp, same monster (elk / biggest first), ranged at exactly 3, melee tank, exactly one capturer, others leave for the nearest camp up | done | `farm()`: no per-camp cap before round 30; shared monster order elk > wolf > small; ring-3 tiles for ranged; capturer = lowest index standing on the spawn tiles; ranged wait at 3 for the melee ally to take the aggro |
| [OPEN] map-specific exceptions (Varg lone elk, Stellar lone cluster, corners 4-to-centre) | not done | hand rules per map in Mite; no general classifier could be validated in the time |
| [MAP] own-half camps only (d_own <= d_en + 3), 1-3 per camp (cap by monster health), no monoliths, mostly skip gold-only, enemy half only while chasing <= ~10 rounds | done | `group_usable()`, `group_cap()`, `choose_group()`, `CHASE_MAX`; claims shared in the 8 shared-memory bytes |
| [TRIB] tribute on every altar pass, never wait; start on the capture tile when an altar is adjacent | done | `tribute_here()` on the capture tile and whenever an altar is within 1; `go_tribute()` detours by bag size (20 gems: 6 tiles, 40: 12, 70+: always) |
| [RECALL] hp < 50% -> recall when the nearest enemy >= 7, walk toward spawn until then; shop recall at ~90-180 gold; recall as a teleport when 5 + spawn->target is shorter; one round on spawn | done | recall block of `play_turn()`, teleport test in the tribute and farm-target paths |
| [FIGHT] spell at 4-5 on the first enemy in range, walk in, prefer isolated, no numbers/hp advantage needed, never chase retreating | done, one deviation (section 4) | `engage()`, `choose_victim()`, `Foe.retreating` |
| [TARGET] killable > nearest > lowest hp%, keep target, everyone on one victim | done | `choose_victim()`, `fight_target` |
| [SPELL] never saved; exclusive spells only on no-walk turns; Stellar single/area (2+ in radius 1); Cassi stun on an enemy within 4 else the awake elk; Ren/Ryth stun and Varg shield only on awake monsters; attack resets double-hit camps; Issac/Ren dash to close and to travel | done | `cast_on_foes()`, `cast_on_camp()`, `basic_attack()`, `step_towards(..., use_dash)` |
| casters attack from 3 and do not kite; melee in front; compact | done | ring-3 tiles, `ally_front` requirement for ranged to approach, back-off toward an ally when the local numbers are against us |
| leave the fight at < ~45% hp | done | covered by the 50% recall rule (step out of monster range first) |

## 2. Iteration history (official maps, both sides; v30 as sparring partner)

| step | vs v30 | gems/100 rounds |
|---|---|---|
| first playable build (farm + fights) | 3-15 | ~150 |
| gem weight / mid-camp penalty in `choose_group`, Cassi aggro fix, pass-based tribute | 1-17 | 164 |
| engagement gate + 40-round danger memory, dangerous altars skipped | 1-17 | 164 |
| full "solo damage budget" check in `choose_group` (reverted, killed the farm rate) | 0-18 | 117 |
| ranged never solo-claim an elk group; bank when an altar is adjacent (final) | 2-16 | 157 |

vs starter-cpp on the official maps: 18-0, 0 faults, 234 gems/100 rounds, 1000 gems reached in every game.

## 3. Final measurement (both sides; maps_hold was never used for tuning)

| opponent | set | W-L | maps won both | maps lost both | deaths/game | gems/100 rounds | mean gem diff | faults |
|---|---|---|---|---|---|---|---|---|
| study25 | maps | 3-15 | 0 | 6 | 3.7 | 155 | -286 | 0 |
| study25 | maps_gen | 6-82 | 1 | 39 | 3.4 | 130 | -258 | 0 |
| study25 | maps_hold | 16-104 | 3 | 47 | 3.9 | 130 | -189 | 0 |
| study24 | maps | 2-16 | 0 | 7 | 3.8 | 150 | -332 | 0 |
| study24 | maps_gen | 8-80 | 2 | 38 | 3.0 | 135 | -204 | 0 |
| study24 | maps_hold | 20-100 | 5 | 45 | 3.9 | 131 | -168 | 0 |
| v30 | maps | 2-16 | 0 | 7 | 4.4 | 150 | -292 | 0 |
| v30 | maps_gen | 7-81 | 1 | 38 | 3.8 | 129 | -241 | 0 |
| v30 | maps_hold | 23-97 | 3 | 40 | 4.6 | 130 | -162 | 0 |
| v29 | maps | 3-15 | 0 | 6 | 3.7 | 165 | -176 | 0 |
| v29 | maps_gen | 9-79 | 2 | 37 | 3.8 | 130 | -233 | 0 |
| v29 | maps_hold | 21-99 | 3 | 42 | 4.2 | 131 | -153 | 0 |

Totals: 120-692 over 812 games (14.8%); never above 19% against any opponent on any set; every sign test p <= 0.03.
Deaths/game 3.0-4.6 (our deaths), gems/100 rounds 130-165 vs roughly 200-240 for the opponents.

Arena summary lines (`out/scratch_logs/<opp>_<set>.txt`):

```
bots/mite_scratch vs bots/study24: 2W 16L 0D of 18 (0 failed) | winrate 11% | mean gem diff -332 | gems/100 rounds 155.9
bots/mite_scratch vs bots/study24: 8W 80L 0D of 88 (0 failed) | winrate 9% | mean gem diff -204 | gems/100 rounds 141.6
bots/mite_scratch vs bots/study24: 20W 100L 0D of 120 (0 failed) | winrate 17% | mean gem diff -168 | gems/100 rounds 136.1
bots/mite_scratch vs bots/study25: 3W 15L 0D of 18 (0 failed) | winrate 17% | mean gem diff -286 | gems/100 rounds 161.1
bots/mite_scratch vs bots/study25: 6W 82L 0D of 88 (0 failed) | winrate 7% | mean gem diff -258 | gems/100 rounds 137.0
bots/mite_scratch vs bots/study25: 16W 104L 0D of 120 (0 failed) | winrate 13% | mean gem diff -189 | gems/100 rounds 134.9
bots/mite_scratch vs bots/v29: 3W 15L 0D of 18 (0 failed) | winrate 17% | mean gem diff -176 | gems/100 rounds 172.4
bots/mite_scratch vs bots/v29: 9W 79L 0D of 88 (0 failed) | winrate 10% | mean gem diff -233 | gems/100 rounds 137.0
bots/mite_scratch vs bots/v29: 21W 99L 0D of 120 (0 failed) | winrate 18% | mean gem diff -153 | gems/100 rounds 136.3
bots/mite_scratch vs bots/v30: 2W 16L 0D of 18 (0 failed) | winrate 11% | mean gem diff -292 | gems/100 rounds 157.0
bots/mite_scratch vs bots/v30: 7W 81L 0D of 88 (0 failed) | winrate 8% | mean gem diff -241 | gems/100 rounds 136.2
bots/mite_scratch vs bots/v30: 23W 97L 0D of 120 (0 failed) | winrate 19% | mean gem diff -162 | gems/100 rounds 135.1
```

`python3 sign.py 'out/scratch_logs/*_maps*.txt'`:

```
study24_maps.txt             games 2-16  maps won both sides 0, lost both 7, sign-test p=0.02
study24_maps_gen.txt         games 8-80  maps won both sides 2, lost both 38, sign-test p=0.00
study24_maps_hold.txt        games 20-100  maps won both sides 5, lost both 45, sign-test p=0.00
study25_maps.txt             games 3-15  maps won both sides 0, lost both 6, sign-test p=0.03
study25_maps_gen.txt         games 6-82  maps won both sides 1, lost both 39, sign-test p=0.00
study25_maps_hold.txt        games 16-104  maps won both sides 3, lost both 47, sign-test p=0.00
v29_maps.txt                 games 3-15  maps won both sides 0, lost both 6, sign-test p=0.03
v29_maps_gen.txt             games 9-79  maps won both sides 2, lost both 37, sign-test p=0.00
v29_maps_hold.txt            games 21-99  maps won both sides 3, lost both 42, sign-test p=0.00
v30_maps.txt                 games 2-16  maps won both sides 0, lost both 7, sign-test p=0.02
v30_maps_gen.txt             games 7-81  maps won both sides 1, lost both 38, sign-test p=0.00
v30_maps_hold.txt            games 23-97  maps won both sides 3, lost both 40, sign-test p=0.00
```

## 4. Known gaps vs the real Mite (and deliberate deviations)

1. Economy is the main deficit: 130-165 gems/100 rounds vs ~200-240 for the opponents. Leaks seen in replays: Cassi/Stellar taking camp aggro and recalling (7 recalls/game on expanse before the "wait for the melee ally" rule), champions walking to a camp that turns out to be respawning, slow fan-out after the opening, and too many short early tribute trips. Mite's measured ~37 gems per capture vs our ~33 comes from bigger bags per trip.
2. Group fighting on single-chokepoint maps (collision, corners, packs): Mite moves as a pack; our champions converge on the middle altar one by one and die (0 tributes on collision). Deviations added to stop feeding: an engagement gate (do not walk into a bigger local group unless the victim is killable, back off toward an ally instead) and a per-champion 40-round memory of where it was outnumbered. Pure Mite needs no numbers advantage.
3. No map-specific opening exceptions (Varg lone elk, Stellar lone cluster, corners 4-to-centre).
4. Danger knowledge is local (vision + memory); Mite's team-wide picture of the enemy pack is not reproduced (only 8 bytes of shared memory, used for claims and one cooldown).
5. Not Mite rules but kept: ranged champions never solo-claim an elk group after the opening; a wounded champion steps out of monster range before recalling; altar locks placed only on contested altars (Mite's every-other-trip cadence is kept on the purchase side only).
6. "Retreating" = the enemy increased its distance last round; Mite's up-to-10-round chase is approximated only by the enemy-half time limit.
7. The 3-pick draft rule for packs follows the task statement (path <= 45 -> Varg/Ryth/C&I) although Mite drafted Ren/Stellar there.
