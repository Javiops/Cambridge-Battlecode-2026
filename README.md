# Cambridge Battlecode 2026a: team Live Love Larp

Our C++ bot for [Cambridge Battlecode 2026a](https://2026a.battlecode.co.uk) (12 October to 18 November 2026).
We did not qualify for the finals. Our best recorded ladder rank was 52, and on 8 November we were 125th of 826 with
a rating of 1925.

- **[POSTMORTEM.md](POSTMORTEM.md)**: what we did, what worked, what did not, and what we would do differently.
- **[bots/live-love-larp/](bots/live-love-larp/src)**: the final bot, version v21 (site version 212). It was live in
  ranked from 30 October and played the 4 November international qualifier.

## The bot

About 8,900 lines of C++20 compiled to WebAssembly. Every champion runs its own instance.

| File | What it does |
| --- | --- |
| `main.cpp` | Draft, world model, farming, banking, recall and the turn loop |
| `fight.h`, `verdict.h`, `bcfight.h`, `combat_policy_v1.h` | Champion fights: damage model, first-contact verdict, kiting and focus |
| `plan_t10.h` | Per-map, per-50-round camp plan built from about 600 top-10 vs top-10 games |
| `mapplan.h`, `mapplan_game.h` | Map-feature rules (map size, altar distance, camp layout) |
| `<champion>.h` | One header per champion: shop plan, abilities, special rules |
| `params.h` | Compile-time switches (`P_*`) for every behaviour that was tested |
| `track.h`, `utility.h`, `profile.h` | Enemy tracking, helpers, fuel profiling |

Code comments are in Spanish, as they were written during the competition.

## Build and run

You need the official `cambc` CLI. We finished on CLI 4.0.0 (engine 2.0.0).

```bash
pip install cambc
cambc init --yes                  # SDK, toolchain and the official map pool
cambc build bots/live-love-larp --release
cambc run bots/live-love-larp bots/starter-cpp --map maps/<map>.map26a -o out/game
cambc view out/game
cambc bundle live-love-larp --output live-love-larp.zip   # the zip the site accepts
```

## History

Earlier bots, test tools, online-testing scripts and analysis are in this repository's git history and branches.
`main` was cleaned on 8 November 2026 to hold only the final bot and the postmortem.
