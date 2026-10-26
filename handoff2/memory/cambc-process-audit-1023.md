---
name: cambc-process-audit-1023
description: 10-23 audit of the 12 rejected candidates since V15: code did what it said in 7/7, failures = ignored known interactions (gemrace/oro, shootfirst/fight.h:90, sfflp), cutguard bug, unmeasurable changes, underpowered local tests; mechanism-sheet method
metadata:
  type: project
  modified: 2026-10-23T08:56:53.315Z
---
Thread "Por qué nuestras ideas no llegan online" cmsg_017gbamt2g1g8hMHRHQBc6qb4SPY6VkcM5315HRcVUnGt1 (user 10-23 08:33 UTC: "algo se nos escapa; metemos ideas correctas mal y no anticipamos la interacción"). Report: /mnt/project-files/analysis/process-audit-1023/README.md (scripts scratchpad an/pair.py, fuelx.py).

FINDINGS (online paired vs v122, same draw/opp/map/side):
- Mechanism moved as designed in 7/7 measurable candidates (gemrace gems far +20-22%, shootfirst Vesper dmg +62%, hshield HoR shield +75%, idletpc idle -80%). Implementation is NOT the main failure.
- Known interactions ignored: gemrace-v4/v7 paid gold@400 -12%/-6% (rule "early gold = fight power" since 10-21); shootfirst roots Vesper every round she shoots (fight.h:90 "Measured: a ranged champion that attacks can no longer move this turn") -> Vesper deaths +0.2 (v124), +0.9 stacked with flpoke (v126 near 22/29).
- VERIFIED BUG cutguard (fixpack v125): fuelExhausted 4.7->6.2/g; replay a0efb96f big_world: Vesper frozen at (28,19) full hp from r500, no status lines r500-775 (fuel_ok(12000) fails with reserve 40000), r775 probe-exhausted target=-1, 236 cuts on alternate rounds r525-1329. Loop: cut -> reserve 40000 -> all fuel_ok fail -> cut again -> cut_until renewed forever. NEVER stack cutguard.
- Noise/drift/unmeasurable: stay (5 lines, ~1% decisions), mega-far (-7 with 5 in identical near maps), flpoke (control subset 16/3 = drift), mega (base hot .617).
- Lines closed on underpowered tests: rally-v1 -6/-2 in 52 mirror games, rlf 23-29, open32 26 maps -> "unresolved", not negative. Micro r50-75 hypothesis (mates converge 76% vs 19%) still open.
- idletpc far: Vesper dmg@400 -39%, deaths 0.9->1.9 (40 pairs, no replays): unverifiable because the rule leaves no counter.
- Since V15: 12 online candidates, 2 passes (both power changes +10..+20/100); everything else expected +0..+6 < batch noise ±5.

METHOD (mechanism sheet before panel): causal chain with an online number; exposure count (farm thread tracer); interaction list (flee 33/29, kite step-first, recall, gold->shop->power, fuel_ok guards); counter in status line for every new rule; 80g vs pHuntF checking 6 side-effect gauges (gold@400, deaths, Vesper deaths, fuelx, first 20+ capture, clears@400); no line closed under 300 paired games; online control subset; expected < +6/120 -> stack, never a lone batch; stacked rules of the same turn tested together first.
EXPOSURE TRACER (farm thread 09:55 UTC, orch/RESULTS.md): P_XP 1 build scores groups with base+cand pricing, prints [xp]/[xp-trig], xp=changed/calls in status line; 40g vs pHuntF. stay-v1 22.6/515 changed (4.4%, 64% after r400, no cascade) -> effect ~0; idlerush fires in 4/40 games. Standard: report changed/game, % by phase, maps with 0, mode 25 rounds later; refuse <~50 changed/game unless a fight/death rule.
TIME BUDGET (farm thread 10:35 UTC, online-far/timebudget.py): v122 vs ranks 26-75 same games: dead 9.0 vs 9.0%, fight 12.2 vs 12.6, camp 35.5 vs 35.3, walk 30.5 vs 30.3, wait 9.0 vs 8.9; gold +31% us, gems equal -> we mirror our rivals; loser dead 12.5% vs winner 5.4%: deaths decide. Top-10 vs top-10: gems/round +18% vs us, gold/round -12%, fight 10.6 vs 12.2%, dead 8.0 vs 9.0. Farm/pathing candidates aimed at a dimension already equal. Gem-first+fight-avoidance combo KILLED 09:20 UTC by capture accounting: with gold@400 fixed, gems@400 does not predict wins (958 games; gold+gems- 51%, gold-gems+ 44%); kill speed and squad size equal rivals/top10; we take more <10-gem captures (19.5 vs 13.7/11.5). Farm line exhausted on data; deaths decide.
USER 10-23 09:09 UTC: 'aplica el metodo a todos los hilos y reabrimos rally' -> method mandatory everywhere; rally-v1 reopened (deaths thread). Exposure tracer packaged for all threads: /mnt/project-files/tools/exposure/ (README, xp_scaffold.py, run_xp.sh, xp_parse.py).
Related: [[cambc-panel-v16-1022]] [[cambc-farm-macro-1021]] [[cambc-fight-model-1022]] [[cambc-idle-wallmaps-1023]]
