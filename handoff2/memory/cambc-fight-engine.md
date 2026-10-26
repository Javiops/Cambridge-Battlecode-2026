---
name: cambc-fight-engine
description: Fight-code work on the CAMBC bot (2026-10-13 afternoon): the fuel-gate bug that fakes bad results, the switchable fight patch, and where the scripts and duel arena live
metadata:
  type: project
  modified: 2026-10-13T15:20:00.000Z
---

Fight ("micro") work on v3td, measured on the 9-map arena vs `bots/v3td` (farming) and `bots/hunter2`
(deaths). Baseline v3td: 140.6 gems/100 rounds, 18-0 vs hunter2 with 95 deaths and 96 kills per 18 games.
Games are deterministic (same bots + map = identical replay), so repeat runs measure nothing; a single
rule change reshuffles the whole game, and 18 games move by about +-30 deaths from that alone.

**The trap (cost half a day):** gating the fight block on `fuel_ok(30000)` made every variant die 2-2.5x
more than v3td (180-250 deaths). `bc::vision::camps()` alone costs up to 36k fuel at the spawn, so on
heavy turns the fight code was skipped and the champion farmed into the enemy. With the gate at 0 the
same code equals v3td (101 deaths). Rule: the fight block always runs; make it cheap instead
(cache per-enemy static data by roster index, no strings or printf per turn). Init already costs ~50k
(build_shop), so round 1-2 are partly lost in every version; that is normal.

**Tried and rejected:** the full per-tile engine on the pack bot (`patch_micro.py`): 0-18 vs v3td on
the 9 maps at 47-83 gems/100r. Kill-time-race commits (`P_TTK_COMMIT 1`): 3-15 vs v3td. Standing to
fight when spawn is far (`P_STAND`). Strength-first shop: a strength shard is only +5 str (7%) vs +100 hp
(12%) for Vendetta, so health first is right at our gold levels; top teams buy 16-36 strength shards
late, from kill gold.

**patch_fight.py** (`arena/tools/fight/`, applied on bots/v3td) is fully switchable with P_* macros so
each rule is measured from a v3td-identical base (`mkvar.py` writes the variants; `summ.py LOGS` tabulates
wins, gems/100r, deaths, kills). Base = P_FOCUS_V3 1, P_RULES_V3 1, P_ACT_V3 1, P_PRIO 0, P_SPELL4 0,
P_SHIELD_NEAR 0, P_HEALSPAWN_V3 1, P_SHOP_STR 0, P_HOLD_CAST 0, P_TWIN 0, P_TWIN_FOLLOW 0,
P_BLOCK_REACH 0, P_FORTRESS 0, P_FOCUS_SHARE 0, P_BAIL_PCT 18. Rules available: value-table focus with
shared byte 7, conservative intents with low-hp retreat and hysteresis, fighting retreat (melee
attack-then-move is legal, seen as 'atk mv' turns in replays) towards the nearest ally, never stepping
onto tiles two enemies can hit, spawn fortress, spells from range 4, Varg shield at contact, Issac
follows Cassi, set_priority. `patch_eco.py` on top: one capturer per dead camp (melee first), tribute at
36 gems / altar within 6, shop trip at 240 gold at any health.

**Results (deaths per 18 games vs hunter2, base 76, v3td 95, noise +-30):** spell range 4: 88,
Issac follows Cassi 100, bail 30%: 103, eco patch 107, Varg shield 109, fortress+heal 110, actions 116,
priority 118, intents 120, hold-cast 120, strength shop 128, tile blocking 131, value-table focus 143.
Nothing beats the base; eco patch 9-9 vs v3td. Do not re-run these; measure new ideas against a
stronger opponent (one that packs the centre and focus-fires) or on the ladder.

**Tools:** `duel.py BOT_A BOT_B --out DIR` (4 small maps in `arena/maps_duel`, 300 rounds, ~4 s, weak
proxy: single camp group, enemies heal on a spawn 4 tiles away; decide on the 9 maps only).
`tracefight2.py OUTDIR SIDE R0 R1` (needs OUTDIR/dump.jsonl from `replaydump.js --camps` and a build with
`#define STATUS_EVERY 1`). Docs: `analysis/micro-design.md`, `analysis/winners-micro.md`,
`analysis/playbook-top10.md` (ranked economy changes).
