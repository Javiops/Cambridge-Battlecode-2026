---
name: cambc-ga-macro
description: 2026-10-16 macro/economy GA (idea I040, PR #24, tools/ga/mga.py + macro_genome.py + cousins.py): 48 genes on ga65a6 (v44), unlimited-fuel training, site-map cousins; how to run/resume
metadata:
  type: project
  modified: 2026-10-16T11:52:53.218Z
---

2026-10-16 11:38 UTC thread "macro genome" (coordinator: go all in on the genetic path). Branch claude/ga-macro-aa5r2c, draft PR #24, doc docs/I040-ga-macro.md (copy /mnt/project-files/analysis/ga-macro-2026-10-16/README.md).
- Base bots/ga65a6 (untracked) = study27-economy (main, P_MONO) + fight genome 65a6d152b6 = online v44; `mga.py base` rebuilds it.
- Genome tools/ga/macro_genome.py: 48 genes (camp choice, stacking, banking/chain, recall trips, shop, draft P_UNI_PATH), magic 'GAM2'; reuses ga.py from PR #19 unchanged via monkeypatch (ga.G, json shim for cambc 2.2 stats, `--json`, MGA_FUEL adds `--fuel`).
- Default genome == base: 102/102 identical games with `--fuel 10000000`; with normal fuel 43/102 differ (fuel chaos). So training runs with MGA_FUEL=10000000; validation/gate with normal fuel. Cache keys ignore fuel: never mix fuel modes in one work dir.
- Training pool adds 204 site-map cousins (/mnt/project-files/arena/maps/cousins, tools/ga/cousins.py; mapjson.js read -> mkmap.js write; editor stores each camp once and mirrors it, identity check 17/17).
- Opps: ga65a6 (weight 2), spar11, spar16; pop 16, 12 maps/gen, 1152 games/gen. State out/mga (container only), restart out/mga/go.sh. Kill by pid, never `pgrep -f "mga.py run"` inside a loop in the same shell (killed the shell).
- PR #18 switches not included (branch on older main).
**How to apply:** results in out/mga/log.md; winners -> `mga.py validate` (v100) -> export -> gate.py vs ga65a6. Related: [[cambc-ga-micro]] [[cambc-ga-structure]] [[cambc-online-is-economy]]

**Container lesson (12:31 UTC):** the thread container is reclaimed within minutes of the session going idle (uptime 0, files kept, processes gone). A long-running job survives only while a `run_in_background` Bash task of the session is alive: keep one waiting on the next N generations, and restore with /mnt/project-files/ga-farm/islands/macro/restore.sh when it died.

**Run 1 result (13:10 UTC):** fitness base x2 + spar11 + spar16 -> best 0abaecb2ec: v100 81-42 pairs vs control (p=0.001) but only 32-28 vs the base itself (gains all vs casters 84-2); gate vs ga65a6 FAIL 6-19, gems/100r 172 vs 177. Lesson: the caster panel is saturated and dominates fitness; judge macro on head-to-head vs the online bot. Run 2 (out/mga2): base bots/v44x = online zip mybot_ga65a6_mono_fuelguard_jackpot.zip (copy in islands/macro/base_v44x.zip), rivals base x3 + spar16, 16 maps/gen, 50 genes (+P_JACKPOT). Even with the fuel guard, normal fuel changes 22/68 games.

**Run 2 check (14:20 UTC):** gen-18 leaders (+0.10 in training) tie the base on v100 (38-37 pairs normal fuel, 44-45 unlimited, gems/100r -0.5..+1.6 ±1.1): winner's curse from 16 maps/gen, not fuel. Continued with pop 12 x 40 maps/gen (out/mga2/go.sh). No zip yet.

**Run 3 (15:20 UTC):** run 2 leader 378af7382f (led gens 27-30, n=6) on v100 normal fuel: pairs 47-42 p=0.67, vs v44x 21-31 (worse), vs spar16 80-1: gains are again caster-only. Run 2 stopped (state in islands/macro/run2/). Run 3 = out/mga3, rival v44x only, pop 12 x 40 maps, seeded with run 2's top 11; restore.sh/sync.sh now point at mga3. Never `pkill -f` a pattern that appears in your own command line (killed the shell twice).
**Run 3 result (17:05 UTC):** leader c5e3448391 = first macro win. gate bots/gamacro3 vs v44x PASS (fresh 32-13, gems/100r 175 vs 167, panel 21-29 ok). Ported onto the v49 online zip (mybot_online1252_jackgo_imp.zip, bots/v49): gamacro3p fresh 81-47 p=0.003 but caster panel 11-33 VETO. Zips in /mnt/project-files/bot/mybot_gamacro3{,p}.zip, not cleared. Ablation by gene group (bots/abl_*, out/abl/*.log) to find the caster cost. Recorded as I040.
**17:45 UTC:** v49 panel veto is spread over all gene groups (ablation). On the teammate base bots/capture_fix (user's new base since 16:30): gamacro3m PASS farm (fresh 57-31 p=0.007 with fresh300, 92-67 p=0.057 without; gems 172 vs 168; panel 17-30 no veto) but 8 of 17 site maps lost both sides. Zip mybot_gamacro3m.zip, not uploaded.
