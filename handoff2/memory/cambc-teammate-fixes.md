---
name: cambc-teammate-fixes
description: 2026-10-16 switch list of the behaviour fixes built on the teammate base (thread "Arreglar comportamientos del bot del compañero"): what each P_* does, its round-1 panel number, and the user's rules (ship all but P_CAPHOME, P_NOLEAVE by vision, P_OUTNUM 6 for Tavi walking into 3 foes); round 2: CAMPFOE+BACKHOME 86-55 holds, neutrals subtract when stacked, CAPPRIO costs farm speed
metadata:
  type: project
  modified: 2026-10-16T17:59:55.757Z
---

Companion to [[cambc-teammate-base-1630]] (user decisions) for the thread root cmsg_017gbamt2g1g8hMHRHQBc6qbJCcNsUuvE7oieoatFWTfJv. Base = teammate bot (P_CAPRECALL 2 already captures and recalls together; P_TWIN exists but off). Panel = 5 specialist bots, 77 maps both sides; base 76.4%.
- **P_CAMPFOE** mid-fight (foe within 3) hit the foe or leave, never the camp: 81.2%, flips 84-47 (p=0.002). Ship.
- **P_BACKHOME** go home after depositing at the centre when no camp is left: 78.7%, 50-32 (p=0.06). Ship.
- **P_NEEDHEAL** no idle wait when the camp "needs heal" at 80%+ hp (bug, ~800 idle turns): neutral 60-53. Ship (user: all in).
- **P_KITEALLY** kite towards allies even when the nearest is >6 tiles: neutral 25-19. Ship.
- **P_NOCHASE2** no walking towards foes 5-6 tiles away: neutral 43-48. Ship.
- **P_CAPHOME** extension of capture+recall (also with foes 4-7 away; skip deposit while a camp waits within 2): 72.1%, 70-103 (p=0.015), hurts vs the farmer. OFF (user).
- **P_CAPPRIO** who captures: Stellar > other casters > Ren > tanks only if nobody else; Stellar takes it when alive, not recalling and within 6. Round 2.
- **P_NOLEAVE** (user): carries that see a ready camp go for it, leave only if staying kills or a higher-priority carry claimed it; non-carries note it in shared memory and move on. Round 3.
- **Issac** (82 pair deaths in 30 games, 33 with Issac 9+ tiles from Cassi): P_TWIN on, and Issac farms Cassi's camp / no solo entry with foes near. Round 2.
- **P_OUTNUM 6** (user, Tavi walks into 3 foes alone): with 2+ more foes than non-recalling allies within 6, step away, unless a one-shot kill is in reach. Round 3.
**Round 2 (17:54):** CAMPFOE+BACKHOME 80.4%, 86-55 (p=0.01); + NEEDHEAL+KITEALLY+NOCHASE2 77.3%, 90-83 (the neutrals subtract when stacked); P_TWIN 78.2%, 60-46 (helps a little); P_TWINFARM (Issac farms Cassi's camp) 73.5%, 69-91 (worse); P_CAPPRIO 71.6%, 70-107 (p=0.007): costs farm speed, vs the farmer 66% -> 51% while the tank waits for Stellar; CAPHOME halves noise or worse. Round 3 on CAMPFOE+BACKHOME+TWIN: + P_OUTNUM, + P_NOLEAVE (vision), + P_NOLEAVE with the caster cache. Proposed zip = CAMPFOE+BACKHOME+TWIN + round-3 winners; thread asked the user whether to include the three neutrals.
**17:56 user rule, farming by roles (from scratch, after the fixes zip):** only the DPS (casters and Ren) capture, never a tank; tanks do not farm on their own, they escort a DPS to its camp, absorb damage, help kill and step aside so the DPS captures; no 'tank farms alone if no carry is free' exception. Measured risk: Issac following Cassi cost 76% -> 73.5% (parallel farming is faster), so the design must win carry gold without losing much farm speed. User decided 17:57: the zip = CAMPFOE + BACKHOME + NEEDHEAL + KITEALLY + NOCHASE2 + TWIN (neutrals included), then farming by roles on top.
**17:59 zip** /mnt/project-files/bot/mybot_teammate_fixes1.zip = teammate bot + CAMPFOE, BACKHOME, NEEDHEAL, KITEALLY, NOCHASE2, TWIN; switches off = identical to the teammate bot (17/17), no bot faults. Vs panel without TWIN 77.3% (tie); vs teammate bot on 60 fresh maps 11-21 both sides (p=0.11), 158 vs 165 gems/100 rounds (slower: leaves camps with foes near, goes home after deposit). Coordinator recommended uploading it as bot B for the online A/B vs v49.
Caveat: local fight gains have been smaller online ([[cambc-online-ab]]); user wants few versions. Related: [[cambc-local-judge]] [[cambc-micro-strategy]].
Coordinator idea (island cloud-e 9271169af0) on fixes2, site maps: P_GA_AVOID_HP 68 125/170, P_CHASE_GEMS 118 132 (1-0 flips, no effect), both 124 vs 131: rejected.
18:58 fixes3 = fixes2 + P_MAPPLAN 1 (new-maps thread draft rule): 136/170 vs 131, stampede 5->9; zip mybot_teammate_fixes3_mapdraft.zip, pushed to PR #31. P_MAPPLAN 0 = 0 flips vs fixes2.
