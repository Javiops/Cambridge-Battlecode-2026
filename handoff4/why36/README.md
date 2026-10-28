# Por qué perdemos contra los 15 de delante (c34 + c36 parcial), 28-10 ~09:30 UTC

Datos: v4o2 y e1foco online contra los rivales 56-70: c34 completo (150 partidas) y c36 parcial (72 de 150, commit cb6f0f3).
Todas las réplicas están decodificadas con replaydump.js corregido (6746f59). e1foco c34 se redecodificó (dec/e1fix), porque la decodificación anterior era de las 22:13.
Hay 115 derrotas y 107 victorias. Tabla por partida: why36_losses.txt. Scripts: why36*.py (índice combo.json).

1. **Dónde está la diferencia.** En las derrotas, hasta r600, capturamos 217 gemas por partida frente a 401 del rival. 143 de esas 184 gemas de diferencia (78%) son grupos de 40 gemas o más: 66 frente a 209.
   - El rival hace el doble de daño a esos grupos: 17.2k frente a 8.9k.
   - Captura con 2.42 cuerpos frente a nuestros 1.89.
   - La eficiencia es la misma: unas 5k de daño por captura los dos.
   En las victorias es al revés: los grupos grandes son nuestros.
2. **Tiempo.** Pasamos 400 rondas-campeón muertos hasta r600, frente a 174 del rival (+226). Él pasa 258 rondas en grupos grandes y nosotros 173.
   Muertes r151-600: 5.90 frente a 2.31. Morimos más que el rival en 79 de 115 derrotas.
3. **Cómo morimos.** 2.12 muertes por partida (rival 0.31) son con 3 o más rivales a ≤6 (244 casos):
   - El 91% de esas peleas empiezan igualadas o a favor: el primer contacto es un rival a ≤6 frente a 2 nuestros.
   - El tercer rival llega 8.5 rondas después de media. La pelea dura 22 rondas.
   - La víctima tenía el 74% de vida cuando ya veía 3 rivales a ≤8. Lo vio durante 11.7 rondas y en el 77% de los casos acabó más cerca de ellos.
   - En el 74% de los casos no estaba en un campamento.
4. **Código** (v4o2 = e1foco aquí):
   - verdict.h:66-73 decide la pelea una sola vez, en el primer contacto. Con P_PV 1 un "quedarse" (0) no se vuelve a evaluar, porque `if (g_verdict)` salta cuando vale 0. Así que los refuerzos rivales nunca la convierten en "irse".
   - Lo demás de la cascada no cubre ese caso:
     - P_OUTNUM 0, la regla de inferioridad está apagada;
     - P_BCF 1, el LEAVE de bcf no se ejecuta;
     - "avoid" (main.cpp:5019) solo actúa con menos del 45% de vida o un rival a ≤2.
   - Ya se vio el 10-19 con el motor antiguo, donde se estimó que salvaba 0.06-0.35 muertes.
5. **Ojo con la causalidad.** Estar en inferioridad es también efecto de ir por detrás:
   - en nuestras victorias, el rival queda en inferioridad 3.46 veces por partida y muere el 23% de esas veces;
   - nosotros, en derrotas, 5.53 veces y el 31%; en victorias, 3.33 veces y el 20%.
   - La diferencia ya existe a r150: 47-57 gemas frente a 64-76, y 60 rondas muertos frente a 31.
6. **c36.** El patrón es el mismo en mapas nuevos (derrotas: muertes r151-600 6.07 frente a 2.39). Nada específico ha cambiado: el +6/+8 de c34 estaba dentro de la barra.
