# Replay decision dataset and behaviour cloning (2026-10-16)

Thread "Imitation learning from top replays". Goal: learn the top teams' fight decisions from their replays, in features
our bot can compute itself, and turn what is learned into GA seeds or a rule test.

## Files

| file | rows | what |
|---|---|---|
| `turns_top101.parquet` / `.csv` | 115,133 | one row per champion per round in contact, 101 ladder games of #1 Mite and #2 Univardisty (both sides; the other side is a top-20 team, tag `opp`) |
| `targets_top101.parquet` / `.csv` | 23,807 | one row per (turn that hit an enemy champion, candidate enemy within 4): which candidate was chosen |
| `turns_us_v44.parquet` / `.csv` | 24,345 | the same rows for 27 of our online v44 games vs top-10 teams (16 Oct 10:46-11:00, known maps only); our side `us_v44`, the rival `opp` |
| `targets_us_v44.parquet` | 3,699 | target rows for those games |
| `games_top101.json`, `games_us_v44.json` | | game lists (match id, map, side, team, result) |
| `bc/metrics.json`, `bc/coefs_engage_vs_retreat.csv`, `bc/model_lr_engage_retreat.json` | | behaviour-cloning results and the fitted logistic model (standardisation + weights, ready to embed) |
| `bc/compare_us_vs_top.txt` | | our decisions vs theirs in the same situations |
| `scripts/build_dataset.py` | | builder: `build_dataset.py STEPS_DIR GAMES_JSON MAPS_DIR OUT_DIR` (11 s for 101 games) |
| `scripts/bc.py` | | behaviour cloning: `bc.py turns.csv OUT_DIR` |
| `scripts/fetch_ours.sh` | | download + decode our games (needs the visualiser wasm v0_0_2: run `cambc view <any zip>` once so it lands in ~/.cache/cambc/assets) |

Sources: top games = `analysis/top2-dissection-2026-10-15/data/steps.tgz` (decoded every step, format in its `DATA.md`);
maps = that folder's `mapsj/`. Our games = `online/data/games.jsonl` rows since 08:00 vs rank <= 10 (85 games, 42 on the 9
known maps, 27 decoded completely; the rest failed to decode or are on new maps without a map json).

## One row (turns)

A champion that is alive at the start of round R, is not in the middle of a recall/tribute channel, and has at least one
living enemy champion within Chebyshev 8. Features are the state at the start of R (end-of-round R-1 snapshot); labels are
what the champion did during R; outcomes look ahead from R.

Identity: `match, map, round, champ, team (0 = side a), team_tag (mite|uni|opp|us_v44), type, melee`.

Features (all computable by our bot at its turn; distances Chebyshev unless noted):
`hp, maxhp, hp_frac, gems, gold, d_altar` (BFS to nearest altar), `d_spawn` (BFS to own spawn), `own_casts_last8`
(own casts in the last 8 rounds, a proxy for spells on cooldown), `dmg_taken_last1, dmg_taken_last3` (from anything),
`n_ally8, n_ally4, ally_hp8, ally_lowfrac8` (lowest ally hp fraction within 8), `n_en8, n_en4, n_en3, n_en1, en_hp8,
en_maxhp8, near_en_dist, near_en_hpfrac, near_en_melee, min_en_hp, min_en_hpfrac, en_gems8, en_casts_last8`
(enemy casts in the last 8 rounds = their spells likely on cooldown), `en_ranged8, hp_ratio8` = (own + allies hp within 8) /
enemies hp within 8, `en_dmg_last1` (damage our team did to those enemies last round), `round`.

Labels: `action` = recall | tribute | kite (hit an enemy champion and stepped away) | hit | advance (stepped closer to the
nearest enemy) | retreat (stepped away) | hold (no step relative to the nearest enemy; includes farming a camp in place);
`action3` = engage (kite, hit, advance) | hold (hold, tribute) | retreat (retreat, recall); `attacked_champ, cast, hit_camp,
moved_delta` (change of distance to the nearest enemy from its own step), `moved_delta_mean` (mean over visible enemies),
`target` (global index of the enemy it damaged most, -1 none).

Outcomes: `died5, died10, died20` (dead at any point in the next N rounds), `dmg_taken5, dmg_taken10, dmg_dealt10`
(own damage to enemy champions), `en_died10` (enemies visible now that die within 10), `gem_swing20` = (our team carried +
tributed gems change) - (theirs) over 20 rounds.

Targets: `cand, cand_type, chosen, n_cands, dist, hp, hp_frac, gems, melee, is_lowest_hp, is_nearest, hit_by_team_last1,
cand_casts_last8`.

Caveats: vision is approximated as Chebyshev 8 (no shadowcasting, so enemies in bushes count as seen); the state is the
start of the round, so enemies acting earlier in the same round moved up to 1 tile; spell readiness is inferred from casts
(the bot can read real cooldowns); recall start = step kind 11 off the own spawn (some bots spam kind 11 on spawn, ignored);
"retreat" is a step away from the nearest enemy, which also catches walking to the next camp, so the labels are noisy.

## Behaviour cloning (Mite + Univardisty turns, 5-fold CV grouped by game)

| task | rows | majority class | hp threshold only | logistic regression | MLP 16 |
|---|---|---|---|---|---|
| engage vs retreat | 41,463 | 62.6% | 72.4% (retreat below 42% hp) | 74.0% | 74.2% |
| engage / hold / retreat | 61,966 | 41.9% | | 53.1% | 54.4% |

In plain words: their fight-or-flee choice is mostly one number, their own health. A single cut at 42% hp explains 72% of
it; the other 28 features (allies, enemies, spells, gems, distance to altar) add only 1.6 points, and a small neural net adds
nothing on top of the linear model. After health, the features that matter are distance to the nearest enemy (further away
= more likely to back off), an enemy in melee contact (stay and fight), own max hp (tanks stay), own spells used recently
(back off while on cooldown), and allies close by (stay). The model fitted on the top two predicts Mite best (77.5%),
Univardisty 71%, the other top-20 teams 69%: Mite is the most consistent player.

Targeting: the chosen target is the nearest candidate 85% of the time for Mite (76% Univardisty), the one the team hit
last round 59% (base rate 38%), the lowest-hp one only 50% (random would be 44%); Univardisty picks the target carrying
most gems 84% of the time.

## Where we differ (v44 online vs top-10, same features)

Share of turns that retreat, among engage-or-retreat turns with an enemy within 5:

| own hp | Mite | Univardisty | top-20 | v44 (us) |
|---|---|---|---|---|
| 30-40% | 0.64 | 0.61 | 0.62 | 0.76 |
| 40-50% | 0.42 | 0.50 | 0.55 | 0.68 |
| 50-60% | 0.27 | 0.46 | 0.45 | 0.49 |
| 60-70% | 0.20 | 0.37 | 0.34 | 0.40 |
| 90-100% | 0.15 | 0.21 | 0.29 | 0.24 |

Over all contact turns (enemy within 8) we hit an enemy champion on 10% of turns (Mite 12%) and hold more (38% vs 33%).
Backing off earlier does not keep us alive: dead within 10 rounds from a contact turn at 20-30% hp = 35% for us vs 16%
for Mite, and over all contact turns 14.8% vs 11.7% (the top-10 teams in the same games: 5.4%). This matches the
2026-10-15 finding that 2/3 of our deaths happen while fleeing. v44's curve comes from P_UNI_FLEE 44 (caster draft flees
below 44%), P_LOWHP 50 (back off below 50% with a foe within 6) and the "unfavourable group" rule (back off below
P_GA_AVOID_HP 60% or whenever a foe is within P_AVOID_DIST 4).

## What was done with it

- GA seeds: three genomes in `/mnt/project-files/ga-farm/migrants/imitation_*.json` (v44 + the changes below, no fitness yet):
  `im_a` 9aee4f367f = P_UNI_FLEE 33, P_LOWHP 40, P_GA_AVOID_HP 45, P_AVOID_DIST 2 (Mite's curve);
  `im_b` cebb64a4a6 = im_a + P_ENGAGE2 60 (call more fights favourable);
  `im_c` 8634a1118b = milder, 38 / 44 / 50 / 3.
- Rule test: idea I060, `bots/im_a` gated against the online zip with tools/gate.py (kind fight; standard map set hold60 +
  dev200 = 260 maps both sides, declared before the run). Results against the v44 zip:

  | candidate | fresh maps won/lost both sides | caster panel flips for/against | verdict |
  |---|---|---|---|
  | im_a | 54-25, p=0.001 (gems/100 rounds 168.2 vs 164.9) | 11/19, p=0.20 | PASS (fight) |
  | im_b | 56-27, p=0.002 | 16/23, p=0.34 | PASS (fight) |
  | im_c (milder) | 47-41, p=0.59 | 10/27, p=0.008 | FAIL (panel veto) |

  Candidate to upload: im_a, `/mnt/project-files/bot/mybot_ga65a6_imitation.zip` (v44 + the 4 params, no P_MONO). Fight
  rules that won locally have failed online before, so only the online A/B (online/lfl.py) decides.

## For the Q-learning thread

`died10`/`died20` and `gem_swing20` are the outcome labels for a fight/flee value; the features list above is the input
schema. `bc/model_lr_engage_retreat.json` holds `mean`, `scale`, `coef`, `intercept` for P(retreat) on the feature order in
`features` (with the log transforms listed in `transforms`), 29 multiplies per turn.

## Round 2 (14:10-15:20 UTC): on the 12:52 online bot

Base = `mybot_ga65a6_mono_fuelguard_jackpot.zip` (v44 + contest fix + fuel guard + jackpot). Gate kind fight, 260 maps.

| candidate | change | fresh maps won/lost both sides | caster panel flips | verdict |
|---|---|---|---|---|
| im_a | P_UNI_FLEE 33, P_LOWHP 40, P_GA_AVOID_HP 45, P_AVOID_DIST 2 | 63-38, p=0.017 | 17/20 | PASS |
| im_d | stronger: 28 / 32 / 38 / 1 | 50-37, p=0.20 | 21/11 | PASS |
| im_e | im_a + P_FLEE_PCT 24 | 75-49, p=0.024 | 16/15 | PASS |
| im_p (I062) | im_a's thresholds only with an ally within 2, v44's alone (`im_p.diff`) | 38-49, p=0.28 | 22/11, p=0.08 | PASS |
| pair a/b/c | im_a + farm pair genes (P_PAIR_N 2/3, STICK, ENGAGE) vs im_a | 5-19, 4-21, 16-33 | | FAIL |
| tgt DW 150 / 400 (I061) | im_a + target score distance weight 40 -> 150 / 400 (`tgt_dw.diff`) vs im_a | 8-6 / 16-6 (p=0.052) | 3/4, 8/6 | PASS (small) |

New columns `near_ally_dist` (any distance) and `ally_delta` (own step toward(-)/away(+) from the nearest ally).
Mite fights with an ally within 2 tiles on 59% of contact turns, Univardisty 41%, v44 39% (`bc/ally.txt`). Mite's retreat
curve hardly depends on that (`bc/ally_curve.txt`), but deaths do: at 30-50% hp alone we die 27% within 10 rounds (Mite
20%), paired only 8.5% (Mite 11%).

Behaviour check (`bc/beh_cmp.txt`, `bc/deaths_check.txt`): 36 local games each (9 official maps x 2 sides x spar11 and
spar16, the caster bots). im_a's retreat curve now matches Mite's (40-50% hp: 0.36 vs online bot 0.70), but:

| bot | wins of 36 | our deaths | their deaths |
|---|---|---|---|
| online bot | 34 | 34 | 302 |
| im_a | 32 | 89 | 299 |
| im_e | 32 | 91 | 303 |
| im_p | 36 | 56 | 285 |

Reading: im_a beats the online bot in self-play by fighting more, but against the caster bots (the local rivals that kill
like online teams) it dies 2.6x more for the same kills. im_p keeps the commitment only when paired: it loses a little in
self-play and does best against the casters. Zips (not uploaded): `bot/mybot_ga65a6_mono_fuelguard_jackpot_imitation.zip`
(im_a) and `bot/mybot_ga65a6_mono_fuelguard_jackpot_imitation_paired.zip` (im_p).

**15:45 UTC:** im_p + nearest-first targeting (P_TGT_DW 400) vs im_p: fresh 14-8 (p=0.29), panel 2/6; vs the caster bots 36/36
wins, 54 deaths, 268 kills (im_p 56 and 285). No clear gain, so I061 is paused and im_p stays the candidate.

## Round 3 (15:35-16:00 UTC): recalls and gem-carrier targeting

Recalls (`bc/recalls.txt`, every recall start off the own spawn, retries merged). Per 1000 champion-rounds: Mite 11.5 recalls
and 2.2 deaths, Univardisty 9.7 and 2.7, v44 13.8 and 2.9. Mite recalls far from spawn (median 18 tiles, v44 12), with more
gems (mean 14 vs 8), at either low hp (35% below 30% hp, v44 20%) or near full hp (17% above 90%, v44 6%: recall used as a
teleport home), and 36% of its recalls start 6-8 tiles from the nearest enemy (v44 17%). Completion rates are the same
(~92%). The "recall as transport" part was tested before (P_CAPRECALL, Mite macro) and lost on our engine, so no new test.

Gem carriers (`bc/gemtarget.txt`): when the candidate targets carry different gems we already pick the richest more often than
the top two (v44 60%, Univardisty 51%, Mite 43%, random 44%). No gap.

So the clearest remaining gap is formation: Mite has an ally within 2 tiles on 59% of contact turns, we 39%. im_p only
changes what we do once paired; getting paired more often (moving as a pair between camps) is the next lever.
