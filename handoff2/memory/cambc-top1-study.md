---
name: cambc-top1-study
description: 2026-10-14 study of #1 Univardisty only: wins fight maps with ranged casters at range 4 + early recall; farm maps beatable
metadata:
  type: project
  modified: 2026-10-14T12:10:30.405Z
---

11:51 UTC 2026-10-14 the user asked to study only the #1 team (Univardisty of Shingtonwash, 1832, ladder 11:52).
Report: /mnt/project-files/analysis/top1-2026-10-14/como-juega-el-numero-1.md; scripts there (uni_agg.py,
uni_fights.py, castdist.py, opening.py). Data: ws/uni (80 games vs top 15, 57 distinct; replays, prof, teams.jsonl),
our v24 comparison in ws/ours24.

**Findings:** 40-17 overall; fight maps (collision/corners/elkring/interlock) 28-1, farm maps (expanse/packs/rows/
lanes/monolith) 12-16, they lose expanse farm mirrors. Draft fixed per map (table in report), Stellar on 8/9 maps,
3-4 damage casters (Stellar/Tavi/Prism/Ren) on fight maps buying power-f. Fight-map damage per game 23.5k dealt vs
our 5.8k (same 13k taken); K/D 13.1/4.7 vs our 1.4/8.8. Per real fight 1.27 kills / 0.36 deaths (ours 0.20/1.09),
hit first 67%. Spell hits ~12.2k dmg/game vs ours ~700 (~17x); 60-73% of caster hits with nearest foe >= 4 tiles.
Below 30% hp near foes: 36% recall / 42% walk / 17% die (ours 4/54/33). Corners mirror vs hello (same 5 champs)
1012-96: the play, not the draft. Focus fire is NOT the gap (87% vs our 89%). Not a tight ball (packed 21%).

Related: [[cambc-spell-gap]] [[cambc-volley]] [[cambc-caster-ball]] [[cambc-micro-strategy]]

**12:18 the user chose "Copiar su pelea".** Damage interrupts a recall (their unhit recalls finish, hit ones stop);
they recall with the nearest foe at 4-6. New fbase switches: P_DRAFTUNI 2 (their draft by team size when spawn
path <= P_UNI_PATH 45; also sets s.casters = team has Stellar, and sweep 3 only then), P_SHOPUNI (Ren/Prism/Stellar
power-f), P_RECALL_NEAR N (+ P_UNI_RN 1 = caster draft only; on v26's draft it lost gen 29-59). Arena vs spar7-10:
v26 15-33, u4 (draft+KITE+KITE_OUT 2+SWEEP 3+HOLD 200) 20-28, **u5 = u4 + RECALL_NEAR 5 + UNI_RN 26-22** (deaths 373,
kills 314 vs v26 373/101); u5 vs v26 13-5, gen 49-39, vs v24 12-6, hunter2 18-0.
**12:26 UTC: study19 = site version 27** (= u5; bot/mybot_study19.zip, main/params/fight_study19), uploaded.
**Online v27 (12:42-12:50, 65 games vs 13 top teams, ws/ours27 index): 19-46**; vs the 6 rivals met before 11-19
(before 7-28). Caster-draft maps 14-24: dealt 18.9k/taken 13.1k, spells 13.5k, K 7.6, D 8.7 a game; long maps 5-22.
Per real fight 0.65 kills / 0.84 deaths. Gap left = deaths: below 30% hp we die 37% (#1 17%), our Stellar dies
2.2 a game (#1 0.8). P_UNI_FLEE 35/45 (u6/u7, flee earlier with casters): vs spar7-10 29-19 / 26-22, vs v27
10-8 / 8-10, deaths not lower for u6: not uploaded. Tools: ws/tools/cmp27.py (before/after), kd.py, watch_draft.sh.
**13:09 "Morir menos":** online our Stellar dies 2.2/game, sparring only 0.9 (local can't reproduce it). Tried (fbase):
P_UNI_STAND 1 (no rooted pre-move cast with melee in reach; _HP) 24-24 vs spar; P_UNI_RENKITE 1 (Ren kites) Ren
deaths half, Cassi&Issac double, 22-26; P_UNI_FLEE 45 (u7) 26-22, C&I -60% Ren -40% deaths, but 8-16 vs v27 on
caster-draft gen maps. **13:18 study20 = site version 28** = study19 + P_UNI_FLEE 45 (bot/mybot_study20.zip),
uploaded for an online A/B vs v27 (card "Probar online" recommended). tools/champdeaths.py = per-champion arena deaths.
