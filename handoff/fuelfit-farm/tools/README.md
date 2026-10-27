# Farm thread analysis tools (engine 2.0.0)

Paths inside the scripts point at the farm thread's cloud container (`/tmp/claude-0/ff/...`); adjust `RESDIR`/cache paths to reuse.

Bench (statistics JSON written by `cambc run-batch --statistics X.json --json`, files named `A_<map>.json` / `B_<map>.json` by our side):
- `bench_deaths.py x RESDIR...` our deaths per game by round window and cause (camp monsters vs champions), kills.
- `mapgroups.py` builds `cache/mapgroups.json` (one replay per map, decoded with `replay2/dump2.py`): camp groups with gems, gold, kinds, centre.
- `bench_caps.py RESDIR...` our group clears per game by window and kind (elk / gem cluster / gold-only / mixed), matched by position.
- `bench_jack.py RESDIR...` jackpot maps (a group holding >= 50% of the map's gems): who clears it first, median round, clears <= r600.

Real online replays (cache of per-round rows r <= 300 built by `gem/ebmetrics.py` with `MAXR=300` over a set directory of `A_`/`B_` links,
side = our team; `cmpwin2.ok` drops games whose dump mixes group ids):
- `t5b_arrive.py SET` arrivals at live camp groups (LO/HI rounds via env): allies within 6, enemies within 10, local balance, death within 15 rounds.
- `t5b_deathctx.py SET`, `t5b_deathctx2.py SET` context of each death and what happened between first sight of an enemy and the death.
- `t5b_elkleft.py SET` elk groups on our half: first taken by us / them / nobody, strength, approach, contest.
- `t5b_cleartime2.py SET` real clear time of elk groups by strength and champions present (kiting gaps allowed).
- `t5b_income.py SET` capture gold by kind and kill gold, both sides.
- `c34_winlose.py / c34_lossanatomy.py / c34_lossdeep.py / c34_midcaps.py SET` wins vs losses against the ranks 56-70 (index.json of pcassets/replays_c34).
