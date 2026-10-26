---
name: cambc-spacing-1019
description: 2026-10-19 top-30 diagnosis (top30_diag_1019.md): same-situation deaths are structural; travel/respawn + lone hurt champions = biggest death slices; audit held hurt-team-event and asked for a spacing (nearest-ally) measurement
metadata:
  type: project
---
21:10 UTC top30_diag_1019.md (decoded only: v65 vs 1-10, v72 vs 13-29, v76 vs 13-30, plus 71-95): in losses captures ~80% of margin, 55-60% of it time dead. Wins vs top come from kill transfers (their hurt champs carry 17-18 gems, ours 8-9).
STRUCTURAL: our death rate 11-13%/contact round and 41%/hurt episode in every pool+version; top-30 3-6%/14%; 71-95 8-9%/29%. Their hurt champ gains 3.4 tiles/3 rounds, recalls 44%; ours 1.6, 30%, trades down to 29-33% flee line (main.cpp:3016-3036, 3271-3315; fight.h:228). Lone hurt champ (no ally within 6) dies 54% vs 17%. Travel+respawn contacts = 3.2 of 5.1 deaths/game gap. team-fight-v1 vs top 30 moved finishing only.
API proposal hurt-champion-team-event: Expected -0.3 to -0.6 deaths vs top 30 -> AUDIT HELD 21:15 (under user's >=1 death bar; overlaps failed leave rules retreat-api-v1/escape-v1). Asked: nearest-ally distance at contact by situation (both sides, both pools); travel/respawn deaths by alone/hp/gems/initiator/place; how their travellers move/regroup; cohesion cost in wolves. If spacing explains both slices -> spacing doctrine system; judge pool to Javier if effect is top-only.
See [[cambc-elk-feasibility-1019]], [[cambc-power-at-contact-1019]].
21:14 UTC SPACING RULED OUT: nearest ally at contact ours/theirs travel 5.1/4.7, farming 3.7/4.1, respawn 5.6/3.8, hurt 6.3/5.1; equal-spacing gap persists; their cohesion = ours, no wolf cost. Travel/respawn deaths 5.62 vs 1.83/game: 94% at 85%+ hp, 82% vs ONE rival, 68% with ally near, WE CLOSE FIRST 32% vs 13% -> residual = full-hp 1v1s we start and lose (~3.5 of 5.1). NEXT (no design): matchup, engage path + its win rate, first-3-round damage/spells, could loser leave. Audit added: cooldowns at contact start, turn order, third parties, per-path win rate, fit with user's P_NOCHASE doctrine (10-14).
21:19 UTC duel study and duel-v1 -> see [[cambc-duel-v1-1019]].
