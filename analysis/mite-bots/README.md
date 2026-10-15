# Two Mite-style bots and their win rates (2026-10-15)

Follow-up to the #1/#2 dissection (`analysis/top2-dissection-2026-10-15/`). Two bots were built from the measured
Mite rules and measured against our previous bots (study25, study24, v30, v29):

* **mite_s25** = study25 + the Mite rules that did not lose on the training maps (shop order, fight code, melee wall,
  no kite/volley, tribute at 10 gems). Source `mite_s25_src/`, zip `/mnt/project-files/bot/mybot_mite_s25.zip`.
* **mite_s25_full** = study25 + every Mite rule as a switch (adds Mite's draft and the hp<50% recall). `mite_s25_full_src/`.
* **mite_scratch** = Mite rebuilt from zero, one 1400-line file that implements the dissection rule by rule.
  Source `mite_scratch_src/`, zip `/mnt/project-files/bot/mybot_mite_scratch.zip`, its own report `mite_scratch_REPORT.md`.

Scoring as agreed: maps won on both sides / lost on both sides (`logs/sign.py LOG`); most games are side mirrors, so
game counts overstate the sample. Noise on 44 generated maps is about ±6 net maps; `maps_hold` (60 maps) was never
used for tuning. Map sets: official (9 maps, 18 games), gen (44, 88 games), hold (60, 120 games).

## 1. Results

### mite_s25 (study25 + shop + fight rules)

| vs | official W-L (won/lost both) | gen W-L (won/lost both) | hold W-L (won/lost both) |
|---|---|---|---|
| study25 | 10-8 (3/2) | 50-38 (15/9) | 59-61 (12/13) |
| study24 | 11-7 (3/1) | 47-41 (14/11) | 71-49 (26/15) |
| v30 | 9-9 (3/3) | 53-35 (17/8) | 70-50 (20/10) |
| v29 | 11-7 (5/3) | 56-32 (20/8) | 72-48 (22/10) |

Beats v29, v30 and study24 by a margin that holds on the held-out maps (v29 hold p=0.05, v30 p=0.10, study24 p=0.12).
Against study25 itself it is +6 maps on the training set and 12-13 (even) on the held-out set: **not better than study25**.

### mite_s25_full (all Mite rules, including draft and 50% recall)

| vs | official | gen | hold |
|---|---|---|---|
| study25 | 3-15 (0/6) | 45-43 (14/13) | 68-52 (20/12) |
| study24 | 5-13 (1/5) | 49-39 (18/13) | 74-46 (24/10, p=0.02) |
| v30 | 10-8 (3/2) | 46-42 (16/14) | 75-45 (28/13, p=0.03) |
| v29 | 10-8 (2/1) | 44-44 (13/13) | 84-36 (33/9, p=0.00) |

Odd pattern: loses the official maps (Mite's fixed draft is wrong for our engine there: 4-14 in the ablation) and is
even on gen, but is the best of the three on the held-out set, including 20-12 vs study25. The hold set was generated
with a different seed and has more big maps, where the 50% recall (dying less) pays and the draft matters less.
Taken together with the gen result this is within noise against study25; it is a real gain only vs v29/v30/study24.

### mite_scratch (Mite from zero)

| vs | official | gen | hold |
|---|---|---|---|
| study25 | 3-15 (0/6) | 6-82 (1/39) | 16-104 (3/47) |
| study24 | 2-16 (0/7) | 8-80 (2/38) | 20-100 (5/45) |
| v30 | 2-16 (0/7) | 7-81 (1/38) | 23-97 (3/40) |
| v29 | 3-15 (0/6) | 9-79 (2/37) | 21-99 (3/42) |

120-692 overall (15%); 18-0 vs the starter bot. Head to head mite_s25 vs mite_scratch on gen: 84-4 (41/1).
It farms 130-165 gems per 100 rounds against 200-240 for our bots, and dies 3-4.6 times a game.

## 2. What the ablation said (gen maps vs study25, won both / lost both)

| Mite rule on study25 | result | kept |
|---|---|---|
| fixed draft by team size | 6-22 (official 4-14) | no |
| recall at hp<50% from 7 tiles (always) | 6-17 (deaths 86 vs 233 but -35 gems/game) | no |
| recall at 50% only with a foe within 8 | 10-8 | no (neutral) |
| shop order jungle>durab>bruiser hp>power | 8-11 (official 13-5) | yes |
| Mite target scoring + always engage | 6-5 | yes |
| melee wall params (KITE 0, VOLLEY 0, FRONT_LOCAL 0, FRONT_OUT 250) | 8-9 | yes |
| shop + fight | 12-10 | |
| shop + fight + HALF 10 (= mite_s25) | 15-9 | yes |
| + PACKOPEN 20 | 17-14 | no |
| + TRIBUTE_GEMS 5 | 15-9 | no |
| + SHOP_RECALL 90 | 11-11 | no |

No single rule clears the ±6 noise band. Logs in `logs/ablation/` (names ma..mo as in the thread).

## 3. Reading

1. Mite's behaviour transfers as **rules** only partly: its shop order and its no-chase, focus-one, melee-wall fight
   are at worst neutral on our engine; its fixed draft and its early recall are losers on our engine because our
   farm loop is tuned around our draft and around banking bigger bags.
2. The from-scratch clone shows the measured rules are **not sufficient** to reproduce Mite: a literal implementation
   farms 35% slower than study25 and dies more. What the dissection could not measure from replays (how the pack
   moves as one, the per-map opening exceptions, how it chooses when to walk vs recall over a whole game) is where
   Mite's 1834 rating comes from. Our own farm engine (study25) is a better base than any clone.
3. Recommendation: do not upload either bot as is. mite_s25 is a safe equal to study25 (keep its shop order and fight
   params as switches); mite_s25_full is worth one online A/B on big maps only if the user wants to test the 50% recall.

## 4. Files

* `mite_s25_src/`, `mite_s25_full_src/`, `mite_scratch_src/`: bot sources (mite_s25 variants build on study25; the
  switches are `P_MITE_DRAFT`, `P_MITE_SHOP`, `P_MITE_RECALL` (distance), `P_MITE_FIGHT`, `P_MITE_PCT` in `params.h`).
* `logs/final/<bot>_<opp>_<set>.txt`: the 24 final runs; `logs/scratch/`: the clone's 12 runs; `logs/ablation/`.
* `mite_scratch_REPORT.md`: rule-by-rule implementation table, iteration history, per-map weaknesses of the clone.
