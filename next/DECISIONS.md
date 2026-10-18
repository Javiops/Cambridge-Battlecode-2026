# Decisions and evidence

Conclusions that should outlive one experiment, each with the numbers behind it (after Carson's
screeps-rl DECISIONS.md). Open questions go to ROADMAP.md.

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
