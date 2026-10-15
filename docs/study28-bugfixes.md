# study28: auditoría de bugs (2026-10-15)

Lectura completa de `bots/study28/src` (main.cpp, fight.h, params.h) buscando código que no hace lo que dice su
comentario o su switch. Cada arreglo es un switch en `params.h`, medido solo y junto contra study28 original
(mapas ganados por los dos lados, oficial 9 + hold60 + dev200) y contra el panel de casters (spar11/12/16).

## Arreglados (switch = 1 en params.h)

| bug | dónde | qué hacía mal | arreglo | solo vs study28 (ganados/perdidos ambos lados) |
|---|---|---|---|---|
| bucle cancelar-reiniciar recall | main.cpp `play_turn`, `rsafe` | P_CHANCANCEL cancelaba un recall y el mismo turno near-recall / flee-recall lo volvía a empezar (con un enemigo a 5-6 casillas). En los 9 mapas oficiales: 325 de 391 recalls cancelados se reiniciaron en el mismo turno; un Ren estuvo 8 rondas quieto así | `P_CHANFIX 1`: no se empieza un recall que la regla de cancelar cancelaría el turno siguiente; el turno huye o pelea | 17 / 27 (p 0.17, ruido); panel oficial 48-6 vs 44-10 |
| amenaza de canal cuenta enemigos que no atacan | main.cpp `channel_threat` | sumaba enemigos en su spawn o canalizando (tributando/recall) como si vinieran a pegarnos | `P_CHANTHR 1`: los ignora | 14 / 15 |
| byte de peligro resucita | main.cpp `update_danger` | el byte 7 guarda `(ronda/8) & 31` y nadie lo borra: un avistamiento viejo vuelve a parecer nuevo cada 256 rondas durante ~48 rondas (se evitan campamentos y un altar sin enemigos) | `P_DANGERFIX 1`: el byte solo vale P_DANGER_T rondas desde que cambió | 2 / 2 |
| paso de desatasco | main.cpp `step_towards` (P_UNJAM) | comentario "una casilla que no esté más lejos", código `> here + 1` (nunca filtra nada) | `P_UNJAMFIX 1`: `> here` | 0 / 0 (nunca se da en local) |
| "ni con vida llena se puede" | main.cpp `farm` | comparaba con `mhp * 0.75` (la reserva antigua); con P_RESERVE_PCT -60 la etiqueta "too-strong"/"need-heal" salía al revés y un campeón esperaba junto a un campamento que necesitaba 2 | `P_FULLFIX 1`: usa la misma vida asumible que `choose_target` | 18 / 15 |

**Todos juntos vs study28:** 35 / 36 (oficial 2/2, hold 5/8, dev 28/26): igual en local.
**Panel de casters (oficial / hold60):** spar11 16-2 / 93-27, spar12 16-2 / 110-10, spar16 16-2 / 95-25;
study28 original 14-4 / 95-25, 17-1 / 109-11, 13-5 / 95-25. Pasa el veto (oficial 48-6 vs 44-10, hold 298-62 vs 299-61).

Probado y descartado: `P_CHANFIX 2` (al revés: no cancelar un recall que la regla de empezar llama seguro):
8 / 16 (dev 5 / 14) y panel hold 295-65, peor. `P_CHANSTART 1` encima de P_CHANFIX: 17 / 29, igual que sin él.

## Encontrados, no arreglados (cambian estrategia, no son errores claros)

- `squad_needed` (main.cpp) supone que el daño de los monstruos se reparte entre n campeones, pero los monstruos
  concentran el fuego en uno: subestima el daño al que tanquea por un factor n. Cambiarlo es retocar el modelo de
  farmeo entero (P_RESERVE_PCT -60 probablemente se ajustó encima de esto).
- `farm` deja un objetivo que reaparece si `espera > distancia en línea recta + 4`, pero `choose_target` lo elige con
  distancia andando: con muros el campeón lo elige y lo suelta cada turno y llega tarde.
- Los campos de distancia de P_PATHD atraviesan altares (`spawn_pd`, `altar_pd` ~1 casilla cortos).
- La emisión de cooldown (bytes 5/6) redondea hasta 8 rondas de más.
- `engage` con un campeón a distancia solo lanza hechizos a 3 casillas aunque el alcance es 4 (sin comentario que lo explique).
- `P_U34_RESET_LIVE` está definido dos veces en params.h; gana el 2, que es lo que se quería.

Combustible: ningún cálculo caro por enemigo y por turno; `channel_threat` solo recorre los enemigos visibles.
