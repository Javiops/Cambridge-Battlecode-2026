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
