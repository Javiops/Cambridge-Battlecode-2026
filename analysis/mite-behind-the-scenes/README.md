# What Mite does off-screen (2026-10-15, 11:15 UTC)

Question: our clones of Mite's visible rules do not reproduce its strength. What is Mite doing in preparation or
behind the scenes? Four measurements, all from public data (the 54 Mite games decoded for the dissection, the public
match list of the last 13.5 hours, and 18 study25 games played locally on the same 9 maps for comparison).

## 1. Mite's play on the known maps is a fixed script, not a decision engine

For each map, Mite's champion positions were compared round by round between its games against different top-20
opponents (same side; `scripts/prep.py`). The first round where two games differ:

| map | first divergence between games (same side) |
|---|---|
| rows | 103, 103, 125, 125, 290, 369 (two games identical for 369 rounds, almost the whole game) |
| monolith | 92, 92, 93, 93, 100, 120 |
| expanse | 16, 80, 80, 80, 172, 289 |
| lanes | 43, 43, 54, 54, 58, 80 |
| interlock | 6, 6, 31, 31, 37, 41 |
| collision | 30, 30, 36, 36, 38, 45 |
| packs | 26, 26, 27, 27, 33 |
| corners | 18, 18, 18, 19, 20 |
| elkring | 4, 4, 44, 47, 65 |

Mite does exactly the same thing against #2, #3, #4, #5, #7 and #8 until the enemy touches it (on farm maps for
100-370 rounds). Its draft is also fixed per map (one draft in all 6 games on every map). Univardisty, by contrast,
diverges at round 1 on most maps (random draft each game, play depends on it). So Mite's edge on the ladder is a
hand-tuned plan per known map (route, draft, who goes where), prepared offline and polished with the testing in point 2.
This matters for us: qualifying maps are new ([[cambc-new-maps-rule]]), and nothing here shows how Mite would read a map
it has never seen. Its 1859 rating is earned on 9 maps it has scripted.

## 2. Mite tests online at industrial scale, around the clock

Public match groups (`scripts/crawl.py`, 20,743 groups from 2026-10-14 21:32 to 10-15 10:57 UTC, `data/groups.jsonl.gz`):

| team | unranked groups in 13.5 h | started by them (side a) | map games won-lost | groups per hour |
|---|---|---|---|---|
| Mite (#1) | 1244 | 360 | 5103-1116 (82%) | 40-123, every hour of the night |
| hello (#3) | 904 | | | 48-102 |
| Univardisty (#7 now) | 1011 | | | 33-115 |
| Intercontinental Fish (#2) | 340 | | | 12-46 |
| us | 96 | 50 | 235-245 | |

Each group is 5 maps. Mite itself starts about 27 challenge groups per hour (135 games) against the top teams
(Univardisty 89 groups, hello 71, #15 69, VeryGood 47, procless 33...), continuously since at least yesterday evening,
which only an automated script does. On top of that, 884 groups per 13.5 h are other teams challenging Mite: the whole
ladder tunes against it, and Mite gets 6,000 games of data on its active version per day for free. We played 96 groups.
Versions and submission ids are not public, so how often they upload cannot be read from the API.

## 3. Camp kill speed: Mite puts two champions on every camp, we put one and a half

From every capture in the decoded games (`scripts/stack2.py`; Mite 1344 captures in 54 games vs top-20 teams,
study25 451 captures in 18 games vs study24):

| camp group hp | Mite attackers | Mite hit-to-capture | study25 attackers | study25 hit-to-capture | damage per attacker-round (Mite / us) |
|---|---|---|---|---|---|
| < 800 | 2.0 | 12 rounds | 1.2 | 14 | 23 / 32 |
| 800-1500 | 2.05 | 17 | 1.5 | 23 | 42 / 42 |
| 1500-3000 | 2.4 | 21 | 1.9 | 24 | 48 / 57 |
| >= 3000 | 3.5 | 23 | 2.6 | 24 | 51 / 71 |
| first 50 rounds | 3.2 | 15 | 1.85 | 20 | |

Damage per attacker-round is the same or better for us, so the micro is not the gap: Mite simply sends two champions
to every camp (three or four to groups over 3000 hp, the whole team to the first camp) and clears each group 5-6 rounds
faster. Its rule, as measured: attackers = 2 for anything under 3000 hp, 3-4 above, whole team before round 50; the
number does not depend on distance from spawn or on the round. At the capture tick only one or two are still within 4
tiles (the others have already left for the next camp). Captures per champion-round alive are equal (Mite 1.13 per
100, study25 1.10 per 100), so our farm engine keeps up on the maps measured here; the point is that Mite keeps up while
also losing fewer champions.

## 4. Walking is not the gap; idling is not the gap

Moves made between purpose points (capture, tribute, recall arrival) vs the shortest path (`scripts/walk.py`):
Mite 0.75 (4.0 extra moves per leg), Univardisty 0.59, study25 0.80 (3.5 extra). Our champions walk straighter than
Mite's. Champion-rounds with no action at all: Mite 18%, Univardisty 16%, study25 18%. "Never looks lost" is not
visible as idle time or detours; what differs is that Mite's champions are always walking to a scripted next camp,
and ours decide each round, which is only a problem when the decision changes (the retarget flip-flops other threads
have seen).

## What this means for us

1. The strength we cannot copy from replays is preparation: a plan per known map and ~6,000 online games a day to
   polish it. Mite is unlikely to carry the same edge onto new qualifying maps; a general engine like ours could.
2. The one mechanical rule worth copying is the squad size: 2 per camp (3-4 on 3000+ hp groups, everyone on the first
   camp). The "Read the map" thread is building exactly this; the numbers above are its target.
3. If we want Mite's kind of data, the challenge API lets a logged-in web session start unranked groups
   ([[cambc-site-access]]: `POST /api/v1/challenges`, quota per hour); our 96 groups vs their 1244 is the real gap in
   preparation. That needs the user's browser session; the CLI token cannot start challenges.

Files: `scripts/` (prep.py trajectory comparison, stack2.py squad/kill speed, walk.py walking efficiency, crawl.py +
versions.py match-list crawl), `data/` (ladder.json, groups.jsonl.gz, captures_mite.json).
