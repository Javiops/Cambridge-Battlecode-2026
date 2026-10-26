---
name: cambc-audit-1021
description: audit verdicts 10-21..10-23: hpshare/goldfarm/goldval/mate-treasure/rally, local-vs-online lesson, gem-margin judge proposal, duplicate-game dedupe rule
metadata:
  type: project
---
- 51-75 diagnosis (10-21): draft base hp ruled out (918 vs 926/unit); rival fields HoR in 77% of our losses vs 57% of wins; the hp gap is the shop (3.0 max hp = spawn + hp shards) -> hpshare-v1.
- goldfarm-v1 268aadf4: one guard (main.cpp:1787 P_GOLDONLY) so gold-only groups are farm targets (1.0.2 rivals take 6.2 gold-only groups by r300 in our losses vs our 2.7).
- 10-21 ONLINE: hpshare-v1 v94 +3/59 changed (bar 15.4), goldfarm-v1 v95 -4: both rejected by the judge. LESSON: local self-play overrates econ/shop changes (40-30, 42-28 -> +3, -4): a local win means no-harm only. hpshare lever moved (deaths 17.85->14.62, paired t -4.2; gem margin +76/g, t 2.7) but flips were low-power. Paired gem-margin t: goldfarm 0.0, vision 0.5, hpshare 2.7, draft-meta 2.8; card to Javier (pass if t>=2, flips>=0, no harm) unanswered.
- 11:14 Javier promoted v94 hpshare-v1 = BASELINE V8 anyway. goldval-v1 4e4cf99a (v94 + P_GOLDONLY + P_GOLD_W_EARLY 25->100, choose_target only, < r940) cleared 11:25; audit flagged: the '11 maps where v94 loses' set is outcome-selected (circular), redefine it by a map feature (gold-only share of nearby camp gold); early gold_w changes mixed-group ranking on all maps.
- 15:58 mate-treasure-v1 ede4af1a (v98 588ba42a + teammate dash/probe/failed-engage fixes + treasure-first, hunk = treasure-v1 82ae10c5) cleared: two ideas in one; dash rewrite hard-codes dash_range 2 / radius 1 and scans a +-2 box although ab.valid_tiles() and ability_dash range/radius come from the engine (follow-up before 30 Oct); lethal-camp escape fired 0 locally. v96 goldval passed +16 (V9), v98 horfocus passed +12 (V10) without audit review.
- 10-23 09:20 rally (deaths thread): rally_ficha.md gaps sent (recall/sweep interactions, online control subset, expected flips, gemLoss indicator) and closed by that thread. Diff vs V17 0fbe0733: rally-v1b clean (P_HELP_R 6->10 has no other live reader; rl_arr = within 4 at trigger; favourable=true bypasses P_ENGAGE2). rally-focus-v1 score change is a no-op for melee (uniform -40 shift) and never touches the rally target (rally overwrites tgt): ranged-only, likely a rider. 09:37 rally CHAIN UNSUPPORTED online (747 losses: mates drift equally, 0.30 vs 0.28; 76/19 was killer-proximity selection) -> per method §3.1 no online batch even if panel17 is positive; rlB3 also +72 gems lost/g.
- 10-23 DUPLICATES: rematches are byte-identical; judge impact small (no verdict changes), judge_pinned.py dedupes copied pairs. See [[cambc-online-duplicates]].
Related: [[cambc-fuelfix-1020]] [[cambc-judge-two-step-1019]]
