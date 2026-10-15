# Results — fresh confirmation failed

**The final package did not meet the predeclared confirmation gates.** Positive descriptive totals do not establish that it is stronger than the cleaned PR11 control. The source remains experimental.

| Cohort | Maps | Direct wins–losses | Direct score | Matched five-reference delta |
|---|---:|---:|---:|---:|
| Development | 253 | 281–225 | 55.53% | +12 / 2,530 games; +0.47 pp |
| Previously exposed transfer | 128 | 143–113 | 55.86% | +25 / 1,280 games; +1.95 pp |
| Fresh confirmation | 512 | **521–503** | **50.88%** | **+114 / 5,120 games; +2.23 pp** |

There were no draws in these direct comparisons. Development and transfer were used for adaptive selection, so their results are descriptive. Coverage counts are not counts of new independent evidence: earlier stages and exact cached games were reused where applicable.

The fresh cohort was generated after freezing one candidate, using seed `296314875`. All **11,264 distinct physical games** were newly simulated: 6,144 candidate games against the control and five references, plus 5,120 matched control games against those references. Every map was played from both sides. No alternate candidate was tested on the final cohort.

| Fresh gate | Observation | Result |
|---|---|---|
| Positive direct score | 521 wins, 503 losses | Pass |
| Direct paired-map significance | 123 maps won from both sides; 114 lost from both sides; p = **0.603397** | **Fail** |
| Positive matched-panel mean and map direction | +114 game scores; 194 positive maps, 165 negative, 153 neutral | Pass |
| Panel map-direction significance | p = **0.139357** | **Fail** |
| No reference regression beyond 2 pp | All five deltas positive | Pass |
| All-side reported faults/reinitializations | 0 / 0 | Pass |

Both significance gates required a two-sided map-grouped sign-test p-value below 0.05. Sides and opponents are correlated; the tests group their observations by map. The result concerns the complete four-feature package, without a fresh per-feature ablation.

| Fixed reference | Fresh candidate win score | Control win score | Delta |
|---|---:|---:|---:|
| spar11 | 864 | 834 | +2.93 pp |
| spar12 | 907 | 893 | +1.37 pp |
| spar16 | 867 | 836 | +3.03 pp |
| challenge_fastbank | 533 | 500 | +3.22 pp |
| challenge_brawl | 638 | 632 | +0.59 pp |

Each reference comparison contains 1,024 candidate games and 1,024 matched control games. The three spars are older fixed bots; the two challengers are fixed parameter-style probes. They do not represent contemporary top ladder teams.

Zero reported faults does not mean error-free execution. Across both teams in the 11,264 fresh games, the independent audit counted **394,171 caught-error log samples** and **15,307 logged low-fuel samples**. These are samples, not distinct causes or failed-game counts. Policy activity counters are sampled cumulative maxima and provide lower bounds; a death after camp activity does not establish its cause.

The frozen sources, ordered WASMs, maps, runtime, coverage, chronology, and seven gate decisions were independently checked against the final verdict. The audit and failed verdict are included in the [review bundle](../../analysis/study27-economy/v2/README.md). One procedural distribution and fixed local opponents cannot prove performance on every unseen tournament map or the current ladder.
