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
