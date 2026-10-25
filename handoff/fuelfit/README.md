# fuelfit: kvvl con el turno más pesado siempre dentro del fuel

**Objetivo (usuario, 10-24 22:00 y 22:47):** un bot cuyas decisiones no dependan del fuel. Criterio de hecho: +20 y
+2000 instrucciones inútiles por turno cambian 0 de 800 partidas en el PC (pad.py + diffcount.py), y el Juez 2 da la
misma fuerza que kvvl. Hasta entonces no sale nada online.

**Por qué:** cualquier recompilación cambia el fuel que gasta cada turno; `fuel_ok()` decide distinto desde r2 y las
partidas se reparten de otra manera. det8 (contador que imita el fuel) no lo arregla: el contador no acierta en los
turnos pesados y el veto del fuel real sigue saltando. La única salida robusta: que el turno más caro quepa siempre
(objetivo ≤ 85k de 100k) y quitar todas las comprobaciones de fuel.

## Diseño

1. **Ninguna decisión lee el fuel.** Todo `fuel_ok(n)` / `bc::fuel_remaining()` desaparece de main.cpp y de los `<champ>.h`
   (solo queda el valor en la línea de estado, como dato).
2. **Cada pasada está acotada por construcción:** tope fijo de iteraciones, cachés de lo que es estático en la partida
   (mapa, plan de compra, listas por campeón) o de lo que no cambia dentro del turno (campeones visibles).
3. **Trabajo opcional en calendario fijo de rondas**, no "cuando sobra fuel": línea de estado, registros, raíces de
   altar, escaneo de agujeros, ward.
4. **Inicialización en turnos fijos.** Hoy el primer turno pide ~270k (init-groups ~112k, tienda 42k, farmeo 37k,
   logs 31k) con un presupuesto de 200k: el corte depende del tamaño del código y de ahí viene la divergencia en r2-3.

## Banco de pruebas (carpeta tools/)

- **Fuel ilimitado:** `cambc run-batch MANIFEST --release --json --fuel-quantum 2000000`. Así se ve lo que cada turno
  pide de verdad y se comprueba exactitud.
- **Exactitud:** una optimización que no cambia decisiones da `replay.repl26a` idéntico byte a byte con fuel ilimitado:
  `python3 -I same.py res/BASE_q2000000 res/CAND_q2000000` debe decir `differ 0`. Hasta ahora todas las piezas
  (o01-o05) pasan 52/52.
- **Fuerza:** una pieza que sí cambia decisiones (un tope nuevo) se juzga por fuerza: `pair.py`, `vstat.py` (a14@300)
  y Juez 2 en el PC frente a kvvl.
- **Perfil:** `mkprof.sh NAME` construye kvdet8+opts con `ungate.py` (todo fuel_ok pasa; coste real por sección y
  por turno), `autoprof.py` (coste por función, inclusivo y exclusivo) y `profhdr.py`. Lectura: `pragg.py RES
  profnames.json`, `secagg.py RES`, `secpct.py RES` (percentiles por sección y coste de los turnos 1-3).
- **Piezas como parches:** `opts/oNN_nombre.py SRCDIR` edita el código con reemplazos exactos (assert si no casan);
  `applyopts.sh BASE/src OUT/src` aplica todas en orden. Así se combinan sin conflictos. Nueva pieza = nuevo fichero
  `oNN_*.py` con comentario de qué hace y por qué es exacta (o qué cambia).
- **Manifiesto:** `mk.sh NAME` (26 mapas no lejanos x 6 rivales del panel17 x 2 lados = 312) y `subq.sh FUEL NAME...`
  (subconjunto de 52 con `--fuel-quantum`). Rivales: `analysis/local-filter-1021/panel17/{rTop1,rD,rF,rHunt,mV19,mV10d}`.

Candidata: **`fuelfit-b14.zip`** (10-25 02:40 UTC) = b10 + o13 (ward solo con arbusto cerca) + o35 (campos de altar
1 por turno en mapas > 2500 casillas) + o57 (primera ronda de juego por modelo de coste de la init: 68k + 18/casilla +
5k/grupo, 1 ronda si ≤ 186k, si no 1 + ceil((est-186k)/86k); mapas pequeños ≤ 14 grupos siguen en la ronda 2) + farmeo
o52 (K=12 grupos en choose_target, cambia decisiones), o53 (isle cada 10 rondas), o54-o56 (exactas). Las exactas se
comprobaron con same.py (52 cercanas / 56 lejanas idénticas). Local a fuel normal: **+20 instrucciones cambia 0/52
cercanas y 0/56 lejanas**; victorias cercanas 39/52 (kvvl 41, barra 7,5), lejanas 48/56 (kvvl 42). El Juez 2 decide.
Costes de init medidos por mapa (40 mapas): fragment 101k … monolith 199k, ambush 280k, islands 315k, road_of_riches
328k, big_world 373k (`tools/heavy.py`).

Base validada: **`fuelfit-b10.zip`** (10-25 01:10 UTC) = kvvl + o01-o12 (este hilo) + pelea o17-o30 + recall o31-o34 +
farmeo o41-o49. 36 piezas; `fuel_ok()` es siempre true. **Inicialización v3 (o08):** toda en el turno 1 de golpe (no
se emite ninguna acción, así que si no cabe en los 186k el motor la termina en la ronda 2 sin que nada pueda divergir);
primera ronda de juego fija por mapa: 2 si el mapa tiene ≤ 14 grupos (init medida ≤ 143k), 3 si no (hasta 252k con 31
grupos). La ronda ociosa de los mapas grandes calcula campos inversos de farmeo (o47) con precio fijo por casilla.
La init por pasos anterior (v1) hacía perder 3-5 rondas de apertura: a14@300 +0,64 → +0,25 (medido por farmeo).

Local a fuel normal (52 cercanas x 6 rivales; 56 lejanas x 2 rivales):

| | kvvl | b9/b10 |
|---|---|---|
| victorias cercanas /52 | 41 | 40 / 41 |
| victorias lejanas /56 | 42 | 43 / 41 |
| +20 instr.: cambiadas cercanas | 41 | 0 / 2 |
| +20 instr.: cambiadas lejanas | - | 3 / 6 (todas antes de r50: primeros turnos de farmeo en mapas 100x100) |
| +200 instr.: cambiadas cercanas | - | 7 (2 ganadores) |

Lo que queda: en mapas lejanos los primeros turnos de farmeo (choose_target 28k + step_towards 13k + campo inverso
7k + ward) pasan de 86k; farmeo prueba o51-o53 (topes con cambio de decisión, por fuerza).

Anterior: **`fuelfit-b3.zip`** = kvvl (k_vvl_mgwp) + o01-o10 (este hilo) + o21-o26 (pelea) + o31-o33 (recall/altares/
campamentos) + o41-o42 (farmeo). `diff_b3_vs_kvvl.patch`. Ya **no lee el fuel en ninguna decisión** (`fuel_ok()` es
siempre true). Anterior: `fuelfit-a1.zip` = kvvl + o01-o05 (exacta).

## Dos hechos del motor medidos el 10-24 (noche)

- **El fuel disponible al empezar nuestro código es `quantum - 14.016`**: 85.984 en un turno normal, 185.984 en el
  primero (no 100k/200k). Objetivo de peor turno: ≤ 76k.
- **Una función `bool` sin `return` al final es un trap de wasm y el motor reinicia el programa del campeón** (estado
  perdido, vuelve al turno 1 de inicialización cada turno: el campeón queda muerto en la práctica). Por eso b3 imprime
  `[boot]` una vez por campeón al arrancar: `tools/restarts.py RES` cuenta reinicios (debe dar 0).
- Pasarse del fuel en un turno **no** reinicia: el turno continúa en la ronda siguiente (las acciones ya emitidas se
  quedan; las que faltan se emiten tarde). Por eso una base sin lecturas de fuel todavía puede divergir con +20
  instrucciones si algún turno pasa de 86k.

## Inicialización en pasos (o07-o08)

Cada paso tiene un precio fijo de peor caso (medido con fuel ilimitado en 52 partidas x 4 campeones, redondeado hacia
arriba): mapa 56k (tableros, altares, spawn, `camp_groups`), un grupo 8k, campos de camino 31k, roles + tienda 56k,
agujeros de dash 14k. Un turno ejecuta pasos mientras quepan en su presupuesto (176k en la ronda 1, 76k después). El
calendario depende solo de la ronda y del número de grupos. El campeón juega desde el turno siguiente al que acaba.

## Resultado b3 (52 partidas, fuel normal)

| | kvvl | a1 | b1 | b2 | b3 |
|---|---|---|---|---|---|
| victorias /52 | 41 | - | 38 | 39 | 40 |
| +20 instr.: partidas cambiadas | 41 | 17 | 5 | 1 | 2 |
| ... antes de r300 | - | - | 0 | 0 | 1 |
| ganador cambiado | - | - | 0 | 0 | 0 |

pair.py b3 frente a kvvl: neto -1 en 11 cambiadas (barra 6.6): sin pérdida medible. Reinicios: 0.

Cola de turnos que queda (fuel ilimitado, 295k turnos): 1,76% ≥ 75k, 0,58% ≥ 85k, 0,13% ≥ 100k, máximo 170k. Por
sección (máx / p99.9): farm 100k+ / 52k (choose_target_impl 23k y step_towards 8k en turnos pesados), fight 90k / 35k,
recall 60k / 32k, shop 55k / 32k, init(dead-shop) 50k / 22k, decide 42k / 25k.

## Resultados PC (800 partidas, J2 listón ~8.3, reserva listón ~4.5) y estado al 10-25 04:00 UTC

| versión | qué es | J2 | reserva | pad +20 |
|---|---|---|---|---|
| kvvl | base V20 + counter | +10.4 | +15.8 | 42% |
| b10 | init entero en turno 1, primer turno fijo | +11.7 | +16.9 | 4% (+200 22%, +2000 74%) |
| b12 | b10 + o13 + farm o52-o56 | +11.3 | +17.2 | 2% |
| b14 | b12 + o35 + o57 | +9.5 | +14.4 | 0.5% |
| **b15** | b12 + o35 (sin o57) | **+11.8** | **+17.0** | 2% |
| b16 | b15 + o58/o59 | +11.2 | +14.4 | 2% |
| b18 | b19 + o57 | +8.3 | +15.0 | 2% (+200 15%, +2000 68%) |
| b19 | b16 + o60-o62 exactas | +6.0 | +17.0 | 2% (+200 19%, +2000 73%) |
| b20hp | b19 + o70 (hitpass-v2 sin fuel) | pendiente | pendiente | local 0/52, lejos 1/56 (r1322) |
| b21hp | b15 + o70 v1 (hitpass sobre la base elegida) | +10.4 (cerca -11/b15 -9, medios +27/+23, lejos -1/+19) | +16.6 | 2% (+200 24%) | local cerca 0/52, lejos 3/56 |
| b25 | **b15 + o71** (exacta: el campo al spawn enemigo del init solo si hay candidato a jackpot; arranque -6k..-32k en los 14 lejanos) | pendiente | pendiente | cerca idéntica a b15 (52/52); lejos 16/56 distintas (el juego empieza antes), 42/56 frente a 45, sonda 3/56 |
| **b24hp** | **b15 + o70 v6** (hitpass apagado en lejanos con el camino que el draft envía por memoria, byte 29: cero trabajo en el init) | **+13.5** (medios +29, lejos +15) | **+17.4** | 3% (+200 21%) | cerca = v2 (52/52 idénticas); lejos 12/56 difieren de b15, las mismas 12 que con hitpass compilado fuera |
| b23hp | b15 + o70 v3 (hitpass apagado si el camino spawn-spawn >= 60: PC b21hp lejanos -20, medios +4, cercanos -2) | +12.2 (lejos +14) | +17.4 | 2% (+200 22%) | cerca = v2 (52/52 idénticas); lejos 14/56 difieren de b15 = cola de fuel de b15 en mapas grandes |
| b22hp | b15 + o70 v2 (hitpass reutilizando la lista de campamentos del turno) | +12.3 (cerca -11, medios +29/+23, lejos +12/+19) | +16.8 | 1% (+200 18%) | local cerca 1/52 (r801), lejos 1/56 |

hitpass local frente a b15: cerca 37/52 = 37 (neto 0 en 10 cambiadas); lejos 39/56 frente a 45 (neto -6 en 16, barra 8.0; v1 -7/17). Dispara desde la apertura (divergencia mediana r62) en las 56 partidas lejanas: cambio de decisión, lo juzga el PC. Si el PC confirma la pérdida en lejanos, variante = hitpass solo en mapas cercanos (d_spawn < 60).

**Base elegida: b15.** b19 (o58-o62, exactas a fuel ilimitado) pierde 5.8 de J2 (cambia 189/800, lejanos +19 -> +3,
castigadores +23 -> +11) sin ganar determinismo: a fuel normal el primer turno de juego en mapas grandes sigue por
encima de 86k y el trabajo extra del turno de espera mueve dónde se corta. b16 ya había perdido reserva (+14.4). o58-o62
quedan fuera (opts_off/) hasta que el turno de espera quepa de verdad en 100x100.

El PC recomienda b15 como base; o57 (esperar rondas según modelo de coste) cuesta -2.7 de reserva y se descarta
(opts_off/o57). pA (o61 antiguo, vkite-v3+mstick) sobre b6: J2 +6.7 frente a +9.1 -> descartada. monoguard, vco,
lshop y vkite ya están dentro de kvvl: no hay nada que portar salvo hitpass-v2 (o70, `fuelfit-b20hp.zip`): local
35/52 frente a 36 de b19 (11 cambiadas, neto -1, barra 6.6).

## Mapas grandes: el arranque ya no cabe y cualquier cambio mueve la partida (10-25 mañana)

En big_world, road_of_riches, fracture, lanes e islands el turno de arranque gasta 2-4 rondas de fuel (big_world 373k).
Cualquier trabajo extra en el init (o58-o62; una BFS de 5k en r2) o incluso un cambio estructural sin efecto (hitpass
compilado fuera, solo el vector en State y la referencia: 12/56 partidas lejanas cambian frente a b15, mediana r62) mueve
el momento en que empieza el juego y la partida cambia. La sonda +20 solo cambia 2/56 ahí: la sensibilidad es a cientos
de instrucciones por turno, no a decenas. Para que la base sea robusta en lejanos hay que bajar el arranque y los turnos
de r2-r10 en 100x100 por debajo del presupuesto, sin añadir trabajo (v5 enseñó que las variables del draft no
sobreviven: usar la memoria del draft, byte 29 = camino spawn-spawn, que init_map ya lee en g_tpc_path).

Perfil del arranque con fuel ilimitado en los 14 lejanos (kidbg, `[dbgI]`): mapa 30-74k, grupos 25-100k (2k por grupo:
spawn_tiles+positions+camps+5 is_* por campamento), caminos 25-92k (tres distance_field.compute; exportar los campos en vez
de leer por casilla sale un 10% peor: la exportación se mide por tamaño), roles+tienda 43-52k, dash 11-15k, warmup 15-51k
(600 por grupo). Suma 149k (rows) a 330k (big_world) frente a 186k del turno 1. Primer turno de juego (r2 o r3): 77-168k
frente a 86k (big_world r3 168k, islands 109k, expanse 104k, fracture 103k, road_of_riches 98k); picos de 60-90k en r8-r9.
Siguiente: grupos (2k/grupo exacto) y el primer turno de juego (choose_target con 24-51 grupos: hilo farm).

## Reglas para portar una pieza a la base sin fuel

1. Nada de `fuel_ok()` ni `bc::fuel_remaining()` en decisiones (solo como dato en la línea de estado).
2. Todo bucle con tope fijo de iteraciones; nada de "mientras quede fuel".
3. Trabajo opcional en calendario fijo de rondas (`round % N == 0`), no "cuando sobra".
4. Sin `printf` nuevos en el turno (2,5k cada uno; la línea de estado con `LineOut` cuesta ~1k). Un `printf` por partida
   está bien.
5. `std::vector` estático o con `reserve`; buffers estáticos (el fuel cuenta instrucciones: zero-fill de 20KB = 10k).
6. Toda función que devuelve `bool` termina en `return`.
7. Pieza = `opts/oNN_nombre.py` con reemplazos exactos (assert si no casan) y comentario de qué cambia y por qué es
   exacta; exactas se validan con `same.py` a fuel ilimitado; con cambio de decisión, por fuerza (pair/vstat/J2).

## Lo medido (kvvl con fuel ilimitado, 52 partidas, 270k turnos)

Coste por sección de `play_turn` (miles de fuel; percentiles sobre turnos > 1):

| sección | p50 | p90 | p99 | p99.9 | máx |
|---|---|---|---|---|---|
| pre-sweep (hechizos antes de moverse) | 2.5 | 7.5 | 12.5 | 17.5 | 27 |
| shop | 2.5 | 2.5 | 7.5 | 37 | 57 |
| vision | 2.5 | 5 | 5 | 5 | 5 |
| groups (refresh_groups) | 5 | 7.5 | 10 | 10 | 10 |
| foes (escaneo de enemigos, amenaza) | 2.5 | 7.5 | 15 | 20 | 27 |
| camps (near_camps, monoguard) | 5 | 10 | 17 | 25 | 97 |
| decide/flee | 2.5 | 2.5 | 17 | 25 | 50 |
| fight (fight.h, engage, cast_offense) | 5 | 15 | 27 | 37 | 80 |
| recall/tribute (go_tribute, br_plan, altares) | 2.5 | 7.5 | 20 | 32 | 90 |
| farm (choose_target, step_towards, engage_camp) | 7.5 | 20 | 40 | 52 | 87 |
| post-sweep + altar lock + ward | 2.5 | 17 | 22 | 25 | 30 |
| log (línea de estado) | 2.5 | 2.5 | 22 | 22 | 22 |

Turno completo: mediana 44k; 1,2% > 90k; 0,46% > 100k; máximo 175k (era 307k antes de o01-o05).

Costes unitarios del motor (fuel por llamada, `sdk_costs.md`): `vision::champions` ~3000 (lista reconstruida cada
vez), `champion_at` 510, `champion_tiles` 410-690, `visible_tiles_into` 412, `distance_field.compute` 1400-1900,
`ward::visible_tiles_from` 478, `camp_group state` 807, `vision::camps` 1372, `camp.health` 2220, `bitboard.positions`
750-1775 (según bits), `item_count` 231, `can_buy` 66, `pow` 300, **`printf` 2500 (3 enteros) y la línea de estado
19000**, `std::vector` sin reserve 50 por push (100 push = 5000; 4 push = 1000), lecturas de un campeón 50-80.

## Reparto propuesto

Cada hilo trabaja sobre `fuelfit-a1.zip` y entrega piezas `oNN_*.py` + resultado (exacta: same.py 52/52; o con
cambio de decisión: pair/vstat local y Juez 2). Objetivo por sección: p99.9 ≤ el valor de la columna "meta".

| hilo | secciones | meta p99.9 | ideas |
|---|---|---|---|
| farmeo | farm (choose_target 15k en turnos pesados, step_towards, engage_camp_e4), groups | 25k | leer el campo de distancias una vez (export_linear_buffer) con índices de casilla precalculados por grupo; tope de búsquedas de camino por turno; precalcular por grupo lo estático (distancias a centros, jackpot, monolito) |
| pelea | fight, foes, pre/post-sweep, decide/flee, bucles de HoR y Vesper | 25k | una sola lista de enemigos por turno (Foe) compartida por fight.h/spell_sweep/track; tope de candidatos en kite/safe_step/front_line; cast_offense sin recalcular alcances |
| recall/altares/campamentos | recall/tribute (go_tribute, br_plan, best_altar), camps (near_camps 97k máx), altar lock | 20k | br_plan ya cachea por altar: acotar el resto; near_camps: group_state (807) solo para grupos cuyo estado puede haber cambiado; una sola visible_tiles_into por turno compartida |
| yo (este hilo) | init en turnos fijos, logs (formateador barato, calendario), tienda (tope de compras por turno), ward, integración, validación final | — | — |

Reglas para todos: nada de `fuel_ok`/`fuel_remaining` en la pieza; todo bucle con tope fijo; sin printf nuevos
(2,5k cada uno); `std::vector` con reserve o estático; comentar en el código qué cambia y por qué es exacto.
