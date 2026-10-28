# t10plan-v11g (2026-10-28 ~21:30 UTC): no retreat / fight preemption inside a block capture — STILL BROKEN (7/140 vs kvvl)

Zip `zips/e1foco-t10plan-v11g.zip` sha256 `12550f52dca214323a03395704197ce9dd2aabff5aafe853f7769168b2694616`, diff `src/t10plan-v11g_vs_v11f.diff`
(90 lines: main.cpp, v9.h, params.h). Variant v11g2 (`zips/e1foco-t10plan-v11g2.zip` sha256 `8cb344b0344a42c6b6edd94a175e6c80ac873af11dc1a6b63462922a129f8a40`,
diff `src/t10plan-v11g2_vs_v11g.diff`): v11g + the non-capturing members walk to the next group within 16 tiles instead of 10 (`P_V11G_NEXT`).
New tool `an/nopre.py TAG`: every round with 0 hitters inside a gold-group capture (20+ gold, first hit -> capture, r<=600) classified
against the decoded state and the stdout episode lines ([v9-retreat]/[v9-fight]/[v11-retreat], which persist per champion until no
rival within 8; [v11-idle] reasons of that round).

Bench of this session: cambc 4.0.0 engine, kvvl = k_vvl_mgwp v164 (handoff/fuelfit-farm/rivals/kvvl.zip), maps = pcassets/maps70 (70 x 2 sides).
v11f and v11g were also played on the 70 platform-named copies of the same maps (280 games); the table gives the 70-map subset.

## 1. Diagnosis (v11f replays, an/nopre.py: 879 captures, 19480 rounds, 9883 with 0 hitters = 50.7%)

| share of the 0-hitter rounds | v11f |
|---|---|
| group already dead, reward on the ground, 5-7 round engine capture wait (`gs=reward_available`) | **66.1%** |
| members <=6 of the camp walking, no rival within 6, no idle line (approach / change of camp) | 12.5% |
| no member within 6 of any camp of the group | 6.7% |
| [v9-retreat] episode (rival within 6) | 4.3% (+0.4% with no rival within 6) |
| [v9-fight] episode | 3.2% (+0.2%) |
| [v11-retreat] episode | 1.4% (+0.1%) |
| member <=6 standing still, no rival, no idle line | 2.2% |
| rival within 6, no episode line (campfoe / avoid / kite) | 1.6% |
| rally-hold / solo-hold / capture-* idle lines | 0.7 / 0.4 / 0.2% |

So retreat + fight + v11-retreat explain **9.6% of the 0-hitter rounds (4.9% of all capture rounds)**, rally-hold 0.7%. The dominant
"0 hitters" is the engine's capture wait: a gold-group capture of 17 rounds (median) is ~10-11 rounds of hitting + 6-7 rounds of
reward wait, and only 1 member can stand on the tiles. Excluding the reward wait, 25.9% of the hitting rounds have 0 hitters, 7.4 points
of them retreat/fight, 9.5 walking, 5.1 nobody near. The "52% 0-hitter" number of v11e/v11f is mostly this mechanical wait; the diagnosis
"retreat/fight preemption is the dominant cause" is not confirmed.

## 2. Change (v11g, under P_V11)

main.cpp before step 3 (fight): `v11g_skip` = v11 on, in the block, not on spawn, a rival within 8, `s.target` = the locked target whose
rally condition was met (`v9::g_go_t == s.target`), and me within `P_V11G_D` (4) of a camp of that group. Real threat = 2+ rivals within 6
with more rivals than us (me + block members within 6), or hp < `P_V11G_HP` (30%). Without a real threat the whole step 3 (v9 fight /
retreat, v11-retreat, pv verdict, kite, engage) and the campfoe branch are skipped: the champion goes on to recall/farm (hits the
monster). One line per episode: `[v11g-nopreempt] r=.. ch=.. grp=.. m=.. n=.. hp=.. dc=..` (31 lines a game); status line `np=` count.
Nothing runs before r30 or in init (the gate is `v9::v11_on(round)`); draft, shop and fight.h untouched. Fuel markers: 0.

## 3. Numbers (an/nopre.py, an/v11an.py)

| | v11f | **v11g** | v11g2 |
|---|---|---|---|
| wins vs kvvl (70 maps x 2) | 8/140 | **7/140** | 4/140 |
| 0-hitter share of gold-capture rounds (all / excluding reward wait) | 50.7% / 25.9% | 50.8% / 25.4% | 49.5% / 23.5% |
| retreat+fight+v11-retreat share of capture rounds | 4.9% | **2.6%** | 2.9% |
| nobody within 6 / walking / still (share of capture rounds) | 3.4 / 6.3 / 1.1% | 4.8 / 6.3 / 1.5% | 4.9 / 5.4 / 0.8% |
| rounds first hit -> gold capture, mean / median | 18.4 / 17 | 18.5 / 18 | 18.1 / 17 |
| gold-group captures / game (<=600) | 5.47 | 5.42 | 5.34 |
| captures <=600 / gems banked r300 / r600 | 20.7 / 91 / 195 | 20.9 / 86 / 170 | 20.6 / 88 / 175 |
| deaths r151-600 (3+ rivals <=6) / 1-vs-N | 2.32 (0.79) / 1.10 | 2.57 (1.01) / 1.23 | 2.56 (0.86) / 1.24 |
| block cohesion r50-600 | 56.3% | 56.4% | 54.7% |
| [v9-retreat] / [v9-fight] lines a game | 89.7 / 55.3 | 77.2 / 44.3 | 82.2 / 45.6 |

Gates: wins < 40 (broken, like v11-v11f); 0-hitter share unchanged (the preempted rounds became "nobody near" / "still" rounds, not hits);
capture duration unchanged (the hitting phase is 11-12 rounds for 4 bodies against groups of 20+ gold, plus 6-7 of engine wait).

## 4. Why the v11 line loses locally (dec/v11fk, 140 games, means per game)
kvvl: 33.8 captures and 323 gems by r600; us: 20.7 and 204 (r150: 42 vs 37, r300: 120 vs 91). Dead champion-rounds r151-600 120 vs 134.
One block of 4 captures one group at a time (5.4 gold groups and 20 captures by r600) while kvvl farms with 5 bodies in parallel; the
block is not slower per capture than the top 5 (17-18 rounds including the 6-7 wait) but captures 40% fewer groups. The local bench
cannot be passed by the block design against a parallel farmer; what it still shows is that no per-champion rule inside the capture
(reward idling v11f, rally ring v11f, retreat/fight v11g, next-group radius v11g2) changes captures, gems or deaths.
