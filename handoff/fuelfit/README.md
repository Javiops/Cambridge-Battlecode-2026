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

Base actual: **`fuelfit-b10.zip`** (10-25 01:10 UTC) = kvvl + o01-o12 (este hilo) + pelea o17-o30 + recall o31-o34 +
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
