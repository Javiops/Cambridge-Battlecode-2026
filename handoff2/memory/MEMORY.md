# Team memory index

## LOOP RESUMED (USER 10-25 08:33 UTC "dale un loop con v20 y v21"): chain 19 = V20 base vs V21 (b27 fuelfit det bot, jeb4pf 76c4f20); kvvl v164 back on ranked after. Madrid = UTC+1 since 10-25 (DST ended).

## CURRENT FOCUS (USER 10-25 08:33 UTC): loop RESUMED: chain V20 base vs 'V21' = b27 (deterministic: b15 + hitpass off on far maps + farm o59/o63/o64; branch claude/project-thread-jeb4pf commit 76c4f20 handoff/fuelfit/fuelfit-b27.zip). PC 800 g: pad +20 1%, +200 11% (kvvl 96%), J2 +9.6, reserve +17.4 (kvvl +10.4/+15.8). b24hp J2 +13.5 same reserve. V21 NOT yet promoted by user; online strength unknown until this chain. Fuelfit details [[cambc-fuelfit-1025]].
## LOOP RULE (USER 10-25 11:48 UTC): do NOT always relaunch the previous/base bot for comparison; send only the candidate on the last chain's same pinned groups and compare with that chain's existing base games (online is deterministic). 10-25: c19 b27 -7 vs V20 (rivals ranks 43-67), c20 b32 -1 vs kvvl (ranks 53-77; near 47 vs 52, far 20 vs 16). Replays show det bots die earlier on near maps (r100-300 fights, outnumbered, carrying gems). b35 sent alone 11:49 UTC on c20 groups.
## LOOP METHOD (10-25 12:09 UTC, after user 12:08 'llevamos 30 y pico versiones... nada online'): ONLINE judges each det piece. b35 v173 alone on c20: -4 vs kvvl, -3 vs b32 (far identical to b32 => no rival change). Loop runner scratch pinq.sh: TAG.zip in pinq/todo -> alone on c20 pinned groups, kvvl back, cmp_ref.py vs 164/172/173.
## RIVALS (USER 10-25 12:12 UTC): loop rivals = the 15 teams directly ahead (was 25). loop_config fight_rank_mode 'ahead15' (common.py now reads aheadN). After b15 on c20: one kvvl reference draw on 15 groups (chain 21), then each candidate alone on those pinned groups (~3/hour).

## TIME (USER 10-24 21:28 local): give times to the user in THEIR LOCAL time (Madrid). Since 2026-10-25 01:00 UTC DST ended: local = UTC+1 (CET), not UTC+2.

## ACTIVE RANKED BOT (USER 10-24 18:01 UTC): kvvl (k_vvl_mgwp, v164) active in ranked until user says otherwise. kvvl c14 +1, c15 +4 (the "kall" v163 was kvvl by upload bug). Sprint 2 tournament: user "no es relevante", V20 stays entered.

## COORDINATOR RULES (USER 10-22 11:24 + 13:09, angry twice; 10-23 10:48 "deberías saberlo"): ONLY relay what a thread's LATEST message confirms, with its time; if unconfirmed say "no lo sé". Never guess. Never resolve/close threads. Reply in Spanish. CHASE the loop if silent >20 min during a batch (loop must report every 15 min).

## GOAL (USER 10-23 11:37 UTC, unhappy): TOP 10. Do NOT compare with current mid-table rivals/mirrors; study how top-10 teams play among themselves (plan, micro, economy, timings, abilities) and make us play like that. Lead thread "Qué hace mejor el top 10" cmsg_017gbamt2g1g8hMHRHQBc6qbBdt3Cqy7w8tYFiNejQcHf9. User expects big progress. Rank 83 -> 56 (10-24 11:45) -> 67 -> 55 (kvvl 23:04 local) -> 67 (00:18).

## BASE V20 = v139 v6d (V19 + bcf-v3 engage only + richcap-v2). USER promoted 10-23 19:33 UTC. Chain format: V20 base draw + up to 5 mejoras on same pinned groups, rivals = 25 directly ahead live.
## PREV BASES: V19 = v136 pack-v1w. V18 = v132 nightpack-v2.

## User and rules
- 10-24 13:59 LOCAL JUDGE = J2 (scripts/judge2.py; hard panel with far x0.42 + rPun5 a-d), r 0.80 vs online on 8 old pieces. 10-24: kvvl+counter only (same logic) changes 771/800 J2 games, 233 winners; J2 +10.4 -> +1.6, so J2 differences <~9 mean nothing until the bot is deterministic.
- 10-24 18:24 ONLINE GAMES ARE DETERMINISTIC (60 duplicated V20 pairs identical); every changed game = code (fuel chaos or rule) or rival bot change. Chain 16 pairs diverge median r3 (fuel_ok branches flip).
- 10-24 08:41 (Javier approved stall-thread doc claude.ai/artifact/LVut8QwAcyscnziWWoAexE): PAUSE late pieces (r400+, late shop). Focus = first 150 rounds on NEAR maps; judge by state at r300-400 (a14.py) + fixed losses.
- USER 10-24 17:46: top10 doesn't die less by caution, they fight better -> top10 fights outnumbering (+2) 36-43% vs ours 12-21% (local 22-29% all variants; retreat rules don't create superiority). USER 18:12 approved pelea-v1 (audit [[cambc-audit-1024]]); 18:51 "todavía no son lo suficientemente significantes"; 22:00 UTC "no deberíamos estar satisfechos... organizarlo/plantearlo mejor".
- [[cambc-champion-headers-1023]] USER 10-23 20:36: per-champion code lives in <champion>.h (v20c, PR #47); rules keyed to champion type with generic fallback.
- USER 10-23 19:37: STANDING permission to update shared local-filter bases to each promoted base; user offers space on their PC (C:\Users\Javier\Cambc2026).
- USER 10-23 17:42/17:47: more ambition, but bar is not +20; positive pieces keep being improved; small pieces ride with a bigger one. No thread should sit idle.
- USER 10-23 14:32 LOOP FORMAT: base draw then up to 5 candidates on the same pinned groups; download+analyze each version's games as they arrive; user decides after all contenders finish.
- USER 17:24: delete replays no Claude is working on. Project folder file limit 50k.
- [[cambc-user-prefs]] — user writes Spanish; olympiad medallist + competitive programmer; zips in /mnt/project-files/bundles/.
- USER RULES: whole-system causes, map FEATURES not maps; AMBITIOUS changes; GROUP changes into combined candidates; most promising first.
- STANDING CYCLE: review -> deeper cause -> fix -> local filter -> loop, without asking (loop currently paused by user).
- [[cambc-deadline]] — bot done by 3 Nov 2026; no new ideas after 30 Oct.
- [[cambc-repo-versioning]]; [[cambc-team-repo-panel-1022]].

## Threads
- [[cambc-top10-fresh-1025]] "Comprobar si las stats del top 10 están anticuadas" cmsg_017gbamt2g1g8hMHRHQBc6qbVoK5gm5dbDsc5ynjLYzo5q: top10 turnover + draft shift (Tavi 46%, Ryth 29%) since 10-23; refs being recomputed on 10-25 games.
- Audit "Auditar por qué hoy no hemos avanzado" cmsg_017gbamt2g1g8hMHRHQBc6qbBWagZSTwAEb4cNuhfTwZNJ [[cambc-audit-1024]].
- PC thread "Iterar rápido con el PC al 100%" cmsg_017gbamt2g1g8hMHRHQBc6qbWJRRHAshe4LstJTtEWjk6y (Remote Control on user's PC, J2 800 g in ~5 min, pad.py/diffcount.py). Hand-offs via git branch claude/project-thread-dxkoko (loop reads bundles/ there). PC cannot message other threads: coordinator relays.
- Champ thread "Mejorar cada campeón en su fichero" cmsg_017gbamt2g1g8hMHRHQBc6qbWGcBmLAuLLertF3G524Tfj: HoR closed; pA (vkite-v3+mstick) online +2; mstick threshold 70% final; next = Marcella camp damage (-31% vs top10).
- [[cambc-stall-root-cause-1024]] "Encontrar la causa real del estancamiento" cmsg_017gbamt2g1g8hMHRHQBc6qbMCr1xtTHNadcy4CYx8C6b9: owns deterministic bot (branch claude/project-thread-jeb4pf handoff/det/), divergence analysis, Vendetta vopen (neutral).
- [[cambc-camp-deaths-early-1024]] deaths: gold_rush monolith; monoguard +6/250.
- [[cambc-pelea-v1-1024]] pelea-v1 on kvvl: all neutral/negative online.
- [[cambc-vin-1025]] 10-25: fight dmg/fight-round top10 33 vs us 27; Vesper at range+1 step+reset+shoot; vin-v1 on b28 to PC.
- [[cambc-buddy-1025]] 10-25: we split WALKING between camps (paired 37-39% vs top10 55%), equal at camp; buddy-v1 bd2c/bd4c to PC.
- [[cambc-pairs-loneliness-1024]] pairs/loneliness line closed (symptom).
- [[cambc-camp-execution-1024]] rich-group kills slow = damage/hit + heal trips (build).
- [[cambc-archive-mac-1023]] old data archived on Windows PC C:\Users\Javier\Cambc2026\archive (bridge repo Javiops/cambc-archive).
- [[cambc-far-maps-1023]] "Por qué perdemos en mapas lejanos" cmsg_017gbamt2g1g8hMHRHQBc6qbUxbgSPLp9vPnusV9eHZpHC: kall far pieces fire online but add nothing.
- [[cambc-bc-top10-1023]] "Copiar las decisiones del top 10" cmsg_017gbamt2g1g8hMHRHQBc6qbQPhKweT21j8todRu8Zjgsz: pelea-v1 entry rule, hpb/hitpass-v2 (bundles/kvvl-hitpass-v2.zip on dxkoko).
- [[cambc-process-audit-1023]] "Por qué nuestras ideas no llegan online" cmsg_017gbamt2g1g8hMHRHQBc6qb4SPY6VkcM5315HRcVUnGt1: mechanism-sheet method.
- "Farmeo y macro del bot" cmsg_017gbamt2g1g8hMHRHQBc6qbNed5z8z938V5Rz7J13UhBn.
- Online loop "Dissect the top 2 teams" cmsg_017gbamt2g1g8hMHRHQBc6qbWeKMaoE8NCQvPbmGsL7Q11: only holder of site cookie; guard needs the user's own words before switching active bot. Upload checks: size match + not cancelled + counter grep; waits for activation/compile.
- Audit "How Carson starts a bot" cmsg_017gbamt2g1g8hMHRHQBc6qbYYHEj1fcZ1onR2Z8wchFpR: holds the cookie: never copy/attach.
- API "Análisis de partidas con la API de Claude" cmsg_017gbamt2g1g8hMHRHQBc6qbV3DPQ7yeCHNYFqNdcuQChh.
- [[cambc-local-filter-panel-1021]] "Local filter vs online results" cmsg_017gbamt2g1g8hMHRHQBc6qbWnjE4KEXGfnJtTiybgJFDM (built J2).
- [[cambc-shop-abilities-v96-1021]] "Tienda y habilidades" cmsg_017gbamt2g1g8hMHRHQBc6qbUzvqhsvAPJPqRHESyZb7ej.
- [[cambc-map-class-1022]] "Mapas y macro" cmsg_017gbamt2g1g8hMHRHQBc6qbL4KhEXALQA8csoPRcu5t5Y.
- [[cambc-v96-deaths-1021]] "Cómo muere" cmsg_017gbamt2g1g8hMHRHQBc6qbHXbGbRJnfVW1WKFTx1zR7b.
- [[cambc-priority-1023]] "Prioridad pública de 32 bits" cmsg_017gbamt2g1g8hMHRHQBc6qbSpM8Nm9EhZmQgNj8F8WDic.

## ENGINE / SITE / DATA
- [[cambc-fuel-model-1024]] FUEL = instruction metering (C++ loop ~10/iter); SDK prices; engine BFS rules. Farm fuelfit hand-off: branch claude/project-thread-jhnqzy handoff/fuelfit-farm/ (exact o41-o46 80/80 identical; caps o51-o53 judged by strength), bench ws /tmp/claude-0/ff (farm thread container).
- [[cambc-games-side-bug-1023]] games.jsonl side flip; ~22% duplicates.
- Engine 1.0.3 (cambc 3.0.5). Site pool 40 maps. Unranked quota 50 groups/hour; batch 25 groups. Simulator supports unlimited fuel (--fuel-quantum) for exact-identity checks.
- API match `draft` ids are NOT champion_type: 0 ryth,1 vesper,2 vendetta,3 cassi&issac,4 stellar,5 prism,6 marcella,7 willow,8 ren,9 varg,10 tavi,11 hor.
- champion_type: 0 ryth,1 vesper,2 vendetta,3 cassi,4 issac,5 stellar,6 prism,7 marcella,8 willow,9 ren,10 varg,11 tavi,12 heart_of_ruin.

## Judge / loop rules (USER)
- STANDING (10-23 09:09 UTC): mechanism sheet MANDATORY before panel/online; no line closed <300 games; online control each batch.
- STANDING (10-23 06:59): after EVERY online batch, loop auto-downloads replays and API thread auto-dispatches analysis.
- Candidate active ONLY during its batch, then back to kvvl (ranked). RIVALS: 25 teams directly ahead.
- Judge: pass if (for-against) >= 2*sqrt(changed). User may promote below bar.

## History
- Lineage: v96 goldval, v98 horfocus, v102 mate-dash, v105 stallfix, v110 need2, v117 marc-bfill (V15), v120 t10draft-v2 (V16), v122 t10shop-v2 (V17), v132 nightpack-v2 (V18), v136 pack-v1w (V19), v139 v6d (V20).
- CLOSED LINES: death-cutting variants, squads/recruit, territory/holdcamp, far gem-first, bigrush, opening, rally, fight-execution, farm macro overall, pairs/loneliness, HoR target, retreat-when-outnumbered. idlerush parked (user).
- ACTIVE SLOT CONFLICT: teammate account (uploader 7240d898) hand-activates its bots.
- [[cambc-online-decides-rule-1018]] [[cambc-judge-two-step-1019]] [[cambc-pinned-replay-1019]] [[cambc-online-loop]] [[cambc-game-mechanics]] [[cambc-claude-api-pipeline-1018]] [[cambc-top10-micro-1023]] [[cambc-top10-plan-1024]] [[cambc-top10-eco-1023]] [[cambc-chain-tools-1024]]

## PC (sesiones locales en C:\Users\Javier\Cambc2026)
- [PC Judge 2 lab](pc-judge2-lab.md) — local 800-game Judge 2 bench on the PC, scripts and gotchas
- [Coordinador en esta app](cambc-coordinator-here-1025.md) — USER 10-25: la sesión de escritorio en el PC coordina; una sola cola de J2; sin /mnt/project-files ni cookie aquí
- [Loop online en el PC](cambc-pc-loop-1025.md) — lab\loop: subida por POST /submissions (sin cambc login), control de kvvl tras cada lote, cadena 21: b35nohp +11/10,4
- [Sesgo de deathmode](cambc-deathmode-bias-1025.md) — kvvl se salta líneas de estado en turnos pesados; usar campdeath/campdiff; hitpass culpable (+35/+49), kvvl→b15 era artefacto
- [Cookie compartida](cambc-cookie-shared-1025.md) — USER 10-25 15:00: todas las sesiones usan C:\Users\Javier\.cambc_cookie; solo el loop sube/activa/reta
- [Razones, no síntomas](cambc-reasons-not-symptoms-1025.md) — USER 10-25 15:25: buscar la variable oculta que hace óptimas las decisiones del top 10; el uso no preocupa
- [Medio/final de partida reabierto](cambc-late-game-unpaused-1025.md) — USER 10-25 16:05: pregunta D (morimos con gemas tras r400); anula la pausa de r400+ del 24-10
- [Por qué al top 10 le funciona (A/B/C/D)](cambc-top10-why-1025.md) — 10-25 PC: medido en 95 partidas top10 de hoy vs cadena 21; herramientas lab\top10; piezas F1-F3/P1
- [Regla de promoción](cambc-promote-rule-1025.md) — USER 10-25 19:18: solo se promueve si pasa la barra en el loop online contra los 15 de delante
- [Regla de copiar X](cambc-copy-x-rule-1025.md) — USER 10-25 ~20:00: si copiamos X y no funciona, X no era el problema; buscar lo que hace que a ellos X les funcione, ir a fondo
- [Fallo de método: métricas simétricas](cambc-symmetric-metrics-flaw-1025.md) — 10-25 ~20:10: resultados de top10 vs top10 no se comparan con los nuestros; pregunta única: por qué perdemos el intercambio de daño
- [Plan c97 y diagnóstico vs top 5](cambc-plan-c97-1025.md) — 10-25 noche: apertura (pareja al alce rico, resto solo) + bola de nieve; c95shop online, elkopen v3, combinada c97
- [Menos informes al usuario](cambc-less-reporting-1025.md) — USER 10-25 21:35: el coordinador lleva todo solo; avisar solo veredictos online, decisiones suyas o problemas
- [Parche 2.0.0](cambc-patch-2-0-0-1026.md) — 26-10 00:15: motor 2.0.0/CLI 4.0.0, objetos nuevos, nerfs a nuestro draft, referencias 1.0.3 anuladas, pool 70 mapas
- [Bundles solo el loop](cambc-bundles-loop-only-1026.md) — 10-26: solo el loop baja bundles de repeticiones; el resto se los pide; resúmenes por API libres
- [Vesper step+reset, ranged move XOR attack](cambc-vesper-step-reset-1026.md) — 10-26 engine rule and top-5 Vesper closing pattern; vstep candidate co_vs; local bench biased vs E1
- [Laboratorio ML](cambc-ml-lab-1026.md) — 10-26 sesión ML en lab\ml (CMA-ES, imitación top 5, ES de red); p1c gen 0 +0,055 local (sin empaquetar); PARADA por el usuario 20:45, no relanzar; 27-10 clústeres A100 + 10×V100 concedidos (el valor son sus núcleos)
