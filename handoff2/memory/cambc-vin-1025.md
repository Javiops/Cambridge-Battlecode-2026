---
name: cambc-vin-1025
description: 10-25 fight damage gap vs top10 (attributed per hit, every-step decode): Vesper uptime at range+1; vin-v1 piece on b28 sent to PC
metadata:
  type: project
---
Measured 10-25 ~10:45 UTC with handoff/vin/ scripts (branch claude/project-thread-dxkoko commit 3cf37c0): dmg.py (every-step replaydump, damage attributed to actor), turn.py (per-turn action kinds), tagg.py, dagg.py.
- Step kinds: 4 move, 5 basic attack, 6 ability; 9/11/16 appear only in top10 bots (likely debug/indicator, ignore).
- Vesper abilities: k0 attack-reset, k1 dash; NO damage spell (spell-first patch spf did nothing). Vesper attack range 3. SPELL_RANGE 4 in our code.
- Champion damage to champions per own fight round (foe<=4): top10 33, us (b27 online) 27. Vesper 40 vs 28, Marcella 36 vs 26 (per hit-round 110 vs 90 = build/items), HoR equal. Focus (multi-hitter rounds on one target) 71% vs 55% (small n).
- Top10 Vesper at foe distance 4: step+reset+shoot or dash+shoot; ours dashes away. vin-v1: vin1 (step+reset+shoot), vin2 (+dash in). Local: Vesper attack at d4 8->18%, results noise (vin1 -3/7, vin2 +2/8). Sent to PC via coordinator.
- Next lead: Marcella damage per hit (build) - coordinate with farm thread before touching shop.
Related: [[cambc-buddy-1025]] [[cambc-camp-execution-1024]] [[cambc-game-mechanics]]
