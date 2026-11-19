# Un fichero por campeón (V20c = V20 v139 v6d reorganizado)

Todo lo que hace un solo campeón vive en `<campeón>.h`. `main.cpp` no nombra campeones (salvo el draft, que es de equipo).

| fichero | campeón | qué tiene hoy |
|---|---|---|
| `heart_of_ruin.h` | Heart of Ruin (slot 1, Ren en mapas lejanos) | plan de tienda top 10, guarda el dash para atacar, `dash_strike` (el dash como golpe, mejor aterrizaje) |
| `vesper.h` | Vesper (slot 2) | solo `is()`. Su plan sale de la capa genérica; activa el modo caster |
| `marcella.h` | Marcella (slot 3) | plan de tienda top 10 |
| `ryth.h` | Ryth (slot 4) | plan de tienda top 10 |
| `vendetta.h` | Vendetta (slot 5) | plan de tienda top 10 |
| `ren.h` | Ren (lejanos) | solo `is()`. Plan de casters (capa antigua), cuota de vida 0.50, rango de captura 2 |
| `stellar.h`, `prism.h`, `tavi.h`, `varg.h`, `cassi_issac.h` | drafts antiguos | lo suyo (Tavi compra en el campo, Varg splash, gemelos Cassi/Issac) |
| `champions.h` | interfaz | declaraciones + los hooks que llama main.cpp |

## Hooks (champions.h, namespace `champ`)

| hook | dónde lo llama main.cpp | cuándo |
|---|---|---|
| `legacy_plan(s)` | `build_shop` | arranque: capas históricas de emblemas (gana la última que aplica) |
| `shop_plan(s)` | final de `build_shop` | arranque: el plan propio del campeón, final (sin relleno bruiser) |
| `own_plan(s)` | `shop()` | cada compra: true = el plan propio lleva la vida, `hp_pick` apagado |
| `hp_share(s, share, fam)` | `hp_pick` | cada compra: cuota de fragmentos de vida y familia |
| `caster_mode(ally)` | `init_roles` | arranque: el equipo juega modo caster |
| `melee_by_name(n)`, `cap_rank(n, ranged)` | `tank_bits`, `refresh_groups`, capturas | prioridad de captura |
| `heart_of_ruin::keeps_dash_for_attacks(s)` | `step_towards` | cada paso |
| `heart_of_ruin::dash_strike(...)` | `cast_offense` | cada hechizo ofensivo |
| `varg::splashes(s)`, `tavi::shops_in_field(s)` | `my_dps`, regreso a tienda | |
| `cassi_issac::pair_ok / twin_guard / twin_farm` | peleas y farm | |

## Reglas para una pieza nueva de un campeón
1. Clave por campeón: `if (marcella::is(s.name))`, nunca por slot ni por índice de aliado. Si el campeón no está (el draft cambia: Ren por HoR en lejanos, otros picks), el hook no hace nada y queda el comportamiento genérico.
2. Va en `<campeón>.h`. Si ningún hook sirve, declara uno en `champions.h` y añade UNA llamada en el sitio de main.cpp donde actúa.
3. Los hooks son `CHAMP_HOOK` (inline forzado): cuestan lo mismo que el código en línea. Un hook que corre cada turno tiene que ser barato: el fuel por turno cambia decisiones (`fuel_ok`) y por tanto las partidas.
4. Los ficheros de campeón se incluyen al final de main.cpp: pueden usar cualquier función genérica (`step_towards`, `cast_offense`, `fight::hit_now`, ...).

## Verificación frente a V20 (v6d)
Ver el mensaje del hilo "Un fichero por campeón": partidas con fuel ilimitado idénticas byte a byte (misma lógica) y fuel por turno comparado.
