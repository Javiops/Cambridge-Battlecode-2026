# fuelfit: recall, altares y campamentos (piezas sobre fuelfit-a1)

Aplicar en orden sobre `fuelfit-a1/src`: `python3 opts/o21_camps.py SRC; python3 opts/o22_altars.py SRC; python3 opts/o23_campread.py SRC`.
Comprobado con fuel ilimitado (`--fuel-quantum 2000000`), 52 partidas (26 mapas no lejanos x 6 rivales panel17, cada 6ª línea):
`same.py a1 o21` 52/52 idénticas, `a1 o21+o22` 52/52, `a1 o21+o22+o23` 52/52 (`replay.repl26a` byte a byte).
Solo cambian líneas de log: el contador `errs=` y algunas líneas `[err #n]` (o21 deja de leer campamentos tras el primero despierto; o23 no imprime el texto del error).

| pieza | qué hace | por qué es exacta |
|---|---|---|
| o21_camps | near_camps: una sola `camps()` por grupo y `reserve`; test de campamento despierto corta al primer `true`; cadena de banca calcula `my_dps` una vez | mismo turno, mismos handles; el flag solo pasa a true; my_dps lee nuestro campeón, no cambia en el bucle |
| o22_altars | campos de altar (brcache) en calendario fijo: `P_BRC_PER`=2 por turno desde `P_BRC_R0`=3, en play_turn, nunca dentro de br_plan. Fuera los `fuel_ok` de br_plan (50k/22k), br_threat_block y br_safe_move (26k, código muerto con br_policy 1), isla (12k), salida del monolito (20k) y pairfarm (12k) | todos los que llaman a best_altar necesitan gemas > 0, que nadie tiene antes de r3 + altares/2; con fuel ilimitado esos fuel_ok siempre daban true |
| o23_campread | el test de campamento despierto lee el campamento con una llamada `sdk_camp` sin excepción | `sdk_camp` cuesta ~60 de fuel; una excepción del motor (campamento ya fuera de visión, error 97) cuesta ~5,5k en deshacer la pila. El flag nunca se ponía en una excepción |

## Perfil (miles de fuel por turno de campeón, 52 partidas, `tools/prof2.py` + `tools/zagg.py`)

| sección | a1 p99.9 | a1 máx | o21-23 p99.9 | o21-23 máx |
|---|---|---|---|---|
| camps (sección entera) | 24 | 94 | 17 | 23 |
| near_camps | 18 | 19 | 13 | 18 |
| test despierto | 6 | 76 | 4 | 5 |
| monoguard | 9 | 10 | 9 | 10 |
| best_altar | 7 | 47 | 6 | 12 |
| br_plan | 4 | 45 | 4 | 6 |
| altar_lock | 2 | 8 | 2 | 8 |
| go_tribute | 18 | 33 | 19 | 34 |
| banca (sub-sección) | 27 | 87 | 26 | 66 |
| recall (sub-sección) | 12 | 65 | 12 | 43 |

Lo que queda alto en recall/banca/back-home está en funciones de otros hilos que estas secciones llaman: `step_towards`
(máx 43k, dentro de go_tribute), `choose_target` (45k, back-home) y `flee`/`back_off`/`engage` (campfoe 41k).

## Pista para todos: las excepciones son caras
Cada error del motor lanzado y capturado por `attempt()` cuesta ~5-8k de fuel (la llamada en sí, 60). En estas 52 partidas
los más comunes: 32 "Destination is unreachable" (365), 97 "Unit is not in vision" (169), 63 "Champion cannot act" (118),
42 "Target must be a visible enemy" (91), 22 "Known occupied destination" (82). Una media de ~25 por campeón y partida,
cada uno un pico de 5-8k en su turno. Comprobar antes (o leer el código de retorno crudo como `camp_snap`) los quita.

## o34 sobre fuelfit-b6 (25-10)
`python3 opts/o34_sealed.py b6/src`. Exacta: `same.py b6 b6+o34` 52/52 idénticas con fuel ilimitado.
- altar_sealed: lee visión y campamentos en tableros estáticos (`*_into`) y la prueba "alguna casilla del anillo en visión sin campamento vivo" pasa a álgebra de tableros, sin `positions()` ni `is_set` por casilla.
- cr_return_walk: el campo a casa ya no espera `fuel_ok(22000)`.
- Probado y descartado: mover la preparación estática de altar_sealed (~11k la primera vez de cada campeón) a un turno fijo temprano NO es exacto (boss_battle 2/2 cambian: las casillas de campamento que lee cambian después de r5).

Turnos > 76k en modo tribute en b6 (52 partidas, herramienta [hv] por sección): el coste está repartido en fight (10-27k),
foes (5-18k), post-sweep (12-17k) y step_towards dentro de go_tribute (6-16k). Lo propio del viaje (go_tribute sin
step_towards, best_altar, br_plan) es 2-8k. Dos picos de log fijos: `[econ]` de br_note cuesta 8k en las rondas
múltiplo de 50 (printf de 9 enteros) y la sección init marca 9k en esas mismas rondas. Back-home > 76k: 50k es
choose_target (32k) + step_towards (17-19k).
