# pelea-v1: entrar en las peleas solo con ventaja numérica (sobre kvvl = handoff/chain14/k_vvl_mgwp.zip)

Auditoría 10-24: online, en mapas cercanos y antes de r150, el top 10 pasa el 36-43% de sus rondas de pelea superando en 2
al rival (pvpnum.py, num = 1 + aliados − rivales a 3 casillas, con un rival a 4 o menos). Nosotros, el 12-21%.
A la par: ellos 22-26%, nosotros 34-47%.

| zip | P_NUM | P_NUM_GANG | P_JOIN | qué hace |
|---|---|---|---|---|
| pelea-v10.zip | 0 | 0 | 0 | control: kvvl + solo el contador (mismo juego que kvvl) |
| pelea-v1a.zip | 1 | 0 | 0 | regla de entrada: para acercarse a un rival hay que ser uno más a 4 de él (yo incluido); en alcance, casi muerto (hp ≤ 0.5 golpes) o canalizando, siempre se le pega |
| pelea-v1b.zip | 1 | 6 | 0 | a + convergencia: un rival a 6 o menos, sin otro rival a 4 de él y con un aliado nuestro a 4 de él → vamos los dos (P_GANG reescrito) |
| pelea-v1c.zip | 1 | 6 | 1 | b + join-v1: con ningún rival a la vista, ir al aliado marcado "en pelea" en su byte de reclamación (r30-150, cercanos) |

La regla se aplica a la persecución (chase), a la entrada aprendida (bcf ENGAGE), a la entrada final (favourable / helping) y a
campfoe. Retenerse por la regla no convierte el turno en retirada (sigue farmeando); las retiradas en inferioridad ya se probaron.

Por qué estaban apagados P_GANG y help_target: los dos bloques llevan `if (false)` en el código (P_GANG 0 no hacía nada), y help_target
escribe en el byte 7 de memoria compartida, que ahora es del altar de peligro (update_danger). join-v1 usa los bits 6-7 del byte de
reclamación en su lugar.

Contador en la línea de estado: `fn=e2/e0/fr` (rondas de pelea con +2, a la par, y totales, r<400). Además se imprime una línea
`[fn] r150|r300 <campeón> fr e2 e1 e0 en skip gang join`.
Métrica: pvpnum.py (rama claude/project-thread-l6gm1j, handoff/champ/tools/). Objetivo: num=+2 del 12-21% al 30%.
Juez 2: solo veto (≥ −5).
