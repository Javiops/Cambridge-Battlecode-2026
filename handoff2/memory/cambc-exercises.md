---
name: cambc-exercises
description: 2026-10-14 the user wants to code their own ideas; coding guide docs/ejercicios/programa-tu-idea.md (zones + camp efficiency); results; P_BAG 80 12-6
metadata:
  type: project
---

08:35 UTC 2026-10-14: guided exercises written in Spanish at `/mnt/project-files/docs/ejercicios/ver-partidas.md` (renamed)
(with v19.zip, v20.zip, mite-rows.zip = Mite vs NOVA rows replay ca5ab7b0). Built on v19 (study11) because
v20 (study12, P_HOLD 200) went 7-28 online, 0-7 on corners/collision, while beating v19 4-0 locally.
Note: study11's main.cpp has no P_HOLD code; use v20.zip to compare the hold.

Exercises: 0 setup (Windows PowerShell, Expand-Archive into bots\NAME, never copy a built bot folder: the
hidden .cambc breaks CMake); 1 `#define P_BAG 80` on the farm maps; 2 watch an online v20 loss vs a caster
team and write a rule for facing casters; 3 compare Mite's rows farming with ours; 4 fill a per-map plan table
(draft, plan, vs casters) that we then code via map detection in the draft (P_DRAFTMAP style).

Local result: P_BAG 80 on v19 vs v19 both sides, all 9 maps: 12-6 (farm maps 6-2; loses collision 0-2).
Earlier P_BAG 70/130 on v17 lost 8-10, so it is a candidate only. Expected outputs are in the file; the
engine is deterministic, so the user's runs must match exactly.

**How to apply:** when the user sends back exercise answers, turn rule descriptions into P_ switches and
test them against the caster sparring bot from the top-10 thread. Related: [[cambc-micro-strategy]],
[[cambc-centre-hold]], [[cambc-arena-setup]], [[cambc-user-prefs]].

**08:40 UTC the user said watching replays is Claude's job: they want to LEARN TO CODE their own ideas.**
Their main idea: split the map into our / their / middle zones, camp efficiency gems/hp and gold/hp, a small
penalty on middle camps, then test grouped vs split farming per map. Guide: `docs/ejercicios/programa-tu-idea.md`
(6 steps on v19, Windows, VS Code), `soluciones.md`, `solucion.zip` (reference), `quieto.zip` (idle bot: draft
then end_turn; measure rounds to 1000). Reference results vs idle: P_MEDIO 60 slower (5-13 vs v19);
P_EFICIENCIA (score = (gems+gold_w*gold)/hp / (travel+6)) faster on rows (432/405 vs 481/490), interlock,
expanse, corners, slower on collision/elkring/packs, 9-9 vs v19; only on those 4 maps (detected by
groups/altars: rows 9/2, interlock 16/4, expanse 30/10, corners 30/5) = 11-7 vs v19. P_PACKOPEN 2000 (all
grouped) much slower everywhere. Coach them; don't write their code unless asked.
08:50-09:00 UTC: the user flipped the idea to a BONUS for middle camps (P_MEDIO > 100: "a contested resource we get
is one they don't"). Locally it does not help on v19 (130: 7-11) nor on v21 (study13 + zona/P_MEDIO, scratch
build): vs idle total rounds 7859 (100) / 7853 (130) / 8111 (160) / 9292 (200); vs v21 9-9 / 7-11 / 4-14 / 6-12.
Only an online test could show the denial value.
09:02 UTC: v21 failed online (5-25 vs top 10); site advice is v22 (study14 = v19 + no-chase). Bonus 130 on v22: vs idle 7282 vs 7171 rounds, vs v22 5-13. Middle bonus not recommended on any base.
09:20: guide step 6 rewritten for unseen maps (no map detection): 6a P_RUTA path distance, 6b test on mapas-nuevos.zip,
6c grouped vs split; solucion.zip now = zonas + P_RUTA 1. See [[cambc-unseen-maps]].
