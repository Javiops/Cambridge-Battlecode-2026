# fuelfit — farm section (choose_target, step_towards, engage_camp, refresh_groups)

Exact optimisations over `handoff/fuelfit/fuelfit-a1.zip` (kvvl + o01-o05). Every patch here was checked with the
unlimited-fuel bench (`--fuel-quantum 2000000`, 40 maps x 2 sides vs 6 rivals = 80 games, `tools/same.py` -> `differ 0`).

## Patches (`opts/`, apply in name order after the integrator's series)

| patch | what | exactness argument | 80-game check |
|---|---|---|---|
| `o41_ctfield.py` | choose_target: ONE export of the reached mask (bitboard, packed bits) and ONE export of the distance field instead of `is_set` (47) + `get` (41) per group tile; per-group tile indices computed once per game (groups are fixed after `init_groups`) | exports are tile-exact copies (bench: 0 mismatches of 10000); same min over the same tiles | differ 0 |
| `o42_stepsnap.py` | step_towards (tpc / dash / stuck scans), `mp_dash_hole_step` ring scan, `isle_escape` landing scan read from static exported snapshots (`BitSnap`, `DistSnap`) instead of one SDK import per tile; `vblock` copied only when the volley ring writes to it | snapshots taken after the last write to the field they copy; loops keep order, bounds and strict `<` tie-breaking; `isle_escape` still iterates `pocket.positions()` (its order decides ties); the 8-tile stuck scan uses the snapshot only when a scan above already paid for it | differ 0 |

`o06`-style numbering in the original development copies: o41 = o06, o42 = o08 (comments say so).

## The finding that changes the design: fuel is instruction metering

Bench (`a1b`, big_world / corridors):

| C++ work | fuel |
|---|---|
| trivial loop, 10 000 iterations (volatile sink) | 100 011 (~10 per iteration) |
| scanning 1 681 exported bits | 26 055 |
| own C++ BFS over 10 000 tiles | > 1 000 000 (the turn dies) |
| zero-filling a 20 KB `std::vector` (DistSnap on 100x100) | ~10 000 |
| one `printf` line | 568 |

Engine-side search is native and cheap by comparison: `distance_field::compute` ~3.4 fuel per visited tile (3 367 on 41x41,
30 616 on 100x100). So: never move an engine search into C++ (an "o09" that did this was exact but 30x dearer and killed
round 1 on big maps); every snapshot buffer must be a function-level static (a first o42 with per-call vectors was exact
but MORE expensive than the imports it replaced); count loop iterations when fitting the worst turn.

## SDK prices measured (per call)

bitboard: is_set 47, set 75, copy/or/not/and-not 500-660, is_empty 62-196, count 196, positions(16) 716,
export_linear_buffer 190 (packed bits LSB-first, index y*w+x, size (w*h+7)/8), draw_chebyshev 505-660, ctor+set 267, copy+clear 298.
distance_field: get 41, compute(200) 3.4k (41x41) / 30.6k (100x100), compute_to 1.1k-3.9k when the destination is reached
(exhaustive = full compute when it is not), export_linear_buffer 457 (41x41) / 2536 (100x100), next_moves_from 848.
champion: health/attack_range/position/can_move/can_cast 44-76, abilities() 71, abilities()[k].is_ready 616 (!), cooldown 175,
consumables() 7, consumables.count 32, gem_count 49, is_alive 49. camp: health/max_health/strength/position 45-48 each
(one `detail::sdk_camp` read gives all four: 19), is_visible 52, spawn_position 6, state 32, group.camps() 7.
vision: visible_tiles_into 299, champion_tiles 566, camp_tiles 251. read_sm 26, my_roster 1.2-1.7k, vis_champions (o01 copy) 2.7-4.1k.
`sdk_costs.md`'s camp_health 1997 was not reproduced.

## Engine search rules (verified, useful for exactness arguments)

* `distance_field::compute` = 8-neighbour BFS; a wall blocks only its own tile (a diagonal step past a wall corner is
  allowed); tiles at distance == max_distance are reached, farther ones are not. All 40 maps, every champion's position,
  rounds 3-60: 3 182 comparisons, 0 mismatches in distances and in the visited mask (alternative corner rules fail).
* `next_moves_from(p)` = the neighbours with distance d(p)-1, in compass order from north with north = (0,+1):
  (0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1). 4 569 samples, 0 mismatches.
* The visited mask of an early-stopped `compute_to` could NOT be replicated (expansion order unknown: 12 candidate
  orders/stop rules all mismatch). Exact code may read a `compute_to` field only at tiles whose distance is below the
  destination's distance (those layers are complete whatever the stop point). This is what makes a bounded
  `compute_to(..., max_distance = bound)` exact when every read is of a distance < bound.

## Profile (80 games, 108 270 champion turns, unlimited fuel, `tools/prof_fp.py`)

farm section p50 10k, p90 22.5k, p99 52.5k, p99.9 72.5k, max 213k (base a1). On heavy farm turns choose_target_impl
~24k mean when it runs (compute 11k + scoring loop 8.5k + pd_gd 4.6k before o41) and step_towards ~12k (its heavy
cases: `mp_dash_hole_step`'s exhaustive compute_to when the goal is unreachable through holes, the jammed-corridor second
compute_to, `isle_escape` 190k before o42). Numbers after o41+o42 in RESULTS (farm thread) once the profile run ends.

## Tools (`tools/`)

`prof_fp.py SRC` turns the FP/FP_SCOPE no-ops into a per-section/per-scope fuel meter (`[fpt]` heavy turns, `[fph]`
histograms); `fph_pct.py RESDIR` percentiles per scope; `fpt_agg.py RESDIR [THR]` composition of heavy farm turns;
`ct_prof.py SRC` sub-scopes inside choose_target_impl / step_towards (on top of prof_fp.py; anchors match a1+o41+o42).

## Added 2026-10-25 (all 80/80 byte-identical over fuelfit-a1 + o41 + o42)

| patch | what | exactness argument |
|---|---|---|
| `o43_dashcap.py` | `mp_dash_hole_step`: the hole-route `compute_to` bounded by `max_distance = here - P_MP_DASHHOLE` (it was exhaustive, ~30k on 100x100, whenever we are unreachable through the holes) | reached within the bound -> same BFS distance; not reached -> the original returned 0 at `hh > here - P_MP_DASHHOLE` with no side effect; every later read is at a distance < hh (complete layers) |
| `o44_dist.py` | `dist()` in 32-bit arithmetic (vec2::chebyshev_distance promotes to int64: 50 fuel per call; ~6 calls per group per choose_target, loops in step_towards and the fight code) | coordinates < 2^15, same max of the same absolute differences |
| `o45_ctrev.py` | choose_target: (A) per-group REVERSE fields (one `compute` from the group's tiles over static walls, once per game: 42k on corridors/12 groups .. 551k on big_world/24; then `is_set` + `get` at pos per group, 1.2-3.3k per call) replace the forward search from pos (3.4k-30k every retarget turn); the original path stays for the turns before all fields exist and when pos is a static-block tile. `P_FARM_PD_PER_TURN` (default all) lets the integrator spread the precompute over turns: same decisions, different fuel schedule. (B) scoring loop: claimers counted in one pass over the claim slots, per-group constants (doorstep / half-map booleans, recall cycle) once per game, `walk()` computes the straight-line distance only when used | (A) undirected unit grid with fixed walls: d(pos, group) = min over tiles of the forward BFS = the group field at pos; verified identical on 6 maps, 287 positions, 0 mismatches. (B) same integers and the same double expressions in the same order |

Profile after o41..o45 pending (RESULTS in the farm thread). `o46_groupvis.py` (refresh_groups / near_camps read one exported vision board) is in its 80-game check.

| `o46_groupvis.py` | refresh_groups: "any tile of the group visible" from ONE export of `s.vis` (static buffer) and per-game tile indices instead of `is_set` per tile (100-300 imports every turn); near_camps: the engine vision board `tv` exported once instead of `is_set` per camp spawn tile | same bits read after the board was written (s.vis assigned once per turn before refresh_groups; tv filled in near_camps); `any` is order-independent. 80/80 identical. Needs BitSnap from o42 |

Profile after o41..o45 (80 games, 108 270 turns): farm section p90 20k -> 17.5k, p99 52.5k -> 35k, p99.9 70k -> 47.5k,
turns >= 50k 1401 -> 87; choose_target p99 32.5k -> 17.5k, p99.9 50k -> 27.5k; step_towards unchanged (p99.9 37.5k;
heavy-turn mean 15.5k = exhaustive compute_to 7.9k + dash-holes 9.6k + move 4.1k + tpc 4.8k); turn total p90 62.5k -> 57.5k,
p99 90k -> 82.5k. The remaining choose_target cost is the pure C++ scoring loop (~500 fuel per group). Exact pieces plateau
around farm p99.9 ~45k: the 25k goal needs decision changes (K nearest groups scored, one path search per turn, isle_escape
every 10 rounds), judged by strength, never by fuel.

## o5x: decision-changing caps (NOT exact), judged by strength against the base on the same games

Paired comparison: same 80 games (40 maps x 2 sides, 6 deterministic rivals rotating), base = a1 (== a1+o41..o46).
`pair.py` net = wins gained - lost over the games whose result changed, bar = 2*sqrt(changed); `vstat.py` a14 = state at
r300 (gems, gold, deaths, monster damage; +0.637 for the base), `divloc.py` = games whose timelines differ.

| patch | rule | 80 games | verdict so far |
|---|---|---|---|
| `o51_onesearch.py` | step_towards: when the first field does not reach us, no second ("corridor jammed") search this turn (P_ONE_SEARCH) | 11 games differ, 3 results changed, net -3 (bar 3.5); a14 +0.637 -> +0.612 | doubtful: 240 more games running |
| `o52_ctk.py` | choose_target scores only the P_CT_K = 12 nearest groups by walking distance (+ current target + leader's group) | 57 differ, 22 results changed, net +2 (bar 9.4); a14 +0.637 -> +0.827, gems300 +19.7 -> +26.0, gold300 +256 -> +321 | neutral-to-positive on strength, cuts the scoring loop on 24-46-group maps; 240 more games queued |
| `o53_isle10.py` | isle_escape plans at most once every P_ISLE_EVERY = 10 rounds off the mainland | 2 differ (first divergence r502+), 0 results changed | neutral: safe to take |

Fuel effect is not measured here (unlimited-fuel bench); the integrator's worst-turn fit decides what each cap buys.

## o48_warmup.py (over b6 = o01-o11, o21-o26, o31-o33, o41-o47; anchors on the integrator's reanchored o46)

The once-per-game farm tables out of the first playing turn: `bool farm_warmup(State& s, int quota)` builds, for up to
`quota` groups per call, the shared per-group tile index list (used by o41 and o46, which each built their own) and the
o45 scoring constants; returns true when every group is done. Call it from the init steps after stage 3 (needs groups,
centres, spawn_pd). Any farm code needing the tables before that completes them on the spot (`farm_warmup_now`), so the
decision never depends on when they were built. BitSnap/DistSnap now keep an uninitialised heap array (`new T[n]`, the
export overwrites every byte) instead of a zero-filled std::vector: the first load of a 20KB distance snapshot no longer
costs ~10k. Measured (b6wm, unlimited fuel): first group 1.5-2.6k (includes the table allocation), then ~450-520 per group
(corridors 12 groups 68 tiles: 1483 + 5753; big_world 24/92: 1923 + 10775; islands 46/118: 2613 + 20171).
Price to budget: 2.5k + 600 per group. 80/80 byte-identical replays (b6 vs b6+o48).

## o49_warmup2.py (over b6 + o48)

More once-per-game work into `farm_warmup`'s first call: share_pow's std::pow table (o05; 303 fuel per pow, up to 18 on the
first choose_target calls) is global and filled in the warm-up; `tank_bits(s)` and the roster handles are learned there;
the reverse-field objects (`s.pd_rf` / `s.pd_rv`, N bitboard constructors at 251 each) are allocated there instead of in
farm_pd_ready's first call (the 12k "first field"). `my_roster` returns a const reference (it copied the vector on every
call, also in vcarry_on). Exact: same values computed earlier / not copied. 2/2 games identical to b6; 80-game check running.
Per-game price of the first farm_warmup call: 18 pows 5.4k + roster/tank_bits ~2.5k + N x ~260 for the field objects + 2.5k
tables; later calls 600 per group.

## o49 check: 80/80 byte-identical replays (b6 vs b6+o48+o49), 10-25 00:48 UTC.

## o5x on the integrator's b10 (10-25 01:10-01:50 UTC; unlimited fuel; 56 far = far.sh, 80 near = subq)

| patch | far 56: differ / results changed / net | far wins | far a14 | near 80: changed / net | near a14 |
|---|---|---|---|---|---|
| b10 | - | 36/56 | -0.106 | - | +0.437 |
| o52 K=12 | 14 changed, net +4 (bar 7.5) | 40/56 | +0.131 | 10 changed, net +2 | +0.643 |
| o51+o52+o53 | 16 changed, net +2 | 38/56 | +0.137 | 11 changed, net +3 | - |
| o51 | 2 changed, net 0 | 36/56 | | | |
| o53 | 0 changed | 36/56 | | (earlier: 2 differ, 0 results) | |

Verdict: **o52 yes** (positive on every panel so far: 80 a1 +2/22, 80 b10 +2/10, 56 far +4/14, a14 and gems300 up each
time; it is the piece that cuts the scoring loop on 24-46-group maps). **o53 neutral** (take it for the cap). **o51 drop**
(nothing to gain, doubtful on 160 earlier games).

## Far-map profile of b10 (12 games: islands, ambush, big_world, great_wall, expanse, fracture x rTop1 x 2 sides)

tools/prof_fp48.py + ct_prof48.py (48 scopes; [fpt] also on tribute >= 25k), fpt_st.py (heavy turns by section),
fph_tot.py (turns by total cost from the [fph] histograms). b10: 15438 turns, 286 >= 77.5k (1.85%), 132 >= 87.5k.

Finding 1 (fixed by **o54_pdsched.py**, exact): choose_target_impl runs only every few rounds per champion on far maps, so
the o45 reverse fields (one per call) took 250-500 rounds to warm up, and every call meanwhile paid the forward field AND
one reverse field: ct:compute 30-35k from r11 to r300 (present on 95-100% of heavy farm turns). o54: choose_target never
computes a reverse field (uses them only once all exist, else the forward field); the warm-up runs at the end of every
playing turn that did not pay the forward field and is not a tribute walk (dead, fight, approach-cached, recall turns), one
field per turn, fixed rule, no fuel read. init_wait (o47) keeps computing them on the idle round.

Finding 2 (fixed by **o55_stskip.py**, exact): step_towards off the mainland (big_world (71,80) after a dash over holes,
ambush's moated room, islands) ran two exhaustive searches (live block, then static+camps; 26-30k each on 100x100)
before isle_escape's third. Both block sets contain s.static_block, so with every goal on the mainland neither can reach
us: skipped. The mainland bitboard (component of our spawn over static walls) is global now (g_mainland), computed in the
first o54 warm-up slot or by isle_escape as before.

Finding 3 (**o56_islecache.py**, exact, small): isle_escape's landing scan (<= 80 pocket tiles x 24 landings x wall
check, ~30k C++) is built once per island and kept with the pocket; the pocket field runs before the goal field so an
island over P_ISLE_MAX returns before the exhaustive search. isle still costs ~55k when it runs (the goal field is
exhaustive by nature: dest unreachable) -> o53 (every 10 rounds) stays useful.

After o54+o55(+o56), same 12 games: turns >= 77.5k 286 -> 156 (1.0%), >= 87.5k 132 -> 57; heavy farm turns (farm section
>= 30k and total >= 76k) 1153 -> 547; ct:compute mean on them 21k -> 4.4k. 12/12 replays identical to b10 (profile builds).
Exactness (b10 vs b10+patch, byte-identical replays): o54 80/80 near + 56/56 far; o55 80/80 near + 56/56 far; o54+o55+o56 80/80 near + 56/56 far. All three integrated in the integrator's b12 (commit fbc87a3) with o52+o53.

What remains on far maps (mean on heavy farm turns after o54-o56, present%): step_towards 25.6k (99%: goal search st:ct1
9k, dash holes 11.5k when present, isle 55k on 5%), choose_target 24k (74%: ct:score 15k -> o52), engage_camp 15k (15%,
max 88k: one outlier to look at), and outside farm: play_turn start "init" section 23k on 27% (cf_observe /
br_static_step: recall thread), post-sweep 15.5k on 51% and log 12.8k on 22% (pelea / integrator), shop 25k on 31% of
tribute turns. Tribute turns: step_towards 24k (st:ct1 8k, dash holes 9k), not 44k: the 44k figure was isle_escape.

Final check (01:50 UTC): o52 on top of o54+o55+o56 (f52) gives exactly the same 56 far + 80 near games as o52 on b10 (0
replays differ), so the three exact pieces are exact also with the cap on; strength as o52: far net +4/14, wins 40/56,
a14 +0.131; near net +2/10, a14 +0.643. b12 (integrator) = b10 + o52-o56.

b14 (integrator: b12 + o35 altar fields 1/turn on big maps + o57 first playing round by init cost model) vs b10 on the
same panels (02:15 UTC): far 56: 15 changed, net +5 (bar 7.7), wins 36 -> 41/56, a14 -0.106 -> +0.029 (below o52's
+0.131: the later first round on 100x100 maps costs early state, not results); near 80: 15 changed, net +9 (bar 7.7,
passes), WR 0.66 -> 0.78, a14 +0.437 -> +0.700. vs o52-on-b10: far +1/11, near +7/11.

## First playing turn on 100x100 maps (b16, 02:40-03:00 UTC; prof_fp48 printing every turn <= r8; 8 games)

Measured (per champion, unlimited fuel): ambush r4 131-162k, big_world r5 155-171k, islands r4 104-126k, road_of_riches
r4 102-113k. Parts: choose_target 38-57k (forward field 26-31k + o41 read-out 6-16k + K-cut/score), recall section
26-31k (cr_return_walk computes the home field on its first call: recall thread), br_static altar field 23-27k (o58 moves
it), step_towards 16-40k (goal search 11-14k, dash-hole search 14-20k, move 8k), fight 6k, decide 3.6k, post 6.5k.
On islands/road_of_riches the forward field is cheap (6k: few passable tiles) but choose_target still paid 20-25k outside
the scoring loop: unreach() asked s.mp_dashholes.is_empty() (SDK, ~200) for every unreachable group, twice per call.

- **o59_unreach.py** (exact): is_empty() once per choose_target call. Saves 7k (big_world) to 11-17k (islands) per call,
  every call, not only the first.
- **o60_pdprefill.py** (exact): the forward field from the spawn and its read-out are computed in init_wait (idle round),
  into the per-position cache; the first turn finds `cached` and skips both (keyed by position: a moved champion misses
  and pays as before). The first playing turn is marked as having paid its field so the o54 warm-up slot skips it
  (otherwise the end-of-turn reverse field, which profiles in the "log" section, ate the saving).
  First turn after o59+o60: ambush 100-130k, big_world 116-131k, islands 91-108k, road_of_riches 87-99k.
  Idle round cost grows by ~14k (prefill 32k minus one reverse field less).
What is left on the first turn that is not the engine's goal search: recall home field 26-31k and altar field 23-27k
(both static: idle-round material), then ambush/big_world would be ~50-80k. Exactness runs (56 far + 80 near vs b16) in
progress.
Exactness of o59+o60 over b16 (03:08 UTC): 56/56 far and 80/80 near byte-identical replays. Both are in the integrator's
b18 (with o58 altar fields and o62 recall home field on the idle round): first playing turn on 100x100 ambush 97k,
big_world 100k, islands 91k, starvation 89k, road_of_riches 81k; what is left there is the engine's goal searches of
the first step_towards. b18 is the night's candidate; the PC's Judge 2 decides between b15/b16/b18.

## b15 (chosen base, no idle-round work): first playing turn on the 14 far maps (05:50-06:10 UTC, unlimited fuel)

Per champion (min..max over the 5), b15 -> b15+o59+o63:

| map | groups | first turn b15 | +o59+o63 | choose_target | forward field | recall (home field) | altar field (init-sec) | step_towards |
|---|---|---|---|---|---|---|---|---|
| ambush | 12 | r2 108-139k | 108-139k | 39k -> 39k | 26k | 26k | 0 | 16-40k |
| big_world | 24 | r3 155-171k | 150-164k | 56k -> 50k | 31k | 31.5k | 27.5k | 9-28k |
| starvation | 14 | r2 101-124k | 98-120k | 37k -> 34k | 21.6k | 21.8k | 0 | 17-35k |
| expanse | 24 | r3 96-108k | 91-103k | 34k -> 28k | 11.8k | 12k | 15.7k | 8-21k |
| fracture | 28 | r3 99-106k | 93-101k | 39k -> 33k | 15k | 15.3k | 11.4k | 7-15k |
| islands | 46 | r3 87-111k | 78-95k | 42k -> 28k | 6k | 6.4k | 10.7k | 7-19k |
| road_of_riches | 51 | r3 92-100k | 83-90k | 39k -> 30k | 6k | 6.6k | 10.4k | 5-10k |
| pilgrimage | 23 | r3 88-96k | 83-92k | 32k -> 28k | 11.8k | 12.1k | 11.4k | 7-17k |
| lanes | 42 | r3 78-86k | 70-79k | 33k -> 25k | 5.7k | 0 | 12.1k | 7-15k |
| concentrated_wealth | 11 | r2 75-92k | 75-92k | 24k -> 24k | 13.5k | 13.9k | 0 | 12-22k |
| great_wall | 17 | r3 68-80k | 64-76k | 23k -> 19k | 4.5k | 5k | 9.8k | 5-18k |
| shortcut | 21 | r3 76-81k | 71-76k | 24k -> 19k | 3.9k | 4.4k | 10.1k | 5-9k |
| split | 32 | r3 74-79k | 67-73k | 29k -> 23k | 3.8k | 4.3k | 9k | 6-12k |
| rows | 9 | r2 52-61k | 52-61k | 17k -> 17k | 7k | 7.2k | 0 | 6-11k |

- **o63_gdonce.py** (exact, after o52): each group's walking distance computed once per call (pre-sized static array)
  and reused by the scoring loop; with o59 it takes 5-13k off choose_target on 24-51-group maps, on every call (islands
  42k -> 28k, road 39k -> 30k, lanes 33k -> 25k). On 9-12-group maps it is neutral (+0.1-0.2k).
- What remains in choose_target's own code on big maps: 3k exports, ~4k claim reads, ~200 per group in walk() (dist +
  cache checks), 4-6k scoring of the 12 nearest. The forward field (engine) is 4-31k and cannot be prefilled on b15
  (no idle-round work: the PC rejected b19); the field export writes 65535 for unreached tiles (probe), so the reached
  mask is not needed for the read-out (190 fuel: not worth a patch).
- The same static engine fields appear three times on the first turn of big maps: forward field (farm), home field
  (recall: cr_return_walk's first call, 26-31k on ambush/big_world/starvation) and an altar field (o35, 10-27k). The
  recall and altar ones are not needed on the first turn (no gems); moving them to the o54 end-of-turn slot (one static
  field per turn that did not pay a forward field and is not a tribute) would take 26-59k off it with no init work.
- Boundary view (budget 85,984 per round, ~172k for two): a turn that always spills by a wide margin and emits its
  action at the end is as deterministic as one that fits. The risky first turns are the ones within ~2k of a multiple:
  lanes 78-86k and concentrated_wealth 75-92k straddle 86k; islands 87k and pilgrimage 88k sit just over it; big_world
  171k sits just under 172k. After o59+o63: lanes 70-79k and split/shortcut/great_wall clear of it; islands 78-95k and
  road 83-90k now straddle it, pilgrimage 83-92k too: cutting the home field (26-31k) as well is what moves ambush,
  starvation, expanse, fracture, islands, pilgrimage, road under 86k together.
Exactness over b15 (06:10 UTC): o59 56/56 far + 80/80 near; o59+o63 56/56 far + 80/80 near byte-identical replays.
Both add no init work and no idle-round work: safe for the b15 line.

## o64_staticq.py (over b15 + o59 + o63; 06:30 UTC): the end-of-turn slot becomes the static-work queue

One engine field per turn that did not pay the forward field and is not a tribute walk, fixed order: recall home field
(cr_home_prepare, factored out of cr_return_walk, which keeps the on-demand compute as fallback) > altar fields
(br_static_step, no longer at the start of play_turn; br_plan keeps its cached/uncached paths) > mainland (o55) >
reverse group fields (o45). cr_capture_extra asks for the home walk only when it can change the answer (hp < 90% or
gold >= 90: cr_optional_value is false otherwise whatever the walk; the counters are under the same condition).
First playing turn, b15 -> b15+o59+o63+o64 (per champion, 14 far maps): big_world 155-171k -> 91-105k, ambush 108-139k
-> 82-113k, starvation 101-124k -> 77-99k, islands 87-111k -> 62-78k, expanse 96-108k -> 64-76k, fracture 99-106k ->
67-74k, road 92-100k -> 66-74k, pilgrimage 88-96k -> 61-69k, lanes 78-86k -> 58-67k, concentrated_wealth 75-92k ->
62-79k, great_wall 68-80k -> 50-62k, shortcut 76-81k -> 57-62k, split 74-79k -> 55-60k, rows 52-61k -> 45-54k.
Ten of the 14 maps are now under 86k for every champion on the first turn; big_world stays over (forward field 31k +
step_towards 9-28k + base), ambush and starvation straddle it (step_towards 16-40k: dash champions pay the dash-hole
search).
Exactness over b15 (06:35 UTC): b15+o59+o63+o64 56/56 far + 80/80 near byte-identical replays (same.py differ 0).
So the queue never changes a decision: br_plan's uncached path before the altar fields are ready, the home field
computed later and the recall fallback all give the same answers as computing them on the first turn. o64 is exact
and adds no init work and no idle-round work: safe for the b15 line (and b24hp/b26).

## o65_fieldreuse.py (over b15 + o59 + o63 + o64): the two goal fields of a walking turn kept and reused -- CLOSED 10-25 10:30 UTC, NOT ADOPTED

Script kept in opts/not-adopted/ (v6; exact by construction, v1-v3 verified 56/56 far + 80/80 near, v4-v6 not re-verified
because none saves fuel where it matters). Do not apply it.

What it does: step_towards' goal field (roots = goal tiles, walls = s.blocked, stopped at our tile, 14-17k on ambush,
13-17k starvation, 8-9k big_world) and mp_dash_hole_step's field (holes open, 14-20k / 13-16k / 4-8k) are kept in State
and reused when every read is provably the same: (a) each tile that became a wall has cached distance >= D, (b) each tile
that stopped being a wall has all 8 neighbours at cached distance >= D - 1, (c) no changed tile inside the goal mask
(roots unchanged); exhausted bounded searches are a negative cache (D = B + 1); after a pass with changes the kept walls
become today's. The rule is right (0 mismatches cached vs fresh in 240k checks, x65n) and holds on 60-72% of walking
searches overall (x65p) -- but almost only on quiet turns.

Six versions, full-game profiles against e64 (14 far maps vs rTop1, unlimited fuel, prof_fp48 + ct_prof48, cmpprof.py):
- v1-v4 (bitboard copies of roots/walls, == compares, 8 reads per freed tile): turns >= 86k WORSE (ambush 25 -> 54/43,
  big_world 26 -> 59/53). Microbenchmark on 100x100 (x65m): bitboard copy 480 (alloc ~280 + import 199), == 222,
  xor/and/not/shift ~390, is_empty 217, count 215, positions(n) ~450 + 45n, is_set 61, get 64, camp_tiles 384,
  champion_tiles 1007, compute_to minimum 2.9k (+~3.4 per visited tile), std::vector of 1250 B 1.7k. On 41x41 about half.
  => a reuse test that copies anything costs more than the field it saves on short searches, and the miss path is what
  heavy turns pay.
- v5 (no copies: s.blocked double-buffered by swap with a generation counter, goals keyed by object pointer, one shared
  wall diff per step_towards, lazy goal bbox): heavy turns no longer worse (ambush 25/25, starvation 7/7, big_world
  26/31) but not fewer; common turns +0.4-0.9k.
- v6 (chebyshev rings keyed by centre+radius from engage, cf, bank, group, fight, cassi: zero-cost compare): same
  picture (ambush 25/25, big_world 26/33, 77.5k: ambush 79/75, big_world 74/81).
Why it cannot land (x65q, miss reasons printed per turn on 6 heavy maps): of 87 turns >= 86k, 58 come from the camp
probe (goals = g.mask & ~probe_seen & ~s.blocked, a new mask each turn; keyable but see next), 11 from the bank ring,
11 from cf. Among keyed checks on printed (heavy/early) turns the dominant miss is "a tile that became a wall has
cached distance < D" (ambush 116 of ~170, big_world 328): a teammate stepping ahead of us in the group walk. Target
changes (key miss) are the next. Hits happen on quiet solo walks, which never reach 86k. Each failed check on a churn
turn costs == 222 + xor 394 + count 215 (+ positions and reads when listed) ~0.8-1.5k: exactly the turns at the
boundary pay it. Relaxing the rule to "only the tiles we read keep their distance" needs a chain of reads down to the
changed tile (50-100 gets = 3-6k) and a delicate proof: not worth it.

Also measured (x65q, same 6 maps): the exact skip of the hole search "no crossable hole within Chebyshev hole_bound of
the goal bbox" applies to 3% (ambush, fracture, islands), 6% (starvation), 22% (big_world), 38% (lanes) of the hole
searches and to 1/42, 0/13, 1/45, 0/12, 7/31, 2/3 of the heavy turns: not a lever. The hole route IS the behaviour on
ambush/starvation/fracture (reached and used on 56-82% of calls) and pure cost on big_world/lanes (reached 0/766,
0/168: ~11k per call for nothing) and islands (30/952).

Correction (integrator, 08:46 UTC): in b15 and everything above it fuel_ok() is a stub returning true (o07), so the
`fuel_ok(40000)` in front of the hole step decides nothing: the hole search always runs and its cost is deterministic.
The first-turn chaos on ambush/starvation/big_world is the total turn cost against 86k (overflow pushes actions to the
next round), not a fuel-read branch.

Lesson (fuelfit): an exact cache only pays if the MISS path costs ~0 and the misses are not the heavy turns. Here the
heavy turns are the misses by construction (group walks, new targets).

## First-turn forward field of choose_target: NOT reducible exactly on ambush/starvation (10-25 09:00 UTC, x65r bench build)

Per group on the first turn (r2/r3), Chebyshev distance vs walking distance, and the forward field's distance histogram,
14 far maps. A bounded search (max_distance B) reads the same as the full one only if (1) the P_CT_K = 12 nearest
groups are reached within B (their exact distances feed the K-cut and the scores) and (2) every unreached group is
provably beyond the cut: without a dash it is skipped either way; with a dash unreach() prices it 2*cheb+10, so
2*cheb+10 > cut is needed, else the fake value enters the scoring where the true one would not. s.target and the lead
group are scored beyond the cut and must be reached too. With n <= 12 groups there is no cut and every group needs its
true distance, unreachable ones included (which cannot be told from "beyond B" without the full search).
| map | n | unreachable | bound needed | area needed / full | B from 1.3*cheb+6 |
| ambush | 12 | 2 | 107 (all groups) | 6680 / 7542 | 100 (fails: unreachable groups) |
| starvation | 14 | 0 | 160-180 | 4387-5484 / 5667 | 85 (fails) |
| big_world | 24 | 4 | 83-88 | 4523 / 8780 | 72 (fails, close) |
| expanse | 24 | 0 | 63 | 3751 / 6134 | 78 (ok) |
| fracture | 28 | 2 | 78-89 | 1755 / 3386 | 55 (fails) |
| pilgrimage | 23 | 0 | 107-152 | 1685-2533 / 2583 | 48 (fails) |
| lanes | 42 | 0 | 37 | 1163 / 2597 | 54 (ok) |
Chebyshev underestimates the walking distance 1.5-2x on these maps (ambush: farthest group cheb 74, walking 107), so
the bound cannot be guessed; a short bound plus the full search costs more than today. big_world would save ~48% of
31k with the right bound, ambush 11%, starvation 3-22%: no exact lever on the three chaos maps. Not pursued.

## r8-r9 peak on 11 of 14 far maps (integrator's kidbg profile): the periodic re-choice

e64pf full-game profile, r6-r10 turns >= 60k: the dominant scope is choose_target (15 = 27-46k, forward field 23 =
13-30k) on ambush r8 (all five, 77-95k), starvation r8 (71-90k), big_world r9 (vendetta 86k), fracture r9 (62-66k),
road_of_riches r9 (68-71k), expanse r9, islands r9, concentrated_wealth r8. It is `refresh` in the farm step:
round - s.target_round >= P_E_RETARGET = 6 (the first choice is r2 on 12-14-group maps, r3 on the others), no fuel
involved. The champion has moved since r2, so the per-position cache misses and the reverse fields (o54: one static
field per cheap turn, 26k each on 100x100; farm_pd_done needs all 12-24) are not complete until ~r15-r27: the full
forward field is paid again. Exact ways out: none found. Two reverse fields per warm-up turn would put r3-r7 (60-75k
with the 22-26k warm-up field already inside) over 86k; a hybrid read (reverse fields where they exist, Chebyshev
bound for the rest) needs cheb > cut for every missing group, which the 1.5-2x gap defeats; the r2 forward field kept in
s.pdf is from another position (triangle bounds only). Non-exact option for the stall thread: defer the periodic
refresh until farm_pd_done (the re-choice then costs ~1.5k instead of 26-31k, but it happens at r15-r27 instead of
r8-r9: a decision change, judge by strength). The other half of those turns is the first step_towards to the new target
(goal field + hole field, 20-35k): the same two engine searches as on the first turn.

## o66_readout.py (over b15 + o59 + o63 + o64; 09:15 UTC): mask-free read-out, direct scans on big maps (EXACT)

(a) choose_target's read-out of the forward field (o41) tested the reached bit of every group tile before taking its
distance (24-51 groups x ~30 tiles: 8-13k, scope 25). The export holds 65535 on every unreached tile, larger than any
reached distance, so the reached mask export and the bit tests go: one min() per tile; -1 when the min is 65535.
(b) step_towards' dash scan (25 tiles) and tp-crystal scan (29 tiles) took three snapshots first (o42: s.blocked,
s.visited, s.df = 2.9k on 100x100, ~840 on 41x41). On maps of 4096+ tiles they now read directly: an unreached tile
reads 65535 and never beats bestd, so the reach test is implied; the wall test only for a tile that would win. Same
candidates in the same order, same best. Smaller maps keep the snapshots.
Profile e66p vs e64pf, r2-r12, common turns: ambush -578 per turn (first turn 113k -> 108k), big_world -796 (105k ->
101k), expanse -658, fracture -783, road -440, great_wall -386, others -30..-350. (The e66p profile build's scope 38
anchor did not match, so 38 is folded into 16/37 there; the totals are right.)
Exactness of o66 over b15 (b15+o59+o63+o64+o66; 09:45 UTC): far 56/56 and near 80/80 byte-identical replays.

## o67_rfdefer.py (over b15 + o59 + o63 + o64 (+ o66); 10:00 UTC): the periodic target refresh waits for the reverse fields (NOT EXACT)

Decision change, for the PC to judge by strength against b27. `refresh` (round - target_round >= P_E_RETARGET = 6) is
skipped while the reverse fields are not complete (farm_pd_done) and we are not on the tile the cached distances were
measured at, only on maps of P_RF_DEFER_AREA = 4096 tiles or more (near maps play exactly as before: the forward field
costs 4-14k there) and only while round < P_RF_DEFER_R = 60. A missing or expired target chooses at once, as before.
Profile e67p vs e64pf (14 far maps, r2-r40, unlimited fuel): choose_target turns >= 15k on r4-r12 per map 3-5 -> 0
(islands 1: an expired target); max turn r4-r12 ambush 95k -> 86k, starvation 90k -> 80k, big_world 91k -> 88k,
road 71k -> 62k, split 53k -> 41k, concentrated_wealth 67k -> 60k; turns >= 77.5k over r2-r40: ambush 27 -> 14,
starvation 16 -> 6, big_world 23 -> 16, others unchanged. Behaviour: the first periodic re-choice happens when the
reverse fields are complete (~r15-r27 on 12-24-group maps) and costs ~1.5k instead of 26-31k; until then the champion
keeps its first target unless it expires. Near 80 (must be byte-identical: the rule is off below 4096 tiles) and far 56
(strength vs rTop1/rD) running.
o67 runs (10:50 UTC, unlimited fuel, P_RF_DEFER_AREA = 4096): near 80 and far 56 vs b15: 132 of 136 replays
byte-identical, including both sides of ambush, big_world, starvation, expanse (far) and corners (near): the deferred
refresh confirms the target the r8-r9 refresh would have chosen, so only the fuel changes there. The 4 that differ are
the A side of fracture (61x71 = 4331 tiles, 28 groups): b15 won all four by ~1030-340 gems; e67 lost two (936-1199 vs
rD, 781-1070 vs rF) and won two narrowly. Keeping the first target ~30 rounds on fracture is a real loss, and its forward
field is only 15k. => P_RF_DEFER_AREA raised to 5000 (fracture excluded; 100x100 and 80x80 maps and corners kept).
With that default every game of this panel is byte-identical to b15 (far 56 re-run in progress to confirm): on this
panel o67 behaves as an exact piece; the PC's 800 games decide whether other big maps change.
o67 with P_RF_DEFER_AREA = 5000 (11:20 UTC): far 56/56 byte-identical to b15 (near 80 were identical already below the
threshold). On this panel o67 only removes fuel (r8-r9 re-choice field on ambush, big_world, starvation, expanse).

## o68_nohole.py (over b29; 10-25 12:30 UTC): the dash-hole shortcut (mapplan rule 5) off, or only when it does not split the group (NOT EXACT)

Why near fight maps lose (user: c19 b27 -41 gems/game on near maps; reverse_spiral -337, rushbait_v2 -228). Local, b27 vs
kvvl (bot/mgwp), 2 maps x rTop1/rD/rF/mV10d x 2 sides, normal fuel: reverse_spiral b27 0/8 (kvvl 7/8). Same target
(group 9) in both, but in b27 Heart of Ruin and Vesper die at r24-r27 in every game (17 deaths <= r100 over 8 games,
kvvl 0), so the camp is cleared at r100+ instead of r74: 7 gems / 0 gold at r100 over 8 games (kvvl 366 / 1528).
Per-round trace (status line every round): HoR and Vesper take the dash-hole shortcut (mp_dash_hole_step; HoR dash r7
(10,10)->(7,9), Vesper r9) through the middle, alone, next to the enemy spawn (spawn-to-spawn path 1), and the enemy
Marcella kills them; Marcella and Ryth walk the long way (y = 21) like all four of kvvl. kvvl never did this: the step is
behind fuel_ok(40000) and, as the stall thread then measured, kvvl's mp_find_dashholes gate (P_DHFUEL_NEED) said no
3699 times and yes 0 on 26 near maps, so kvvl had no dash holes at all; b15+ computes them in init (o06) and fuel_ok is
a stub. b27 with the step off (b27nh): reverse_spiral 7/8, 0 deaths <= r100, net gems +2238 (b27 -2770, kvvl +887);
rushbait_v2 7/8, +2859 (b27 +506, kvvl +642).
P_MP_HOLE: 0 = never (kvvl's behaviour everywhere, near and far: proposed as b31), 1 = as b29, 2 = only when no ally
without a dash (by name: ren, vesper, vendetta, heart) claims the same target group while we farm (dash_bits +
hole_splits_group, ~30 fuel per call). Panels running on b29 / b29h0 / b29h2: 6 losing maps (reverse_spiral,
rushbait_v2, fragment, hooks, contest, starfish) x 6 rivals x 2 sides, far 56, near 80.

## o68 panels (10-25, local, b29 = b28 + o66 + o67; h0 = P_MP_HOLE 0, h2 = P_MP_HOLE 2)

| panel | b29 | b29h0 | b29h2 |
|---|---|---|---|
| 6 losing near maps x 6 rivals x 2 sides (72) | 45 (+19984 gems, 83 deaths <= r100) | 53 (+28533, 48) | 49 (+24053) |
| far 56 (rTop1, rD, both sides) | 43 (+13822, 18) | 40 (+9764, 16) | 48 (+15546, 13) |
| near 80 (one game per map and rival) | 55 (+17615, 52) | 56 (+21853, 40) | 58 (+22201, 43) |
| sum (208) | 143 | 149 | 155 |

reverse_spiral in the 72: b29 0/12, h0 6/12, h2 4/12; contest/fragment/hooks identical (no dash champion uses a hole
there). h0 loses the far maps where the hole routes are real shortcuts (road_of_riches 3->1, shortcut 4->3, islands
3->2, concentrated_wealth 4->3). Recommended P_MP_HOLE 2 (integrator: b31 = h0, b32 = h2, b33 = h2 + small holes).

kvvl on the same near 80: 54/80 (+23271, 41 deaths). b29 vs kvvl: 33 outcome flips (+17 -16), no identical game
(different lineages). Near maps where b29h2 is still below kvvl (kvvl 2/2, h2 1/2): elkring (gems 330 vs 1320),
gem_fields (243 vs 905), gemfight (191 vs 1648; b29 2/2, an h2 regression), lost_world (647 vs 1797), rows (148 vs
1094), split (273 vs 680), stampede (480 vs 1280), starfish (30 vs 983), swirl (-39 vs 1927). Where h2 beats kvvl:
broken_curve, corridors, eight, expanse, fracture (kvvl 0/2), fragment, interlock, islands (kvvl 0/2), quadrants,
shortcut, pilgrimage. Results: farm container /tmp/claude-0/ff/ws/res/{kvvl,b29,b29h0,b29h2}_n80; table by
`python3 -I cmpbots.py "" kvvl_n80 b29_n80 b29h2_n80`.

## Gem macro: how the top 10 take gem-bearing elk groups (10-25, coordinator's request)

Data: 40 top-10 near-map games (analysis/top10-micro-1023/dec300, rounds <= 150) vs b29 and kvvl on the near 80
panel above (replays decoded with capkind_light.dump; scripts in the farm container /tmp/claude-0/ff/gem: capseq.py,
elkdetail.py, ebmetrics.py, openshape.py, perteam.py, trace.py). A capture = the group's captureTeam switching to us.

| per game, rounds <= 150 | top 10 (40) | b29 (80) | kvvl (80) |
|---|---|---|---|
| elk+gem captures by r50 / by r150 | 0.62 / 1.70 | 0.29 / 0.86 | 0.23 / 0.74 |
| own-side elk+gem groups available (>= 15 gems) | 2.92 | 2.60 | 2.60 |
| gold-cluster captures by r50 | 0.75 | 1.35 | 1.31 |
| first capture: round, champions within 4 | r22, 3 | r25, 2 | r26, 2 |
| first capture is a gold cluster | 10/40 | 47/80 | 43/80 |
| first three captures with 3+ champions / solo | 55% / 17% | 31% / 45% | 26% / - |
| champions within 5 of the nearest own-side elk+gem group at r10 | 1.31 | 0.80 | 0.72 |
| deaths <= r100 | 0.35 | 0.65 | 0.51 |

Elk+gem captures by the top 10 arrive with 3 champions (median; 57% with 3+), arrival spread 8 rounds, first approach
to capture 55 rounds (median; the opening ones r1 -> r12-r26). From r50 on our elk capture rate matches theirs
(0.57 vs 1.08 per game between r50 and r150, with the same number of champions). The whole gap is the opening: the
top 10 open with the team on one group (elk+gem when it is the nearest rich group, else wolf+gem or a gold cluster),
capture it at r12-r26 with 3-5 champions and then spread; we open with 5 solo gold clusters (median 1 champion) and
reach the first elk group at r48-r54. Per team (perteam.py): Fish, willow best girl, :3, Shingtonwash, Claudus,
policy wonk and procless all show first captures with 3-5 champions; Mite and Trzy Kwaterki open more spread.

### o69_teamopen.py (teamopen-v1; NOT exact, judge by strength)
Until round P_TO_R (40) the first alive ally in draft order leads: its choose_target values every group for the
whole team (the dormant `pack` hook: value not shared, clear time with the roster, no "needs company" discount); the
others take the leader's claimed group x P_GROUP_W (the existing ball code, groups > 8 tiles from the leader x 0.3)
and re-choose every 3 rounds. P_TO_NEAR 1 limits it to near maps (spawn-to-spawn path < P_PF_MAX). No fuel read;
followers' extra choose_target calls in r0-r40 cost fuel on 100x100 maps (the forward field) - measure on the PC.
Two test games (elkring, hooks vs rTop1): hooks first capture elk+gem r27 with 4 champions (b29: gold cluster r23
with 2, the elk group at r90); elkring both bots send the team to the altar-held group 20 tiles away (P_HOLD 200), the
rival contests it and o69's five fight there (2 deaths) while b29's four captured it at r30. Local panel (near 80 +
far 56 vs b29) running; results below when done.

### o69 teamopen-v1: local panel vs b29 (10-25 10:15 UTC)

| panel | b29 | b29 + o69 | flips |
|---|---|---|---|
| near 80 | 55/80 (+17615 gems, 52 deaths <= r100) | 61/80 (+25457, 56) | +13 -7 |
| far 56 | 43/56 (+13822, 18) | 47/56 (+16848, 33) | +10 -6 |
| total 136 | 98 | 108 | +23 -13 (bar 2*sqrt(36) = 12) |

Near maps gained: collision, elk_arena, elkring, gem_fields, great_wall, hooks, lost_world, pilgrimage, road_of_riches,
rows, starfish, starvation; lost: boss_battle, gemfight, gold_rush, islands, packs, shortcut. Far: ambush 1->3,
starvation 2->4, pilgrimage 2->3, islands/road/split 3->4; big_world 4->3 (12 deaths <= r100), concentrated_wealth
4->3, great_wall 3->2 (10 deaths), rows 3->2. Far deaths <= r100 double (18 -> 33): the team walks together into
contested middles on 100x100 maps. If the PC confirms the far loss, P_TO_NEAR 1 keeps far maps identical to b29.

Mechanism (ebmetrics/openshape on the same near 80; top 10 for reference):

| rounds <= 150 | top 10 | b29 | b29 + o69 |
|---|---|---|---|
| first capture: round, champions within 4 | r22, 3 | r25, 2 | r29, 3 |
| first three captures with 3+ champions / solo | 55% / 17% | 31% / 45% | 50% / 27% |
| first capture is elk+gem / gold cluster | 13 / 10 of 40 | 9 / 47 of 80 | 39 / 20 of 80 |
| elk+gem captures by r50 / r150 | 0.62 / 1.70 | 0.29 / 0.86 | 0.51 / 1.09 |
| gold-cluster captures by r50 | 0.75 | 1.35 | 0.79 |
| group gems captured <= r150 per game | 80.5 | 106.7 | 85.4 |
| deaths <= r100 per game | 0.35 | 0.65 | 0.70 |

The opening now has the top-10 shape (3 champions on the first group, elk first); early group gems drop (fewer solo
gold clusters) while the final gem margin rises (+25457 vs +17615 over 80 games); early deaths do not fall yet (the
team fights where it meets the rival). Package for the PC: /mnt/project-files/bundles/teamopen-v1-b29.zip (644d36e9,
b29 src + o69, P_TO 1 / P_TO_R 40 / P_TO_NEAR 0). Variants worth a PC run: P_TO_NEAR 1; P_TO_R 25.

### o69 v1 over b32 (10-25 11:00 UTC; local b29h2 = b32 up to the inert P_MP_HOLE_SMALL 0)

| panel | b32 | b32 + o69 v1 | flips |
|---|---|---|---|
| near 80 | 58/80 (+22201, 43 deaths <= r100) | 58/80 (+26645, 52) | +11 -11 |
| far 56 | 48/56 (+15546, 13) | 44/56 (+16002, 34) | +7 -11 |

Over the stronger base v1 is neutral on near maps and loses far maps (deaths <= r100 13 -> 34: big_world 12, great_wall
10, fracture/shortcut 4). Part of the gain seen over b29 was reverse_spiral-type games that o68 already fixes. Not a PC
candidate as is. Losses with v1 (gemfight, packs, gold_rush, trace.py): the leader's team valuation sends the whole team
to the rich centre group (gemfight 78 gems, 12 camps; packs 28; gold_rush) and two champions die there at r27-r45.
v2 = P_TO_OWN 1: the team valuation applies only to groups on our side (closer to our spawn by P_TO_OWN_D 2); the top
10's elk captures are own-side in 47 of 68. v2 panel over b32 running.

### o69 v2 (P_TO_OWN 1) over b32 (10-25 11:55 UTC) - line closed

| panel | b32 | b32 + o69 v2 | flips |
|---|---|---|---|
| near 80 | 58/80 (+22201, 43 deaths <= r100) | 59/80 (+27000, 42) | +13 -12 |
| far 56 | 48/56 (+15546, 13) | 42/56 (+14198, 35) | +7 -13 |

Own-side-only valuation removed the centre-group losses (gemfight, packs, gold_rush now even or won) but the near
panel stays neutral and the far panel loses the same games as v1 (big_world 12 deaths <= r100, great_wall 10,
concentrated_wealth 4->1, islands 4->2): on 100x100 maps the team arriving together does not stop the early deaths.
Over b29, b32 and 408 local games the opening ball moves the mechanism (first capture with 3 champions, elk first) but
not the result: neutral on near maps, negative on far maps. teamopen is NOT a PC candidate (P_TO_NEAR 1 would only be a
neutral near-only piece). The opening shape of the top 10 is therefore a correlate, not the lever; the deaths that
separate us (0.65-0.70 vs 0.35 per game by r100, 62-71% of them with an enemy within 3) are fight outcomes.

## b35 on the bench (10-25 11:30 UTC) and the r150-300 elk gap

b35 (= b32 + o74 start-up) near 80: 62/80 (+27328, 53 deaths <= r100) vs b32 58/80 and kvvl 54/80; far 56 identical to b32
(48/56, 56/56 same replays). Near maps where b35 is still behind kvvl (kvvl 2/2, b35 1/2): elkring, gem_fields, rows,
split, stampede, starfish. On all six b35 farms as much as or more than kvvl in r0-150 (same opening sequences, one round
later; elkring vs rD 6 captures / 132 gems vs 4 / 88); the losses are team fights (elkring: 4v4 clashes r44-58 on our side
vs the mirror) or decided after r150.

### Where the top 10 out-farm us: elk+gem groups in r150-300 (19 common maps, t10 40 games vs b32 38)

| | top 10 | b32 |
|---|---|---|
| captures r150-300 per game | 8.15 | 8.11 |
| of them elk+gem / wolf+gem / gem cluster / gold cluster | 2.27 / 2.80 / 0.90 / 2.17 | 1.11 / 3.24 / 1.66 / 2.11 |
| group gems r150-300 per game | 106 | 80 |
| group gems r0-300 per game | 187 | 146 |
| own-side elk+gem groups captured by r300 | 43% | 31% |
| elk episode (first approach -> capture): duration, champions involved, deaths | 23 rounds, 4, 0.05 | 25 rounds, 3, 0.05 |

Same number of captures, different mix: the top 10 go back to the elk groups (27 gems each), we take wolves (10) and gem
clusters (10-14). When we do go, the episode costs the same as theirs, so the gap is the choice. Scripts: gem/elk300.py,
episodes.py, calib.py, deathdetail.py (farm container).

### Cause: the cost model charges the group's full strength for the whole clear

choose_target: rounds = travel + hp/(dps x team) + 6 + (incoming / mhp) x cycle with incoming = str x t_clear / team and
team = max(1 + claimers, needed <= P_NEED_CAP 2). Debug print (b35, the_farm r167, Heart of Ruin choosing, dps 30, mhp
1000): a 2-elk group (4800 hp, 120 str, 30 gems) is charged 4800 incoming = 4.8 heal cycles -> 277 modelled rounds,
score 0.17; a 3-wolf group (2640 hp, 60 str, 29 gems) 85 rounds, 0.29; gem clusters 0.3-0.5. Measured on the replays (hp
of every participant from first approach to capture, b35 near 80, rounds <= 300): hp lost = 0.46 x (str x duration) for
elk groups (133 episodes) and 0.63 for wolf groups (343); top 10 0.34 / 0.47. Camps die one by one and monsters focus one
champion, so the full-strength charge is 2x reality, and the error grows with the group's strength: exactly the elk
groups. The per-champion dps model is right (measured solo camp damage per round: Marcella 45-50, Ryth 47-55, Vesper
55-90, Vendetta 70, Ren 35, Heart 34-38 median).

### o70_incoming.py (P_INC_PCT 50; NOT exact, judge by strength)
incoming x 0.5 in choose_target and the same factor in squad_needed (needed / too-strong). One parameter, no fuel read,
whole system (every monster group), biggest effect on elk groups. Expected mechanism: elk+gem captures r150-300 up from
1.1 towards 2.3 per game, group gems r300 up; watch deaths (the model now tolerates stronger groups). Panel vs b35 running.

### o70 (P_INC_PCT 50) over b35: local panel (10-25 12:50 UTC)

| panel | b35 | b35 + o70 | flips |
|---|---|---|---|
| near 80 | 62/80 (+27328, 53 deaths <= r100) | 60/80 (+27601, 37) | +8 -10 |
| far 56 | 48/56 (+15546, 13) | 48/56 (+16154, 25) | +7 -7 |

Mechanism (80 near games, replays): elk+gem captures r0-150 0.84 -> 1.05 per game (group gems 50 -> 67), r150-300 1.09
-> 1.31 (56 -> 67); gold clusters 4.33 -> 3.99 and 3.85 -> 3.60, gem clusters 0.96 -> 0.65; group gems r0-300 213 -> 234
(+10%); deaths <= r100 0.66 -> 0.46 per game on near maps (far 13 -> 25 in 56 games: road_of_riches 6, shortcut 5). Elk
episodes unchanged (26 rounds, 3 champions, 0.06 deaths). W/N neutral on both panels, net gems +1-4%. The mechanism moves
in the right direction but only a fifth of the way to the top 10 (2.27 elk captures r150-300). Package for the PC:
/mnt/project-files/bundles/incoming50-b35.zip. Variant P_INC_PCT 35 (the top-10 ratio) running.

### o70 variant P_INC_PCT 35 (10-25 13:35 UTC): near 63/80 (+27949, 56 deaths) vs b35 62; far 42/56 (+12258, 32 deaths) vs 48
(+7 -13; starvation 4/4 -> 0/4 with 7 deaths, concentrated_wealth 4 -> 2, rows 3 -> 2). Discarded: the lower charge sends
champions into groups they cannot finish on the sparse 100x100 maps. P_INC_PCT 50 also drops starvation (4 -> 1) while
winning ambush/expanse/great_wall/rows; it stays the only PC candidate of this line (zips/incoming50-b35.zip).

### o70 variant P_SHAREEXP 40 (10-25 11:05 UTC; the reward of a group is ONE pickup for one champion, so the value share
by team^0.75 was suspected of keeping champions off big groups): near 62/80 (+26394, 50 deaths) = b35; far 46/56
(+14529, 40 deaths: great_wall 13, starvation 7) vs 48. Elk+gem captures unchanged vs o70 (1.01 / 1.32 per game r0-150 /
r150-300), group gems r0-300 234 -> 207. The share exponent does not drive the elk choice; discarded.

### Why o70 loses starvation (11:15 UTC; far_b35 vs far_e70 statistics + replay camp map)
starvation (80x80): 22 gold clusters in pairs/triples, two monoliths (200 gems each) and ONE gem group: 4 elks + 4 gold + 4
gem clusters (240 strength, 9600 hp, 88 gems, 440 gold) with a 4-cluster gem group next to it. b35 4/4, b35 + o70 1/4.
Deaths per game: b35 2/7/8/9 (camp deaths 1/0/3/3), o70 21/29/15/25 (camp deaths 9/26/11/17), all after r300, 71 of them
within 5 tiles of the 4-elk group and its clusters, 16 at the monoliths. Mechanism: squad_needed caps needed at
P_NEED_CAP 2 even when no team of 5 could afford the group, and the cost model only PRICES the hp lost (heal cycles);
the inflated incoming kept such groups out of range, the calibrated one brings them back: two champions arrive, take
120 a round each (elk range 4, all four alive at the start) and die in 10 rounds, before the retreat rules act. The
P_INC_PCT 35 and P_SHAREEXP 40 variants lose starvation the same way (0/4 each).

### o78_feasible.py (P_TTD 20, P_FEAS_PCT 100; NOT exact; companion of o70, apply after it)
A group is an option for a team of t only if its full strength leaves each member >= P_TTD rounds to live
(mhp / (str / t)) or the clear is over first; needed grows to the smallest t that passes, and if the roster cannot, the
group is skipped (the existing needed > roster check). Monolith trips (mono_only) and the jackpot team keep their rules.
Examples (mhp 1200, dps 50): 4-elk group needs 4 (ttd 20), 3 elks 3, 2 elks or a golem 2, 1 elk or wolves 1.
Panel b35 + o70 + o78 (bots/e72): far 56 first (starvation), then near 80.

### o78 feasible-team gate: CLOSED (10-25 11:30 UTC; 136 + 136 games)
v1 (team grows until str / team is survivable): far 45/56 vs b35 48, 38 deaths <= r100 vs 13; 4-5 champions walked to the
4-elk group from r75 and died the same way (monsters focus one champion). v2 (skip a group whose full strength kills the
focused champion in < 10 rounds unless the roster clears it first): near 57/80 vs 62, far 44/56 vs 48 (islands 4/4 -> 1/4:
its gem groups are 3 elks, 180 strength, which b35 clears with 0 deaths by r300; starvation still 2/4). The premise is
wrong: 180-strength groups are routine, 240 is not, and a threshold between them is a per-map tuning with mhp 1000-1200.
o70 stays as offered (incoming50-b35.zip); its starvation loss is a trade the PC judge weighs. Script kept for the record.

### Measurement correction (11:40 UTC): the replay dump mixes group ids in ~5-9% of games
Checked captureTeam against the champions standing within 6 tiles at the capture: it matches in 96% of 2529 local captures
and 93% of 1101 top-10 captures, so the team attribution is right. But in 7/80 local games (quadrants, concentrated_wealth,
...) and 5/40 top-10 games the camp list of round 0 pairs an elk with clusters 13 tiles away, captures toggle group ids and
each toggle counted as a capture: those games inflated our gem counts (99 -> 61 gems r0-150 after excluding them). Tool
gem/cmpwin2.py excludes a game when < 80% of its captures have the capturing team present. CORRECTED TABLE (clean games,
captures per game, group gems per game):

| window | top 10 (35 g) | b35 (73 g) | b35 + o70 (72 g) |
|---|---|---|---|
| r0-150 | 7.66 caps, 81 gems; elk+gem 1.77 (1-elk 1.43), wolf 2.71, gold cl 2.06 | 8.33, 61; elk 0.75 (1-elk 0.51), wolf 1.96, gold cl 4.63 | 7.49, 50; elk 0.86 (0.68), wolf 1.94, gold cl 4.14 |
| r150-300 | 8.23, 107; elk 2.51 (1-elk 1.94), wolf 2.89, gold cl 1.89 | 9.30, 66; elk 0.88 (0.59), wolf 2.81, gold cl 4.08 | 8.68, 74; elk 1.19 (0.81), wolf 2.44, gold cl 3.90 |

So the gap is bigger than the earlier sheet said (group gems r0-300 188 vs 127), it sits in SINGLE-elk groups (60
strength: top 10 take 1.4-1.9 per game per window, we 0.5-0.8) and in time spent on gold-only clusters (4.1-4.6 per game
vs 2.0). o70 moves elk +15-35% but total group gems do not rise (124 vs 127): it trades clusters for elks. Nobody takes
180+ strength groups before r300 (top 10 0.03 per game).

### Why the single elk next to spawn is never taken (11:50 UTC; e70dbg = e70 + every choose_target candidate and pick printed)
the_farm vs rD, A side: 67 decisions in r20-300; in 39 of them a single-elk group (29 gems, 11-13 tiles) had a HIGHER raw
value/rounds than the pick, and in 32 of those the pick won only by its multiplier: x2 (P_HOLD, a group near the altar we
hold) x 1.25 (P_STICK hysteresis) = x2.5 on g16, a 2-wolf group with 8 gems and 120 gold. The team farms that 8-gem group
all game while the 29-gem elk 11 tiles away is never approached. elkring (all groups single elks): the same x2.5 just picks
the held elk, harmless. shortcut: both candidates 29-gem elks. Running e70dbg on the near 80 panel to count, over all
decisions, how many gems the pick gives up to the hold multiplier.

### Decision dump of b35 + o70 on the near 80 panel (12:00 UTC; e70dbg prints every choose_target candidate and pick; run
with --fuel-quantum 2000000 because the prints cost fuel: with normal fuel the instrumented bot won 47/80 instead of 60)
7604 decisions in r20-300 (gem/ctparse.py on the team stdout of each replay bundle):
- The hold-altar x2 (P_HOLD) is on the pick in 17% of decisions (1256; 305 of them groups under 15 gems). In 548 (7%,
  21/80 games: corridors, gem_fields, eight, the_farm, shortcut, yellow_brick_road, collision) a richer gem group (>= 15
  gems, <= 120 strength) had a higher raw value / rounds and lost to the multiplier alone: 27 gems difference per decision.
- A single-elk group (>= 15 gems) within 25 walking tiles exists in 2427 decisions; we pick it in 49%. In 989 the MODEL
  prefers the pick (median raw ratio elk / pick 0.67): 448 times a gold-only cluster (40 gold, 7 tiles, 21 rounds = 1.86 a
  round vs the elk's 29 gems + 90 gold in 79 rounds = 0.81), then 2-wolf (137), 1-wolf (124), other elk (106) groups. In
  240 the elk wins on raw and loses to a multiplier.
- Gold-only clusters are 30% of all picks (2317), flat over r0-300. gold_w = P_GOLD_W_EARLY / 100 = 1.0 before r600: 40
  gold counts as 40 gems. The top 10 take 2.0 gold-only clusters per game per window, we 4.1-4.6.

### o79_holdgems.py (P_HOLD_MIN 15; the hold x2 only for groups with >= 15 gems) over b35 (12:05 UTC)
near 63/80 (+25634, 45 deaths <= r100) vs b35 62/80 (+27328, 53): flips +3 -2, 58 identical games (the piece touches 22).
far 48/56 identical outcomes (11 games changed, same winners). Mechanism (clean games): elk+gem 0.75 -> 0.86 (r0-150) and
0.88 -> 0.97 (r150-300), gold clusters unchanged, group gems r0-150 61 -> 53, r150-300 66 -> 68. Small and safe; a rider,
not a candidate on its own. Variant without any hold bonus (P_HOLD_MIN 1000, bots/e79b) and o80 (gold weight 50 / 70 before
r600, bots/e80 / e80b) queued on the same panels.

### Ground truth from the statistics JSON (12:20 UTC; gem/goldcmp.py: team medians at r150 / r300, top-10 online near
summaries (40, their side) vs local near 80 (our side))

| bot | gold earned | gold spent | gems collected | monster damage done |
|---|---|---|---|---|
| top 10 | 562 / 1410 | 480 / 1250 | 65 / 159 | 12102 / 25392 |
| b35 | 496 / 1112 | 380 / 980 | 38 / 106 | 8010 / 15852 |
| b35 + o70 | 486 / 1144 | 360 / 1015 | 38 / 99 | 8409 / 17288 |
| b35 + o79 | 516 / 1139 | 380 / 995 | 42 / 107 | 8240 / 16881 |
| b35 + o79b (no hold bonus) | 557 / 1155 | 380 / 1005 | 42 / 110 | 9309 / 20008 |

The top 10 deal 50-60% more monster damage in the same rounds, earn 13-27% more gold and collect 50-70% more gems: it is
THROUGHPUT (time on monsters), not only which group. Our picks are 30% gold-only clusters (120 hp: no damage, a trip of
~20 rounds each) -> 2.5 more trips per champion per 150 rounds than the top 10. Different opponents (they play ranked
bands ~40, we play our own older bots), so absolute numbers are indicative; monster damage depends mostly on us.

### o79b (P_HOLD_MIN 1000 = no hold-altar bonus) over b35 (12:20 UTC)
near 63/80 (+8 -7, 46 identical) vs 62; far 49/56 (+1 -0) vs 48. Mechanism (clean games): captures 8.33 -> 8.97 (r0-150)
and 9.30 -> 9.78; elk+gem 0.75 -> 0.85 and 0.88 -> 1.12; gold clusters unchanged; group gems r0-300 127 -> 132; gold
earned r150 496 -> 557 (top 10 562), monster damage +16% / +26%. Bigger than o79 and still safe; the hold bonus is the
closed territory line and removing it only helps. Candidate rider / small piece. o80 (gold weight 50 / 70) running next.

### o80_goldw.py over b35: CLOSED (12:50 UTC; 136 + 136 games)
P_GOLD_W_EARLY 50: near 54/80 (+7 -15) vs 62, far 46/56 vs 48. 70: near 60/80 (+5 -7), far 45/56. Ground truth unchanged:
gold earned r150 496 -> 496 / 500, gems collected r150 38 -> 40 / 42, monster damage r150 8010 -> 7436 / 7980. Halving the
gold weight does not cut the gold-cluster trips nor raise gem income: at 7 tiles a 40-gold cluster still scores 0.95 a
round (50%) against the single elk's 0.81, and the lost gold weakens the shop. The elk's modelled cost (79 rounds solo, 44
as a pair with the value shared) is what keeps it out, and the top 10 take it with 3-4 champions from r30. Line closed:
the next step is to decompose the throughput gap (rounds in contact with monsters vs damage per contact round) before
touching the model again.

### Time budget per champion, r1-300 (13:00 UTC; gem/contact.py on replays + statistics JSON; top 10 = 40 online near
games, b35 / o79b = near 80 panel; "near" = within 4 tiles of an awake monster, "contact" = within 2)

| | alive champion-rounds/game | contact | at 3-4 | cluster | altar | moving | idle | monster dmg r300 (mean) | dmg per near round |
|---|---|---|---|---|---|---|---|---|---|
| top 10 | 1205 | 0.19 | 0.16 | 0.04 | 0.02 | 0.42 | 0.17 | 26726 | 63.8 |
| b35 | 1252 | 0.17 | 0.09 | 0.04 | 0.02 | 0.51 | 0.17 | 19198 | 58.6 |
| b35 + o79b | 1255 | 0.17 | 0.09 | 0.03 | 0.02 | 0.51 | 0.17 | 20928 | 62.7 |

Rounds near a monster per game: top 10 419, us 328 (+28%); damage per near round +9%; together the +39% monster damage.
The top 10 stand at distance 3-4 of monsters almost twice as often (ranged champions and extra members at the same
group) and walk 9 points less of their time. The farm gap is champions standing at the SAME group (present at capture
median 3 vs our 2), not the damage each deals when there. This is the same mechanism the buddy thread measures from the
walking side (paired walking 37-39% vs 55%).

### o81_stack.py (P_STACK_HP 0; variant + P_SHAREEXP 50) over b35
choose_target splits a group's value evenly (value / team) below P_STACK_HP 3000 hp and by team^0.75 above (study27).
A third champion joining a 2640-hp single-elk group sees a third of it. o81 makes the stacking exponent apply to every
monster group (and the variant lowers it to 0.50). Expected: more champions per capture, more rounds near monsters, less
walking, fewer separate cluster trips; watch deaths and far maps. Panels (bots/e81, e81b) launched 12:05 UTC.

### o81 v1 (P_STACK_HP 0: stacking exponent for every group, clusters included) over b35 (13:10 UTC)
0.75: near 61/80 (+8 -9) vs 62, far 49/56 (+3 -2) vs 48; income flat (gold r150 500, gems 36, monster dmg r300 17297).
0.50: near 53/80 (+7 -16), far 41/56 (+5 -12): gems collected r150 44 (highest so far) and monster damage +14%, but
champions also stacked on 120-hp clusters and the full-game net gems fell (17641 vs 27328). Confounded; v2 = exponent for
monster groups only (g.str > 0), clusters keep the even split (bots/e81c 0.75, e81d 0.50), launched 12:16 UTC.
Trios (buddy thread's form.py, g3 = share of rounds with 3+ allies within 3): top 10 39.7 / 29.7 / 26.1% in r30-90 / 90-150 /
150-300, b35 30.4 / 19.0 / 15.0, b35 + o79b 29.0 / 15.9 / 14.5 (o79b does not form trios; it just roams better).

### o81 stacking: CLOSED (13:40 UTC; 4 variants, 544 games)
v2 (exponent for monster groups only) = v1 to the game: 0.75 near 59/80 vs 62, far 49/56 vs 48; 0.50 near 54/80, far 40/56.
Mechanism of 0.50 (either version): trios g3 41 / 31 / 22% = top-10 level (40 / 30 / 26), paired 51 / 44 / 39% (top 10 58 /
54 / 47), gems collected r150 44 (b35 38, top 10 65), monster damage r300 +15%; BUT rounds within 4 of a monster unchanged
(329 vs 328 per game; top 10 419) and the far maps collapse (40/56). Champions walk together and stand together, not
at monsters longer; the top 10's trios are trios AT camps. The share exponent is not the lever, and trio formation by
itself does not win (useful for the buddy thread: forming trios with a value split reproduces the top-10 formation
numbers and loses). Line closed; the remaining question for the farm front is why our team is near monsters 91 fewer
champion-rounds per game with the same contact share: fewer simultaneous members per camp (3-4 vs 2) AND less
range-3-4 presence (16% vs 9%: the top 10 keep ranged champions and extra members at distance 3-4 of the camp).

### Method (user 12:10 UTC via coordinator): the judge is online (each candidate alone on 15 pinned groups, ~3 an hour);
local panels are prediction only; the one local requirement is beating kvvl head-to-head (ws/h2h.sh NAME, 26 near maps x
2 sides). b35 loses online near maps (-4 vs kvvl, fight-camp deaths); the stall thread is isolating the piece. Running h2h
vs kvvl for b35, o79b, o81 v2, o70 to know which candidates pass the local gate.

### Head-to-head vs kvvl (ws/h2h.sh: 26 near maps x 2 sides, 13:40 UTC)
| bot | W/52 | net gems | deaths <= r100 |
|---|---|---|---|
| b35 | 34 | +15102 | 46 |
| b35 + o70 incoming50 | 35 | +10013 | 39 |
| b35 + o79b nohold | 31 | +9507 | 43 |
| b35 + o81 v2 0.75 | 29 | +6217 | 52 |
| b35 + o81 v2 0.50 | 31 | +8196 | 46 |
All pass the local gate (> 26) but only o70 is at the base's level; nohold is 3 below b35 here while +1 on the rival
panel: at this size (52 games) a 3-game difference is noise, and b35 itself wins 34/52 locally while losing -4 online, so
the head-to-head is a weak predictor too. Candidates for online over the next base: incoming50 first, nohold second.

### Who stands at the same monster group (13:45 UTC; gem/contact.py, group-rounds per game with 1/2/3/4+ own champions
within 4 of an awake monster of that group, r1-300)
top 10 116 / 63 / 32 / 22; b35 98 / 65 / 29 / 12. The top 10 engage more groups solo (+18%) AND with 4+ (x1.8); pairs and
trios equal. Their 4+ engagements are on WEAK groups (total strength <= 60, a single elk or wolf): 8.0 / 4.8 / 6.4
group-rounds per game in r0-50 / 50-150 / 150-300 vs our 5.2 / 2.0 / 2.1; on 61-120 and 121+ groups both sides stay under
1.5. They sweep weak groups with the whole team all game; we do it only in the opening. o81 stacked on every monster
group (including 2-3 elk groups) and lost the far maps.

### o82_sweep.py (P_SWEEP_STR 60, P_SWEEP_R 50) over b35: a weak monster group (0 < str <= 60, hp < 3000) is not value-split
among the champions heading there from r50; everything else as b35. Panels near 80 + far 56 + h2h vs kvvl launched 12:45 UTC.

### o82 sweep: CLOSED (10-27; 188 games)
near 56/80 (+8 -14) vs 62, far 37/56 (+2 -13) vs 48, head-to-head vs kvvl 35/52 (b35 34). Not splitting weak groups'
value sends the team together after single elks and wolves and loses the far maps badly, like o81. Every way of making
our champions stack (o69 teamopen, o81 share exponent, o82 sweep) reproduces the top 10's formation numbers and loses:
in this bot "together" means walking together to one group while the rest of the map stays unfarmed; the top 10 clear
weak groups in 8-10 rounds and are already elsewhere. Line closed on the farm side; what remains measured and unexplained
is the +28% champion-rounds near monsters, and the local candidates that survive are incoming50 (o70) and nohold (o79b).

### CORRECTION with the fresh top-10 vs top-10 sample (10-27 14:40 UTC; 40 near games of 10-25, both sides = 80, from the
"stats anticuadas" thread: /mnt/project-files/analysis/top10-fresh-1025/, decodes dec300_1025.tgz; gem/fresh.py)
The 10-24 reference (top 10 vs ranks 30-60) overstated the throughput gap: against weak rivals the top 10 farm freely.
Among themselves:

| metric (per side, r1-300 or at r150 / r300) | top 10 vs top 10 | b35 (near 80) |
|---|---|---|
| gold earned r150 / r300 | 496 / 1330 | 496 / 1112 |
| gems collected r150 / r300 | 80 / 184 | 38 / 106 |
| monster damage r150 / r300 | 11038 / 22662 | 8010 / 15852 |
| rounds within 4 of a monster per game | 361 | 328 |
| damage per such round | 68.0 | 58.6 |
| engaged group-rounds with 1 / 2 / 3 / 4+ members | 94 / 59 / 30 / 16 | 98 / 65 / 29 / 12 |
| time moving / idle | 0.45 / 0.19 | 0.51 / 0.17 |
| captures r0-150: gem clusters / gold-only clusters / elk+gem / wolf+gem | 3.06 (34g) / 2.11 / 1.74 (69g) / 1.57 (19g) | 0.99 (14g) / 4.63 / 0.75 (19g) / 1.96 (18g) |
| captures r150-300 | 3.15 (42g) / 2.11 / 2.04 (97g) / 1.80 (20g) | 1.53 (19g) / 4.08 / 0.88 (23g) / 2.81 (25g) |
| group gems r0-150 / r150-300 | 123 / 160 | 61 / 66 |

So: same gold, same time budget, same team structure (members per engaged group equal, trios equal), only +10% rounds
near monsters and +16% damage per round. The gap is WHAT they kill: 3x the gem clusters, 2.3x the elk groups, half the
gold-only clusters; gems from groups 283 vs 127 per 300 rounds. Everything I said about throughput and trios on 10-25 was
measured against the vs-band sample and does not hold among the top 10; the choice line (elk and gem-cluster groups over
gold-only clusters) is the farm front, and the local judge cannot see it: our rivals farm like us, so a bot that trades
gold for gems looks neutral or worse locally (o80 at gold weight 50 / 70: gems r150 40 / 42, W/N down). Testing gold
weight 30 (bots/e83) for the mechanism (gems r150, capture mix) and the kvvl head-to-head gate, as an ONLINE candidate.

## e83 = b35 + P_GOLD_W_EARLY 30 (o80_goldw.py SRCDIR 30) — 10-27 14:45 UTC — first piece that moves the gem mechanism

Dose-response of the gold weight before r600 (near 80, same manifest; collectedGems medians from the statistics JSON):

| gold weight | gems r150 | gems r300 | near W/N | deaths<=100 | far W/N | h2h vs kvvl |
|---|---|---|---|---|---|---|
| 100 (b35) | 38 | 106 | 62/80 | 53 | 48/56 | 34/52 |
| 70 (e80b) | 42 | 101 | closed | | | |
| 50 (e80) | 40 | 102 | 54/80 | 47 | | |
| 30 (e83) | 50 | 113 | 56/80 | 44 | 48/56 | 35/52 |

Capture mix r0-150 per game (73 clean games), target = top 10 vs top 10:

| | gold-only clusters | gem clusters | elk+gems | wolf+gems | gems/game |
|---|---|---|---|---|---|
| b35 | 4.63 | 0.99 (14g) | 0.75 (19g) | 1.96 (18g) | 61 |
| e83 | 3.74 | 1.77 (24g) | 0.90 (25g) | 1.75 (23g) | 72 |
| top 10 | 2.11 | 3.06 (34g) | 1.74 (69g) | 1.57 (19g) | 123 |

- Earned gold r150 unchanged (499 vs 496), r300 +4%; monster damage r300 +8%; deaths<=r100 44 vs 53.
- Near W/N drops 62 -> 56 against our own lineage (the local judge cannot price a gold->gem trade, as predicted). Far identical. h2h gate passed (35/52 > 26).
- The jump is non-linear: 70 and 50 did nothing, 30 moves gem clusters +0.8/game and halves the gold-only surplus. Half of the gap remains (gem clusters 1.77 vs 3.06, elks 0.90 vs 1.74) -> e84 = weight 15 running (near + far + h2h).
- Online candidate: zips/gold30-b35.zip (sha in SHA256SUMS). Not sent: user paused sends 10-25 12:50 UTC.

## e84 = b35 + P_GOLD_W_EARLY 15 — CLOSED 10-27 14:51 UTC (gold starvation: the cliff lies between 30 and 15)

| gold weight | gems r150/r300 | gold r300 | near W/N | deaths<=100 | far W/N | h2h vs kvvl | gold-only / gem clusters / elks r0-150 |
|---|---|---|---|---|---|---|---|
| 100 (b35) | 38/106 | 1112 | 62/80 | 53 | 48/56 | 34/52 | 4.63 / 0.99 / 0.75 |
| 30 (e83) | 50/113 | 1154 | 56/80 | 44 | 48/56 | 35/52 | 3.74 / 1.77 / 0.90 |
| 15 (e84) | 57/122 | 1017 | 58/80 | 35 | 43/56 | 20/52 | 3.10 / 1.64 / 0.96 |

- 15 keeps raising gems and cutting early deaths, but gold r300 falls 12%, far maps drop 5 and the kvvl gate fails (20/52): the shop runs dry. 30 stays the candidate; no finer sweep (the user wants mechanisms, not parameter fits).
- The elk side of the gap (0.90-0.96 vs 1.74) is not a gold-weight matter: the single elk loses to the hold x2 and the strength terms (see "why the single elk is never taken"). Next: e85 = e83 + nohold (o79_holdgems.py with P_HOLD_MIN 1000), the two surviving farm pieces as one candidate (small pieces ride together).

## e85 = b35 + gold weight 30 + no hold-altar x2 (o80_goldw.py SRCDIR 30; o79_holdgems.py then P_HOLD_MIN 1000) — 10-27 15:00 UTC — NEW CANDIDATE

| bot | gems r150/r300 | gold r150/r300 | monster dmg r150/r300 | near W/N | deaths<=100 | far W/N | h2h vs kvvl |
|---|---|---|---|---|---|---|---|
| b35 | 38/106 | 496/1112 | 8010/15852 | 62/80 | 53 | 48/56 | 34/52 |
| e83 gold30 | 50/113 | 499/1154 | 8091/17167 | 56/80 | 44 | 48/56 | 35/52 |
| e79b nohold | n/a | 557/- | +16/+26% | 63/80 | 54 | 49/56 | 31/52 |
| e85 both | 55/128 | 520/1172 | 9717/20244 | 57/80 | 43 | 48/56 | 40/52 |
| top 10 vs top 10 | 80/184 | 496/1330 | 11038/22662 | | | | |

Capture mix per game (73 clean): r0-150 gold-only 3.96 / gem clusters 1.88 (22g) / elk+gems 0.97 (33g) / wolf+gems 1.96, gems 77 (b35 61, e83 72, top 10 123); r150-300 elk+gems 1.25 (57g), gems 102 (b35 66, top 10 160).
- The two pieces add up: gems, gold and monster damage all rise together (monster damage closes 60% of the gap to the top 10), early deaths fall, far maps unchanged, and the kvvl head-to-head is the best of the thread (40/52). Near W/N against our own lineage stays below b35 (57 vs 62), as with every gold->gem trade.
- Online candidate: zips/gold30nohold-b35.zip (sha in SHA256SUMS). Replaces gold30-b35.zip as the first choice. Not sent (user paused sends).
- Remaining gap: elks 0.97 vs 1.74 and gem clusters 1.88 vs 3.06, gold-only clusters 3.96 vs 2.11. Next: e86 = e85 + incoming50 (o70, the third surviving piece: +elk choice, fewer starvation deaths) as one combined candidate.

## e86 = e85 + incoming50 (o70_incoming.py) — CLOSED 10-27 15:05 UTC: elks up, but early deaths and the kvvl gate pay for it

| bot | gems r150/r300 | gold r150/r300 | monster dmg r150/r300 | near W/N | deaths<=100 | far W/N | h2h vs kvvl | elk+gems r0-150 / r150-300 |
|---|---|---|---|---|---|---|---|---|
| e85 | 55/128 | 520/1172 | 9717/20244 | 57/80 | 43 | 48/56 | 40/52 | 0.97 / 1.25 |
| e70 (incoming50 alone) | n/a | | | 60/80 | 37 | 48/56 | 35/52 | 0.86 / 1.19 |
| e86 | 56/136 | 478/1144 | 10202/21822 | 55/80 | 55 | 47/56 | 27/52 | 1.01 / 1.66 |

- incoming50 on top of gold30+nohold does buy the elks (single elk r150-300 1.03/game, top 10 1.46) and monster damage reaches 92-96% of the top 10, but gold r150 drops 8%, deaths<=r100 rise 43 -> 55 and the head-to-head falls to 27/52 (gate barely passed, 13 games below e85). The three pieces together over-commit lone champions to strength groups.
- e85 stays the candidate. incoming50 remains a known separate piece, not combined.
- Remaining gap in e85: gem clusters 1.88 vs 3.06 and gold-only clusters 3.96 vs 2.11 (r0-150). Next: decision dump on e85 (instrumented build, --fuel-quantum 2000000) to see what gem clusters lose to now that gold is weighted 0.3.

## ENGINE 2.0.0 (site since 10-26; cambc 4.0.0) — e85 reproduced on the 40 old maps — 10-27 15:30 UTC (PROVISIONAL: 30 new maps running)

Setup: `pip install cambc==4.0.0` in a separate venv (/tmp/claude-0/ff/cv4), `cambc init --yes` workspace /tmp/claude-0/ff/ws4, maps from branch claude/project-thread-l6gm1j handoff/maps2/ (70 .map26a: the 40 old ones unchanged byte for byte + 30 new, 6 of them 3-champion maps), replay decoder handoff/replay2/dump2.py (ebmetrics falls back to it). b35, e85, kvvl and the 6 rivals compile and play unchanged with the 2.0.0 SDK. Camp group rewards are identical between engines (checked on split).

| engine | bot | gems r150/r300 | gold r150/r300 | monster dmg r150/r300 | near W/N | deaths<=100 | far W/N | h2h vs kvvl |
|---|---|---|---|---|---|---|---|---|
| 1.0.3 | b35 | 38/106 | 496/1112 | 8010/15852 | 62/80 | 53 | 48/56 | 34/52 |
| 1.0.3 | e85 | 55/128 | 520/1172 | 9717/20244 | 57/80 | 43 | 48/56 | 40/52 |
| 2.0.0 | b35 | 38/84 | 519/1135 | 8242/16685 | 55/80 | 50 | 48/56 | 30/52 |
| 2.0.0 | e85 | 52/112 | 485/1126 | 10190/19027 | 60/80 | 41 | 50/56 | 28/52 |

Capture mix r0-150 per game (2.0.0, 73-74 clean): b35 gold-only 4.23 / gem clusters 0.90 (12g) / elk+gems 0.74 (30g) / wolf+gems 1.92, gems 61; e85 3.92 / 1.57 (18g) / 0.97 (39g) / 2.12, gems 76.
- The mechanism survives the patch: gems r150 +14, gem clusters +0.67/game, elks +0.23, monster damage +24%, early deaths 50 -> 41. Near W/N now favours e85 (+15 -10), far +2. Gold r150 -7% (was +5% on 1.0.3).
- Head-to-head vs kvvl (both rebuilt with the 2.0.0 SDK): 28/52 vs b35 30/52 — gate passed by 2, no longer the clear win of 1.0.3. The 2.0.0 nerfs (Vesper/Marcella/HoR/Ryth) change fights; the farm gain is unchanged.
- gold30nohold-b35.zip is source-only, so it is the same candidate under 2.0.0. Still not sent (user paused sends).
- The PC's go45/E1 (c95shop + gold 0.45 to r150 + no hold x2 in the opening (+ incoming x0.5)) is the same direction on another base; E1 was the best on the top-5 compass (11-114 vs kvvl 5-120). Not duplicated: e85 removes the hold x2 for the whole game and weights gold 0.3 to r600.

## ENGINE 2.0.0 — the 30 NEW maps (19 near / 11 far by spawn path; 6 are 3-champion maps) — 10-27 15:45 UTC

b35 and e85 vs rTop1 + rD both sides (120 games each) and vs kvvl both sides (60 each). All bots rebuilt with the 2.0.0 SDK.

| | b35 | e85 |
|---|---|---|
| vs rTop1/rD, 30 new maps | 78/120 (net gems 12183) | 82/120 (19698); flips +16 -12 |
| of which near / far | 44/76 / 34/44 | 49/76 / 33/44 |
| of which 3-champion maps / 4-5 | 15/24 / 63/96 | 17/24 / 65/96 |
| h2h vs kvvl, 30 new maps | 35/60 | 33/60 (near 22 vs 20, far 13 vs 13) |
| gems collected r150/r300 | 52/158 | 76/182 |
| gold earned r150/r300 | 406/822 | 352/769 |
| monster dmg r150/r300 | 6318/13863 | 6590/14178 |
| deaths<=r100 | 68 | 67 |
| captures r0-150 /game: gem clusters / gold-only / elk+gems / wolf+gems | 3.52 (67g) / 2.44 / 0.31 / 2.97 | 4.22 (81g) / 1.92 / 0.43 / 2.43 |

Whole 2.0.0 pool (70 maps): vs our rivals e85 142/200 near-type vs b35 133/200, far 50 vs 48 (old far maps); h2h vs kvvl 61/112 vs b35 65/112 (both above half; e85 is not better than b35 at beating kvvl under 2.0.0, it was 40 vs 34 under 1.0.3).
- The new maps are gem-rich and elk-poor (b35 already captures 3.5 gem clusters/game, 0.3 elks): e85 adds +24 gems at r150 there too, but gold r150 falls 13% (fewer gold-only clusters, nothing else to farm). Under 1.0.3 gold went up with e85 (nohold), under 2.0.0 it goes down on both map sets.
- Decision: e85 (gold30nohold-b35.zip, sha 48095c56…) stays the farm candidate for the online loop; its gain is the gem mechanism, its cost is gold (-7% old maps, -13% new maps at r150) and no head-to-head edge over b35 vs kvvl under 2.0.0. Online decides; nothing sent (user paused sends 10-25).
- Bench scripts for 2.0.0: /tmp/claude-0/ff/ws4 (mk.sh/far.sh/h2h.sh use ../cv4/bin/cambc; run_new30.sh builds the new-map manifests; plan30.txt classifies the new maps from the bot's [mapplan] line: ts, altars, size, spawn path).

## Map features in the 2.0.0 pool: enclosed altars — o87 "breach" (opts/o87_breach.py) — 10-27 16:05 UTC — PARKED
Three of the 30 new maps have every altar enclosed by camps: 01boss_battle and 02guardians (altar (20,20), monoliths at (19,20)/(21,20),
the other neighbours walls/holes; P_SEALED already handles them, we win both vs rD but die 33/game vs 13 and often submit 0) and
02the_pack (altar (22,22) in a free pocket inside a ring of 48 wolves = one camp group). On the_pack our whole lineage never submits in
2000 rounds (8/8 games): the bank route finds no reachable ring tile, br_decisions grows, champions freeze at distance 4 from r~500.
Rivals (rD/rTop1/kvvl) submit 0 there too; the game is decided by the tiebreak.
- o87 v1 (static map test "every ok altar unreachable with camps as walls, some ring tile not a camp" -> pick a gate = camp tile adjacent
  to the reached region minimising dist-to-altar; force s.target to the gate's group; fight-camp attacks only the gate camp):
  e87 (= e85 + o87) vs rD/rTop1/kvvl both sides: pocket opens r117-191, we submit 508-862 gems (was 0) BUT the rival walks through our
  hole and submits 631-1039; we win 2/6; our deaths 12-15 (was 1-2). Death list: every early death has 9-14 awake wolves within 3 and
  the nearest enemy 7-18 tiles away -> the ring kills us (hitpass P_HITLAST=1 in b35 hits any camp in reach, and standing in the
  pocket wakes the neighbours), not the rival.
- o87 v2 (gate cost adds 300 per camp within 3 of the gate; admission strength adds the gate's neighbours within 3; re-close detection):
  the admission never passes -> the pocket never opens (0 opens in 5/6 games, r1866 in the sixth); deaths unchanged (5-24). Worse.
- Verdict: 1 map of 70, no rival exploits it either, and the honest fix (open late with the whole team carrying gems, deliver in one
  trip, hold the hole) is a new mechanism. PARKED; E1 (P_HITLAST 0) at least does not wake the ring with finishing blows. Not in any zip.
- adgato_gemcombat maps (gem clusters only): gemcombat5 lost 0/4 by deaths -> fight thread's problem, not farm.

## New base E1 (PC base, branch claude/pc-e1-assets pcassets/zips/e1.zip sha f967edfe…) — 10-27 16:10 UTC
Coordinator 16:02 UTC: build farm pieces on E1 from now on, compare with E1 and kvvl on 2.0.0. E1 = b35 + P_HITLAST 0 (no hitpass)
+ o95 cut (Vendetta/Marcella leave a contact at <40% hp) + o100 incoming x0.5 + o129 gold weight 0.45 UNTIL r150 (P_GWO/P_GWO_R)
+ o125 hold-altar x2 only FROM r150 (P_HOLD_FROM). So E1 already carries the e85 mechanism for the opening only; what e85 adds over E1
is the same rule for r150-600 (gold 0.30 all early game, no hold at all). Bench bots ws4/bots/e1, e1foco built with cambc 4.0.0.
E1 baseline running (run_e1.sh: 40 old maps near/far/h2h + 30 new maps vs rTop1,rD + h2h kvvl = 368 games).

## E1 baseline on 2.0.0 and the e85 rule on E1 — 10-27 16:30 UTC
Protocol per bot (run_var.sh, 368 games, deterministic): "n80" = the 40 old maps x 2 sides vs a rotating rival (rTop1/rD/rF/rHunt/
mV19/mV10d; NOTE mk.sh's FAR filter never matched, so this set contains the 14 far maps too), far = 14 far maps x rTop1,rD x 2 (56),
h2h = kvvl on the 26 old near maps x 2 (52), new30 = the 30 new maps x rTop1,rD x 2 (120), h2hnew = kvvl on the 30 new maps x 2 (60).

| bot | n80 | far | h2h kvvl old | new30 | h2h kvvl new | total | gems r150 old/new | gold r150 old/new |
|---|---|---|---|---|---|---|---|---|
| b35 | 55/80 | 48/56 | 30/52 | 78/120 | 35/60 | 246/368 | 38 / 52 | 519 / 406 |
| e85 (gold30+nohold on b35) | 60 | 50 | 28 | 82 | 33 | 253 | 52 / 76 | 485 / 352 |
| E1 (PC base) | 68 | 42 | 35 | 86 | 44 | 275 | 45 / 84 | 517 / 399 |
| e88 = E1 + gold 0.45 until r600 | = E1 everywhere: b35 already weighs gold 0.45 from r150 (P_RC2_GW), E1 adds the opening only |
| e89 = E1 + no hold-altar x2 ever | 66 | 41 | 30 | 86 | 41 | 264 | 45 / 84 | — CLOSED (h2h) |
| e91 = E1 + gold 0.30 opening + no hold (the e85 rule) | 60 | 44 | 37 | 84 | 36 | 261 | 60 / 76 | 479 / 350 — CLOSED |
| **e92 = E1 + o92 farguard** | 65 | **50** | 35 | **90** | 45 | **285** | 42 / 70 | 522 / 416 |

- E1 beats b35 everywhere except the far maps (42/56 vs 48): rows 0/4, islands 2/4, starvation 2/4, concentrated_wealth 1/4, with
  the same economy to r300 as e85 (rows: gems 131, gold 1585, monster dmg 37910). On rows the game is decided by a ~570-gem jackpot
  around r1050-1200: e85 takes it (collected 656 -> 1240), E1 fights it (monster dmg keeps growing) and the rival captures it
  (rival collected 459 -> 1024), E1 dies 3 times r900-1050.
- Bisect of E1 on the far set (one piece reverted each): cut o95 off 44/56; incoming 100 (o100 off) **49/56**; gold opening 1.0
  (o129 off) **49/56**; hold from r0 40/56; hitpass on 42 (hitpass is already off on far maps via P_HITLAST_FAR). So the two
  opening pieces that make E1 strong on near maps are what loses the far maps: with incoming x0.5 and gold 0.45 the champions
  commit to bigger / gem-bearing groups early on maps where the walk is long and the gold shop lags.
- o92 farguard (opts/o92_farguard.py SRCDIR): on far maps — the bot's existing hp_far flag, spawn walk >= P_HITLAST_FAR 60 from the
  draft byte 29 — o100 and o129 revert to the b35 values (P_FAR_INC 100, P_FAR_GWO 100). Near maps are identical to E1 by
  construction (every path<60 map in n80 reproduces E1 exactly). Far set 50/56 (+8), new30 90/120 (+4: dunes 1->4, ribs 2->4,
  famine 4->2), n80 far maps -3 (great_wall, islands, road_of_riches down; concentrated_wealth, lanes up), h2h kvvl 35/52 and 45/60.
  Net +10 over E1 on 368 games, all of it on long-walk maps. The marker line is "[fuelfit] ... o129_goldopen45 o92_farguard".
- ZIP for the PC loop: zips/e1-o92farguard.zip sha 4bbf67de4feb222cd375f0f8abe6597a82e5d20cf9b79fcc6be267268a518830 (src/ only,
  built from pcassets/zips/e1.zip f967edfe… + o92). Caveat: the online judge is the 15 teams ahead on pinned groups; the local far
  set is rTop1/rD only, and 14 far maps = 1/5 of the old pool, 11/30 of the new one.

## REAL 2.0.0 games vs the top 5 (pcassets/replays_t5b, branch claude/pc-e1-assets commit bcc5124) — 10-27 17:05 UTC
375 online replays (kvvl/E1/e1foco x 125, 25 pinned groups vs Intercontinental Fish, Mite, willow best girl, Claudus Maximus,
prism best girl; results kvvl 5, E1 11, e1foco 14 wins). Decoded r<=300 with dump2 (cache gem/cache/t5b_*.r300h.pkl); both sides of
the SAME games (gem/ebmetrics.py + cmpwin2.py with SWAP=1 for the rival side; t5b_mid.py for the activity split). Clean games 116-119.

| window | side | gems/game | caps | gold-only | wolf+gem | elk+gem (gems) | gem clusters | champ-rounds alive / dead | deaths | at camp / idle / moving |
|---|---|---|---|---|---|---|---|---|---|---|
| r0-150 | top5 (in E1 games) | 81 | 7.10 | 2.79 | 1.75 | 1.54 (49) | 1.02 | 661 / 38 | 0.74 | 50 / 9 / 41 % |
| r0-150 | E1 | 63 | 7.35 | 3.70 | 1.44 | 1.07 (32) | 1.14 | 601 / 69 | 1.51 | 49 / 9 / 43 % |
| r0-150 | kvvl | 42 | 6.95 | 3.84 | 1.71 | 0.63 (15) | 0.77 | 605 / 64 | 1.34 | 47 / 8 / 45 % |
| r150-300 | top5 (in E1 games) | 106 | 8.36 | 3.14 | 2.17 | 1.92 (63) | 1.13 | 662 / 37 | 0.60 | 51 / 9 / 41 % |
| r150-300 | E1 | 66 | 6.55 | 2.84 | 1.83 | 1.09 (38) | 0.79 | 559 / 111 | 1.80 | 46 / 8 / 45 % |
| r150-300 | kvvl | 58 | 7.71 | 3.53 | 2.00 | 0.79 (21) | 1.39 | 560 / 109 | 1.84 | 46 / 7 / 46 % |

- The farm gap under 2.0.0 is two multiplicative halves. TIME: in r150-300 we are dead 111 champion-rounds/game vs 37 (deaths 1.80
  vs 0.60); alive time is used the same way (46-49% next to camps, 8% idle); champion-rounds at camps 259 vs 337 = -23% = the
  capture deficit (6.55 vs 8.36). CHOICE: gems per capture 10 vs 12.7 because they take elk groups (1.5-1.9/game, 30-33 gems each)
  where we take gold-only clusters (3.7 vs 2.8 in r0-150; by r50 1.33 vs 0.74, elks 0.32 vs 0.53). Gem clusters are equal now.
  66/106 = 0.62 = 0.78 (time) x 0.79 (choice). Deaths r100-300 belong to the fight thread (told 17:10 UTC); choice is ours.
- E1 vs kvvl in the same conditions: gems r0-150 63 vs 42 (the o129/o100 opening works online: elks 1.07 vs 0.63), r150-300 66 vs 58.
- Top-5 elk captures by group strength r0-150: 60-str 1.10, 120-str 0.29 per game; ours 0.75 / 0.18 — they take the big ones too.
- Pieces launched on E1 for the choice half: e93 = P_GWO 30 (opening gold weight 0.30, hold rule kept), e94 = o94 elkw (opts/
  o94_elkw.py: score x1.3 for gem-bearing elk groups, new Group::has_elk flag). Judge: elk+gem caps r0-150/r150-300 and gems r150
  toward 81/106 on the bench (cmpwin2 on n80), h2h kvvl gate, far unchanged.

## e93 / e94 CLOSED; the opening in the real games — 10-27 17:25 UTC
| bot (on E1) | n80 | far | h2h old | new30 | h2h new | gems r150/r300 old | gold r150 old | gems new |
|---|---|---|---|---|---|---|---|---|
| E1 | 68 | 42 | 35 | 86 | 44 | 45/104 | 517 | 84/196 |
| e93 = P_GWO 30 | 56 | 44 | 34 | 81 | 38 | 60/120 | 479 | 76/176 |
| e94 = o94 elkw x1.3 | 65 | 40 | 28 | 87 | 43 | 50/122 | 492 | 76/176 |
Both buy gems and lose games (e93 deaths<=100 63 vs 52; e94 h2h old 28/52). Same wall as e85/e91: in this bot a gem-ward
choice costs gold or deaths; the top 5 take the elks AND die less. The choice half is not separable from the fight half.
- Opening in the 375 real games (t5b_open.py): top-5 first capture median r24, 3.0 champions within 3 of the camp (3+ in
  72/118 games), kinds gold-only 34% / elk 31% / wolf 29%; ours r28, 1.9 champions (3+ in 31/118), gold-only 53% / elk 15%.
  By r30/r50/r100 they capture 1.0/1.9/4.4 groups worth 8/23/52 gems, we 1.3/2.5/5.0 worth 7/15/40: more captures, fewer gems.
  Champion-rounds dead by r100: 35 vs 23. (o81 stacking in 1.0.3 produced top-10 trios and lost; "opening" line closed then.)
- o95 packopen (opts/o95_packopen.py): the dormant `pack` switch in choose_target (no team split, clusters not solo) on near maps
  (hp_far false) for round < P_PACK_R. e95 = 40, e96 = 80 launched 17:26 UTC. Far maps identical to E1 by construction.
