---
name: cambc-harness
description: 2026-10-15 development harness (harness/README.md in the repo, in English per the user): 4 stages with gates, tools/gate.py, tools/idea.py tracker, online/lfl.py, online/dissect.py; how every thread must record ideas and results
metadata:
  type: project
  modified: 2026-10-15T21:59:54.247Z
---

2026-10-15 ~22:00 UTC the user asked for "AI engineering": too many open fronts, unclear progress. Built the harness
(PR #14 from thread "Harness de desarrollo", MERGED into main 2026-10-15 22:15 UTC: main now holds harness/, online/, tools/gate.py, tools/idea.py). 22:05 UTC the user said "draft it in english":
all harness docs, the board, stage names and tool messages are in English (the repo README stays Spanish); keep it so.
- `harness/README.md`: the pipeline. 1 brainstorm (ideas with a measurable hypothesis) -> 2 one idea = one branch
  `idea/I###-name`, local gate `python3 tools/gate.py bots/study28 main --kind farm|fight|bug --idea I###` -> 3 online
  A/B alternating hourly vs the same top-30 teams, judged by `online/lfl.py --a "<label>" --b "<label>"` (shared
  opponent+map+side pairings, sign test on flips, p<0.05 decides; undecided after 3 h each = rejected unless farm
  with clear local PASS) -> 4 `online/dissect.py --version "<label>" --ref "<old>"` = scorecard.md (same metrics us vs rival
  per game, by map/tier) ending in "Proposals" that feed stage 1. First scorecard (8 games): 28 fuel-exhausted turns/game vs 1 for rivals.
- Gate numbers: farm/macro = fresh maps (hold60+dev200, maps won both sides) in favour p<0.05, safety clean (0 faults,
  0 broken games, fuel k26 not +30 over base), caster panel spar11/12/16 no veto; fight = not worse (local self-play
  cannot judge fights) + no veto, decided online. Combos are gated against their best part, not the base.
- Tracker: `harness/ideas/I###.json` (one file per idea, no merge conflicts) + generated `harness/IDEAS.md`
  (`python3 tools/idea.py board`). Stages idea -> dev -> local-test -> local-ok -> online -> accepted|rejected|paused.
  gate.py --idea and lfl.py --idea record results themselves. Seeded 2026-10-15 with I001-I018 (lineage + open fronts).
- Online scripts now also live in the repo `online/` (data gitignored; live data stays in /mnt/project-files/online/data);
  `online/version.py "<label>"` registers the active version the minute the user activates it.
- Repo tools added: tools/replaydump.js (auto-finds the visualiser wasm; sync stdout so piping works), tools/compact.py,
  tools/mapjson.js, online/mapsj/*.json (9 official maps). Decoding costs ~20 s per online game.
**How to apply:** every thread that tests or ships something records it with `tools/idea.py` (add/set) and quotes
the gate.txt / lfl output; the coordinator's hourly update reads harness/IDEAS.md. The user uploads/activates on the
site; threads never do. Related: [[cambc-ab-tool]] [[cambc-eval-method]] [[cambc-online-ab]] [[cambc-online-loop]]
[[cambc-repo-versioning]]

**Site maps first (user rule 2026-10-16 18:10):** priority to the 17 official site maps, we look for big wins there. Every gate/panel verdict leads with the site-map result, generated maps second. gate.py: SITE MAPS headline, FAIL at 3 net maps lost both sides (--site-veto), panel veto also on site-map flips alone; panel.py prints site, then generated, then all.
