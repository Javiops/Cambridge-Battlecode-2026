# Piezas por campeón sobre v20c (V20 en un fichero por campeón, bots/v20/src)

Cada carpeta es el `src` completo del bot. Base para comparar: `bots/v20/src` (= v20c, juega como V20).

| carpeta | campeón | qué cambia | parámetros |
|---|---|---|---|
| hortgt-v1a | Heart of Ruin | elige objetivo como el HoR del top 10: grupos guardados con gemas x1.5, grupos de solo oro x0.5 (`heart_of_ruin::target_w`) | P_HOR_GUARD_W 150, P_HOR_GOLD_W 50 |
| hortgt-v1b | Heart of Ruin | igual, más fuerte: guardados x2.0, solo oro x0.3, clusters de gemas sin guarda x0.7 | 200 / 30 / 70 |
| hortgt-v1c | Heart of Ruin | v1a + sin el recorte x0.7 de "necesita compañía" en grupos guardados con gemas | P_HOR_SOLO 1 |

Por qué: online en mapas cercanos el HoR del top 10 está pegado a un campamento 50 rondas por partida en r0-150 (el nuestro 24) y 64 frente a 38 en r150-400, sobre todo en grupos guardados con gemas.
Local (160 partidas contra rTop1 y rD): HoR pegada a campamentos 14% -> 22-23% de rondas r30-150 (25 -> 35-37 rondas/partida), tiempo muerta 14% -> 8-10%; victorias -2 / 0 / -4 (ruido).
Fuera de HoR no cambia nada (el hook devuelve 1.0 si HoR no está en el equipo; Ren en lejanos queda igual). Monolitos excluidos.

## hortgt-v2 (24-10 16:50): solo en mapas cercanos
J2 de v1a/b/c: -4,4 / -5,6 / -4,7 (medios -10 a -18, cercanos -2 a -7, lejanos +2). HoR farmea +25% pero el equipo pierde, sobre todo en medios.
v2 se apaga si el camino entre spawns es >= 35 (P_HOR_NEAR, el mismo corte "near" del Juez 2; collision da 34 aquí y 35 en el Juez, así que aquí cuenta como cercano).

| carpeta | qué cambia | parámetros |
|---|---|---|
| hortgt-v2a | v1a solo en cercanos | 150 / 50 / 100, NEAR 35 |
| hortgt-v2b | solo quita los grupos de solo oro (x0.5), sin subir los guardados, en cercanos | 100 / 50 / 100, NEAR 35 |
| hortgt-v2c | v1b solo en cercanos y solo antes de r150 | 200 / 30 / 70, NEAR 35, RMAX 150 |
