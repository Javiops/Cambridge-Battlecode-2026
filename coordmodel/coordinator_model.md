# Coordinator model: how e1foco decides, and what a top-10 team actually does

Sources. Part A: `pcassets/zips/e1foco.zip` (branch `claude/pc-e1-assets`, sha256 659ded19...), unzipped to
`/tmp/claude-0/-home-user-cambridge-battlecode-2026/8de47290-da50-5e17-ba34-a5ff0b87ab89/scratchpad/e1foco_src/src/` (all `file:line` below are relative to that folder).
Part B: 12 engine-2.0.0 replays decoded with `pcassets/viewer/replaydump.js` + `ext.py` (wasm from branch `claude/project-thread-l6gm1j`, `handoff/replay2/`), per-50-round tables in
`/tmp/claude-0/-home-user-cambridge-battlecode-2026/8de47290-da50-5e17-ba34-a5ff0b87ab89/scratchpad/timelines.md` and per-side key numbers in `.../scratchpad/summaries.md` (scripts in `.../scratchpad/scripts/`).
Camp rewards are per GROUP everywhere below (each camp of a group carries the group total; never summed per camp).

---

## Part A. The e1foco policy in plain language

### A.0 Shape of the program
One C++ program runs per champion (`main()` -> `run_draft()` in the draft, else `run_game()`, main.cpp:5530-5533). Each champion has private memory (its `State`, main.cpp:621) and the team shares only the engine's 8 bytes of shared memory. There is no team planner: every champion runs the same priority list each turn and coordinates only through those 8 bytes (A.5). The draft is fixed by `P_META` (main.cpp:386-389): Heart of Ruin, Vesper, Marcella, Ryth, Vendetta, with Ren replacing Heart of Ruin when the spawn-to-spawn walk is 60+ (`P_FAR_SWAP`, params.h:295). Start-up (map, camp groups, walking-distance fields, roles, shop plan) happens in the first turn(s) (`init`, main.cpp:1221-1253), and the champion plays from round 1-3 depending on map size (main.cpp:1240-1248).

### A.1 Order of decisions in one turn (`run_game` main.cpp:5444-5520 calling `play_turn` main.cpp:4033-5081)
Each step returns from the turn when it acts; later steps are only reached if nothing earlier fired.

0. **Pre-move spell sweep** (main.cpp:5451 -> `spell_sweep`, 5135): with the caster mode on (Vesper or Stellar on the roster, champions.h `caster_mode`, main.cpp:1041-1052 sets `s.sweep=3`), a ready damage/stun spell is cast on an enemy champion within 4 before moving. Shared.
1. **Dead**: shop (dead champions can buy) and drop the camp claim (4058-4063).
2. **Reward arrived** while standing on our target group's tiles: mark the group on cooldown, broadcast it, drop target (4072-4080).
3. **Shop** whenever gold >= 30 (4087-4091; `shop` 1319-1396). It only succeeds on spawn (`shop_open`, 1311). Buys follow the champion's emblem plan in order (A.6); from r400 the "fill" step follows the champion's late Bruiser mix (`lshop_pick`, 1279). A teleport crystal is kept in hand on maps with a spawn walk >= 80 (`P_TPC_PATH`, 1323-1333).
4. **Channelling** (tribute, teleport, recall) or low fuel: do nothing (4103-4110).
5. **Perception**: blocked tiles, own vision, `refresh_groups` (group state alive / reward waiting / respawning for every visible group, cooldown broadcast, 2191-2264), the list of visible foes with "away" marks (a foe that stepped off from us is "gone" for 3 rounds, 4128-4162), the team focus byte (`foco_update`, 3188), the danger map of ready enemy damage next round (`threat_of`/`danger_at`, 541-603) and the nearby camps (4113-4190).
6. **Monolith guard**: step out of an awake monolith's range and treat it as a wall unless we farm it (4190-4214).
7. **Flags** (4225-4238): `in_combat` = foe within 4 or an awake camp near; `safe` = no foe within 8, no awake camp, not hit in 2 rounds; `rsafe` (safe to recall) = safe, or no foe within 7 and not hit this round (caster mode), and never within 2 rounds of a hit or of a rival within 6 (`P_RC_QUIET`).
8. **Support spells** (heal/shield on allies, 4274).
9. **Enemy target of the turn** (4277-4292): the foe within 6 with the lowest `hp - 300*channelling - 5*gems + 40*(distance beyond my reach+1)`; the team focus foe (A.5) overrides when within 6.
10. **Unstick**: 30 turns on one tile with nothing to hit -> drop target, bank or go home (4295-4311).
11. **Vesper keeps a waiting reward** within 6 (P_VCARRY, until r200, 4313-4374): she walks onto it and may recall on it.
12. **Heal on spawn**: standing on spawn below 87% hp, stay (4377-4381).
13. **Finish** (4396-4452): a foe below 30% hp within reach+1, with no more hp than us and not outnumbering us -> hit it, stepping in if needed. This runs before any flee.
14. **Cut** (Vendetta and Marcella only, 4454-4466): with a foe within 4, hit in the last round, hp < 70% and hp minus the last two rounds' damage < 40% -> treated as "flee now".
15. **Flee / recall** (4468-4487): hp < 33% (caster mode; 29% otherwise) or cut: tribute if an altar is adjacent and no foe within 3; else recall if `rsafe`; else hit whoever is in reach and step toward spawn.
16. **Near-recall** (4489-4497): hp < 54%, more than 6 tiles from spawn, no foe within 7 and not hit this round -> recall.
17. **Fight block** (4503-4827), in order:
    - **Chase** (hp >= 50%): a hurt (<50%) or recalling foe within 4, or within 7 while an ally stands within 3 of it, or a foe sitting on one of our hurt allies; dropped if 2+ other foes are within 4 of us or it backs into 2 healthy allies; followed for 4 rounds; a champion carrying a tribute bag (>= 12 gems) does not follow (4505-4592).
    - **Learned engage** (`bcfight.h`, 4596-4636): a decision tree cloned from top-10 replays on (own hp%, distance to nearest rival, its hp%, log of local hp ratio within 6). ENGAGE -> `engage` (spell, hit, step in, hit). LEAVE is not acted on (P_BCF=1).
    - **Ally duty**: a foe within 3 of an ally and within 8 of us becomes the target (4644-4653).
    - **First-contact verdict** (`verdict.h`): at first contact (foe within 6) compute power ratio = (hp x dps of me + allies within 6) / (foes within 6); below 0.6 the verdict is "leave" and holds for the engagement -> `fight::back_off` (hit what is in reach, step to the tile fewest foes can reach, else toward spawn) (4654-4668; verdict.h:41-79).
    - **Kite** (ranged champions in caster mode, fight.h:376-512): step out of every foe's reach keeping the focus within 4, cast, shoot. Vesper shoots first and then dashes out (vesper.h:14-61).
    - **Favourable?** (4692-4714): our hp (me + allies within 6) >= 83% of foes' hp within 8; with a target, also at least as many bodies within 8 of it and hp >= 74%.
    - **Avoid**: hp < 40% with a foe within 6 (4771-4785), or not favourable and (hp < 45% or a foe within 2) (4799-4804) -> `back_off`.
    - **Front line** (fight.h:214-370): with an ally within 4 and not outnumbered, melee hit/step to the foe nearest the group's centre, ranged hold range behind.
    - **Engage** (4813-4826) if the target is killable in one hit or channelling and within reach+1 (never walks after a low foe otherwise, `P_NOCHASE2`), or reachable and favourable, or favourable within 8 with an ally within 2 of it. If a foe is within 5 the turn ends here ("do not farm during a fight").
18. **Recall / shop trip** (4829-4904): want recall when hp < 54%, or gold >= 240 and hp < 50%, or `farm` asked for a heal; a shop trip when gold >= 180, not capturing, 40+ rounds since the last. If our target's reward is waiting and nobody else captures it, step on it and recall there ("cap-recall"). Otherwise recall if `rsafe` and > 6 from spawn, banking first if an altar is within min(home,12) and we carry 10+ gems.
19. **Tribute** (4910-4974): go to the best altar when gems >= 12, or r >= 1850, or gems >= 10 and the altar is within 8, or gems >= 5 and within 2. **Chain**: carrying under 36 gems with the altar more than 2 away, a free gem group within 8 that is closer than the altar and that we can clear alone is taken first (4924-4949). `best_altar` (2922) prefers altars not on our own side (+20 tiles for own-half altars), avoids danger spots (+60) and enemy locks.
20. **Camp-foe** (5019-5032): a live foe within 3 (or within 5 and hit in the last 2 rounds) while not capturing -> fight it if favourable and in reach, else `back_off`; never hit the camp.
21. **Pair walk** (near maps, r30-150, 5039-5071): on the way to our camp, step toward an ally 5-14 away whose claimed group neighbours ours (<= 6 tiles), at most 8 rounds per target.
22. **Farm** (5076 -> `farm`, 3438-3907), see A.3.
23. **After the turn** (5466-5497): post-move spell sweep, altar lock, ward placement, static path fields.

### A.2 How a champion picks a camp group (`choose_target_impl`, main.cpp:2422-2657)
Run when there is no target, the target expired, or every 6 rounds while not committed (`P_E_RETARGET`, 3527; committed = a camp of the group is damaged, we are capturing, or its reward is waiting, 3509-3520). Each group is scored and the highest wins; walking distances come from per-group distance fields (2492-2537), only the 12 nearest groups are scored (`P_CT_K`, 2578).

Skips (2581-2610): group marked bad; within 5 of a danger spot (3+ enemies seen packed, `update_danger`, 2315); unreachable; respawning with wait > walk + 4 (jackpot after r550: wait <= walk+40 allowed); worth nothing; the **jackpot** (a group holding half the map's gems, about equidistant from both spawns, 1019-1038) before r550; needs more champions than the roster; already claimed by `cap` allies where cap = max(needed, 4) for monster groups, 2 for gem clusters, 1 for a waiting reward, the whole roster for a monolith on a monolith-only map, 3 for the jackpot after r550.

Cost model (2611-2621):
- `needed` = `squad_needed(group hp, group strength, my dps, afford)` (2278-2284): the smallest n <= 2 such that `hp x str x 0.5 / (dps x n x n) <= afford`, afford = 1.6 x my max hp here (so most groups "need" 1, big ones 2; never more than 2 because `P_NEED_CAP`=2).
- `team` = max(1 + other claimers, needed); `t_clear` = group hp / (dps x team); `incoming` = str x t_clear / team x 0.5.
- `rounds` = max(walk, respawn wait) + t_clear + 6 + (incoming / my max hp) x cycle, cycle = 8 + walk from our spawn to the group (the recall-and-return cost of the health lost).
- `value` = (gems + gold_w x gold) / team^e, with e = 1 (even split) or 0.75 for 3000+ hp groups ("stacking" pays). **gold_w is 0.45 of a gem from r0 to r940** (1.0 by `P_GOLD_W_EARLY`, but capped at 0.45 before r150 by `P_GWO` and from r150 by `P_RC2_GW`, 2432-2445), 0.24 after r940.
- `score` = value / rounds, then: x0.7 if it needs company not yet claimed (2622); x0.3 for a cluster another ally already claims unless it is a 20+ gem group (2623); x0.6 within 8 of the enemy spawn, x0.3 when 6+ tiles deeper into their half than ours (2625-2626); x2 for groups within 6 of the "hold" altar from r150 (caster mode only; the hold altar is an equidistant altar with 2+ gem groups within 6, 1053-1067; 2630); x1.25 for the current target (hysteresis, 2634); x10 for the jackpot from r550 (2635); x0.4 on near maps r30-150 for a gem group with no ally's claim within 6 (`P_PAIRFARM`, 2636-2640).
- Writing the choice: `write_claim` puts group+1 in the champion's 6-bit slot (2031-2057).

In short: a champion wants the nearest group with the best (gems + 0.45 gold) per round for the number of champions already going there, prefers its own half, and never prices a group as needing more than 2 bodies.

### A.3 Farming, fighting a camp, capturing (`farm`, main.cpp:3438-3907)
- Watchdog: a target that yields nothing for 50 rounds while we stand within 2 is dropped for 200 (3443-3470).
- No target (everything claimed or respawning): wait at range 5 of the group that frees first if hp >= 60%, else ask for a heal / walk home (3556-3580).
- Live camp visible (3590-3775): recompute `needed` with the current hp; `here` = allies within 7 of the group, `coming` = allies claiming it. If `needed > here` and the group is untouched: "too-strong" (bad for 60 rounds) when even a full-health squad or everybody coming would not do; else "need-heal" when fewer are coming than needed (sets `need_heal`, which makes step 18 recall if hp < 80%); else "rally" at camp range+2 until the squad arrives. Then "fight-camp": hit the lowest-hp live camp in reach, spell first; step out of a lethal next-round burst; "bail" and drop the group below 12% hp (3727).
- Reward waiting (3777-3840): stand on the tiles; **one capturer per reward** (`other_captures`, 3283-3334): among allies on or claiming it within 4, the nearest (lowest index on ties); with a Vesper drafted and r <= 200 she ranks first; everybody else steps off or re-targets; a reward held for 30 rounds while someone else should take it is abandoned.
- Respawning (3841-3881): if back within walk+4 rounds, wait 2-3 tiles off (next to an ally on near maps r30-150), else drop.
- Nothing visible: probe the spawn tiles once each (3883-3907).

### A.4 When it fights, flees, goes home (summary of A.1 steps 13-20)
Fight only when local hp favours us (>= 83% of theirs within 8, with body parity near the target) or the learned tree says ENGAGE or a foe is finishable; otherwise step away (`back_off`). Flee at 33% hp (recall if nobody can hit us, else run home shooting back); recall to heal at 54% when 7+ tiles from any foe; recall to shop at 180 gold whenever not capturing (40-round spacing); bank at 12 gems (or 10 within 8 tiles of an altar, 5 within 2), with a detour to a soloable gem group within 8 first. Vendetta and Marcella leave a contact earlier (cut rule). Ranged champions kite (Vesper shoots then dashes out).

### A.5 How allies coordinate (8 shared bytes)
- **Claims** (bits 0-29, one 6-bit slot per ally): the group each ally is going to (`claim_value`/`write_claim`, 2004-2057). Read by `choose_target` (claimers per group, cap), by `farm` (coming), by `other_captures`, by pair-walk and by the position estimator of unseen allies (`pe_update`, 5405: an unseen ally is assumed to walk one tile a round toward its claimed group).
- **Team focus** (byte 4, `SM_PLAN`, 3168-3234): when a champion is in contact (foe within reach+1), the engaged foe with the lowest hp fraction is published (roster index + round stamp, valid 2 rounds); every attack, spell and target choice prefers that foe (`shot_retarget`, 3236; `basic_attack`, 1857).
- **Cooldown broadcast** (`SM_BC_GROUP`/`SM_BC_READY`): the respawn time of a group one champion saw, so others skip it (2113-2119; read in `refresh_groups` 2192-2206).
- **Danger spot** (byte 7): nearest altar to a 3+ enemy pack, valid 45 rounds; camps within 5 of it are skipped and that altar costs +60 (2315-2343, 2719).
- There is no "pack" or leader: `grouped()`/`ball_on()` are hard-wired false (2345-2346), `P_GROUP_R`=0, `fight::call_help` and the gang-up rules are compiled out (`if (false)`, 4725-4766, 4993). The only togetherness mechanisms are pair-walk/wait-pair (near maps, r30-150), the x0.4 pairfarm score, the x0.7 "needs company" factor and the 'rally' wait.
- `P_HOLD` (200): caster mode holds a central altar: its gem groups score x2 from r150 and that altar ignores danger when banking (1053-1067, 2630, 2721). It needs an equidistant altar with 2+ gem groups within 6; on the maps studied here it rarely exists.

### A.6 Per-champion vs shared
Shared: everything in A.1-A.5 except what follows. Per champion (`champions.h` hooks, defined in `<champion>.h`):
- **Shop plans** (final emblem orders, `shop_plan`): Heart of Ruin treasure-h, jungle-f, bruiser-h, durab-h, 2x bruiser-h, then bruiser-f (heart_of_ruin.h:12-16); Marcella treasure-f, bruiser-f, jungle-s, 2x bruiser-h, then bruiser-f (marcella.h:15-19); Ryth treasure-h, jungle-s, bruiser-h, durab-h, bruiser-s, then bruiser-h (ryth.h:8-12); Vendetta treasure-s, jungle-s, bruiser-h, then bruiser-s (vendetta.h:13-17); Vesper and Ren keep the generic layered plan (champions.h:101-141; Vesper: durab-s, jungle-s, bruiser-h, then bruiser-s). Late mixes per champion from r400 (`late_mix`). Health-shard shares (`hp_share`, champions.h:166-181) apply only to champions without their own plan (Vesper, Ren).
- **Vesper**: her presence switches the whole team to caster mode (kite, cast-first sweep, recall near foes, flee at 33%, hold altar) (champions.h:185-188, main.cpp:1041-1052); first on shared rewards until r200 and does not leave a waiting reward within 6 (P_VCARRY); shoots before dashing out when kiting (vesper.h).
- **Heart of Ruin**: never dashes to travel, the dash is a strike landing on the most units (heart_of_ruin.h:19-104).
- **Vendetta, Marcella**: the cut rule (leave a contact before hp minus recent damage < 40%).
- **Ren**: drafted instead of Heart of Ruin on far maps only; caster plan, 50% health shards.
- **Capture priority** (`cap_rank`, champions.h:195-200): Stellar, then ranged, then Ren, then melee; used by the cache/no-leave rules (mostly off: `P_CAPPRIO`=0, `P_CACHE`=0).
- Dead code for drafts no longer taken (Cassi/Issac twin rules, Tavi field shop, Varg splash, Stellar) stays compiled but inert.

### A.7 Round gates
- r30-150 (near maps, spawn walk < 35): pair-walk, wait-pair, x0.4 for gem groups with no ally claim nearby.
- r150: hold-altar x2 begins (caster mode); gold weight cap 0.45 (no change in practice, it was already 0.45).
- r200: Vesper's capture priority / no-leave ends.
- r400: late shop mix (Bruiser blends) for the fill step.
- r550 (`P_JACKPOT`/`P_JACKGO`): the jackpot group may be targeted, scores x10, "needs" at most 3 and the "too-strong" bail is suspended for it (2588, 2600-2607, 3609-3611); the first-contact leave verdict and the hp rules still apply to each champion separately on the way.
- r940: gold weight drops to 0.24.
- r1850: bank any gems.

---

## Part B. What a top-10 team's five champions do, versus ours

Games (winner side for the top-10 games; our side for e1foco games vs ranks 56-70):

| map | top-10 game (winner) | e1foco game |
|---|---|---|
| contest (2 monolith groups of 200 gems, 12 gold groups) | Intercontinental Fish #1 beat Mite #2 1000-0, r925 | loss 0-1000 vs an iq too high, r1235 |
| elk_arena (one 72-gem/180au group in the centre, 28 gold groups of 20-40) | Fish beat prism best girl #4 1008-0, r1208 | loss 0-1032 vs Ding, r1123 |
| stampede (one 160-gem/620au jackpot mid, 12 gold groups) | Fish beat Claudus Maximus #7 1120-0, r1453 | loss 0-1167 vs SquidProxyLovers, r1626 |
| crossing (24 small gem groups 4-57) | Mite beat Fish 1005-887, r814 | loss 930-1005 vs Gamblr, r1115 |
| big_world (100x100, 22 gem groups, two 228-gem centre groups) | Fish beat Mite 1000-778, r955 | loss 880-1004 vs BBL, r1278 |
| fields (20 gem groups incl. 2x256 mid, 2x142 sides) | Fish beat prism best girl 1004-609, r620 | loss 337-1177 vs ha2t, r784 |

Intercontinental Fish drafts Vesper, Vendetta, Heart of Ruin, Cassi&Issac, Marcella (6 bodies); Mite drafts Vesper, Vendetta, HoR, Tavi, Marcella. Our draft was HoR/Vesper/Marcella/Ryth/Vendetta (Ren for HoR on big_world).

### B.1 The top-10 plan, in words
1. **Two carries, three (or four) escorts.** In every Fish game Vesper and Marcella take almost all captures and the gems (contest: Vesper 3627 gold / 400 gems, Marcella 3896 / 600; elk_arena 4621/360 and 5837/648; stampede 5189/640 and 4174/480). Cassi/Issac/HoR earn 0.5-1.7k and absorb the deaths (all 6 Fish deaths on contest and 6 of 7 on stampede are Cassi/Issac; Vesper and Marcella die 0 times in all five Fish games). The carries shop early and often: first shop r48-100, 9-17 trips a game; the escorts shop 2-7 times.
2. **Opening r0-50: one ball on one group.** The whole team walks together to the nearest rich group (not the 4-gem clusters) and clears it in 15-25 rounds: stampede all six on G12 (80au) at r0-49 then G11; big_world all six on G6 (41g/260au); fields all six on G11 (44g/180au) then G1; elk_arena five on the centre cluster triangle G0/G2/G4 while Vesper alone sweeps far clusters. Mean distance to the nearest ally in r0-49 is 1-2 tiles. Capture gold by r150: Fish 870-1000 on every map (big_world 710).
3. **r50-300: two or three subgroups cycling adjacent groups on their own half, the carries shuttling to the shop.** Off-spawn, an ally is within 4 tiles 56-73% of the time (elk_arena 72%, big_world 73%, contest 67%, stampede 56%) and a champion is alone (no ally within 6) 21-33%. Each subgroup rotates 2-3 neighbouring groups as they respawn; the carry on the pair takes the reward (the "+Nau" in the tables sits almost entirely on Vesper and Marcella). They stay on their half: 2-17% of rounds in the enemy half before r300. Spent gold at r300: 1.1-2.6k (contest 2130, elk 2640, stampede 1130, fields 1930).
4. **The big gem group is a timed team job.** Nobody touches the 160-200 gem group before the team has ~2k gold of items; then 3-4 champions arrive together and the carry captures while the others screen: contest G0 (200 gems) first taken r~520 by Vesper (+772au) with Cassi/Issac/HoR within 2-3 tiles, again r650 and r850, Marcella taking G0 r650-699 and r850-899, G1 r750; stampede G10 (160 gems/620au) first taken r650-699 by Vesper after a probe at r600 (Vesper stood at G10 50% of r600-649), then r850 (Marcella), r1000, r1100, r1200, r1300, r1400: one capture every respawn, each banked at once as a 160-gem trip. elk_arena's 72-gem centre G0 is taken 14 times, the first at r50-99 by Marcella with HoR and Vesper beside her, then roughly every 50-100 rounds by whichever carry is nearest, always with 2+ allies within 4.
5. **Farm maps: spread wider but still in pairs, zero deaths.** On fields (r620 win) and big_world (r955) the pairs are 2 champions, each pair owning two neighbouring groups 10-20 tiles apart, recalling together; deaths 0-4 (twins only); bank trips of 40-50 gems; no visit to the 228/256-gem centre groups on big_world (not needed: 22 side gem groups), one visit to G8 (256) on fields at r500-549 by Marcella with Cassi/Issac escorting, which ended the game.
6. **Response to enemies.** Being paired, their local hp ratio is usually favourable, so they take the fight and the kills (Fish: 25-56 kills a game on contest/elk/stampede, 6-7 deaths). When an enemy pack shows up at a group they are not at, the carry keeps farming the next group over; the escorts move to it. Recalls happen at 50-70% hp from 6+ tiles away and are not interrupted.

### B.2 Our plan (e1foco), in words
1. **Five independent farmers.** From r0 each champion scores groups alone and the claims only stop two from picking the same one: stampede r0-49 our five are on five different groups (G11, G12, G3, G1, G5), elk_arena r0-49 on G28/G6, G4, G2, G9/G17, G24/G12. Off-spawn an ally is within 4 only 15% (elk_arena), 22% (stampede), 33% (contest), 43% (big_world), 46% (crossing, fields) of the time; alone (no ally within 6) 36-75%. Mean nearest-ally distance in the first 150 rounds is 8-15 tiles.
2. **Gold income is even and lower.** Everybody earns 0.7-2.2k gold; nobody is the carry (contest 798/718/732/468/972; stampede 716-1596). Capture gold by r150 is 320-710 (elk_arena 1126 is the exception: 29 gold groups and we sweep them alone fast), by r300 0.7-2.2k vs Fish 1.7-3.0k, by r550 1.8-4.1k vs 3.8-5.9k.
3. **The gem group is never assembled for.** contest: 0 gem captures in 1235 rounds (57 gold captures); the monolith groups need the roster (`mono_only`), `needed > here` -> "too-strong"/"need-heal" over and over, and no mechanism brings five champions to one tile. elk_arena: 0 captures of the only gem group G0 (72 gems) in 1123 rounds while Ding took it 13 times; we farmed 178 gold groups spread over the whole map, 75% alone. stampede: 0 gem captures; from r550 the x10 jackpot pulls champions to mid one at a time (r550-599: Vesper, Marcella, Ryth each "mid/G10" with allies 4-6 away) and r600-649 three of them die at mid; the pattern repeats until r1626 (23 deaths, 5 champions each die 4-5 times). On fields we never captured G8/G9 (256 gems) or G12/G13 (142); the one visit was Ryth alone at G13, who died there (r150-199); on big_world the two 228-gem centre groups were untouched by both sides.
4. **Shopping is comparable in frequency, smaller in total.** First shop r36-150 for most champions but r400-855 for some (Vendetta r407 on stampede, Ryth r855 on contest, HoR r383 on contest), 1-14 trips a champion; spent/earned ratio ~85-100% like the top 10, but on 40-70% of the income. Gold in hand sits at 300-500 for long stretches on contest/elk/stampede (shop trip only when a capture is not pending and 40 rounds since the last).
5. **Fights are taken alone and lost.** With one ally within 4 only 15-46% of the time, `favourable` is rarely true, so the step is `back_off`/avoid, and the kills go the other way: contest 32 deaths (K 5), stampede 23 deaths (K 4), vs the winners' 6-7 deaths. On the farm maps (crossing 10 deaths, big_world 3, fields 8) the deaths come from camps and lone encounters at the mid gem groups (fields: Ryth dies at G13 (142 gems) alone at r150-199, Marcella at G2 alone r250-299).
6. **Banking** on crossing and big_world is in 22-28 gem bags (41-45 trips) against 31-45 per trip for the winners, who also chain groups before banking; on fields 26 vs 50.

### B.3 The few numbers that matter (winner side vs our side, same map)

| map | capture gold r150 / r300 / r550 | spent at shop r300 | gem-group captures (of total) | deaths (by r300) | ally within 4 / alone>6 off spawn | first capture of the big gem group |
|---|---|---|---|---|---|---|
| contest, Fish | 998 / 2569 / 5299 | 2130 | 5 of 66 | 6 (4) | 67% / 22% | G0 r~520 (Vesper, 3 allies within 3) |
| contest, e1foco | 672 / 1088 / 1785 | 790 | 0 of 57 | 32 (6) | 33% / 51% | never |
| elk_arena, Fish | 1002 / 3029 / 5934 | 2640 | 14 of 144 | 7 (3) | 72% / 21% | G0 r~60 (Marcella + HoR + Vesper) |
| elk_arena, e1foco | 1126 / 2211 / 4113 | 1710 | 0 of 178 | 6 (0) | 15% / 75% | never |
| stampede, Fish | 874 / 1922 / 3855 | 1130 | 7 of 80 | 7 (0) | 56% / 33% | G10 r~660 (Vesper, Vendetta+Marcella beside) |
| stampede, e1foco | 712 / 1594 / 3267 | 1220 | 0 of 98 | 23 (2) | 22% / 67% | never (3 die at mid r600-649) |
| crossing, Mite | 330 / 600 / 1440 | 660 | 73 of 73 | 7 (1) | 54% / 35% | n/a (small groups) |
| crossing, e1foco | 319 / 665 / 1940 | 670 | 82 of 82 | 10 (0) | 46% / 39% | n/a |
| big_world, Fish | 710 / 1530 / 3199 | 1500 | 40 of 44 | 2 (0) | 73% / 21% | not visited |
| big_world, e1foco | 492 / 808 / 2365 | 660 | 43 of 49 | 3 (2) | 43% / 48% | not visited |
| fields, Fish | 883 / 1676 / 3819 | 1930 | 28 of 28 | 4 (0) | 69% / 23% | G12 (142) r300 Marcella; G8 (256) r~520 Marcella + twins |
| fields, e1foco | 476 / 793 / 1542 | 660 | 46 of 52 | 8 (3) | 46% / 36% | never (G13 visit by Ryth alone r150: death) |

Reading: on the three "one big gem group" maps the difference is not fighting skill but formation: the top 10 arrive at the gem group as a 3-4 body unit after shopping, we arrive as one body at a time or not at all (`squad_needed` caps at 2, `rally` only waits for claimers, the x10 jackpot pulls individuals). On the many-small-groups maps the difference is the pair: their champion is within 4 of an ally two thirds of the time and never dies; ours is alone half the time and dies to camps and lone encounters, and its captures are shared across five equal earners instead of fed to two carries who shop every 50-100 rounds.

### B.4 Where the five champions are at r150-300 (from the per-50 tables)
- Fish, stampede r150-299: Vesper and Marcella on own-half G11/G12/G3 (captures, shop trips of 160-360 gold), HoR and Vendetta between them and the enemy half (kills: Vendetta 2, HoR 1, Marcella 2 in r250-299 as a 4-body group hits enemies crossing to G11), Cassi/Issac next to the carries. Nobody at G10.
- Fish, contest r150-299: Vesper, Vendetta, Marcella rotating G2/G4/G5/G7/G13 in own half with 1-2 allies within 3-6 tiles, Cassi/Issac dead or on spawn (killed at r100-149 and r200-249 pushing too far), HoR at G4/G2 with the carries.
- Fish, elk_arena r150-299: all six within 2-4 tiles of each other around the centre G0/G3/G4 (a = 1-4), capturing G0 twice, 20+ kills in the window.
- e1foco, stampede r150-299: five champions on five different own-half groups (G5/G9, G7/G1, G12/G3, spawn, G11), mean ally distance 5-14, Ryth and Vendetta die alone; r550 onward the five trickle to G10 and die there.
- e1foco, contest r150-299: HoR, Vesper, Marcella, Ryth, Vendetta each on a different own-half gold group (a = 7-21 tiles), 4 deaths in the window, 0 gem income.
- e1foco, elk_arena r150-299: five champions on five different gold groups at the map edges (a = 5-20 tiles), the 72-gem centre untouched.

Full per-50-round tables for all 12 games (position mix, nearest-ally distance, hp bucket, captures with gold share, bank and shop amounts, kills/deaths, team captures and banked gems per window):
`/tmp/claude-0/-home-user-cambridge-battlecode-2026/8de47290-da50-5e17-ba34-a5ff0b87ab89/scratchpad/timelines.md`.
Per-side key numbers for all 12 games (both sides): `/tmp/claude-0/-home-user-cambridge-battlecode-2026/8de47290-da50-5e17-ba34-a5ff0b87ab89/scratchpad/summaries.md`.
Column key in the tables: `G5 30/own26` = 30% of the alive rounds within 3 tiles of group 5, 26% elsewhere on own half (`H` = on spawn, `mid`, `en` = enemy half); `a7(66%)` = mean distance to the nearest alive ally 7, no ally within 4 in 66% of rounds; `cap:G5` = standing on group 5's tiles when the team captured it; `+Nau` = gold received at captures; `bankN` = gems deposited; `shopN` = gold spent on spawn; `KxDy` kills (credited to everyone who damaged the victim in the last 3 rounds) and deaths; `deadN%` share of the window spent dead.
