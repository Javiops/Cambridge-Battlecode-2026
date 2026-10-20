# Engine constants and designs

Printed in a completed release game on `00corners` with `cambc 3.0.1`.
Engine build: `2b36d9c61b2710d06036680d07fc4b7a8319ba35f634e4f1445725e0d99a1e16`.

Regenerate with `python3 -m lab probe`. Numeric values also live in `constants.json`.
Champion growth is per shard, as defined by the SDK. Camp rewards and respawn times are not exposed by the design ABI; consult the official patch notes for those fields.

## Constants

| name | value |
|---|---|
| capture_time | 5 |
| camp_sleep_time | 2 |
| respawn_time | 60 |
| recall_time | 5 |
| submit_gem_duration_multiplier | 0.1 |
| submit_gem_base_duration | 0 |
| submit_gem_minimum_duration | 1 |
| submit_gems_range | 1 |
| max_rounds | 2000 |
| winning_gems | 1000 |
| kill_gold | 100 |
| assist_gold | 0 |
| passive_gold | 0 |
| spawn_healing | 1 |
| active_wards | 1 |
| shared_memory_bytes | 8 |
| draft_memory_bytes | 1024 |
| tile_reveal_rounds | 1 |
| ward_cooldown | 10 |
| ward_lifetime | -1 |
| ward_vision_radius | 6 |
| ward_placement_radius | 2 |
| altar_lock_hits | 5 |
| tp_crystal_time | 3 |
| prism_focus_per_gem | 1 |
| vesper_vale_bonus_gold_percent | 33 |
| marcella_tribute_gold_per_gem | 2 |
| heart_of_ruin_missing_health_damage_max_bonus | 0.5 |

## Champion base stats (growth per shard)

| name | vision | move | range | hp | hp growth | strength | strength growth | focus | focus growth | camp damage x |
|---|---|---|---|---|---|---|---|---|---|---|
| ryth | 8 | 1 | 1 | 1200 | 100 | 45 | 5 | 100 | 10 | 1 |
| vesper_vale | 8 | 1 | 3 | 900 | 100 | 50 | 5 | 100 | 10 | 1 |
| vendetta | 8 | 1 | 1 | 800 | 100 | 70 | 6 | 100 | 10 | 1 |
| cassi | 8 | 1 | 3 | 600 | 65 | 30 | 3 | 70 | 13 | 1 |
| issac | 8 | 1 | 1 | 900 | 80 | 40 | 3 | 100 | 10 | 1 |
| stellar | 8 | 1 | 3 | 750 | 75 | 30 | 3.5 | 85 | 9 | 1 |
| prism | 8 | 1 | 3 | 700 | 60 | 35 | 2.5 | 80 | 8 | 1 |
| marcella | 8 | 1 | 1 | 1200 | 100 | 45 | 5 | 60 | 15 | 1 |
| willow | 8 | 1 | 3 | 700 | 50 | 55 | 3 | 120 | 5 | 1 |
| ren | 8 | 1 | 1 | 900 | 100 | 35 | 5 | 100 | 9 | 1 |
| varg | 8 | 1 | 1 | 1000 | 100 | 40 | 5 | 100 | 10 | 1 |
| tavi | 8 | 1 | 3 | 750 | 75 | 45 | 5 | 100 | 10 | 1 |
| heart_of_ruin | 8 | 1 | 1 | 1000 | 100 | 40 | 5 | 100 | 15 | 1 |

## Camp base stats

| name | hp | strength | range |
|---|---|---|---|
| wolf | 1350 | 20 | 3 |
| elk | 2400 | 60 | 4 |
| gem_cluster | 120 | 0 | 3 |
| gold_cluster | 120 | 0 | 3 |
| monolith | 20000 | 200 | 5 |
| golem | 5000 | 120 | 4 |

## DASH abilities

| name | slot | range | radius | modifier | duration |
|---|---|---|---|---|---|
| vesper_vale | 1 | 2 | 0 | 0 | 0 |
| vendetta | 1 | 2 | 0 | 0 | 0 |
| issac | 1 | 2 | 0 | 0 | 0 |
| ren | 1 | 2 | 0 | 0 | 0 |
| heart_of_ruin | 1 | 2 | 1 | 1.75 | 1 |

## CC abilities

| name | slot | range | modifier | duration |
|---|---|---|---|---|
| cassi | 1 | 4 | 0 | 1 |
| prism | 0 | 4 | 1.5 | 1 |
| ren | 0 | 4 | 1.25 | 1 |
| tavi | 1 | 4 | 1.4 | 1 |
