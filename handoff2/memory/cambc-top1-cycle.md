---
name: cambc-top1-cycle
description: 2026-10-15 study of how #1 Mite / #2 Univardisty farm (camp set, recall as teleport, no fixed loop), distance-only map evaluator, P_FEAT rule port, P_CAPRECALL 1 candidate
metadata:
  type: project
  modified: 2026-10-15T09:14:56.412Z
---

2026-10-15 08:27 UTC the user asked: evaluate maps from distances/resources instead of map types; test their hypothesis
"optimal farm route followed, reset (recall), repeated as a cycle". Ladder 08:22: Mite 1834 is #1, Univardisty #2.
Report: /mnt/project-files/analysis/top1-cycle-2026-10-15/README.md (scripts, data/compact.tgz, maps_gen4 = 60 new
gen maps seed 77, bot-feat/src). Also pushed to repo branch claude/project-thread-6vekv3 (analysis/top1-cycle).

**Findings (101 games vs top 20):** fixed camp SET on own side (never enemy half, never monoliths, rarely elk/gold),
order = nearest camp that is up (38-41% top-1 vs 6% random; own-loop predictors <=36%), revisits respawn+25-45.
Recall is a computed teleport: rows 53/53 recall after capture when 5+home->altar < walk; expanse/lanes/packs recall
on the capture tile; fight maps walk. Kills 9-17 rounds per camp (2-3 champs). Evaluator gems/(home->camp+hp/150+5+
min(altar walk,5+home->altar)), own side, >=0.5 -> matches Mite's farmed set 88% (Uni 84%, baseline 71%).
study24's camp scoring is already this model; its camp set/revisits look like Mite's.

**Bot tests:** study24's 7 fingerprint rules (de_rules.h) worth 14-4 on known maps, never fire on new ones.
P_FEAT (distance versions) on 44 gen maps vs study24: rows/lanes/fight rules neutral; expanse bank-cost rule as
"farm map" loses 24-64 (P_BANKX 100/200 also lose). Single games are chaotic (an init-fuel-only change flipped 5/18).
Tools in ws: tools/pacecmp.py (solo pace on 113 maps), tools/ab.sh (h2h + sign test).
**Candidate:** study24 + P_CAPRECALL 1 everywhere = bot/mybot_study24_caprecall.zip: pace faster on all sets,
h2h vs study24 official 12-6, gen 45-43, gen4 59-61, sparring 46-8 (study24 47-7). Not uploaded; user decides.
**09:50 UTC 9/9 strategy card** (user: goal = map->strategy matching Mite 9/9, bot results irrelevant): analysis/top1-cycle-2026-10-15/strategy-card.md,
scripts/card.py. Fight d<=45; draft by nch + sa(home->altar)<=8 casters; bank recall if home->altar < camp->altar (81% captures);
camp set strategy5 (dmg weight 3, cut 0.55/0.25 x median of nch best) 9/9 but fragile (232/108k combos, leave-one-map-out ~6/9).
**User 2026-10-15: keep recall-while-capturing in every future bot/plan. mybot_study25.zip (P_CAPRECALL 2) supersedes my caprecall zip: same code, level 2 also recalls on the tiles at hp<90% or 90+ gold.**
**10:30 study25 + card rules all lose** (maps both sides gen/hold60): P_TELE -5 3/18, 8/11; P_DMGW 300 3/26, 10/34; P_DRAFTMITE 1 9/17, 15/20; all 2/31. Source bot-st25-card/. Card = description, not transferable habits.
**10:25 key fact:** study25 alone already farms all 41 Mite core camps (card set 8/9 maps); banked by r300 >= Mite's median on 8/9 maps (mirror too on farm maps). Farm plan is not the gap vs Mite; fights are. P_TELE 1 also no win (gen 2/9).
**10:35 online vs Mite (09:39 games, pre-study25; ws/vsmite budget.py):** gap = kill speed from squad size: rows 3-wolf 20r/2.3 champs vs Mite 15r/2.9; lanes gems 6r/1.6 vs 4r/2.1; monolith wolf 17r/1.4 vs 10r/1.8. Same camps, same teleport share 4%.
**10:55 stacking test (user ask):** P_MAX_SHARE 4 / P_SHAREEXP (joiner value gems/team^x) / P_STACK_HP on study25 (bot-st25-card/src): rows solo 436->392, lanes 336->321, but expanse/monolith/elkring slower; best sq8 looked +13 on hold60 but 25/28 on 100 new maps (maps_v100 seed 1015). No win.
Related: [[cambc-top1-study]] [[cambc-user-draft-route]] [[cambc-new-maps-rule]] [[cambc-teammate-bot]] [[cambc-farm-speed]]
