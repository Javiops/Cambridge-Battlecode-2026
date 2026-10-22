# Por qué el filtro local no predice online, y un filtro mejor (2026-10-21)

> Informe original del hilo "Local filter vs online results" (21/22-10-2026), copiado tal cual. Las rutas `ws/bots`, `arena/maps/site35|site40` y `res/` son las de aquella máquina: en este repo los rivales están en `panel/rivals/`, los mapas en `maps_site40/` y los resultados en `out/panel/res/`. Cómo usarlo: `panel/README.md`.

Hilo "Local filter vs online results". Motor local cambc 3.0.4 (= engine 1.0.2, igual que el sitio), 35 mapas del sitio x 2 lados, `--release`.
Se jugaron unas 3600 partidas locales y se decodificaron 120 repeticiones online de v96/v98 contra 71-95.

## 1. Revisión de los candidatos sobre horfocus (v98)
- **midgold-v1-on-hf**, **homedef-v1-on-hf** y **gemkeep-v1-on-hf**: cada diff contra horfocus-v1 contiene solo el cambio previsto (params.h + el bloque marcado). No hay nada más.
- Mecanismo en las repeticiones locales (candidato/base por partida, scripts/mech.py):
  - midgold: los campos de solo oro del medio capturados antes de r300 pasan de 1.4 a 2.1. La palanca se mueve, pero el efecto es pequeño (+0.7 capturas por partida).
  - gemkeep: los campos de solo oro tardíos bajan de 27.2 a 25.1 y los de solo gemas suben de 3.9 a 4.2. Las gemas no cambian (710 frente a 711). La palanca apenas se mueve.
  - homedef: las muertes en nuestra mitad pasan de 8.9 a 8.3, y las muertes totales de 13.6 a 13.0. Es ruido. En local la regla casi no tiene a qué responder (ver el punto 2c).
- Contra el panel de rivales, todos los candidatos nuevos salen negativos (tabla del punto 3): midgold -10, homedef -14 (contra el invasor -6) y gemkeep -7. Online, midgold dio +1, plano.

## 2. Por qué el filtro local actual (70 partidas cara a cara contra la base) no predice

a) **Es ruido.** El motor es determinista: el mismo par da siempre el mismo resultado (midgold reprodujo su 40-30 exacto). Hice cuatro retoques de parámetros de horfocus sin ninguna idea detrás (P_HALF 40 y 22, P_HOLD 230 y 170). Contra horfocus quedaron 36-34, 33-37, **30-40** y 35-35. Los cambios mínimos (P_HALF ±1 o ±2) dieron de 35-35 a 38-32. Todos los candidatos, de 32-38 a 43-27, caen en esa misma franja. Además, el mismo cambio midgold dio 35-35 sobre v96 y 40-30 sobre horfocus. La desviación típica con 70 partidas es de ±4 victorias, así que un 40-30 queda a 1.2 sigmas.

b) **El rival es un espejo.** Online, solo el 9% de las partidas (v94-v98) tienen exactamente nuestro draft. Los rivales eligen HoR en el 54%, Cassi en el 40%, Vesper en el 29%, Tavi en el 27%, Vendetta en el 26% y Marcella en el 23%. En local, el 100% de las partidas son HoR/Stellar/Ren/Ryth/Varg contra lo mismo.

c) **El rival local no juega como los rivales.** Medido en repeticiones (rondas por partida con 2+ o 3+ rivales vivos en nuestra mitad):
| | 2+ invasores | 3+ invasores |
|---|---|---|
| online v96/v98 contra 71-95 (120 partidas) | 314 | 136 (183 en derrotas) |
| local, horfocus contra sí mismo | 189 | 47 |
Además, los rivales capturan la mitad de campos de solo oro que nosotros (4.2 frente a 8.3 antes de r300), mientras que la base local copia exactamente nuestra economía. Por eso un cambio que cubre un hueco de la base, como coger oro, gana sin oposición en local, y online ese hueco no existe.

d) **Lo que no explica el fallo.** La versión del motor no es la causa: local 3.0.4 = 1.0.2. Solo hpshare se filtró en 1.0.1. La mezcla de mapas tampoco: online los 35 mapas salen entre 0.5x y 1.4x de la media, y en local cada mapa sale una vez por lado.

e) **El propio veredicto online también es ruidoso.** Un lote cambia unas 26 partidas, así que la desviación típica es de ±5 y la barra de 10 equivale a 2 sigmas. Los +3 y -4 de hpshare y goldfarm no se distinguen de 0. Con 4 veredictos, ninguna calibración puede ser fina.

## 3. Filtro propuesto: panel de rivales, emparejado como el juez online
- Panel en `panel/`: el cerebro de v82 (draft-meta-v1b) con drafts de rivales:
  - pA: Stellar/Ren/Tavi/Varg/Vendetta
  - pB: Ryth/Cassi/Vesper/Stellar/Ren
  - pC: HoR/Ren/Ryth/Marcella/Vesper
  - pInv: el invasor, draft normal, P_HALF 250 y sin la penalización de "doorstep". Tiene 231 rondas/partida con 3+ en nuestra mitad: invade de más, pero es el único que presiona la defensa.
- Mapas: hasta el 21-10 a las 23:20 el panel usó los 35 mapas de arena/maps/site35. El pool del sitio tiene ahora 40 mapas (arena/maps/site40, sha verificado): los 35 antiguos son idénticos byte a byte y hay 5 nuevos (gem_fields, gemfight, great_wall, lost_world, road_of_riches). Todos los veredictos de la tabla anteriores a execute-v2 son con 35 mapas; desde entonces se usan 40.
- Rivales añadidos el 21-10 a las 20:05 para la banda 66-90: pE Cassi/Ren/Ryth/Stellar/Varg, pG Cassi/HoR/Stellar/Tavi/Varg, pM espejo (v82 con nuestro draft). Base del panel desde v101: treasure-v1. Con 9 rivales: `PAN=pA,pB,pC,pInv,pD,pF,pE,pG,pM python3 scripts/pair6.py BASE CAND`.
- Rivales añadidos el 21-10 a las 19:40 para la banda 91-115 (Vesper 47%, Vendetta 43%, Marcella 39%): pD HoR/Ryth/Vesper/Vendetta/Marcella, pF Ryth/Vesper/Vendetta/Varg/Prism (aún sin calibrar; son más duros: horfocus gana 38/70 y 34/70). Script de 6 rivales: scripts/pair6.py; muertes por campamento: scripts/camp.py.
- Juicio: candidato y base juegan contra cada miembro del panel, en los 35 mapas y los 2 lados (280 partidas cada uno). Se comparan partida a partida (las mismas condiciones dan el mismo rival y el mismo mapa). Se cuentan las victorias a favor y en contra entre las partidas que cambian, con la barra 2*sqrt(cambios), como el juez online.

Calibración con los 4 veredictos online (panel_table.txt):
| candidato | online | cara a cara local | panel neto (barra) | solo invasor |
|---|---|---|---|---|
| goldval (v96 vs v94) | +16 | 43-27 | +4 (19.0) | +8 (11/3) |
| horfocus (v98 vs v96) | +12 | 40-30 | **+26 (17.0)** | +6 (7/1) |
| hpshare (v94 vs v82) | +3 | 40-30 | +12 (18.1) | -3 (4/7) |
| goldfarm (v95 vs v82) | -4 | 42-28 | +2 (15.7) | -2 (6/8) |
| midgold-on-hf | +1 | 40-30 | -10 (11.3) | -1 |
| homedef-on-hf | 0 (11/11, rechazado) | 35-35 | -14 (15.5) | -6 (2/8) |
| gemkeep-on-hf | descartado sin jugar | 32-38 | -7 (10.0) | +1 |
| treasure-v1 | +4 en 2 lotes (+7, -3; barra 14.7), promovido = v101 | 44-26 | +10 (13.9); 6 rivales +25 (17.3) | -3 (3/6) |
| mate-dash-v1 (promovido = v102, base del panel desde 21:40) | +7 en 2 lotes contra v98 (+4, +3; barra 13.4, rechazado por la regla); +4 vs v101 | 43-27 (mate solo) | -8 (15.2); 6 rivales -5 (18.7); 9 rivales -13 (23.2) | -2 (2/4) |
| bankwalk-v2 | — | — | -8 (15.2); gemas -4.6%, paseo 28.5→25.3 | -3 (3/6) |
| lonegem-v1 | — | — | -10 (11.7); gemas -2.5%, capturas 89.5→87.9 | +3 (4/1) |
| horfocus-v2 | — | — | +1 en 6 rivales (8/7); 186/280 partidas idénticas | +1 |
| campsafe-v1 | — | — | -13 en 6 rivales (bar 16.9); muertes por campamento 2.68→2.49 (v2 2.54) | -9 (1/10) |
| powerv-v1 | — | 28-42 | -10 en 6 rivales (bar 19.2); muertes 6.8→5.6, gemas -2.2% | 0 (3/3) |
| powerv-v2 (sobre treasure) | — | — | -38 en 9 rivales (bar 22.1); muertes 6.8→5.9, gemas -3% | -2 (3/5) |
| camp-fragile-v1 (sobre treasure) | — | 14-14 (28) | -19 en 9 rivales (bar 14.6); muertes por campamento 2.56→2.30, por campeón 4.20→4.42 | +1 (1/0) |
| elksquad-v1 | — | — | -27 en 9 rivales (bar 23.1); muertes 6.9→8.0, capturas 88.5→76.2, alce antes de r400 1.8→2.5 | -6 (1/7) |
| kill-convert-v1 | — | 37-33 | -8 en 9 rivales (bar 20.2); kills +0.44, muertes +0.36 | 0 (2/2) |
| execute-v1 | — | — | 0 en 9 rivales (bar 19.0); kills +3%, daño por kill -3%, muertes +0.12 | +1 (2/1) |
| execute-v2 (sobre mate-dash) | — | humo 40 peor | 35 mapas: +5 (bar 20.9); 40 mapas: 0 (65/65, bar 22.8) | 35 mapas +1; 40 mapas -1 (4/5) |
| nogold-v2 (sobre mate-dash) | — | humo 8-4 en mapas de poco contacto | 40 mapas: +3 (bar 23.6); 9 mapas malos +5 (15/10), resto -2; gemas +1.3%, capturas -4% | +2 (4/2) |
| stallfix-v1 (v105 = V13, sobre mate-dash) | +11 (pasa) | — | 40 mapas: +16 (82/66, bar 24.3); muertes +0.1; rivales q: -14 | -4 (3/7) |
| value-v1 (sobre stallfix) | -9 | — | **+30** (96/66, bar 25.5); muertes 7.2→7.9; rivales q: 0, oro@r400 -3.6% | +6 (8/2) |
| goldw40-v2 (sobre stallfix) | -7 | — | **+36** (95/59, bar 24.8); muertes 7.2→7.7; rivales q: +8, oro@r400 +0.4% | +1 (5/4) |
| elksplit-v1 (sobre stallfix) | -3 | — | +21 (90/69, bar 25.2); muertes +0.1; rivales q: -3, oro@r400 +2.9% | +4 (9/5) |
| need2-v1 (v110 = V14, sobre stallfix) | +7 y +7 (barra 15.5), promovido | — | +7 y oro@r400 +3.4% (medido por el hilo de la API) | — |

Lectura de las filas sobre stallfix (22-10):
- El panel dio positivos a los tres candidatos que perdieron online (value +30, goldw40 +36, elksplit +21). Para cambios de farmeo o economía, el neto del panel no sirve como señal.
- Lo que sí los separa son las muertes por partida: value +0.7 y goldw40 +0.5 frente a +0.1 de stallfix. El hilo de la API vio lo mismo online: si el oro en r400 baja, se muere más y se pierden peleas.
- Rivales q (cerebro de v105 con los drafts de pD/pF, más un invasor v105, scripts en ws/bots/qD, qF, qInv): tampoco sirven, porque dan a stallfix -14. Pero reproducen el mecanismo: en las partidas emparejadas donde el oro en r400 baja 200 o más, las muertes suben +4.7, con correlación -0.55 (online -0.60).
- Puerta adoptada para cambios de farmeo o economía: se rechaza si las muertes por partida en el panel suben 0.4 o más, o si el oro en r400 (scripts/gold400.py) queda por debajo de la base.

Lectura:
- El cara a cara dio a los 4 primeros entre 40-30 y 43-27. No separa nada.
- El panel completo pone a horfocus el primero (es el único que supera la barra) y a goldfarm el último. Pero infravalora goldval, porque pB y pC lo castigan.
- El invasor, por sí solo, ordena los 4 igual que online (dos positivos, dos negativos), aunque con pocos cambios.
- midgold, que en local era 40-30, salió plano online (+1). En el panel ya salía negativo.
- Con n = 4, esto es una pista y no una prueba.

Regla práctica propuesta, para el filtro y no como juez:
1. No usar nunca el cara a cara contra la base como señal de ganancia.
2. Subir online si el panel neto es >= 0 y el invasor >= 0. Si alguno sale negativo por encima de su barra, se descarta.
3. Si el candidato tiene una palanca concreta, exigir que la métrica objetivo se mueva en las repeticiones del panel (mech.py) antes de subirlo.
4. Recalibrar con cada veredicto online nuevo: añadir la fila a esta tabla.

Coste: unas 280 partidas por bot. Aquí, con 4 núcleos, son unos 12 minutos; en el PC (16 jobs), unos 3. La base contra el panel se juega una sola vez por base.

## Cómo repetirlo
- Bots en `ws/bots/<nombre>/src`, mapas `arena/maps/site35`. El manifiesto tiene una línea por partida: `bots/X bots/pA maps/m.map26a res/cal_X_pA/A_m.repl26a --statistics res/cal_X_pA/A_m.json --json`, y la línea B con los equipos cambiados.
- `cambc run-batch man.txt --jobs N --release --json`, después `python3 scripts/cal.py` (en ws/) y `python3 scripts/mech.py TAG`.
- `scripts/mech_online.py` mide lo mismo sobre las repeticiones online (online_mech.json).
