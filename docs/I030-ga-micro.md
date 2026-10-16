# I030 - genetic algorithm over the fight parameters

Tool: `tools/ga` (README there). Base: study27-economy (the online bot on 16 Oct). Macro unchanged.

## First candidate: genome 65a6d152b6 (16 Oct, after 26 generations)

Changes vs study27-economy (`python3 tools/ga/ga.py export --id 65a6d152b6 --out bots/<name>`):

| param | base | evolved |
|---|---|---|
| P_FLEE_PCT | 25 | 29 |
| P_UNI_FLEE | 35 | 44 |
| P_RECALL_PCT | 55 | 54 |
| P_RECALL_NEAR | 5 | 7 |
| P_BAIL_PCT | 18 | 12 |
| P_ENGAGE2 | 120 | 74 |
| P_GA_FAV (favourable without target, %) | 90 | 83 |
| P_GA_KILL_X (killable = hp <= str x N/10) | 20 | 5 |
| P_GA_SPAWN_HEAL (% hp before leaving spawn) | 95 | 87 |
| P_FRONT_OUT | 130 | 145 |
| P_GA_KITE_HP | 130 | 128 |
| P_VOLLEY | 70 | 43 |
| P_CHASE_GEMS | 150 | 144 |
| P_DANGER / _T / _R | 3 / 40 / 6 | 4 / 45 / 5 |

Results:
- Validation (v100, never trained on; vs base, spar11, spar16 and two evolved rivals): pairs better/worse than the
  control 134-89, p=0.003.
- Gate (`tools/gate.py ... --kind fight --extra fresh300`): **PASS**. Sealed maps hold60+dev200+fresh300: 180-79 maps
  won/lost on both sides (p<0.001), gems/100 rounds 168.1 vs 160.4; panel flips 36 for, 16 against (p=0.008);
  0 faults; fuel-exhausted turns 162 vs 140 (limit +30).
- Zip: `/mnt/project-files/bot/mybot_ga65a6.zip` (not uploaded). Next: online A/B (stage 3), which decides fight rules.
