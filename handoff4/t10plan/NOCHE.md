# Noche 27-28 oct: copiar el plan del top 10 sobre e1foco

**Qué se probó online** (cadena c34, 75 partidas contra los rivales 56-70; kvvl hace 31-44 y e1foco 37-38):

| bot | qué añade sobre e1foco | resultado | frente a e1foco |
|---|---|---|---|
| v2 | horario por mapa del top 10 + roles carry/escolta | 29-46 | −8 |
| v3 | horario por posición de campamento (decodificador corregido) | 26-49 | −11 |
| v4b | sin horario; la escolta sigue al carry en todos los mapas | 29-46 | −8 (cercanos +3, lejanos −5) |
| v4n | v4b solo en mapas cercanos (camino spawn-spawn <35) | 33-42 | −4 |
| **v4o2** | v4n con la pareja desde r50, Vendetta libre, la escolta acaba su grupo y lejanos idénticos a e1foco | **39-36** | **+2 (la mejor de la cadena, +8 frente a kvvl)** |
| v4q | v4o2 + juntarse en 4 ante 3 o más rivales | 35-40 | −2 (cerrada) |

**Lo que se sabe con certeza**
1. El horario del top 10 cuesta partidas las dos veces que salió: quita el 40-44% de los cobros de oro.
2. La pareja carry/escolta cambia algo visible en los 23 cercanos (todos divergen de e1foco hacia r50-65):
   - baja las muertes en inferioridad entre un 10% (v4o2) y un 46% (v4b);
   - baja las capturas en 17 de 23, sobre todo en elk_arena (−65 en 3 partidas), swirl y stalactites;
   - convierte solo 2 resultados (fragment y vault, los dos a favor).
3. Un segundo cuerpo en el mismo grupo no lo limpia mucho más rápido. El carry baja de 45 a 37 rondas por captura; el carry ganador del top 10 hace 42 con la misma métrica.
4. En los mapas lejanos la pareja pierde (local 34/98 frente a 62; online −5): se queda fuera.
5. Con los mismos mapas, el top 10 no elige otros campamentos para el carry: cúmulos, oro, lobos y alces salen igual. La tienda del top 5 tampoco acelera la captura.
6. Combustible: un printf de más en el turno de init movía un turno el init de un campeón y cambiaba 27 de 98 partidas lejanas. En v4o2 los lejanos son idénticos a e1foco en 94/98 en local y 51/75 online. Cualquier línea nueva cambia algo de la partida por puro combustible.
7. Decodificador: el replaydump antiguo ponía mal spawn y recompensa en 18 mapas, y eso explicaba map=none en v2. Ya está corregido (PC 6746f59).
8. El banco local contra kvvl no predice el resultado online: v4o2 hace 80/140 frente a 87 de e1foco y online le gana.

**Tres preguntas abiertas y el dato que las decide**
1. ¿Es real el +2 de v4o2 sobre e1foco? Lo decide la cadena c35, que está jugando ahora mismo con kvvl, e1foco y v4o2.
2. ¿Puede la pareja dejar de costar capturas en cercanos? Haría falta un mapa cercano donde el top 10 tenga dos cuerpos en un grupo y cobre más que uno solo (capturas por cuerpo en las réplicas top 10 contra top 10 de esos 21 mapas). Si no existe, la pareja solo sirve para morir menos.
3. ¿Qué falta en los lejanos (60% de las partidas, donde seguimos siendo e1foco)? Lo decidiría una comparación por tramos del top 10 ganador frente a e1foco en mapas ≥35: muertes en inferioridad r151-300 y gemas a r300, el mismo análisis de pareja que ya se hizo con los cercanos.

Todo está en la rama claude/project-thread-w1dkw0, carpeta handoff4/t10plan: README (cifras locales por versión), zips con su sha y an/ (escort, cyc, carryanal, mapcmp, pairfoe, divq).

**Respuestas a las preguntas 2 y 3** (an/night23.py, 03:55 UTC; top 10 = lado ganador de las partidas top 10 contra top 10, decodificación nueva, o la antigua en los mapas que la corrección no toca; nuestros = c34 online. Los mapas no coinciden del todo y los rivales tampoco: los suyos son top 10, los nuestros 56-70.)

2. Mapas cercanos, r0-400, top 10 / v4o2 / e1foco:
   - capturas por partida: 19.5 / 19.0 / 22.1;
   - rondas de campeón en campamento: 844 / 655 / 686;
   - capturas por cada 100 rondas en campamento: 2.31 / 2.91 / 3.23;
   - aliado a ≤4: 64 / 55 / 45%;
   - muertes: 2.4 / 3.6 / 3.3.

   El top 10 no captura más rápido por cuerpo, captura incluso más despacio. Su ventaja es estar vivo y en campamento más rondas. Implicación: la pareja vale por las muertes que evita, no por limpiar antes, y mientras cueste rondas de campamento no compensa.
3. Mapas lejanos (≥35), por tramos de 50 rondas, top 10 (140 partidas, 36 mapas) frente a e1foco (52, 33 mapas); tabla completa en timeline/far_t10_vs_e1foco.md:
   - aliado a ≤4: 52-63% frente a 37-43%;
   - en su mitad: 72-75% frente a 80-84%;
   - en campamento: 50-53% frente a 43-48%;
   - muertes por tramo: 0.18-0.29 frente a 0.33-0.63, casi la mitad desde r150;
   - capturas por tramo: 3.2-3.4 frente a 2.6-3.0, con más cúmulos (1.1-1.2 frente a 0.6-0.8) y menos oro solo (0.6 frente a 1.0);
   - gemas entregadas por tramo: +20-70%.

   Implicación: en lejanos lo que falta es no morir en r150-600 (la mitad de muertes) estando más juntos y más adelantados. Es el mismo eje que la pareja en cercanos, pero allí la pareja que sigue al carry costó −5. Haría falta otra forma de estar juntos que no cueste rondas de campamento.
