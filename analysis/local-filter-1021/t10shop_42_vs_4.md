# t10shop-v2: por qué +42 en local y solo +4 online (22-oct, 19:00 UTC)

## Resumen
1. **No es una contradicción, es el denominador.** +42 son 42 victorias netas en **720** partidas (5,8%). Online son
   120 partidas: el mismo efecto daría **+7**. Online salió +4 (19/15). La diferencia de +3 está muy dentro del ruido
   del batch (±6).
2. **Un tercio del +42 viene de un rival blando.** pB (draft Ryth/Cassi/Vesper/Stellar/Ren) aporta +16 (17/1). Sin
   él quedan +26 en 640 partidas, es decir +5 por cada 120.
3. **El rival más realista da exactamente lo de online.** pHuntF (caza campeones aislados; acierta el signo online
   en 7 de 8 cambios) da +3 en 80 partidas, que son **+4,5 por cada 120**. Online: +4.
4. **El efecto realista de t10shop-v2 es de +4 a +7 por cada 120 partidas.** Es positivo, pero está por debajo de la
   barra de un batch (11,7). Con 2 batches (240 partidas) se esperan +9 a +14, contra una barra de unos 16,5. Lo
   más probable es que no la pase solo, aunque sí sume.

## Datos locales (reproducido aquí, cambc 3.0.4, 40 mapas × 2 lados)
Panel de 9 rivales: t10shop-v2 vs t10draft-v2 da **+42 (74/32, barra 20,6)**. Gemas 973 vs 933, muertes 3,7 vs 5,4.

| rival | victorias de la base | t10shop | neto (a favor/en contra) |
|---|---|---|---|
| pA | 71/80 | 71/80 | +0 (4/4) |
| pB | 57/80 | 73/80 | **+16 (17/1)** |
| pC | 61/80 | 67/80 | +6 |
| pInv | 72/80 | 74/80 | +2 |
| pD | 62/80 | 67/80 | +5 |
| pF | 57/80 | 65/80 | +8 |
| pE | 63/80 | 67/80 | +4 |
| pG | 71/80 | 74/80 | +3 |
| pM | 69/80 | 67/80 | -2 |
| **pHuntF** | 64/80 | 67/80 | **+3 (8/5)**, muertes 6,5 a 4,0 |
| pHunt | 73/80 | 76/80 | +3 (5/2) |

La base gana el 81% en local. Online gana el 57% (68-52). En local solo hay unos 135 partidas de 720 «en juego».

## Online, partida a partida (draw 16:51)
Rivales del batch (24 grupos): meowest, Hidden Altar Keepers, error404, lETHal, BattleCats, noobers,
Martin Shkreli's Defense Team, EvilMangohh, Sic Mundus Creatus Est, Gem Simons, Rogue Lock Pickers, FF15, SilverSamurai,
Ninja Turtles, Midnight Wardens, QS2isLaw, opsec level opera gx, Danger Bille, Funky monkeys, FRChronic, y,
Stranger Danger, Kaizen, team (ranks 68-100 aprox.).

Mi copia del montaje solo tiene 80 de las 120 partidas (games.jsonl sin actualizar desde las 18:01). Sobre esas 80:
v120 43, v122 45, a favor 14 / en contra 12.
- Mapas cercanos (55): 37 contra 37. Mapas lejanos (25): 6 contra 8. La base ya pierde casi todos los lejanos.
- **Un mismo rival puede inclinarlo todo.** Contra Martin Shkreli (draft con Ren/Stellar), t10shop pierde 3 mapas
  cercanos que v120 ganaba por paliza (1013-120 pasa a 128-1011, y 1017-45 a 63-1018). Dos de ellas acaban antes de
  la ronda 950: es una pelea temprana perdida. Encaja con que el emblema Treasure abra la tienda y retrase la
  defensa. Las victorias que gana son al revés: partidas largas o de 2000 rondas que v120 perdía por gemas
  (BattleCats, EvilMangohh, Ninja Turtles 1020-88).
- **Las inversiones son caóticas.** Entre v117, v120 y v122 en las mismas 70 partidas, solo 37 tienen el mismo
  resultado con las tres versiones (16 victorias y 21 derrotas). Entre dos versiones cualesquiera cambia entre el 29%
  y el 34% de las partidas, y el suelo de ruido sin ningún cambio es del 9%. Muchas inversiones son palizas en los
  dos sentidos.

## Por qué el panel exagera
- Es blando: la base gana el 81% en local frente al 57% online. Las partidas «en juego» en local son las que pierde
  contra rivales con un draft concreto (pB), y ahí un cambio de economía gana casi siempre.
- Los rivales del panel no castigan la economía temprana: no persiguen al campeón aislado y no ganan la pelea de la
  ronda 300-900. pHuntF sí, y ahí la ventaja baja a +3.
- Las muertes bajan en local (5,4 a 3,7) y también contra pHuntF (6,5 a 4,0). Las muertes online siguen pendientes:
  los resúmenes de v120/v122 se están descargando.

## Qué hacer
- Comparar siempre por cada 120 partidas: neto del panel × 120/720. Una barra local equivalente a la online
  necesitaría unos +70 de 720.
- Usar pHuntF como veto y construir un panel con fuerza de V16 (en curso).
