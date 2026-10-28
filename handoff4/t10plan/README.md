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

# t10plan-v3 (2026-10-28 ~00:40 UTC)
Zip `zips/e1foco-t10plan-v3.zip` sha256 `6036727fb08a866ef7803e90dd64f3fad2aec3f455d2793d013c88aa15f9b231`, diff `src/t10plan-v3_vs_e1foco.diff`.
Marcadores: `[init] t10plan-v3 rtog=0 depart=10 farcut=0 until=650 end=800 ball=50 bigstr=120 lo=50 hi=250 free=25 roles=1 escw=150 maps=70`;
desde r150 una vez por campeón `[t10plan] who=.. map=<mapa|none> side=.. games=.. groups=.. camps=.. tried=..`; estado `pl=on/off dep=.. rtog=..`.

Cambios frente a la v2:
1. **Horario por posición de campamento** (no por id de grupo), solo ganadores, con el decodificador corregido del PC (6746f59) en los 18 mapas
   afectados; peso = rondas golpeando x (120 / vida máxima)^0.35, para no sobrevalorar alces lentos frente a cúmulos. El bot suma los campamentos
   de cada grupo suyo. La huella del mapa es el número de campamentos y que todos caigan sobre una casilla de un grupo: reconoce 70/70 en local.
2. **Horario desde r150** (la apertura de oro queda como en e1foco; online la v2 cobraba -44% de grupos de solo oro). Los grupos de solo oro
   nunca bajan por el horario. Salida suave de r650 a r800 (sin acantilado).
3. **El carry captura**: una escolta deja la recompensa a Vesper o Marcella si están en el grupo o al lado; el carry ignora a las escoltas.
4. Roles toda la partida; mitad rival y puerta enemiga solo con compañía (otro aliado reclama el grupo o es el grupo del carry), sin incursiones
   en solitario; grupo grande del horario hasta 4 cuerpos (jackpot incluido cuando el top 10 lo toma); salir del spawn esperando a un aliado
   que se cura o hace recall (≤10 rondas; dispara poco).

Probado y descartado (vs kvvl, e1foco 87): horario solo en cercanos 71-84; escolta en el campamento vecino 75-79; escolta x3 73-75;
pairfarm hasta r400 86 pero sin cohesión (49%); recall en pareja 73 (dispara 1 vez por partida); suelo x1.5 del oro 76.

| bot vs kvvl (140) | victorias | aliado a ≤4 fuera del spawn r50-600 | muertes r50-600 por partida |
|---|---|---|---|
| e1foco | 87 | 43% | 4.9 |
| solo roles + captura del carry | 85 | 48% | 4.8 |
| **v3** | **82** | **51%** | **4.2** |
| v3 con horario desde r0 | 74 | 53% | 4.0 |

Ruido local: dos bots casi iguales (el recall en pareja dispara 1 vez por partida) dan 85 frente a 71 y 82 frente a 73: ±7 en 140 partidas.
12 partidas con timeline.py en `timeline/` (6 mapas x 2 lados): v3 aliado 50% frente a 31%, muertes 4.2 frente a 4.1, 9/12 frente a 7/12.
Puerta del coordinador (>55% y ≥87): NO pasa (51%, 82).

# t10plan-v3i (2026-10-28 ~01:45 UTC), SIN horario (orden del coordinador tras v3 online −11)
Zip `zips/e1foco-t10plan-v3i.zip` sha256 `d2501443e78844d39de45418dc6adf42fa9643fccc278cbd499b45230a8c0057`, diff `src/t10plan-v3i_vs_e1foco.diff`.
Marcador: `[init] t10plan-v3i plan=0 cmem=0 ballw=200 bigwait=0 eshome=1 rtog=0 depart=10 ... ball=0 ... roles=1 escw=150 maps=70`.
Contiene: roles carry/escolta (la escolta toma el grupo de su carry, x1.5), el carry captura, la escolta hace recall cuando su carry
hace recall o está en el spawn (ESCHOME). Horario apagado (P_T10PLAN 0): la elección de campamento es la de e1foco salvo el vínculo escolta→carry.
Bola r0-50, memoria del grupo del carry y espera de 3 ante grupo grande están en el código, apagadas por parámetro (P_T10_BALL, P_T10_CMEM, P_T10_BIGWAIT).

Alternativa `zips/e1foco-t10plan-v3i2.zip` sha256 `0ffe399e8e351d5ec2e7e675db949a4a6bd2d23a9ef1ac735e249cf90e3eca30` = v3 (con horario) + ESCHOME.

| bot vs kvvl (140, 70 mapas x 2 lados) | victorias | aliado a ≤4 fuera del spawn r50-600 | muertes r50-600 |
|---|---|---|---|
| e1foco | 87 | 43% | 4.9 |
| v3i2 = v3 + ESCHOME (dos tiradas) | 84 / 83 | 54% | 4.0 / 3.7 |
| v3i2 + bola r0-50 | 71 | 55% | 4.1 |
| v3i2 + espera de 3 ante grupo grande | 68 | 54% | 3.7 |
| v3i2 + memoria del grupo del carry | 74 | 54% | 3.6 |
| v3i2 + las tres + recall en pareja | 43 | 49% | 6.0 (2 partidas) |
| **v3i** (sin horario, roles + ESCHOME) | **67** | **52%** | **4.3** |
| v3i + escolta x3 | 65 | 54% | 4.5 |
| v3i + bola suave (x2 sin correa) + espera sólo si vienen 2 más | 54 | 51% | 5.0 |
| sin horario con las cuatro piezas | 55 | 52% | 4.6 |

12 partidas con timeline.py (`timeline/summary_v3i.md`, `timeline/timelines_v3i.md`): aliado 44% (v3 50%, e1foco 31%), muertes 4.4 (4.2 / 4.1), 3/12 (9/12 / 7/12).
Puerta (>55% y muertes < e1foco): ninguna variante pasa del 55%. El log de distancia escolta-carry (`ef=` en la línea de estado) no sale en local: run-batch no guarda el stdout.

Corrección: v3i en las 12 partidas gana 6/12 (el primer resumen leía outcome al revés; v3 9/12 y e1foco 7/12 se mantienen).

# t10plan-v4 / v4b (2026-10-28 ~02:15 UTC): vínculo escolta→carry estructural, sin horario
- `zips/e1foco-t10plan-v4b.zip` sha256 `9f34c751bb4bfcd114eb354f156b1082eb8f4bf8b2b3ff7f0b8b4e7fce9660dc`, diff `src/t10plan-v4b_vs_e1foco.diff`,
  marcador `[init] t10plan-v4 neigh=6 v4=1 follow=4 plan=0 cmem=0 ballw=200 bigwait=25 eshome=1 ...`; estado `fol= v4=<publicaciones del carry>/<elecciones de escolta>/<vecino>`.
- `zips/e1foco-t10plan-v4.zip` sha256 `07475e36dacb22236a1e1d6096bc8e6002da717cd27163b87db162d566a57389` (sin vecino).
1. El carry, al capturar, elige y publica su siguiente grupo en el mismo turno (nunca claim −1 vivo).
2. La escolta no puntúa: su objetivo es el grupo del carry; si reaparece, el vivo más cercano a ≤8 de él. v4b: antes, un grupo vivo sin reclamar,
   sin elk doble, a ≤6 del grupo del carry (la captura propia de la escolta).
3. Vínculo posicional en play_turn: escolta viva fuera del spawn a >4 del carry (o de su grupo si no lo ve) camina hacia él; en v4b no tira mientras
   farmea el vecino con el carry a ≤9. Si el carry se va, tira (suelta el vecino). El carry no espera nunca.
4. Bola fuera; espera de 3 sólo ante jackpot/str≥120 y sólo si otros dos reclaman ese grupo.

| bot vs kvvl (140) | h2h | aliado ≤4 | muertes r50-600 | capturas r<400 | cerca/esc muerta/esc spawn/carry muerto/carry spawn/separados |
|---|---|---|---|---|---|
| e1foco | 87 | 43% | 4.9 | 18.6 | 19/11/7/5/7/52 |
| v3i | 67 | 52% | 4.3 | 16.4 | 31/10/6/5/5/43 |
| v3i escolta x10 | 60 | 54% | 4.7 | 15.0 | 32/11/6/5/4/41 |
| v3i + vínculo posicional ≤3 | 56 | 62% | 4.3 | 13.3 | 40/10/6/4/4/35 |
| v4 | 47 | 63% | 4.3 | 12.7 | 42/10/5/4/4/34 |
| **v4b** (vecino ≤6) | **56** | **60%** | **4.2** | **14.1** | 38/11/6/5/4/36 |
| v4c (vecino ≤9) | 49 | 56% | 4.1 | 15.1 | 35/9/7/5/5/39 |

Capturas r<400 por campeón (a ≤1 de una casilla del grupo al capturar): e1foco HoR 3.8, Marcella 3.6, Vesper 3.5, Ryth 2.5, Vendetta 1.3;
v4 Marcella 4.0, Vesper 3.6, HoR 1.4, Ryth 1.2, Vendetta 0.6; v4b 4.0/3.6/2.1/1.5/0.8. El carry no llega a 7: su tiempo r0-400 es el de e1foco
(campamento 39-42%, camino 41-43%, spawn 8-9%, muerto 8-9%). Herramientas: an/escort.py, an/capby.py, an/carrytime.py, an/tlsum.py.

# t10plan-v4n (2026-10-28 ~02:50 UTC): v4b sólo en mapas cercanos
`zips/e1foco-t10plan-v4n.zip` sha256 `38a5b2dc943e8124939a743d919e45c386ace177684959848d5758dca45d0d6a`, diff `src/t10plan-v4n_vs_e1foco.diff`.
Marcadores: `[init] t10plan-v4n nearp=35 neigh=6 v4=1 follow=4 plan=0 ...` y `[t10plan] roles=<0|1> spawn_path=<n> nearp=35`.
Roles, seguimiento, publicación del carry, salida/recall juntos y espera de 3 sólo si el camino spawn-spawn < 35 (21 de 70 mapas); en el resto, e1foco.
Motivo: v4b online c34 cercanos 23 vs 20, lejanos 6 vs 11 frente a e1foco; en local igual (tabla).

| vs kvvl, victorias por camino | <35 (42) | 35-50 (44) | ≥50 (54) | total |
|---|---|---|---|---|
| e1foco | 25 | 31 | 31 | 87 |
| v4b | 22 | 17 | 17 | 56 |
| **v4n** | **21** | **32** | **29** | **82** |

Mapas cercanos (42 partidas), e1foco / v4b / v4n: aliado ≤4 47% / 60% / 60%, muertes r50-600 5.5 / 5.4 / 5.4, capturas r<400 16.6 / 13.4 / 13.3.
Todo el banco: v4n aliado 45%, muertes 4.4, capturas 17.4, rondas por captura del carry 44.
Carry mapa a mapa (an/mapcmp.py, timeline/mapcmp_v4b.md, 53 mapas comunes): top 10 ganador vs v4b cúmulo ≥50 0.16/0.10, cúmulo <50 1.89/2.11,
oro 2.03/2.69, lobos 2.33/2.63, alces 1.79/1.81: el objetivo del carry no es la diferencia.

# t10plan-v4o (2026-10-28 ~03:20 UTC): v4n + pareja desde r50 + Vendetta libre + la escolta acaba su grupo
Zip `zips/e1foco-t10plan-v4o.zip` sha256 `767a00f7568a6859e0e0656af93707abe873a93fa958ee5664b382a4803af8d3`, diff `src/t10plan-v4o_vs_e1foco.diff`, marcador `[init] t10plan-v4o rolefrom=50 freeven=1 keep=1 nearp=35 ...`.
vs kvvl: total 80/140 (cercanos 19/42, lejanos 61/98); cercanos: aliado ≤4 55%, muertes 5.4, capturas r<400 14.6 (e1foco 16.6, v4n 13.3).
Primera captura en cercanos vuelve a la de e1foco salvo fragment a (r114). elk_arena 53/53 (e1foco 63/73, v4n 35/35).
Online v4b en cercanos (timeline/online_v4b_near_deaths.txt): muertes tempranas de HoR siguiendo al carry; capturas perdidas casi todas en elk_arena.

# t10plan-v4o2 (2026-10-28 ~03:45 UTC): v4o con roles=0 idéntico a e1foco
`zips/e1foco-t10plan-v4o2.zip` sha256 `0b7ff143bc6f726c10bf41ab3f794c9125e49df66e12d394a50d50b266a7cbd2`, diff `src/t10plan-v4o2_vs_e1foco.diff`.
Marcador sólo en mapas con roles: `[t10plan] v4o roles=1 spawn_path=<n> nearp=35 rolefrom=50 freeven=1 keep=1 neigh=6 follow=4 bigwait=25 eshome=1`.
Causa de la diferencia v4n vs e1foco en lejanos: el printf largo de init y la primera llamada a t10_on() (spawn_path en la apertura) movían el init de un
campeón un turno; 27/98 partidas lejanas divergían (desde r2-3 en algunas). v4o2: sin printf de init, t10_act mira la ronda antes de spawn_path,
horario plegado en compilación, línea de estado sin campos nuevos con roles=0. Lejanas idénticas a e1foco posición a posición: 94/98
(las 4 restantes por diferencias de combustible de ~300 en r25: starvation a r4, crossing a r324, gem_fields a r517, road_of_riches b r551).
vs kvvl 80/140 (cercanos 21/42, lejanos 59/98); cercanos: aliado 53%, muertes 5.6, capturas r<400 14.8.

# t10plan-v4q (2026-10-28 ~04:10 UTC): v4o2 + juntarse en 4 ante 3+ rivales
`zips/e1foco-t10plan-v4q.zip` sha256 `33d0d2a582eb3b206e99a7941017e62d0132b39beb1524f8c09ec8309fb33ac7`, diff `src/t10plan-v4q_vs_e1foco.diff`, marcador `[t10plan] v4q roles=1 ... join=1`.
Online v4b cercanos (an/pairfoe.py): 4.35 episodios/partida de pareja viendo 3+ rivales a ≤6; otra pareja a ≤10 en 76%: muertes 0.18 vs 0.33, kills 0.41 vs 0.17.
Regla: miembro de pareja con 3+ rivales a ≤6, ninguno a ≤2, <4 aliados a ≤4 y 4 alcanzables a ≤10: camina hacia el aliado más cercano a 5-10 (join4).
vs kvvl 81/140 (cercanos 22/42, lejanos 59/98); cercanos: aliado 54%, muertes 5.3, capturas 15.3. Dispara 1.3 rondas por partida en local.

# t10plan-v6 / v6b (2026-10-28 ~04:30 UTC): subgrupos por región en mapas lejanos — CERRADA
Diff sobre v4o2 `src/t10plan-v6_vs_v4o2.diff` (sin zip). En ≥35: grupos partidos en 2 regiones por ángulo desde el spawn (3+2 campeones, Vendetta en la rica),
fuera de región x0.3 (v6) o x1.0 (v6b); con rival a ≤8, ir a ≤6 del compañero de región (línea `[v6-join]` por disparo, 24.5 por partida).
Lejanos vs kvvl (98), aliado ≤4 / con rival a ≤8 / capturas r<400 / muertes r150-600 / victorias: e1foco 40% / 50% / 19.4 / 3.10 / 62; v4o2 40 / 50 / 19.4 / 3.11 / 59;
v6 32 / 42 / 18.7 / 3.67 / 41; v6b 41 / 51 / 19.0 / 3.06 / 59. Las regiones separan al equipo; la regla de juntarse sola no mueve nada.

# t10plan-v7 / v7r (2026-10-28 ~10:50 UTC): las dos causas de why36 sobre v4o2
Diffs: src/t10plan-v7_vs_v4o2.diff y src/t10plan-v7r_vs_v4o2.diff.

**Regla 1, P_V7RJ** (verdict.h; main.cpp en pv-leave y bcf). Desde r30, un "quedarse" se vuelve a juzgar cada vez que entra otro rival a ≤6. Si power_ratio < 0.60, el veredicto pasa a "irse":
- el campeón camina a casa con flee(), porque safe_step se quedaba quieto fuera de alcance;
- bcf no lo vuelve a meter en la pelea;
- nunca deja un campamento a medias (awake_camp_near);
- escribe una línea `[v7-rejudge] r= who= foes= ratio= n=` por disparo.

**Regla 2, P_V7J** (choose_target_impl). El campeón libre (sin despejar un grupo a ≤3 y sin ir él mismo a uno de 40+) toma el grupo de 40+ gemas que reclama un solo aliado, si está a ≤12. Escribe `[v7-join]` por disparo.

**Mecanismo, local, 140 partidas contra kvvl, frente a v4o2.** El banco local no juzga; solo sirve para ver si la regla hace lo que debe.

| | v4o2 | v7 (las dos reglas) | v7r (solo regla 1) |
|---|---|---|---|
| disparos de rejudge por partida | — | 11.3 | 11.4 |
| disparos de join por partida | — | 3.5 | 0 |
| muertes r151-600 con 3+ rivales a ≤6 | 0.96 | 0.83 | 0.89 |
| muertes r151-600 | 3.49 | 3.47 | 3.35 |
| capturas de 40+ hasta r600 | 1.50 | 1.40 | 1.46 |
| capturas hasta r600 | 27.51 | 26.68 | 26.89 |
| gemas de captura hasta r600 | 336 | 326 | 330 |

- La regla 2 dispara, pero no sube las capturas grandes y cuesta capturas. No cumple su propio mecanismo, así que se manda **v7r**.
- Réplicas idénticas a v4o2 hasta el primer disparo: 138 de 140.
- Las otras 2 divergen antes:
  - gato_gemcombat5_a en r4: en el stdout las posiciones de r25 son iguales y el combustible difiere en unas 30 unidades;
  - crossing_a en r35.
  - Las dos se repiten igual al volver a jugar v4o2, así que es combustible (código distinto), no una regla.
- Zips (estructura src/ como v4o2):
  - zips/e1foco-t10plan-v7r.zip, sha256 a6dd4c0f05aaeade2a4f38f45fc9d12141d84c28411c0dcb4f905b838d080633;
  - zips/e1foco-t10plan-v7.zip, sha256 d5821a543ee7dfc9e28a3dab8b3b8a30b521d2da514f227ad96151bf654af16a.

# t10plan-v8a (2026-10-28 ~11:45 UTC): v7r con los grupos de 40+ gemas ×1.5 en choose_target
Desde r30, en grupos de 40+ gemas que no estén en su puerta. Línea `[v8-big] r= who= g= gems=` cuando el objetivo nuevo es un grupo de 40+; si el bonus solo mantiene el objetivo actual, no se registra.
- Combustible: ninguna partida diverge de v4o2 antes de r35. Hay 7 de 140 que divergen entre r35 y r79, antes de la primera línea registrada; son los casos de mantener objetivo, que no se registran.
- Mecanismo local contra kvvl (kvvl farmea oro, no es juez):
  - capturas de 40+: 2.11 frente a 1.46 de v7r;
  - capturas totales: 23.7 frente a 26.9;
  - gemas: 317 frente a 330.
- Diff: src/t10plan-v8a_vs_v7r.diff. Zip: zips/e1foco-t10plan-v8a.zip.

# t10plan-v8b: NO CONSTRUIDA (28-10 11:37 UTC), traspaso a coordinación
No hay código: la edición se paró antes de escribirse. Base: v8a (6665a2c).

Dato de an/big40.py sobre 140 derrotas online c34+c36, intentos sobre grupos de 40+ hasta r600 (nosotros / rival):
- intentos por partida 4.0 / 5.2, de los que acaban en captura propia 0.96 / 2.76;
- primer golpe con 2-3 cuerpos: 21 de 563 nuestros frente a 102 de 724 del rival;
- por intento: vida perdida 1155 / 850, muertes 0.22 / 0.06.

Diseño previsto:
1. **Esperar.** Bloque antes de `if (PR.campfoe ...)` en play_turn. Desde r30, sin rivales a la vista y sin campamento despierto cerca: si el objetivo es un grupo de 40+ gemas con str>0, vivo, a 5-8 tiles, y otro aliado lo reclama (count_claimers ≥1) pero no hay ninguno a ≤5, esperar hasta P_V8W=20 rondas en modo "v8-wait", con una línea `[v8-wait]` por objetivo.
2. **Que llegue el compañero.** P_V7J 1 (bigjoin) para que el aliado libre más cercano acuda.
3. **No abandonar** (pedido de coordinación). Con dos cuerpos a ≤3 del grupo y el campamento despierto, sin rival nuevo a ≤8, mantener s.target, sin re-choice ni recall por vida salvo flee_pct.
4. **Comprobación.** Réplicas idénticas a v8a donde no dispara la regla.

# t10plan-v9 "escuadras" (2026-10-28 ~13:30 UTC): una política de equipo por ronda desde r30 — NO PASA LA PUERTA
Zip `zips/e1foco-t10plan-v9.zip` sha256 `bc2910825675efafc89105ef312a5ec8ff2e964caee6607ebf7ef442fdd6d2f1` (src/ como v4o2 + `v9.h`), diff `src/t10plan-v9_vs_v4o2.diff`.
Todo bajo `P_V9` (params.h). Con `P_V9 0` el juego es el de v4o2: 8 partidas (elk_arena, crossing, starvation, gem_fields x 2 lados) con las líneas de estado
(posición, vida, modo, objetivo) idénticas a v4o2; con `P_V9 1` las reglas v4 (t10_on/t10_act) quedan apagadas y nada nuevo corre antes de r30 (ni init, ni printf).

**Diseño** (`v9.h` + main.cpp):
1. **Plan** (`v9::plan`, cada ronda desde r30, misma entrada en todos: roster propio, posiciones vistas, reclamaciones): líderes Vesper y Marcella (si falta uno, el vivo con más vida);
   los otros 3 van al líder más cercano con histéresis de 4 casillas, nunca 4+1 (el más lejano pasa al otro); con ≥16 grupos (P_V9_MANY) el más lejano de ambos farmea libre (2+2+1).
   Un aliado no visto se sitúa en el centro de su grupo reclamado (o el spawn). Línea `[v9-plan]` en el primer plan y cada 100 rondas.
2. **Objetivo del líder** (choose_target_impl): valor (gemas + gold_w·oro) / (camino del más lento = camino del líder + distancia del miembro más rezagado, + espera de respawn + hp_grupo / dps combinado de la escuadra + 6 + daño recibido repartido · ciclo de recall);
   sin tope de squad_needed; nunca el grupo del otro líder ni uno reclamado fuera de la escuadra; rivales vistos a ≤8 del grupo > miembros ×0.3; mitad rival ×0.5 antes de r300; puerta ×0.6; grupo a ≤12 del recién capturado ×1.5 (rotación); objetivo actual ×1.25. El líder publica su siguiente grupo al capturar (como el carry v4).
3. **Seguidor**: su objetivo es el grupo reclamado por el líder (acaba antes un grupo vivo a ≤3 ya dañado); si el líder no tiene grupo vivo, el grupo libre más cercano a ≤8 del líder.
4. **Marcha**: el seguidor camina al líder (visto) hasta ≤6 (P_V9_FOLLOW) salvo si ya está a ≤6 de su grupo, y no se adelanta más de 2 (P_V9_AHEAD) al líder hacia el objetivo (espera ≤8 rondas); el líder espera (≤8 rondas por objetivo, P_V9_LAGWAIT) a un miembro visto a >5 por detrás. `[v9-wait]`.
5. **Despertar** (farm): con campamentos vivos y ninguno dañado, needed = lo que pide el dps combinado (tope = tamaño de escuadra); se espera (≤8 rondas, anillo fuera de alcance) a que todos los miembros vistos a ≤10 estén a ≤4; `[v9-wake]` al empezar. Todos reclaman el mismo grupo y golpean el campamento de menos vida (fuego concentrado).
6. **Pelea** (antes de chase/bcf/veredicto, cada ronda): rival a ≤6: n = miembros a ≤6 con ≥40% (yo incluido), m = rivales a ≤6; n ≥ m → pelea (pv_fight = true, el veredicto "irse" no manda); n < m o yo <40% → flee() a casa (`[v9-retreat]`), un `[v9-fight]`/`[v9-retreat]` por episodio.
   Línea de estado: `v9=rol/líder/n pk= wt= wk= fi= rt=`.

**Comprobación local** (70 mapas x 2 lados vs kvvl, motor 2.0.0; an/v9an.py sobre dec/ con MAXR=700, an/decall.sh; ours = lado del bot):

| | v4o2 | v9 it.0 (follow 4, esperas 15/20, cuenta miembros no vistos) | **v9 (zip: follow 6, esperas 8/8, solo miembros vistos a ≤10)** | v9b (= v9 + grupos 40+ ×2, ciclo ×0.5; src/t10plan-v9b_vs_v4o2.diff, sin zip) |
|---|---|---|---|---|
| victorias | 72 | 11 | **32** | 22 |
| aliado a ≤4 fuera del spawn r50-600 | 44.5% | 54.4% | 48.8% | 46.9% |
| muertes r151-600 (con 3+ rivales a ≤6) | 3.74 (1.04) | 3.12 (0.71) | 2.81 (0.48) | 3.86 (0.54) |
| rondas-campeón muerto r151-600 | 226 | 186 | 170 | 233 |
| capturas hasta r600 | 27.1 | 19.6 | 23.2 | 18.5 |
| capturas de grupos de 40+ | 1.50 | 0.86 | 1.08 | 1.54 |
| gemas de captura hasta r600 | 328 | 228 | 268 | 235 |
| gemas entregadas r300 / r600 | 114 / 277 | 83 / 186 | 92 / 224 | 90 / 208 |
| líneas por partida fight / retreat / wait / wake | — | 99 / 56 / 25 / 54 | 110 / 63 / 26 / 70 | 110 / 64 / 25 / 57 |
| rondas de estado en v9-wake-wait / v9-follow (muestras cada 25 r, lado a) | — | 934 / 708 | 509 / ? | — |

- Divergencia antes de r30 frente a v4o2 (posiciones del replay): 3 de 140, las mismas en las tres variantes: gato_gemcombat5_a r4, starvation_a r4 (las dos ya divergían en v7r por combustible del tamaño del código), stalactites_b r25. Mediana de la primera divergencia: r32 (la regla).
- Combustible: 0 líneas de estado con low-fuel / fuel-wait en v4o2 y en las tres variantes v9.
- vs e1foco: no jugado (sin tiempo; e1foco se reconstruye con `patch -R` del diff v4o2_vs_e1foco sobre v4o2, está en bots/e1foco del workspace).

**Lo que dice el mecanismo.** Las escuadras se forman a medias (49-54% frente a 44.5%, la meta era >55%) y mueren menos (2.8 frente a 3.7; en inferioridad de 3+ la mitad), pero
farmean menos: −4 capturas y −60 gemas, y las capturas de 40+ no suben (1.08; con ×2 suben a 1.54 = v4o2, a costa de 4.6 capturas y 11 victorias). Causas vistas:
1. El tiempo en espera: it.0 pasaba el 11% de las rondas en `v9-wake-wait` (920 esperas de 20 rondas con 0/2 miembros, esperando a un aliado que no venía) y el 9% en `v9-follow`; el zip lo baja a la mitad, no a cero.
2. El líder sigue eligiendo grupos pequeños: 1210 despertares en grupos de 40+ frente a 9935 en pequeños (it.0); el modelo valor/rondas con el dps real de 2 cuerpos (elk 2400 hp x2) da 30+ rondas de limpieza y el daño recibido pesa; con ×2 toma los grandes pero el equipo pierde más (muertes 3.86).
3. 110 episodios de pelea por partida: n ≥ m pone pv_fight y el equipo entra en peleas igualadas que v4o2 evitaba por vida; las muertes bajan igualmente, pero el tiempo en pelea sale del farmeo.

**Huecos conocidos / siguientes pasos:** (a) la espera de despertar debería exigir que el miembro esperado se acerque (distancia bajando) y limitarse a grupos de 40+; (b) la rotación ×1.5 y la mitad propia ×0.5 no se han medido por separado; (c) el seguidor tarda hasta 6 rondas (P_E_RETARGET) en leer el nuevo grupo del líder; (d) la pelea n ≥ m debería contar vida (power_ratio) además de cuerpos; (e) sin partidas vs e1foco; (f) el banco local vs kvvl no juzga (README v7); online decide.

# t10plan-v9c "escuadras sin esperas" (2026-10-28 ~12:45 UTC): v9 sin esperas explícitas, objetivo compartido, pelea solo con ventaja — NO PASA LA PUERTA (47/140 vs kvvl)
Zip `zips/e1foco-t10plan-v9c.zip` sha256 `fda7417ee470e59bf5073682f9b59700322a05628bdcdab8481d1f186cbd6c71` (src/ como v9 + cambios abajo), diff `src/t10plan-v9c_vs_v9.diff` (297 líneas).
Mismo `P_V9` (params.h); nada corre antes de r30; una línea por disparo (`[v9-plan]`, `[v9-pick]` (≤40 por partida), `[v9-wake]`, `[v9-slack]`, `[v9-fight]`, `[v9-retreat]`).

**Cambios sobre v9** (main.cpp, v9.h, params.h):
1. Sin esperas: se eliminan `v9-wake-wait`, `v9-wait` (líder), `v9-hold` (adelantado) y `v9-follow`. Líder y seguidores caminan cada uno al grupo compartido; el líder (y cualquier miembro) golpea al llegar: needed = 1 si el daño recibido con el dps combinado es asumible, si no nsq+1 (too-strong).
2. Holgura del seguidor (`P_V9_SLACK 25`, `P_V9_SLACK_R 10`): a >25 del grupo del líder toma el grupo vivo con gemas más cercano a ≤10 que no alargue el camino más de 10, publica la reclamación (`[v9-slack]`, 2.4/partida) y vuelve.
3. Objetivo del líder: valor = gemas + oro/5.4; dps combinado = miembros vivos (no recall, fuera del spawn) a ≤10 del líder (`P_V9_DPS_R`); sin término de rezago. Volcado `[v9-pick]` con el mejor grupo de 40+ a ≤15.
4. Pelea: entra solo con n > m, o n == m y suma de vida (miembros a ≤6 con ≥40%) > la de los rivales a ≤6; si no, sigue el juego v4o2 (veredicto) y solo huye (`v9-retreat`) con rival a ≤3 o vida <40%.
5. Reparto: con menos de 6 grupos de valor ≥40 (`P_V9_BIGMAPS`) solo la pareja de Vesper (+ el vivo más cercano, con histéresis); los otros tres farmean solos como v4o2. Con 6+ el 2+3 / 2+2+1 de v9.

**Comprobación local** (70 mapas x 2 lados vs kvvl; an/v9an.py; base de divergencia dec/v4o2k):

| | v4o2 | v9 | **v9c (zip)** | v9d (= v9c sin término de daño en rondas, dps de miembros a ≤20 o no vistos) |
|---|---|---|---|---|
| victorias vs kvvl | 72 | 32 | **47** | 33 |
| aliado a ≤4 fuera del spawn r50-600 | 44.5% | 48.8% | 42.5% | — |
| muertes r151-600 (con 3+ rivales a ≤6) | 3.74 (1.04) | 2.81 (0.48) | 2.89 (0.63) | — |
| rondas-campeón muerto r151-600 | 226 | 170 | 175 | — |
| capturas hasta r600 | 27.1 | 23.2 | 25.8 | — |
| capturas de grupos de 40+ | 1.50 | 1.08 | 1.31 | — |
| gemas de captura hasta r600 | 328 | 268 | 319 | — |
| gemas entregadas r300 / r600 | 114 / 277 | 92 / 224 | 111 / 247 | — |
| líneas por partida fight / retreat / wake / pick / slack | — | 110 / 63 / 70 | 60 / 44 / 64 / 23 / 2.4 | — |
| % de líneas de estado de miembros de escuadra: fight-camp / approach / tribute / dead / capture / wait / v9-retreat | — | — | 23.5 / 23.2 / 10.9 / 8.6 / 5.5 / 3.6 / 3.5 | — |

- Divergencia antes de r30 frente a v4o2: **5 de 140** (límite 3): gato_gemcombat5_a r4, starvation_a r4, stalactites_b r25 (las de v9) + gemfight_a r2 y gemfight_b r2 (nuevas: el movimiento de apertura cambia en r2; nada de v9c corre antes de r30, así que es combustible/tamaño de código como en gato/starvation). Mediana de la primera divergencia: r35.
- Combustible: 0 marcadores low-fuel / fuel-wait (base 0).
- `[v9-pick]` (volcado de decisión): el grupo de 40+ a ≤15 NO gana la puntuación con 2 cuerpos: ej. ambush r41 pick=8 (gd 28, 0.36) frente a big=11 (gd 10, 0.30, rounds=257, sdps=50); anvil r69 pick=9 (1.03) frente a big=10 (0.61, rounds=418, sdps=109). Con dps real (50-65 por cuerpo) un 2-elk (4800 hp) son 40-50 rondas de limpieza más el daño recibido (×ciclo): nunca 15-25. v9d quitó el término de daño y contó a todos los miembros vivos: los grandes ganan la puntuación, pero 33 victorias (el equipo se desangra en ellos, como v9b).
