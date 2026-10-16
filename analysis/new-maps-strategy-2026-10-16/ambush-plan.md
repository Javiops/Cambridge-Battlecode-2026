# Ambush: qué hacen nuestros campeones y qué hacen los top (16-10-2026, 20:40 UTC)

Fuentes:
- **Nuestro bot:** 10 partidas locales de v52 (mybot_teammate_fixes3_mapdraft.zip) contra los 5 especialistas, por los dos lados. Todavía no hay partidas de v52 en ambush en el sitio; la última es de v51, a las 18:50.
- **Los top:** 15 victorias de equipos del top 10 (Univardisty, Intercontinental Fish, Shawn), de las repeticiones del estudio de la mañana.
- **Herramienta:** `python3 tools/nm/ambplan.py bots/f3` para nuestras partidas y `--top` para las de los top.

Coordenadas vistas desde nuestro lado (salida en la esquina 3-7,3-7). Campamentos con gemas:
- 106 gemas en (21,44)
- 72 gemas, alces, en (31,44), a 10 casillas del de 106
- 120 gemas en (56,34)
- 120 gemas en (43,65)

## El plan de los top

1. Los 5 o 6 van juntos al de 106 y lo capturan en r73-77.
2. Solo el portador vuelve a casa a depositar. Dos campeones van directos al de 72, que capturan en r96-111 en el mismo viaje.
3. Desde r200 añaden los dos de 120, de tres en tres: por ejemplo Ren, Stellar y Cassi en r240.
4. Depositan una vez cada 30-50 rondas, con bolsas de 106-120 gemas, y llegan a 1000 gemas en r534-667.

Tiempo de cada campeón: caminando 70-80 %, en un campamento 8-13 %, parado fuera de casa 10-20 %, muerto 0-11 %.

## Lo que hace v52

1. **Primer campamento.** Captura el de 106 en r88-90, 13-15 rondas después que los top. Hay dos causas:
   - Los que tienen dash rodean las líneas de agujeros (la fila 37 encima del campamento).
   - Ren cambia de objetivo a medio camino: 11 → 8 → 6 → 1 → 8 → 11. Hay 4 campamentos con puntuación parecida (0.29-0.53), y cada reclamación de un aliado cambia cuál es el mejor.
2. **Después de la captura** se rompe la ruta:
   - El de 72 cae en r190-243, unas 100 rondas tarde.
   - Dos campeones sanos se van solos al de 120 (56,34), que necesita 3-4 campeones. Caminan 35 rondas, no llega nadie más y vuelven (traza r96-150).
3. **Los de 120** no los tomamos nunca antes de r640. Al de (43,65) además le quitamos el 70 % de la puntuación por estar «en su mitad», aunque allí no hay enemigos.
4. **Cassi&Issac** no llegan a un campamento hasta r173-794. Mueren mucho: 14-30 % de sus rondas.
5. **Resultado:** llegamos a 1000 gemas en r800-1066, o no llegamos. Pasamos parados fuera de casa el 20-30 % de las rondas, frente al 10-20 % de los top.

## Reglas probadas (interruptores sobre v52, apagados = v52)

Cada panel tiene 170 partidas: 17 mapas del sitio, por los dos lados.

| Interruptor | Qué hace | Mi panel (v52 = 120) | Panel 12:52 (v52 = 124) | Ambush |
|---|---|---|---|---|
| P_MP_DASHHOLE 4 | dash sobre agujeros de 1 casilla | 131 (18-6) | 128 (15-11) | muertes 9.6 → 5.7 |
| P_MP_DASHHOLE 8 | igual, solo si ahorra 8+ casillas | 129 (15-6) | 130 (14-8) | |
| P_MP_STICK 200 | mantener el objetivo lejano | 122 | 128 | 7-9 de 10 |
| P_MP_SPREAD | no apilar más de lo que pide el campamento | (peor en ambush, sin panel) | | nadie toma el de 106 a tiempo |
| P_MP_COMPANY 30 | en mapas lejanos, no ir solo lejos a un campamento que pide escuadra | 119 | 129 | 8 → 10 en mi panel, muertes 9.6 → 4.3 |
| P_MP_COMPANY 30 + DASHHOLE 8 | las dos | 128 | 125 | |
| P_MP_CHAINPLAN 300 | tras una captura al lado, los que no llevan gemas puntúan x3 los campamentos a 15 casillas | 117 | 125 | 8-9 de 10, +40 gemas |
| CHAINPLAN + DASHHOLE 8 | | 126 | 123 | |
| CHAINPLAN + COMPANY 30 | | 116 | 125 | muertes 9.6 → 5.0 |

- **Rasgo del mapa:** los mapas lejanos son los que tienen la mediana del camino de casa a los campamentos con gemas ≥ 60. Son ambush (73), rows, pilgrimage y expanse.
- **Veredicto:** ninguna supera +10 en los dos paneles.
  - El dash es lo más fuerte en mi panel, pero cuesta 4 en stampede en el panel 12:52.
  - P_MP_COMPANY es el mejor en el panel 12:52 y arregla ambush en mi panel, pero no gana en el total de mi panel.
- **Parche:** /mnt/project-files/bot/mapplan_v52_wave3.patch. El código está en la rama claude/new-maps-strategy-5ffnvq, en bots/newmaps.

**La cadena (21:20 UTC) tampoco gana.** En la traza, cuando cae el de 106 en r90, solo quedan 2 campeones libres al lado: Cassi e Issac ya han muerto y el tercero se ha ido a casa con 17 % de vida. Uno solo no puede con los alces de 72 gemas. Lo que corta la cadena son las muertes en el primer campamento, no la elección del siguiente.

## Lo que falta para jugar como los top

Lo que separa nuestro plan del suyo es lo que pasa justo después de cada captura. Ellos tienen un plan de escuadra: el portador a casa y el resto al campamento de al lado, juntos. Nosotros dejamos que cada campeón vuelva a elegir solo cada 6 rondas.

La siguiente regla sería una cadena de campamentos calculada del mapa. Al empezar la partida se ordenan los campamentos con gemas por distancia andando, en la cadena de 106 → 72 → 120. Después de cada captura, los que no llevan gemas van juntos al siguiente eslabón de la cadena, y el portador va a depositar.
