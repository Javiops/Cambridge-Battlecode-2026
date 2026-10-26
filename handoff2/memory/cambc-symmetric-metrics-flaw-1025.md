---
name: cambc-symmetric-metrics-flaw-1025
description: Method flaw found 10-25 ~20:10 - outcome metrics from top10-vs-top10 games (damage ratio 1.00, K/D, deaths/game, farm rates) are symmetric or rival-dependent and cannot be compared with ours vs mid-table; compare decisions per situation or top10 vs our-level rivals
metadata:
  type: project
---
Found by the coordinator 2026-10-25 ~20:10 Madrid (aprox., sin reloj) while going deeper on the user's request ("parala, estamos buscando fixes que no vienen a cuento, profundiza"). The b35nohp online series was stopped at 450 pairs (+14, bar 23.5, not promoted).

- Top10-vs-top10 games give damage done/received = 1.00 and kills/deaths 0.27/0.27 by construction (both sides are top 10). Comparing them with our 0.82-0.91 vs ranks 52-71 says nothing about why they win. Durations, deaths per game, gems per 100 rounds and win rates of intruder fights also depend on the rival's strength.
- Valid comparisons: decisions per matched situation; or top-10 games against rivals of our level (Sprint tournaments, public games vs ranks 40-90).
- What survives: within our own games, we lose the damage exchange at equal bodies with more max HP (0.89-0.91 early, 0.82-0.84 at r401-600) vs our band. Deep question set to top10 + evaluador: decompose it (rounds hit without hitting back and why, ability vs basic damage, unused ready abilities, target choice and overkill, heals/shields, item stats), wins vs losses, kvvl vs b35nohp. Peleas/farmeo paused new pieces to help explain each component from the code.

**How to apply:** before using any top-10 number as a target, ask whether it depends on the opponent; if so, it is not a target. Related [[cambc-copy-x-rule-1025]], [[cambc-reasons-not-symptoms-1025]].
