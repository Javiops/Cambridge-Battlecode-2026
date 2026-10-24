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

Base actual: `fuelfit-a1.zip` = kvvl (k_vvl_mgwp) + o01-o05, exacta frente a kvvl. `diff_a1_vs_kvvl.patch`.

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
