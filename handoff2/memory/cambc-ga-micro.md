---
name: cambc-ga-micro
description: 2026-10-16 genetic algorithm over 22 fight params on study27-economy (tools/ga, PR #19, idea I030): design, cost, fuel-chaos control, how to resume; v100: small unproven edge, caster panel saturated (67-8/85-4/65-9), rivals changed 09:50; 09:56 structure levels 1-3 split to thread 'Evolucionar la estructura de la micro'; 10:38 candidate 65a6d152b6 p=0.003 on v100, gate running
metadata:
  type: project
  modified: 2026-10-16T10:39:05.526Z
---

2026-10-16 08:29 UTC the user asked for "RL for micro" as a genetic algorithm (macro fixed, copied from top teams; NN later).
Built `tools/ga/` on branch claude/ga-micro-vujyq0, draft PR #19, idea I030 (id chosen high to avoid clashes with I019-I022).
- Genome: 22 int genes in tools/ga/genome.py (17 existing P_* fight macros + 5 literals turned into P_GA_*), base = bots/study27-economy
  (copied untracked from fran/study27-economy since main lacked it before PR #17).
- One instrumented wasm (`ga.py prepare`), genome = volatile array with magic 'GAM1'; candidates are byte-patched copies, no build.
  `cambc run` accepts a .wasm path directly.
- Fuel chaos: any code change alters ~18% of games (default genome 111/136 identical to base; identical with `--fuel 10000000`).
  So the GA always compares to a control (default genome, same wasm), never the base build.
- Fitness: 12 fresh maps/gen from 211 training maps, both sides vs study27-economy + spar11/12/16; selection by margin over control,
  shrunk sum/(n+1). Validation v100; sealed hold60/dev200/fresh300. ~2 games/s on 4 cores, 1536 games = ~13 min/gen.
- State in out/ga (container only, lost with the session): state.json, log.md, games.jsonl. Resume: `ga.py run` again after `prepare`
  would change the template offset, so keep out/ga or restart from scratch.
**How to apply:** report results per generation from out/ga/log.md; exported winners go through tools/gate.py then online.
Phase 2 (tiny fight/flee net, weights as genes) only if phase 1 shows headroom. Related: [[cambc-rl-assessment]] [[cambc-harness]]
[[cambc-eval-method]] [[cambc-sparring-v27]]

**09:50 UTC gen 16 on v100:** best genomes only slightly above control (70-54 pairs, p~0.18), others did not hold. Caster panel saturated vs study27-economy (online bot wins 67-8 spar11, 85-4 spar12, 65-9 spar16): no signal near the current bot. GA resumed with harder rivals: spar12 dropped, two best genomes added; base + spar11 + spar16 kept.

**09:56 UTC split:** weight GA keeps running here; a parallel thread "Evolucionar la estructura de la micro" (branch claude/ga-structure, coordinator post cmsg_017gbamt2g1g8hMHRHQBc6qbPQo5wPuHRfieCrrmbVdAuU) builds structure levels: (1) fight switches + rule order as genes (~1 day); (2) genetic programming of the engage/back-off condition as bytecode + tiny in-bot interpreter (3-4 days); (3) NEAT net choosing fight/kite/flee/recall/farm (unlikely before 3 Nov). Best genomes exported to /mnt/project-files/analysis/ga-micro-2026-10-16/genomes/ as rivals for it.

**10:38 UTC first real candidate:** genome 65a6d152b6 beats the online bot on v100 (100 never-trained maps): 134-89 map-rival pairs vs the control (p=0.003), 33-14 maps won both sides vs the online bot, fewer deaths. Changes vs online: P_ENGAGE2 120->74, P_FLEE_PCT 25->29, P_UNI_FLEE 35->44, P_CHASE_GEMS 150->144, P_VOLLEY 70->43, leave spawn at 87% hp instead of 95%. Exported as a normal bot; gate.py running on hold60/dev200/fresh300 + panel (evolution paused meanwhile). Online test is still the judge for fight changes.

**10:43 UTC gate PASS** (65a6d152b6, bots/ga65a6 untracked): sealed 560 maps 180-79 both sides, gems/100r 168.1 vs 160.4, panel flips 36-16,
0 faults, fuel-exhausted 162 vs 140. Zip /mnt/project-files/bot/mybot_ga65a6.zip (not uploaded), doc docs/I030-ga-micro.md.
Ops: kill the GA by pid (`pgrep -f "^python3 tools/ga/ga.py run"`), never `pkill -f` (it killed the calling shell); restart out/ga/go.sh.
**12:09 UTC switched to the farm:** old ga.py run stopped (gen 31, leader 9e94397d24 +0.18 n=5, exported as flat migrant
ga-farm/migrants/micro_*.json; old checkpoint moved to ga-farm/islands/micro-legacy-ga). This thread now runs island `micro`
(tools/ga/island.py, branch claude/ga-farm-d37xlq checked out as worktree /home/user/farm, cambc 2.2.1, --scope micro --jobs 4),
self-wake send_later every 12 min re-running `island.py ensure`. See [[cambc-ga-farm]] if it exists.
**13:40 UTC ops lesson:** the cloud container is reclaimed within minutes after a turn ends (uptime 0 at each wake), so a
keepalive that only runs `ensure` loses the running generation. Each wake now waits in-turn (`timeout 570 tail -f run.log | grep -m2 "gen "`)
and reschedules itself 1 minute later. Gen ~4-5 min at 5-8 games/s.
**17:17 UTC ga5f9d:** farm island micro genome 5f9da0c758 held +0.10 for 19 gens (v100 vs control only 64-48, p=0.16), but
head-to-head gate vs ga65a6 on sealed 560 maps: 161-92 both sides p<0.001, gems/100r 166.3 vs 161.9, panel flips 35-15, PASS.
Includes P_MONO=1. Zip /mnt/project-files/bot/mybot_ga5f9d.zip (not uploaded). Gate must run from the farm worktree:
main-repo tools/ab.py cannot read cambc 2.2 binary --statistics (needs --json). Leaders 2076715ed7/314e9672aa failed v100.

**17:18 UTC:** the user (16:30) considers the GA fight line failed and works from the teammate bot; ga5f9d is on the ga65a6 base, so it is not an upload candidate. Island micro is keep-alive only.
**17:40 UTC:** self-wake loop stopped (base abandoned by user, no value in compute). Island micro checkpointed at gen 57 in ga-farm/islands/micro; resume with `island.py ensure --name micro --scope micro` from the farm worktree if wanted.
