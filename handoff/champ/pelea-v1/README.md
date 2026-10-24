# pelea-v1, piezas por campeón (hilo "Mejorar cada campeón en su fichero"), todas sobre kvvl = k_vvl_mgwp (handoff/chain14)

Base para comparar: kvvl (k_vvl_mgwp.zip de 24fb601). Métrica de comportamiento: ../tools/pvpnum.py (num = 1 + aliados - rivales a 3 casillas en rondas de pelea).
Línea de estado (cada 25 rondas) termina en `vk=<pasos vk3>/<disparos vkite> ms=<retiradas de Marcella>`.

| carpeta | qué lleva |
|---|---|
| pA | vkite-v3 (vesper.h) + mstick-v1 (marcella.h) |
| pB | pA + fightnum-v1a (champions.h outnum_margin: Vesper/Marcella/Vendetta se retiran con rivales >= nosotros + 1) |
| pC | kvvl + fightnum-v1a solo (la mitad defensiva sola) |
| pD | vkite-v3 solo |
| pE | mstick-v1 solo |

- vkite-v3 (P_VK3): Vesper dispara desde el borde de su alcance y sale. Si un rival que la alcanza está a 1-2 casillas y no tiene el dash listo, no dispara: da el paso de fight::kite para salir de su alcance y le lanza el aturdimiento, salvo que el disparo lo mate. Antes disparaba siempre que tuviera >= 45% de vida. Top 10 antes de r150: 9% de rondas de pelea a 1 casilla y 1,5% de vida perdida por ronda; nosotros 14% y 2,5%.
- mstick-v1 (P_MS): Marcella pegada a un rival (<= 1 casilla), con < 70% de vida y sin ventaja (1 + aliados - rivales a 3 <= 0) se retira (fight::back_off), salvo que el rival muera de dos golpes. Top 10 pegada 14%, la nuestra 31%.
