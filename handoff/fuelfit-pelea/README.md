# o61 pA sobre la base determinista (fuelfit-b6)

`python3 o61_pA.py b6/src`. Es pA (pelea-v1: Vesper vkite-v3 + Marcella mstick-v1; J2 +16,7 frente a kvvl +10,4 en la base
antigua) portada a b6: sin fuel_ok, sin printf nuevos (fuera la línea [ms] y los contadores del estado), bucles acotados por
los rivales/aliados visibles (vis_champions de o01, cacheado por turno). Cambia decisiones: se juzga por fuerza.

Local, fuel ilimitado, 52 partidas (subconjunto de 26 mapas no lejanos x 6 rivales panel17): cambian 51/52 replays;
victorias 39 (b6) → 37 (o61), +5 / -7 (ruido a este tamaño). Para el PC: partidas cambiadas y J2 frente a b6.

Parámetros (params.h): P_VK3 1, P_VK3_HP 0, P_MS 1, P_MS_HP 70, P_MS_NUM 0.
