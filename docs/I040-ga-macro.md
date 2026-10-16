# I040: genetic algorithm over the macro (farming and economy)

Second front of the genetic plan, next to the fight GA (I030, `tools/ga/ga.py`) and the fight-structure GA
(`tools/ga/sga.py`). Same loop and machinery; a different genome: how we farm, bank, recall, shop and draft.

## Base and genome

- **Base = `bots/ga65a6`** = `bots/study27-economy` (main, with P_MONO) + the evolved fight params of genome 65a6d152b6,
  i.e. the bot online as v44. Built by `python3 tools/ga/mga.py base` (only P_MONO differs from the uploaded zip).
- **49 genes** in `tools/ga/macro_genome.py`: 33 existing `P_*` macros plus 16 hard-coded constants of the macro code
  turned into `P_GA_*` genes (and two preprocessor switches made runtime). The default genome equals the base: with
  unlimited fuel it plays the 102 check games (17 site maps x spar11/spar16/base x 2 sides) identically to the base build.
- Fight genes (flee, engage, kite, danger spots, bail) stay with the fight GA. No per-map hard-coding is added; the
  genes are thresholds over map features (camp hp, walking distances, spawn-to-spawn path, team size).
- Not included yet: the four review switches of PR #18 (`P_ALTARPICK`, `P_RECALLCOST`, `P_CAMPMODEL`, `P_CHAINWALK`):
  that branch is based on an older main; they become genes once it is rebased.

| gene | default | range | what it decides |
|---|---|---|---|
| `P_GOLD_W_EARLY` | 25 | 0..80 | gold worth this % of a gem in camp choice, early |
| `P_GOLD_W_LATE` | 24 | 0..80 | ... and late |
| `P_GA_GOLD_ROUND` | 600 | 200..1500 | round where the early gold weight ends |
| `P_NOGOLD` | 1 | 0..1 | skip gold-only clusters |
| `P_MAX_SHARE` | 4 | 1..5 | champions allowed on one monster group |
| `P_SHAREEXP` | 75 | 30..100 | a joiner values a big camp at gems / team^(this/100) |
| `P_STACK_HP` | 3000 | 800..8000 | camps with this much hp count as big (stacking) |
| `P_PAIR` | 2 | 1..3 | champions on a gem cluster |
| `P_RESERVE_PCT` | -60 | -150..50 | squad sizing: hp each member may lose, % of max (negative = more than max) |
| `P_HALF` | 30 | 10..100 | score x this % for camps on the enemy half |
| `P_GA_HALF_D` | 6 | 0..15 | ... a camp is on their half when this much nearer their spawn |
| `P_GA_DOOR` | 60 | 20..100 | score x this % for camps near the enemy spawn |
| `P_GA_DOOR_D` | 8 | 0..16 | ... within this many tiles |
| `P_STICK` | 125 | 100..200 | score bonus % for the current target (hysteresis) |
| `P_RESPAWN` | 4 | 0..15 | walk to a respawning camp when it is back within walk + this |
| `P_GA_NEEDCO` | 70 | 30..100 | score x this % when the camp still needs company |
| `P_GA_SOLO` | 30 | 10..100 | score x this % for a claimed gem cluster (solo job) |
| `P_GA_CYCLE` | 8 | 0..30 | cost of a heal trip: this + walk from spawn |
| `P_GA_OVERHEAD` | 6 | 0..20 | fixed rounds added per camp (capture, overhead) |
| `P_BANKW` | 0 | 0..300 | camp cost adds this % of the round trip to the nearest altar |
| `P_R34_BANKCOST` | 300 | 0..600 | same, expanse only (known-map rule) |
| `P_HOLD` | 200 | 100..400 | caster draft: score x this % for camps around the held centre altar |
| `P_HOLD_R` | 6 | 3..10 | ... camps within this of that altar |
| `P_E_RETARGET` | 6 | 2..20 | re-choose a camp we are only walking to every this many rounds |
| `P_ONE_CAP` | 1 | 0..1 | one champion per capture reward |
| `P_TRIBUTE_GEMS` | 12 | 5..60 | walk to an altar once carrying this many gems |
| `P_TRIBUTE_NEAR` | 8 | 0..20 | bank a smaller bag when an altar is this close... |
| `P_GA_NEAR_GEMS` | 10 | 1..30 | ... of at least this many gems |
| `P_CHAIN` | 36 | 0..100 | with fewer gems than this, take a near solo camp before banking |
| `P_CHAIN_R` | 8 | 3..20 | ... within this many tiles |
| `P_BAG` | 0 | 0..100 | no enemy seen for P_BAG_QUIET rounds: carry this many gems before banking |
| `P_BAG_QUIET` | 40 | 10..150 | ... rounds |
| `P_LATE_ROUND` | 1850 | 1500..1990 | after this round bank any gems |
| `P_OWN_ALTAR` | 20 | 0..60 | altar choice: penalty for altars on the enemy half |
| `P_TELE` | 0 | 0..30 | >0: recall instead of walking to the altar when that is shorter by this |
| `P_GA_TRIB_RC_GEMS` | 10 | 1..40 | before a recall, bank first with this many gems... |
| `P_GA_TRIB_RC_D` | 12 | 0..30 | ... if the altar is this close |
| `P_CAPRECALL` | 2 | 0..2 | recall on capture tiles: 1 when needed, 2 also for a cheap heal/shop |
| `P_CAPRECALL_DELAY` | 1 | 0..5 | rounds on the capture tiles before that recall |
| `P_GA_CR_HEAL` | 90 | 50..100 | optional capture recall below this % hp (minus walk cost) |
| `P_GA_CR_GOLD` | 90 | 30..300 | optional capture recall with this much gold (+3 per tile of walk) |
| `P_SHOP_GOLD` | 240 | 100..600 | recall to shop with this much gold when hurt |
| `P_GA_SHOP_HP` | 50 | 0..100 | ... below this % hp |
| `P_SHOP_RECALL` | 180 | 0..600 | shop trip at any hp with this much gold (0 = never) |
| `P_SHOP_PLAN` | 3 | 0..3 | item plan: 0 own, 1 top teams, 2 tank, 3 top-10 winners |
| `P_SHOPUNI` | 1 | 0..1 | casters buy power-f like the #1 |
| `P_NE_POWER_OPEN` | 1 | 0..1 | melee opens with a power emblem |
| `P_UNI_PATH` | 45 | 0..120 | caster draft when the spawn-to-spawn walk is at most this |
| `P_GA_DRAFT_FARM` | 0 | 0..2 | draft on the other maps: 0 own list, 1 Cassi&Issac + Stellar first, 2 Stellar, Cassi&Issac, Ren, Tavi (the top-10 winners) |

Planned: `P_JACKPOT` (I042, farm gold before taking the central group) becomes a gene once it is on main.

## Fitness

- Per generation 12 maps drawn fresh from the training pool: the 17 site maps, **204 generated cousins of the site
  maps** (`tools/ga/cousins.py`: each site map with its camp groups moved and retyped, walls thinned or extended,
  altars nudged, team size changed now and then; 12 per site map, /mnt/project-files/arena/maps/cousins) and the older
  generated sets, minus anything in the validation or sealed sets.
- Every candidate plays both sides vs **the base itself (weight 2)** and the caster sparring **spar11, spar16**
  (a macro change that gets us killed shows there). Pair score = mean of the two sides, win +1 / loss -1, plus
  0.1 x gem margin / 1000 (farm speed as the tie-breaker). Selection is the margin over the **control** (default genome,
  same wasm) on the same games, averaged over every generation a genome played and shrunk toward 0.
- **Training runs with unlimited fuel** (`--fuel 10000000`): no fuel chaos, so a candidate differs from the control
  only on maps where its decisions differ. With normal fuel the default genome already differs from the base build in
  43 of 102 games. Validation and the gate use normal fuel, so a gene that costs fuel is still caught there.
- Population 16, 4 elites, tournament of 3, blend crossover, ~3 genes mutated per child. 1152 games per generation.

## Validation and gate

`mga.py validate` on v100 (never trained on) vs the control, then `mga.py export` and `tools/gate.py` on the sealed
hold60 / dev200 / fresh300 against the online bot (ga65a6). The map count of each verdict is fixed in advance.

## Commands

```bash
python3 tools/ga/mga.py base && python3 tools/ga/mga.py prepare
MGA_FUEL=10000000 python3 tools/ga/mga.py check          # expect 0 different games
MGA_FUEL=10000000 python3 tools/ga/mga.py run --gens 300 --pop 16 --maps 12 --seed 7   # out/mga/log.md
python3 tools/ga/mga.py validate --top 3
python3 tools/ga/mga.py export --id ID --out bots/NAME
```
