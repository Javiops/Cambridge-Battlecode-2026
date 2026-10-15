# Brief para quien coge una idea (persona o hilo de Claude)

Copia esto en el hilo o en el PR al empezar. Todo lo que no está aquí no es parte del trabajo.

- **Idea:** I### <título> (`python3 tools/idea.py show I###`)
- **Hipótesis a comprobar:** <número de la ficha, de cuánto a cuánto, en qué mapas>
- **Tipo y puerta:** `farm` (mapas nuevos a favor con p<0.05) | `fight` (no peor en local; decide online) | `bug` | `macro`
- **Bot base:** `bots/study28` en `main` (commit <sha>)
- **Rama:** `idea/I###-nombre-corto`
- **Un solo cambio:** <la regla / el umbral / el interruptor>. Si por el camino aparece otra mejora, se apunta como idea nueva, no se mete aquí.
- **No tocar:** las ramas de los demás; `maps_hold60`/`maps_dev200` no se usan para ajustar.
- **Tiempo:** <horas>. Si al acabar no pasa la puerta, se entrega igual con el número y se cierra como `rechazada`.

## Entregar

1. Rama con el diff del bot (solo `bots/study28/src`, y `params.h` si es un switch).
2. `python3 tools/gate.py bots/study28 main --kind <tipo> --idea I###` con el candidato final; adjuntar `out/gate/.../gate.txt`.
3. Los 3 peores contraejemplos mirados con `cambc view` y una línea sobre cada uno.
4. `docs/I###-nombre.md` según `harness/templates/resultado.md` y el PR (borrador hasta la decisión online).
5. Tablero: `idea.py set I### --stage local-ok|test-local|rechazada --pr <n> --note "<número que lo decide>"`.
