# Macro de Mite fijo por mapa (P_MITEMACRO)

Banco de pruebas para medir **solo micro y decisiones de medio juego**. Con `#define P_MITEMACRO 1` el bot
(`bots/study28`) juega en los 9 mapas oficiales el macro que el #1 Mite jugó en sus repeticiones:

| lo copia de Mite (fijo por mapa y lado) | sigue siendo nuestro |
|---|---|
| el draft | pelear o no, a quién pegar, hechizos, kite, línea de frente |
| los objetos (familias de emblemas y cuántos, en su orden) | huir y recall cuando estamos heridos |
| por campeón: la lista ordenada de campamentos que farmea | cancelar tributos/recalls condenados (P_CHANCANCEL) |
| quién se queda la recompensa de cada captura | curarse en la base, comprar al pasar por la base |
| sus recalls (también el recall sobre la casilla de captura) | cómo matar el campamento (a qué monstruo pegar) |
| en qué altar tributa y cuándo | |

Con el interruptor a 0 el bot juega exactamente igual que antes (mismas partidas en los 9 mapas oficiales y
en 43 de 44 mapas generados; la diferencia de 1 es ruido de combustible). En un mapa nuevo no hace nada.
`P_MITEMACRO 2` copia solo el draft y los objetos (las rutas son las nuestras), para separar efectos.

## De dónde sale el guion

`extract.py` lee las 54 partidas de Mite decodificadas paso a paso en la disección del top 2
(`/mnt/project-files/analysis/top2-dissection-2026-10-15/data/steps.tgz`, 6 por mapa contra rivales del top 20).
Para cada mapa y lado se usa la partida de Mite con menos muertes de Mite (y la más larga); si solo hay
partidas del otro lado, se refleja con la simetría del mapa. Así los dos lados juegan el mismo guion reflejado.

| mapa | partida usada |
|---|---|
| collision | vs Quantom, gana en 607, 0 muertes |
| corners | vs Quantom, gana en 376, 0 muertes |
| elkring | vs Quantom, gana en 510, 1 muerte |
| expanse | vs hello, gana en 408, 0 muertes |
| interlock | vs VeryGood, gana en 518, 4 muertes |
| lanes | vs hello, gana en 357, 0 muertes |
| monolith | vs Full Damage, gana en 422, 0 muertes |
| packs | vs Univardisty, gana en 473, 0 muertes |
| rows | vs Quantom, gana en 401, 0 muertes |

Cada campeón tiene pasos `C` (farmear el grupo de ese campamento; marca si Mite hizo recall sobre la casilla
y si fue él quien se quedó la recompensa), `R` (recall) y `T` (tributar en ese altar), con la ronda en que Mite
lo hizo. `genheader.py` lo convierte en `bots/study28/src/mite_macro.h`; `mite_exec.h` lo ejecuta.

Reglas de ejecución:
- Los pasos se hacen en orden. Un paso que todavía no empezamos se salta si vamos más de `P_MM_SLACK` (60)
  rondas por detrás del horario de Mite (después de morir o de una pelea larga); un paso empezado se termina.
- Un tributo no se salta nunca mientras llevemos gemas.
- Si no podemos con un campamento solos y nadie llega en `P_MM_RALLY` (12) rondas, pasamos al siguiente paso.
- La captura de un aliado solo cuenta para nuestro paso desde `P_MM_EARLY` (20) rondas antes de la hora de Mite
  (si no, la captura anterior del mismo grupo cerraba el paso de la siguiente vuelta).
- Cuando la lista se acaba (la partida de Mite terminó), vuelve nuestro macro normal.

## Cómo probar un cambio de micro

1. Haz dos variantes con el macro puesto que solo se diferencien en la regla de micro:
   ```bash
   tools/variante.sh mm_base study28 "#define P_MITEMACRO 1"
   tools/variante.sh mm_prueba study28 "#define P_MITEMACRO 1\n#define P_LOQUESEA 1"
   ```
2. Enfréntalas al mismo panel de rivales en los 9 mapas oficiales por los dos lados:
   ```bash
   python3 tools/mitemacro/panel.py bots/mm_prueba bots/mm_base
   ```
   Al final da cuántas partidas (mismo rival, mapa y lado) ganó solo una de las dos, con el test de signo.
3. `tools/ab.py bots/mm_prueba bots/mm_base --sets official` también sirve (cara a cara, 18 partidas).

Para mirar la fidelidad de una partida contra la de Mite: `compare.py` (gemas por campeón y por ronda),
`lag.py` (rondas de retraso por paso; requiere `#define P_MM_LOG 1`) y `campdmg.py` (daño a campamentos).

## Resultados (2026-10-15, base study27 = study28 con P_CHANCANCEL 0)

**Ritmo frente a Mite** (nuestro bot con el guion contra sí mismo, gemas tributadas por el lado A):

| mapa | r200 nuestro / Mite | r300 nuestro / Mite | final nuestro | final Mite |
|---|---|---|---|---|
| rows | 198 / 330 | 495 / 462 | 1056 en r406 | 1056 en r401 |
| interlock | 276 / 334 | 486 / 486 | 1044 en r524 | 1000 en r518 |
| expanse | 442 / 468 | 586 / 656 | 1066 en r472 | 1046 en r408 |
| elkring | 162 / 360 | 288 / 504 | 1008 en r671 | 1008 en r510 |
| packs | 116 / 232 | 300 / 416 | 1016 en r690 | 1012 en r473 |
| collision | 176 / 286 | 220 / 498 | 1116 en r958 | 1016 en r607 |
| monolith | 256 / 388 | 322 / 688 | 746 (pierde en r531) | 1018 en r422 |
| lanes | 240 / 536 | 360 / 688 | 774 (pierde en r475) | 1018 en r357 |
| corners | 70 / 544 | 92 / 912 | 402 (pierde en r660) | 1018 en r376 |

En rows, interlock y expanse el guion va casi al ritmo de Mite. En los demás vamos
por detrás: matamos los campamentos más despacio con los mismos campeones (en rows el Varg de Mite pega 238
por ronda a los campamentos, el nuestro 162: elige el monstruo que salpica a los demás), y en los mapas de pelea
los dos lados siguen el mismo plan y se encuentran en el centro (corners: 20 muertes del lado A).

**Contra el panel** (x_s27 = study27 normal, spar11, spar12, spar16, v30, study25; 9 mapas x 2 lados = 108 partidas):

| bot | partidas ganadas | muertes nuestras-suyas |
|---|---|---|
| study27 normal | 85-23 | 368-617 |
| study27 + draft y objetos de Mite (P_MITEMACRO 2) | 66-42 | 453-366 |
| study27 + macro completo de Mite (P_MITEMACRO 1) | 34-74 | 603-426 |

**Ejemplo de prueba de micro con el macro fijo:** study28 (cancelar canalizaciones condenadas) contra study27,
los dos con P_MITEMACRO 1, en las mismas 108 partidas: 7 ganadas solo por study28, 10 solo por study27
(p = 0.63). Con el macro fijo, la regla no cambia nada medible en local.

## Lo que hay que saber antes de usarlo

- Solo funciona en los 9 mapas oficiales. Los mapas de la clasificación serán nuevos, así que esto es una
  herramienta para medir micro, no el bot final.
- Nuestra micro con el macro de Mite pierde mucho más que con el nuestro: el plan de Mite cuenta con su forma
  de pelear y de matar campamentos. Para comparar dos micros entre sí sirve igual, porque las dos usan el mismo plan.
- En local los rivales son nuestros bots. La prueba de verdad es online contra los mismos equipos (el bucle de
  la hora en `online/`), que no se ha tocado: ni se ha subido nada ni se ha cambiado el bot activo.

## Regenerar

```bash
S=<carpeta con steps/ descomprimido de steps.tgz>
D=/mnt/project-files/analysis/top2-dissection-2026-10-15/data
python3 tools/mitemacro/extract.py $D/selected.json $S/steps tools/mitemacro/mapsj tools/mitemacro/mite_scripts.json
python3 tools/mitemacro/genheader.py tools/mitemacro/mite_scripts.json tools/mitemacro/mapsj bots/study28/src/mite_macro.h
```
