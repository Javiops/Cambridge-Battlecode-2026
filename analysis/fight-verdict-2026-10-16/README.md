# Decidir la pelea antes de empezar (2026-10-16)

Hilo "corte de pelea". Pregunta del usuario: el corte de pelea es "si veo que pierdo, me voy"; muchas peleas se
saben ganadas o perdidas antes de empezar, ¿cómo lo afrontamos?

## 1. Lo que dicen los replays

Datos: 63 partidas online de v52 (site v52, 18:56-19:00, casi todas mapas de pelea: collision, interlock, lanes,
elkring, corners) y, para comparar, las 101 partidas de Mite y Univardisty del estudio top-2. Cada pelea es un
**episodio** por campeón: filas seguidas con un enemigo a ≤8 (hueco > 3 rondas = episodio nuevo), con contacto real
(enemigo a ≤4 en algún momento). **Primer contacto** = primera ronda con un enemigo a ≤6. Perdida = morimos sin
matar a ninguno de los enemigos del episodio; ganada = matamos sin morir.

| | episodios | perdidas | ganadas |
|---|---|---|---|
| nosotros (v52) | 1.843 | **20%** | 19% |
| nuestros rivales en esas mismas partidas | 1.737 | 10% | **36%** |
| top 2 (Mite + Univardisty) | 2.443 | 16% | 32% |

Qué predice, en el primer contacto, que perdamos la pelea (AUC; 0,5 = azar):

| medida en el primer contacto | AUC |
|---|---|
| **nuestra vida (hp %)**, lo que usa hoy el corte | **0,51** (nada) |
| diferencia de cuerpos (nosotros+aliados − enemigos) | 0,59-0,61 |
| poder = (vida × daño nuestro + aliados a ≤6) / (vida × daño enemigos) | 0,65 |
| vida total nuestra+aliados / vida enemiga | 0,67 |
| modelo con todo (18 rasgos) | 0,71 |

Por tramos de poder en el primer contacto (v52 / top 2):

| poder | % de peleas | v52 perdidas | v52 ganadas | top 2 perdidas | top 2 ganadas |
|---|---|---|---|---|---|
| < 0,8 (en contra) | 13% | **40%** | **4%** | 27% | 13% |
| 0,8-1,25 | 8% | 21% | 15% | 20% | 25% |
| 1,25-4 | 28% | 21% | 19% | 21% | 24% |
| > 4 (muy a favor) | 51% | 14% | **24%** | 11% | **41%** |

- **Peleas perdidas antes de empezar:** el 13% de nuestras peleas empiezan con poder < 0,8; ahí perdemos el 40% y
  ganamos el 4%. Son el **26% de nuestras peleas perdidas**. Nos quedamos (atacar/avanzar) en el 85% de ellas.
  Las pocas veces que nos fuimos en las 3 primeras rondas perdimos el 24% en vez del 43%. Nuestros rivales, en la
  misma situación, se van al momento el 42% de las veces y pierden el 19%.
- **El 65% de nuestras peleas perdidas empezaron a favor** (poder ≥ 1,25). En el 82% de esas llegaron más enemigos
  después del primer contacto. Es decir, la mayor parte de lo que perdemos no se ve en el primer contacto: son
  refuerzos y ejecución (en las perdidas, el rival pega primero el 44% de las veces, frente al 29% en todas).
- **Con ventaja clara no rematamos:** con poder > 4 ganamos el 24% y el top 2 el 41%, nuestros rivales el 47%.

## 2. El enfoque

Decidir **una vez** en el primer contacto y **mantenerlo** (histéresis), en vez de un corte de vida que se
recalcula cada turno:
1. En el primer contacto (enemigo a ≤6, tras ≥4 rondas sin contacto) calcular el poder:
   (vida yo + aliados a ≤6) × (daño yo + aliados) / (vida enemigos a ≤6 × su daño). Daño = fuerza + foco×1,5/8
   (`fight::unit_dps`, ya en v52). Coste: una pasada por los campeones en visión, sin BFS (unos cientos de fuel).
2. Poder < 0,6: veredicto **irse**, mantenido hasta que acabe el contacto; solo se revierte si llegan aliados y el
   poder pasa de 1,9.
3. (Variante) Poder ≥ 1,25: veredicto **pelear**: se quitan las retiradas "desfavorables" de v52 (siguen los cortes de
   vida del paso 2). Revierte a irse si el poder cae bajo 0,45 (llegan enemigos).

## 3. El interruptor (P_PV) y lo medido

`verdict.h` + 3 enganches en el paso 3 de `main.cpp` (`verdict_on_v52.patch`). Con `P_PV 0` las 170 partidas de
cada panel son idénticas a v52 (0 cambios). Parámetros: `P_PV` (1 irse, 2 irse+pelear), `P_PV_LEAVE`, `P_PV_FIGHT`,
`P_PV_R`, `P_PV_ER` (radio de enemigos contados), `P_PV_KEEPCAP`.

Panel de especialistas, 17 mapas del sitio × 2 lados × 5 rivales = 170 partidas, cambios ganados-perdidos frente a
v52 (panel A = construido sobre la versión 12:52, panel B = construido sobre v51). v52: A 124/170, B 120/170.

| variante | A | B |
|---|---|---|
| P_PV 1 (irse < 0,8, enemigos a ≤8) | 14-20 | 26-9 |
| irse < 0,6 | 18-18 | 22-11 |
| irse < 1,0 | 13-21 | 28-11 |
| irse < 0,8, primer contacto a ≤4 | 19-18 | 19-17 |
| irse < 0,6 + no soltar captura | 16-19 | 22-14 |
| P_PV 2 (irse + pelear) | 18-20 | 22-16 |
| **irse < 0,6, enemigos a ≤6** (`pver6`) | **17-11 (+6)** | **20-11 (+9)** |
| irse < 0,8, enemigos a ≤6 | 24-20 (+4) | 21-10 (+11) |
| irse < 0,6, enemigos a ≤6 + pelear | 13-14 | 26-13 |

Ninguna pasa el listón (>10 cambios en los dos paneles). La mejor equilibrada, `pver6`, gana en los dos (+15 en 340
partidas) y muere 0,5-1,5 veces menos por partida, pero está dentro del ruido. Pierde en corners en el panel B
(0-3, más muertes); gana en swirl, stampede y eight. Por mapa: `data/permap_pver6.txt`.

Zip candidato (solo para una prueba online si el usuario quiere): `/mnt/project-files/bot/mybot_v52_verdict.zip`
= v52 + `P_PV 1`, `P_PV_LEAVE 60`, `P_PV_ER 6`. No subido.

## Archivos

- `verdict.h`, `verdict_on_v52.patch`: el interruptor sobre v52.
- `data/episodes_v52.csv`, `data/episodes_top101.csv`: un episodio por fila con los rasgos del primer contacto y el
  resultado. `data/feat_output.txt`: tablas y AUC.
- `scripts/`: `poll.py` (descarga con espera de trabajos del sitio), `bd2.py` (build_dataset del hilo de imitación
  con columnas extra: daño recibido de campeones, aliados a 2/3/6, tipos), `episodes.py`, `feat.py`, `permap.py`.
  Reproducir: `bd2.py STEPS games_v52.json online/mapsj OUT` y `episodes.py OUT STEPS`.
