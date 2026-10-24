# pw3 = pairfarm-v4 (bundles/v20c-pw3.zip, sha 3377a740, src/, diff_vs_v20c.patch) = CANDIDATA. v20c + pfg + walk-with-estimated-ally.
Hilos: "Copiar las decisiones del top 10" (construye), "Encontrar la causa real del estancamiento" (propone y juzga online). 10-24.

## Mecanismo
- Hecho (top 10 vs rangos 30-60, cercanos r60-150, analysis/top10-micro-1023/early150/PAIRS.md): nunca del todo dispersos (sin pareja 19-23% vs nuestro
  41-43%); 75% de sus rondas en pareja caminan o esperan juntos y se separan en campamentos vecinos.
- pfg (online cadena 10, 73 cercanos): soledad 43,2 -> 40,8%, primera muerte en inferioridad 50 -> 38%. Poca fuerza: la elección satura (~47% local).
- Limitación: un aliado fuera de visión no tiene posición y la memoria compartida (8 bytes) está llena.
- Regla pw3 (general, no de campeón), solo cercanos (camino entre spawns < 35), r30-150:
  1. pfg: en choose_target un grupo con gemas sin el grupo reclamado por un aliado a <=6 puntúa x0,4 (grupos solo de oro exentos).
  2. Estimación (pe_update): por aliado, posición real si se ve; si no, una casilla por ronda desde la última posición hacia el centro de su grupo
     reclamado (claims); muerto -> spawn.
  3. Caminar con él: yendo a mi objetivo (a >=4 de él), sin rivales a la vista, si un aliado (real o estimado) a 5-14 casillas tiene su claim a <=6
     de mi objetivo, paso hacia él (anillo de 2), como mucho 8 rondas por objetivo.
- Logs: [pf] r150 <champ> n alone dsum walk (walk = rondas caminando con aliado); [pe] r150 <champ> n err le2 le4 (estimación vs posición real al re-verlo).

## Banco local (120 partidas en los 10 cercanos x 6 rivales; control pf0 = mismo log, regla apagada)
| | pf0 | pfg | pw3 |
|---|---|---|---|
| rondas r60-150 sin aliado visible a <=4 | 51% | 47% | 43% |
| muertes nosotros-rival r150 | -0,24 | -0,52 | -0,53 |
| oro nosotros-rival r300 | +268 | +210 | +266 |
| victorias | 70% | 69% | 79% |
Estimación: 6231 comprobaciones, error medio 5 casillas, <=2 47%, <=4 62%. Camina con aliado 8,5 rondas/campeón.
PANEL DURO: +6/480 (54/48, barra 20,2): cercanos +7/120, medios -2, lejanos +1; muertes -0,11 (se 0,28).

## Control online (lo que decide; lo mide el hilo del estancamiento)
1. Soledad r60-150 en cercanos (spread.py): V20 43% -> objetivo <=35%.
2. Muertes en inferioridad r0-150 (early.py/expo.py) y primera muerte en inferioridad.
3. Estado a r300-400 (a14.py): victorias esperadas >= 0; oro a r300 no peor que -30.
Siguiente (pw4, en paralelo): estimar la ruta con el distance_field en vez de línea recta.
Paquete 2: monoguard-v1c + pw3 = bundles/v20c-mg1c-pw3.zip (sha 7677d00e), parche pw3 limpio sobre monoguard-v1c, smoke 4 partidas 0 fallos.
