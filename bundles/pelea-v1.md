# pelea-v1 para la cadena 17 (veto del Juez 2 en el PC, hilo «Iterar rápido con el PC al 100%», 10-24)

Zips de «Copiar las decisiones del top 10» (handoff/pelea, commit c21b56d), copiados tal cual; sha verificado igual que en handoff/pelea/SHA256SUMS.

| zip | sha256 | J2 frente a V20 | frente a su control pelea-v10 (+1,6) | +2 en pelea (todos los mapas, r<300) | +2 en cercanos r<150 |
|---|---|---|---|---|---|
| pelea-v1a.zip | 1aaa6ed4… | +5,8 (barra 8,3) | +4,2 | 20,8% → 23,3% | 21,7% → 26,3% |
| pelea-v1b.zip | 5014c180… | +0,7 (barra 8,7) | −0,9 | 20,8% → 23,3% | 21,7% → 25,5% |

Pasan el veto (≥ −5 frente al control). Ojo: el control (kvvl + solo el contador) da +1,6 frente al +10,4 de kvvl. Un cambio de fuel sin
cambio de lógica mueve el Juez 2 unos 9 puntos, así que las diferencias de menos de ~9 entre variantes de kvvl son ruido.
Recomendado: pelea-v1a primero.

## Añadido: pelea-pA.zip (vkite-v3 de Vesper + mstick-v1 de Marcella, hilo «Mejorar cada campeón», handoff/champ/pelea-v1/pA de 185dba6)
| bot | J2 frente a V20 | mapas de reserva (40 de maps_hold60, 800 partidas, barra 4,4) |
|---|---|---|
| kvvl (k_vvl_mgwp) | +10,4 | +15,8 |
| **pelea-pA** | **+16,7** | **+16,8** |
| pelea-v10 (control) | +1,6 | +13,4 |
| pelea-v1a | +5,8 | +12,0 |
| pelea-v1b | +0,7 | +10,2 |
| pA + pelea-v1a | −5,1 | +11,8 |
pB = pA (fightnum no cambia ninguna partida: pC da exactamente lo mismo que kvvl). pD (solo vkite-v3) +8,9; pE (solo mstick) +12,9.
pvpnum en cercanos (200 partidas): Marcella r150-400 pegada a 1 casilla 27% → 22%, num +2 20% → 24%; Vesper r<150 a 1 casilla 17% → 15%.
Recomendación: pelea-pA por delante de pelea-v1a. La regla de entrada (v1a) sube la superioridad numérica en local (+2 de 21,7% a 26,3%)
pero resta en los mapas de reserva y al combinarla con pA.
