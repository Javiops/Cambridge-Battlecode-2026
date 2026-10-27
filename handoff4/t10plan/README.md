# t10plan-v2: el plan de partida del top 10 sobre e1foco

Zip: `zips/e1foco-t10plan.zip` sha256 `043f34b2bc1b6b84d602de0fbce4a27d1b7a9d32332b975ba5b14a7122d59ca3` (src/ como e1foco.zip).
Marcadores stdout: `[init] t10plan-v2 until=650 lo=50 hi=250 free=25 roles=1 escw=300 maps=69` y, una vez por campeón,
`[t10plan] who=<campeón> map=<mapa reconocido|none> side=<0|1> games=<n> groups=<n>`. La línea de estado lleva `pl=<elecciones en el plan>/<fuera>`.
Diff frente a e1foco: `src/t10plan-v2_vs_e1foco.diff` (+ `plan_t10.h` generado).

## Datos (r1-600, tramos de 50; 600 réplicas top10 vs top10 del 27-10, 75 de e1foco en c34)
| | top10 ganador | top10 perdedor | e1foco | rival c34 |
|---|---|---|---|---|
| aliados a ≤4, r0-50 | 2.26 | 2.07 | 1.52 | 2.10 |
| aliados a ≤4, r50-600 | 0.7-1.07 | 0.7-0.95 | 0.45-0.62 | 0.65-1.02 |
| campeones por campamento golpeado | 1.4-1.65 | 1.3-1.5 | 1.14-1.39 | 1.3-1.56 |
| en mitad propia | 76-80% | 82-85% | 86-89% | 79-83% |

Por campeón (ganadores, partidas enteras): Vesper y Marcella son los carries (28% / 30% de las gemas, 2.1k / 2.0k de oro, 0.7 muertes);
HoR, Vendetta y Ryth escoltan (17% / 22% / 12%, 0.6-1.2k de oro). e1foco: cinco iguales (17-26% de gemas, 0.8-1.2k de oro, 2.3-2.9 muertes).
No hay parejas fijas en el top 10: cada campeón tiene a cualquier compañero cerca más o menos por igual.

## El candidato (una pieza: el horario entero)
1. **Horario por mapa** (`plan_t10.h`, 69 mapas del pool): para cada mapa, lado y tramo de 50 rondas hasta r650, la cuota de rondas-campeón
   que los equipos top 10 pasan golpeando cada grupo (ganador pesa 2). `choose_target` multiplica cada grupo por 0.5 (fuera del plan)
   hasta 2.5 (grupo principal del tramo). En los grupos del plan (≥25% del principal) se quitan las penalizaciones de mitad rival y
   puerta enemiga, se admiten 2 campeones y se quita el "cúmulo es trabajo de uno". El mapa se reconoce por los centros de grupo
   (todos a ≤2 casillas), el lado por el spawn. Desde r650, el juego de e1foco.
2. **Roles**: los escoltas (HoR→Vesper, Ryth→Marcella, el resto al carry más cercano) toman el grupo reclamado por su carry como grupo
   líder (x3) y no se alejan más de 8 de él.

## Comprobación local (70 mapas x 2 lados vs kvvl, motor 2.0.0 en la nube)
| bot | vs kvvl |
|---|---|
| e1foco | 87/140 |
| v1 (horario hasta r2000 + pairfarm en toda la partida) | 59/140 (roto por el pairfarm: solo pairfarm 65, solo horario 79) |
| **t10plan-v2** | **77/140** |
| v2 sin roles | 70/140 |

Mecanismo en 31 partidas locales r50-350 (v2 / e1foco): aliados a ≤4 0.82 / 0.58, grupo mayor 2.25 / 1.95, campeones por campamento
1.54 / 1.33, muertes por tramo 0.31 / 0.40, contactos en inferioridad 7% / 9%, gemas capturadas por tramo 41 / 43, capturas 2.0 / 2.4.
No se mueve: posición (mitad propia 91% / 89%; el top 10 está al 77%).

## Herramientas (`an/`)
feat.py (rasgos por campeón y tramo de un .json.gz de ext.py), agg.py + report.py (tabla top10 vs e1foco), pertype.py, pairs.py,
build_plan.py (genera plan_t10.h), localcmp.py, h2h.sh, score.sh. Decodificado con viewer/ext.py + replaydump_maxr.js (MAXR=700) y el wasm
v2_0_0 de la rama del hilo de campeones (commit 715ca79).
