# t10plan-v12 (2026-10-28 ~22:30 UTC): synchronized engage + one waiter per reward — STILL BROKEN (2-5/140 vs kvvl); closes the block line

Zips (src/ as v11g + changes below; sha256 in `zips/SHA256SUMS`):
- `zips/e1foco-t10plan-v12.zip` sha256 `e3c2a2686be4f64217716016b6cba96ba3aaed39e754cf5961f174341cbbe6ff`, diff `src/t10plan-v12_vs_v11g.diff` (144 lines: main.cpp, v9.h, params.h)
- `zips/e1foco-t10plan-v12b.zip` sha256 `75420513385164f3428b6e4893ca7162c9724b6bca523b524233e5e7ec086dc0`, diff `src/t10plan-v12b_vs_v12.diff` (unseen members claiming the target are waited for)
- `zips/e1foco-t10plan-v12c.zip` sha256 `3d818cf6c34cb2e7310049e29326f01c987b52d3ce04d9559bed0e68955d532d`, diff `src/t10plan-v12c_vs_v12b.diff` (`P_V12_SYNC_WAIT` 6 -> 12)

All under `P_V12` (params.h) on top of `P_V11`; nothing runs before r30 or in init (same gate `v9::active()` / the v11 rally block);
draft, shop, per-champion micro and fight.h untouched. One line per firing: `[v12-sync] r= ch= grp= wait= n=arrived/wanted` (first
go per target), `[v12-next] r= ch= grp= prev= d=`; status line `v12=<syncs>/<nexts>`. Fuel markers: 0.

## 1. Measurement first (an/sync.py, an/where.py, an/member.py, an/phase_by_n.py on dec/v11gk, 280 games = 70 maps x 2 sides x 2 name sets)

Gold-group captures (gold >= 20, r <= 600) of ours, hitting phase = first hit (episode <= 15 apart) -> group dead (first round `gs==2`).

| v11g | |
|---|---|
| gold captures / game | 5.95 |
| hitting phase mean / median | 12.0 / 10 |
| first hit -> capture mean / median | 22.3 / 18 |
| hitters per hitting round 0 / 1 / 2 / 3 / 4+ | 12.5% / 48.7% / 22.1% / 12.7% / 4.0% |
| members that hit per capture, mean / median | **2.0 / 2** |
| arrival spread (member's first hit - block's first hit), mean / median | 4.0 / 1 (hist: 0:1570 1:164 2:176 3:198 4:212 5:188 6:170 7:106 8:84 9:76 10+:442) |
| last member's arrival after the block's first hit (captures with 2+ hitters), mean / median | **9.2 / 7** |
| where our alive champions are during a hitting phase (champion-rounds): hitting / <=4 not hitting / 5-10 / 11-20 / >20 / dead | 32.5 / 16.1 / 20.4 / 16.1 / 9.6 / 5.4% |
| same at the block's first hit | 22.9 / 18.5 / 27.9 / 16.3 / 9.7 / 4.7% |

Phase length by the number of our members that hit (v11g): 1 member 8.4 (hitter-rounds 7), 2 members 14.6 (17), 3 members 15.1 (26),
4 members 19.5 (40). By camps in the group: 1 camp 5.9, 2 camps 7.8, 3 camps 13.1, 4 camps 18.7. The phase is set by the group's
total hp (a 4-camp gold group takes ~40 hitter-rounds = 10 rounds with 4 perfectly synchronized bodies), and the 4-body captures are the
4-camp groups.

## 2. Change (v12)
1. *Synchronized engage* (farm, inside the v11 rally block): `want` = alive block members (not recalling, not on the spawn) whose claim is my
   target (v12: only the seen ones; v12b/c: unseen too, counted as not arrived), `arrived` = those within camp range + `P_V12_SYNC_D` (2) of a
   live camp of the group. Nobody hits until arrived >= want, capped at `P_V12_SYNC_WAIT` rounds (6; v12c 12) from the first arrival, holding
   at the v11 ring (ar+1..ar+2). Sticky per target as in v11f (`g_go_t`). Once going, every member hits the lowest-health live camp of the group
   (the in-range override of the camp choice is off).
2. *One waiter* (reward on the ground): the nearest member (v11f rule) waits; every other member locks the next live group within
   `P_V12_NEXT` (16) of the captured one, nearest to its centre (the same for all), as its target (`s.target`, claim written) and walks. The waiter
   keeps the reward group in choose_target (`g_v12_wait`) until it is captured; a follower keeps its locked next group (`g_v12_next`) until
   it dies / the leader claims it; a leader back from a reward adopts the live group the others claim (`[v11-pick] ... adopt=`).
   First build: each member picked the next group nearest to ITSELF (the block split four ways at r62 of ambush); fixed before the bench.

## 3. Numbers (70 maps x 2 sides vs kvvl; an/sync.py, an/synclines.py, an/v11an.py, an/missing.py)

| | v11g (280 g.) | **v12** | v12b | v12c |
|---|---|---|---|---|
| wins vs kvvl | 7/140 | **2/140** | 5/140 | 2/140 |
| hitting phase mean / median | 12.0 / 10 | 11.6 / 9 | 11.6 / 9 | 11.9 / 9 |
| hitters per hitting round 0/1/2/3/4+ (%) | 12.5/48.7/22.1/12.7/4.0 | 10.2/49.9/23.5/12.1/4.4 | 13.5/49.6/21.1/11.4/4.5 | 13.6/48.2/21.9/11.6/4.6 |
| members that hit per capture | 2.0 | 2.0 | 1.9 | 2.0 |
| last arrival after the first hit, mean / median | 9.2 / 7 | 9.2 / 6 | 8.0 / 6 | 8.0 / 5 |
| first hit -> capture mean / median | 22.3 / 18 | 24.5 / 18 | 24.5 / 18 | 24.8 / 18 |
| gold captures / game | 5.95 | 6.04 | 5.84 | 5.81 |
| captures <= 600 (v11an) | 20.9 | 18.6 | 18.8 | 18.0 |
| gems banked r300 / r600 | 86 / 170 | 91 / 179 | 88 / 181 | 87 / 167 |
| deaths r151-600 (3+ rivals) / 1-vs-N | 2.57 (1.01) / 1.23 | 3.74 (1.13) / 1.72 | 3.69 (1.17) / 1.57 | 3.70 (1.00) / 1.59 |
| block cohesion r50-600 | 56.4% | 46.7% | 47.7% | 49.7% |
| [v12-sync] / [v12-next] lines a game (r<=600) | — | 48.2 / 42.0 | 47.8 / 44.5 | 45.2 / 43.0 |
| sync fired by the cap (arrived < wanted) | — | 9% | 30% | 19% |
| sync wait = 0 rounds | — | 56% | 42% | 42% |
| idle lines a game rally-hold / capture-hold / capture-reward | 17 / 11 / 12 (v11f-style) | 17.1 / 11.3 / 12.0 | 26.5 / 11.2 / 12.5 | — |

Gates: hitting phase 11.6-11.9 (goal <= 7), captures/600 18-19 (goal >= 28), wins 2-5 (goal >= 40). None moves.

## 4. Why the sync does not change the hitting phase
- v12: `want` counted only seen members, so the sync fired at once (wait 0 in 56%) with whoever was in vision: 35% of the firings had want=1.
- v12b/v12c: the far members are wanted; the cap then fires in 30% / 19% of the syncs. At a capped sync on a gold group the missing members are
  (an/missing.py, v12c after 12 rounds of waiting): 45% at 6-10 tiles of the camp, 30% at 11-20, 17% beyond 20; 2-3% on the spawn, 2% hitting
  another camp. They are walking: the block travels in a line 1 tile a round (ambush_a r44-64: Vesper arrives at d=5 at r52, Marcella / Ryth are
  16 behind and arrive at r62, Ren comes from 25 away after a trip and arrives at r62; the leader waited the 12-round cap). Waiting 6 or 12
  rounds buys 1-2 extra bodies for the first hits but costs the same rounds; the net phase is unchanged and the per-capture duration grows
  (first hit -> capture 22 -> 24.5).
- With 4 members hitting, the phase is 17-21 rounds (39-43 hitter-rounds): those are the 4-camp groups (hp ~4 x 2400), whose floor with 4
  bodies is ~10 rounds. A hitting phase <= 7 for gold groups is only reachable on 1-2 camp groups (5-8 rounds already in v11g).
- The one-waiter rule works as logged (42-44 [v12-next] a game) but splits the block: cohesion 56% -> 47-50%, deaths r151-600 2.6 -> 3.7,
  1-vs-N deaths 1.2 -> 1.6-1.7, the leader walks 25-35 tiles to adopt the others' group; captures/600 do not rise (18-19 vs 20.9).

**Conclusion.** The arrival spread is travel, not a rule: the members are 6-25 tiles apart when the first one reaches a camp and nothing a
per-camp rule can do removes that except waiting, which was tested at 6 and 12 rounds (and in v9/v11 as rally waits) without lowering the
hitting phase. With a synchronized block the phase floor for the 4-camp gold groups is ~10 rounds; with the real spread it is 11-12. Together
with v11-v11g (rally, lock, reward idling, retreat/fight preemption, next-group radius) this closes the block line: the block of 4 captures
5-6 gold groups and 18-21 groups by r600 against kvvl's 33.8 whatever the engage rule.

## 5. Tools (an/)
sync.py TAG (phase / hitters distribution / arrival spread), where.py TAG (where the members are during the phase), member.py TAG (per
champion type: hitting / near-not-hitting (moved, still) / far), phase_by_n.py TAG (phase by members hitting and by camps in the group),
missing.py TAG (where the missing members are at a capped sync), synclines.py TAG ([v12-sync]/[v12-next]/[v11-idle] statistics from stdout).
All read /home/user/ws/{dec,rep}/TAG.
