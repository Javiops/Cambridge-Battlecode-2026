# I### <título> (doc de la idea; va en docs/I###-nombre.md con el PR)

**Hipótesis:** <qué número mueve, de cuánto a cuánto, en qué mapas>. Fuente: <ficha / estudio / brainstorm>.

**Cambio:** <una frase>. Switch: `P_XXX <valor>` (base <valor>). Ficheros: `bots/study28/src/...`.

## Puerta local (`tools/gate.py ... --kind <tipo>`)

| fase | resultado |
|---|---|
| seguridad | fallos 0, rotas 0, combustible cand/base <n>/<n> |
| mapas nuevos | <w>-<l> por los dos lados en <n> mapas, p=<p>; gemas/100 rondas <c> vs <b> |
| panel spar11/12/16 | cambian <a favor>/<en contra>, p=<p>, veto no |
| veredicto | PASA / NO PASA (<por qué>) |

Contraejemplos mirados (`out/gate/.../contraejemplos.md`):
- `<mapa>`: <por qué pierde ahí y si importa>
- ...

## Online (`online/lfl.py --a "<versión>" --b "<base>"`)

| batch (UTC) | versión | partidas | bruto | parejas compartidas | solo A / solo B | p |
|---|---|---|---|---|---|---|
| | | | | | | |

Ranked en la ventana: <w-l>. Fallos online: <0>.

**Decisión:** aceptada / rechazada / sin decidir tras <n> horas, con <número>. Tablero actualizado: `idea.py set I### --stage ...`.

## Lo que aprendimos (una o dos líneas que valgan para la siguiente idea)
