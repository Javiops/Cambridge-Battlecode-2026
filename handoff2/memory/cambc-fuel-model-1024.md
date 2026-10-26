---
name: cambc-fuel-model-1024
description: Fuel is WASM instruction metering (C++ loops cost ~10 fuel/iteration), not just SDK calls; measured SDK call prices and exact engine BFS rules (bench 10-24)
metadata:
  type: project
  modified: 2026-10-24T23:47:46.713Z
---

Measured 2026-10-24 (farm thread, bench bot a1b, --fuel-quantum 2000000):
- FUEL = instruction metering: trivial C++ loop 10k iterations = 100k fuel (~10/iter); scanning 1681 exported bits = 26k; own C++ BFS over 10k tiles > 1M (kills the turn); zero-filling a 20KB std::vector ~10k; one printf line 568. Engine-side compute is native: distance_field::compute ~3.4 fuel per visited tile (3.4k on 41x41, 30k on 100x100).
- Per-call SDK prices: bitboard.is_set 47, set 75, df.get 41, bitboard copy/or/not/and-not 500-660, is_empty 62-196, positions(16) 716, bitboard::export_linear_buffer 190 (packed bits LSB-first, index y*w+x), distance_field::export_linear_buffer 460 (41x41) .. 2536 (100x100) (uint16 row-major), compute_to 1.1k-3.9k (exhaustive = full compute when the destination is unreachable), next_moves_from 848, visible_tiles_into 299, champion_tiles 566, camp_tiles 251, abilities()[k].is_ready 616, cooldown 175, consumables.count 32, can_move/can_cast/attack_range/position 56, camp.health/strength/position/max_health 45-48 (sdk_costs.md's 1997 not reproduced), is_visible 52, read_sm 26, my_roster 1.2-1.7k, vis_champions (o01 cached copy) 2.7-4.1k per call.
- Engine distance field = 8-neighbour BFS, a wall blocks only its own tile (diagonal past a corner allowed), max_distance includes d == cap (verified on all 40 maps, 3182 comparisons, 0 mismatches). next_moves_from = neighbours with d-1 in compass order from north, north = (0,+1) (4569 samples, 0 mismatches). The early-stop visited mask of compute_to could NOT be replicated (expansion order unknown): never read tiles at d >= dest distance from a compute_to field if exactness matters.

- 10-25 far-map profile (farm thread, 12 games): on 100x100 maps every engine field costs 26-30k, and choose_target_impl runs only every few rounds per champion, so any per-call warm-up (o45 reverse fields) takes hundreds of rounds and doubles the cost meanwhile: schedule once-per-game work on structurally cheap turns (dead, fight, cached, recall; never tribute) by a fixed rule (o54). A search whose dest is unreachable is exhaustive (full map): test static separation (mainland bitboard) before searching (o55). Far-map exposure after o54-o56: turns >=77.5k 1.85% -> 1.0% (of 15438); isle_escape still ~55k when it runs (exhaustive goal field). Shop 25k, post-sweep 15k, play_turn start 23k (br_static_step/cf_observe) are the non-farm heavy parts.

**Why:** the deterministic-bot work (fuelfit) assumed pure C++ was free; it is not, so exact optimisations must count loop iterations and keep buffers static.
**How to apply:** replace per-tile SDK reads (is_set/get) by ONE export into a static buffer only when the scan has >~6 tiles; never move engine BFS into C++; bound compute_to with max_distance when only distances below a known bound are read. Tools: /tmp/claude-0/ff (bench ws, opts o06/o08, prof_fp.py) in the farm thread's container; evidence in analysis/farm-route-1021/orch/RESULTS.md (fuelfit section). See [[cambc-stall-root-cause-1024]], [[cambc-game-mechanics]].
