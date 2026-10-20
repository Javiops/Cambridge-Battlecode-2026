# Decisions and evidence

Conclusions that should outlive one experiment, each with the numbers behind it (after Carson's
screeps-rl DECISIONS.md). Open questions go to ROADMAP.md.

## 2026-10-20 · Stage 1 complete: use the official rules module for training

The fast environment wraps the exact pinned official WASM module. We avoid maintaining
a separate implementation of the rules. Its authenticated actor observations and action
results match 2,560 release frames across four maps with 3/4/5 picks, including linked
Cassi/Issac bodies. All four matches agree through the final 2,000-round outcome and banks,
with zero faults or fuel exhaustion. Hidden-health mutation leaves the actor observation
unchanged; hidden champion data and enemy inventory queries are denied.

The certified micro-policy envelope is 24 global features, 16 candidates of 12 features,
eight hidden units, 305 float32 weights and at most two decisions per turn. Two full
encode/inference passes stay below the 65,000-fuel admission limit. The earlier larger
three-pass probes exhausted fuel and were rejected before freezing. Retain release fuel
checks for future architecture/feature changes and the eventual trained export.

The g1 pool contains 100 screening maps and 60 sealed generated holdouts; the ten `01*`
site maps are also sealed. Every generated map passed official structural checks and exact
regeneration. The 2,500-game five-control league has zero faults or fuel exhaustion. Ratings:
starter 1,828; seed 1,812; skip10 1,790; skip2 1,384; dummy 687. The 16-point seed gap is
smaller than both handicap gaps (38 and 444). Seed vs starter is exactly 50% over 200 games.
The skip10 interval overlaps starter's, so its rank is a calibration sanity check rather
than evidence that similarly small future improvements are significant.

Saved proofs in `results/stage1-*.json` bind source, configuration, runtime and map/bot
hashes. `python -m lab stage1 ready` is the acceptance check. See STAGE1.md for the actor
contract and reproduction. Stage 2 data collection has not started; no confirmation games
were inspected and no bot was promoted.

## 2026-10-20 · Recalibrate after the week 2 patch

CLI/SDK 3.0.1 changes the rules and design ABI. The lab now pins the observed release engine build,
records an SDK fingerprint for each frozen version and rejects incompatible versions/results.
Pre-patch calibration is historical evidence, not a rating for a current bot.

The fresh three-reference league completed 99 release games on 11 screening maps, both seats plus
mirrors, with zero faults and fuel exhaustion. Total league/report time was 23.679 seconds using
four workers (4.181 games/second on this machine). All 40 unit tests pass; the starter source bundle
rebuilds to exactly its frozen WASM bytes. See `results/calibration-2026-10-20.md` and
`results/patch-validation-2026-10-20.json`.

The seed control rates 1813 (90% interval 1749–1902), starter 1719 (1631–1780), dummy 968 (935–972).
The control's 94-point gap and 64% head-to-head score over 22 games reinforce the need for more maps
before judging small changes. The intervals overlap. The starter remains the reference champion;
no confirm maps were played and no promotion was made.

This was the initial patch-only milestone. The subsequent Stage 1 completion above adds
the fast training environment and neural inference fuel certificate.

## 2026-10-17 · The judge is a pool rating over all versions, not one variant against one base

Every frozen version plays every other on every screen map from both sides. Ratings are fitted
on the whole batch (Bradley-Terry on the Elo scale, `lab/rating.py`) with a 90% bootstrap over
maps. Carson used TrueSkill for the same job; Bradley-Terry needs no package and does not depend
on the order games were played in. Unit tests check that it recovers known ratings within 25 points.

## 2026-10-17 · Calibration: 12 maps x 2 sides can see a large handicap, not a 10% one

Five bots of known strength, 300 games on the 12 screen maps
(`results/calibration-2026-10-17.md`):

| version | what it is | rating | 90% range | final gems |
|---|---|---|---|---|
| calib-seed-v1 | starter with another random seed (same strength) | 1838 | 1770–1923 | 853 |
| calib-skip10-v1 | starter that skips every 10th round | 1830 | 1770–1918 | 840 |
| starter-v1 | the SDK starter | 1777 | 1719–1857 | 824 |
| calib-skip2-v1 | starter that acts every other round | 1384 | 1292–1436 | 510 |
| dummy-v1 | never acts | 672 | 601–704 | 0 |

- The large handicap (half the turns) is clear: 17% against starter, about 400 points below.
- The 10% handicap is invisible: skip10 scores 58% against starter and sits above it.
- Two bots of equal strength (seed vs starter) differ by about 60 points and their ranges overlap
  almost fully. **That is the noise floor of this map set: a gap under ~100 points, or under ~60% head to
  head on 24 games, is not a result.**
- **Consequence:** the loop needs many more maps before it can judge small changes. A map generator is the
  first item in ROADMAP.md. This is the same problem that made our old A/B tests inconclusive, now measured.

## 2026-10-17 · Side B is favoured on the site maps

Every version scores 10–29 points better as side B (seat split in the calibration report). Mirror
games of the starter go to side B 10 times out of 12. A complete tie also goes to B by the rules.
So every comparison plays both sides, and a result from one side is never reported alone.

## 2026-10-17 · Map roles

Only 17 site maps exist locally. 12 are `screen` and 5 are `confirm` (`lab.toml`). The qualifying
maps will be new, so the long-term confirm set is generated maps no one has tuned on.
