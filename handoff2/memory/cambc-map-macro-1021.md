---
name: cambc-map-macro-1021
description: 10-21 map-feature/macro study of v94-96 on 1.0.2: far altars (median spawn->altar walk >= 50) = 2nd loss feature; bank-walk fix failed; real gap is rival clears more, bigger, fewer gem-only clusters
metadata:
  type: project
  modified: 2026-10-21T14:21:32.692Z
---
Thread "Mapas y macro de v96" (cmsg_017gbamt2g1g8hMHRHQBc6qbL4KhEXALQA8csoPRcu5t5Y), 10-21 14:00-14:50 UTC. Outputs analysis/map-macro-v96-1021/ (README.md, scripts/, mapsj/ = all 35 site maps decoded with online/tools/mapjson.js; wasm from cambc 3.0.4 `cambc init` assets in ~/.cache/cambc/assets, works in the cloud even though wasi-sdk download fails).
- Feature alt_dmed (median 8-conn walk spawn -> reachable altars) >= 50, 12 maps: v96 32% (35/108) vs 63%; independent of gem-only groups [[cambc-audit-1021]] (far-only 40%, both 24%, neither 59%, v94-96 n 1040).
- Far maps are low-contact farm races (1-5 deaths/g). Our walk last-clear -> altar 30.9 vs rival 20.9 (our losses); near maps equal. We bank at the nearest altar; the cost is camp choice.
- Code: bank-walk term only for Expanse/Monolith. bankwalk-v1 (local 32-38) and v2 (panel -8) FAILED 10-21 16:35: the walk was a symptom. Far maps: rival clears +16% camps, bigger groups (14.9 gems/94 gold vs 11.6/75), gem-only clusters 8% vs our 16%, NOT nearer altars.
- v98 (240 summ., 18:10): we clear MORE camps (43 vs 36 r<1000, far losses) but small: 5.9 gems/70 gold per kill vs 16.2/111; ELK 10% of our kills vs 24%, 47% ours gold-only clusters; rival 3+ champs farming together 92 vs 39 rounds. lonegem-v1 (x0.6 gem-only) panel -10. Direction sent: elk/big groups as squad target. TP/wards not levers.
- 10-21 evening, local 9-rival panel vs v98 (630 paired games, my container: /tmp/claude-0/ci, scripts analysis/map-macro-v96-1021/local_scripts/pair.py): sticky-target-v1 rejected (gems -4.5% vs pC); joincall-v1 net -23 (clears 89->86; squad steering costs clears, like elksquad -27); elk-opening-v1 (bundles/elk-opening-v1.zip d35fa1a9, first 2 champs pair on nearest uncontested 15+gem monster group before r60) net +5 bar 18, no harm, first elk clear r380->r221. Gotcha: never run `cambc build` while a run-batch is going (runner breaks); CAMBC_WASMTIME_CACHE must be absolute.
- 10-21 night: took over stall fixes from farm thread. Panel vs v102: holefix-v2 +9 (bar 11), stallfix-v1 (holefix+islefix+respawnfix, bundles/stallfix-v1.zip fff2bbda) +16 (bar 22.3), gems +3%, deaths 7.1 vs 6.9. Sent stallfix-v1 to API thread for the loop.
- 10-21 night (analysis/overnight-1021/map_features_macro.md): 40-map site pool (arena/maps/site40; golem maps need CAMBC_MAPEDITOR_WASM=v1_0_2). 9 bad maps: equal gold, rival 3x gems (choose_target gold=gems to r940, elk groups penalised). Online: value-v1 -9 (GOLD CUT kills: gold@400 -200 -> deaths 6.6->12.6; don't cut gold weight), elksplit -3, goldw40 -7, elksplit-v2-fuelwait (v113) +8 vs bar 14.7 (mechanism moved as predicted, effect small). jackpot-near dropped (elk_arena deaths up). fuelwait-v1 rider. v110 'drop' 10-22 = candidates playing ranked (v110_drop.md).
- Style (wins and losses): rival wards 230-270/g vs our 82-93 on far maps; rival teleport crystals (flash range 3) 2.4/g on far maps, we 0.
- Gotcha: t10_stats.py runs main() on import; copy load()/FIX (scripts/dec.py). Never grep the whole /mnt/project-files (hangs).
- 10-22 work continues in [[cambc-map-class-1022]].
