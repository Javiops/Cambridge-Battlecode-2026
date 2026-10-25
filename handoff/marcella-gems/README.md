# Daño de Marcella a campamentos (−31% frente al top 10): diagnóstico y o71 (25-10)

Datos: top 10 online, mapas cercanos, 81 partidas con Marcella (resúmenes + replays), frente a b27 local, 312 partidas (fuel normal,
26 mapas no lejanos x 6 rivales panel17 x 2 lados). Herramientas en tools/ (mcamp.py, mbuy.py, mgold.py, allgems.py, mcap.py).

## No es la ejecución
r30-150: rondas pegada a un monstruo 24,5 (b27) frente a 25,6 (top 10); golpe mediano 45 = 45; los golpes dobles/hechizo dan ~50%
del daño en los dos. Rondas pegada sin golpear 8,5 frente a 6,7.

## Es el oro, y el oro sale de las gemas
| a r150 | top 10 | b27 |
|---|---|---|
| gemas recogidas por Marcella | 25,6 | 6,4 |
| oro ganado | 202 | 93 |
| fragmentos comprados (r150 / r400) | 4,8 / 21 | 2,0 / 11 |
| golpe mediano r150-400 | 70 | 52,5 |

De dónde: capturas de grupos alce+gemas antes de r150. Marcella top 10 0,45 (13 gemas), la nuestra 0,06.
**Equipo entero antes de r150: alce+gemas 1,80 capturas / 45,7 gemas (top 10) frente a 0,61 / 11,3 (b27).** Esa diferencia
(~34 gemas) es casi toda la brecha de gemas del equipo a r150. (Rivales distintos: top 10 online frente a panel17 local.)

## o71 mgems (marcella.h gem_w): NO pasa
Una gema vale para Marcella 1 + P_MGEM% x 2 x gold_w en choose_target (su pasiva: 2 de oro por gema entregada);
P_MGEM_CO quita el x0,7 de "necesita compañía" en grupos con gemas. Sonda +20 instrucciones: 0/52 partidas cambian.
312 partidas frente a b27 (232 victorias): A (100) 222 (−10), B (50) 232 (0), C (100 + CO) 208 (−24).
El mecanismo apenas se mueve (gemas de Marcella a r150 6,4 → 7,1 / 6,4 / 8,9; oro baja): elegir el grupo no es lo que falta.
El cuello es del equipo: tomar grupos alce+gemas antes de r150 (macro de farmeo).
