# fuelfit, sección pelea (hilo «Copiar las decisiones del top 10»)

Piezas exactas sobre fuelfit-a1 (se aplican después de o01-o05, en orden: `for o in opts/o2*.py; do python3 $o SRC; done`).
Validación: 52 partidas del subconjunto (mk.sh | awk 'NR%6==1'), `--fuel-quantum 2000000`, `same.py res/fa1 res/fa1+o21-o26`:
**replays 52 differ 0**.

| pieza | qué hace | por qué es exacta |
|---|---|---|
| o21_reachmemo | fight::reach() memorizado por (ronda, handle del campeón) | lee alcance, nombre y habilidades del rival; nada cambia durante nuestro turno |
| o23_safestep | safe_step: una casilla se descarta en cuanto la suma parcial (amenazas, blocked, casa, aliado) ya no gana; límites del mapa leídos una vez | los tres términos son >= 0; mismos filtros, mismas casillas y orden |
| o24_kitestep | kite: casilla descartada si −1000·amenazas + 400 no supera el mejor; amenazas calculadas una vez | el resto de términos es <= 400 |
| o25_vklog | el printf [vk] de Vesper solo en rondas múltiplo de 100 (contadores acumulados) | solo cambia stdout |
| o26_hordash | dash_strike de HoR: geometría (aritmética) antes de las dos lecturas de bitboard; muros leídos una vez por partida; vida leída una vez | filtros puros reordenados; muros estáticos |

Probadas y descartadas (exactas pero sin ganancia medida): lista de enemigos reutilizada si las casillas no cambian (o22) y
lista de aliados reconstruida sin champion_at tras movernos (o27).

## Medido (perfil solo de la sección 9, turnos con pelea > 33k; mkfprof.sh + fseg.py + fsg.py)

Pelea p99.9 37.5k → 37.5k (cubos de 2.5k), máximo 80k → 62.5k. En la cola (≈700 turnos > 33k, media 37k):
kite 5.2k → 1.3k, safe_step excl 4.2k → 3.6k, reach 4.2k → 1.2k, dash_strike 2.0k → 1.4k.
Lo que queda en la cola: step_towards 10k inclusivo (flee, engage, chase, anillo de front_line: del hilo de farmeo),
vis_champions 4k, front_line 1.6k excl, danger_at 1.2k (anillo de volea dentro de step_towards), y ~2k de pe_update /
pf_log / income_log que corren en run_game tras play_turn y antes de FP(12), y por eso se cuentan en la sección 9.
Por tramos (fseg): back_off (avoid / lowhp / pv-leave) ≈ 15k, front_line 6k, ally duty 2.5k, chase 2.4k, engage final 2.4k.

## 10-25 00:xx: medido sin autoprof (solo ungate; el perfilador por función inflaba la sección 3-5k)

| build | pelea p99.9 | pelea máx | decide p99.9 |
|---|---|---|---|
| det8 + o01-o05 | 35k | 77.5k | 25k |
| + o21, o23-o27 | 32.5k | 60k | 20k |
| + c01 (1 búsqueda de camino en pelea; cambia decisiones) | 32.5k | 60k | 20k |

o27_fplog: contabilidad (los logs de run_game abren la sección 13). Exacta.
rejected/c01_fightpath: sin efecto en p99.9; 312 partidas pair −5/7 (barra 5.3), a14 igual.
o28 (registro de campeón memorizado hasta la siguiente acción): exacta 52/52 pero más cara que la llamada (p99.9 35k): descartada.
Cola > 25k: 0.58% de los turnos, media 29k: front_line 4.8k, back_off 7.7k, pv-leave 2.7k, kite 2.6k, aliados 2.4k, chase 2.3k.

## 10-25 ~02:00: sobre b3 (cb88bb5), piezas exactas nuevas

Aplicar sobre b3 en orden: o18, o19, o20, o29 (o27 es solo contabilidad de perfil). same.py 52/52 con fuel ilimitado
(cada una y juntas); restarts.py 0; las líneas [fin]/[bcf] salen idénticas (quitando los \0 del fichero del equipo).

- o18_fightlogs: [fin] y [bcf] con LineOut en vez de printf (~2.5k cada una, en los turnos de pelea más pesados).
- o19_vdash: escaneo de dash de Vesper (7x7) con poda por cota antes de leer bitboards (~12k → ~2k por escaneo).
- o20_allyvis: la lista de aliados ya no se reconstruye tras cada acción nuestra (sí tras movernos: el orden depende de
  nuestra casilla). Depuración: lista en caché frente a una nueva en cada llamada, 373k llamadas, 0 diferencias.
- o29_sweepready: spell_sweep sale antes de construir la lista de enemigos si no hay hechizo Targeted/Ground listo, y
  mira distancia/spawn antes de leer vida/gemas.

b3 + o18-o29 (52 partidas, fuel ilimitado, percentiles con cubos de 1k, `fh.py`):

| sección | p99 | p99.9 | p99.99 | máx | turnos > 25k |
|---|---|---|---|---|---|
| pre-sweep | 7k | 15k | 21k | 27k | 3 |
| decide/flee | 13k | 20k | 27k | 39k | 45 |
| pelea | 22k | 31k | 39k | 70k | 1054 (0.4%) |
| post (casi todo ward_turn: 13k en sus turnos pesados) | 15k | 17k | 20k | 24k | 0 |

Media por turno 32.75k → 31.94k. Tramos de pelea en turnos > 25k (gseg.py + speck): huida de back_off (flee =
step_towards) 3.4k, safe_step aliados/alcances 3k, chase 2.5k, ally duty 2.2k, dash de Vesper 2k, engage 1.3-1.6k...
