---
name: cambc-priority-1023
description: Turn priority (set_priority, public 32 bits): engine rule, V18 never sets it, top 10 reorder dynamically; prio-v1 candidate
metadata:
  type: project
  modified: 2026-10-23T15:04:33.624Z
---
Thread "Prioridad pública de 32 bits" (10-23, from a Discord remark relayed by the user).
- Engine: `set_priority(int32)` applies next round, persists; inside a team higher acts first, ties = draft order; teams alternate slots, starting team swaps each round. `priority()/prev_priority()` readable for any VISIBLE champion incl. enemies (SDK cambc.h:3853-3919).
- V18 (nightpack-v2) never calls it -> leaks nothing; our replays 100% draft order.
- Top 10 (148 t10 games, order from ph10 events, analysis/priority-1023/order.py, feat.py): 9/10 teams off draft order 84-96% of rounds; in fights first actor = nearest-to-rival 39% vs 30% chance, lowest hp 32% vs 25%; Trzy Kwaterki lowest-hp-first 85%. Reading their priority adds ~nothing beyond visible hp.
- Candidate prio-v1 (bot/prio-v1, FICHA.md): V18 + contact within 4 -> priority 1000+100*(1-hp%), else 0. Counter [prio]. runmech 10-23 16:05 vs V18 240 g: net -2 (bar 17.7), deaths +0.44 (se .5), gold +1.7%, counter 111 fires/game -> neutral, not queued, unresolved.
Links: [[cambc-mechtest-1023]] [[cambc-game-mechanics]]
