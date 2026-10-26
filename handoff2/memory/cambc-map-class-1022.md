---
name: cambc-map-class-1022
description: 10-22 map/macro thread on engine 1.0.3: far-map gap vs top10 = camp damage (draft); farm-macro candidates all too small online; p panel saturated on t10shop-v2
metadata:
  type: project
---
Thread "Mapas y macro" cmsg_017gbamt2g1g8hMHRHQBc6qbL4KhEXALQA8csoPRcu5t5Y. Doc analysis/overnight-1021/v110_engine103.md (all tables). Continues [[cambc-map-macro-1021]]. Scripts analysis/overnight-1021/map-macro/ (v110e3, top10cmp, shopcmp, champcmp, mega.py base cand since [draw], losses.py ver far|near).
- Local 3.0.5 = 3.0.4 bit-identical: panel can't see the online 1.0.3 change.
- Far maps = spawn walk >= 60. v117 vs top10 far: gold@400 1430 vs 1976, first 12+ capture r155 vs r80. Gap = camp damage (+44%), half from draft (Vesper/Vendetta vs Stellar/HoR) -> t10draft closed most of it.
- Rejected/not sent: map-class-v2/v3 (+12/+10), mega-v1 online -3, mega-far v121 online -7, t10far -18, tankfirst +9 (mechanism didn't fire, champs farm apart), fargem fg40/fg60 (far gold_w 40/60 on t10shop-v2: far +4 bar 11.7 / -2; pHuntF +1, deaths =).
- ONLINE NOISE FLOOR: ~9% games flip with no behaviour change (~10/batch). Farm mechanisms move online (first12 far r150->r75, gold +3-4%) but too small; only big moves (t10draft gold +18%, deaths -3) clear the bar.
- v120 online: near WR .82, far .47. Far losses 23/43: 16 farm race (equal gold, rival 1.2-1.6x gems), 7 fights after early starvation (concentrated_wealth, starvation: gold@400 825 vs 1540, first big capture r216 vs r79) = remaining lead.
- Gotchas: `pkill -f "<script>"` kills own shell; replays .repl26a filled disk (~15GB), delete after each batch; pHuntF source from git branch claude/project-thread-til6f5.
- 10-22 21:00 V17 online (222 g): far 30-52, near 99-43. elk_arena WR 11%: centre (only gem group, 5520 hp) flagged jackpot -> P_JACKPOT wait to r550; elkjack-v1 (bundles/elkjack-v1.zip ac86125f): small jackpot (<10000 hp) no wait + team job; local gems@800 130->490, deaths 2.4->5.6. gemrace-v5 = v4 + elkjack (87958c60). Heavy-middle opening (ybr/big_world) shelved: only 3-4 maps, pairopen worse. gemrace-v4 = site v123 (b1 +5 bar 7.2).
- 10-22 FAR GEM RACE: gemrace-v4 (skip gold-only, gw40 far, gem-rich gate >=250) local gems +25% but online REJECTED (far-loss gold@400 -430: gold-only groups = item power). gemrace-v7 (11ab3ceb, skip only if on gold schedule) panel17 +20. Event target ids = replay group index: use map-macro/groups_replay.json. Local mix /tmp/claude-0/ci/fr/mix.py.
- 10-22 23:20 camp-model calibration CLOSED: model overestimates camp dmg 3-5x on average, but scaling it (inccal/campcal, 4 variants panel17) raises camp+champ deaths; best icg (fresh-only) +21 < bar. Rival far edge = more own-half 2k+ solos, earlier.
- 10-23 00:10 farmer rival bundles/rFarm1.zip (V17+elkjack+campmodel x0.3+far respawn wait+far gw0.6): V17 wins 39% vs it on far (online 37%). Handed to local filter for panel17. gemrace-v4 online split was far +3 / near -1.
- 10-23 05:00 gemrace-v7 REJECTED online (far b1 9/3, b2 3/7; gems +20% online but no wins): far gem-first CLOSED (4 tries). farswap (far-only HoR slot swap, 7 champs): best fs_ren panel17 +25, not sent. Rule: need ~+80/800 panel17 for one batch.
- 10-23 07:20 USER-approved cleanup: deleted online/data summaries+replays of versions <=121 (4.35 GB). Night 10-23 v122: near WR 66%->59% (mirror drafts: rivals copy HoR/Vesper/Marcella/Ryth/Vendetta, mirror near 65%->55%; losses = fights 14 vs 3 deaths), far 38%->43%. Script map-macro/daynight.py. Sent to deaths thread.
