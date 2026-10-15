# Brainstorm <fecha> (plantilla)

Antes de empezar, en la mesa:
- `ficha.md` de la última disección (`online/data/dissect/<versión>/ficha.md`): la tabla nosotros/rival y las **Propuestas**.
- Salida de `lfl.py` de la última idea online (qué cambió y qué no).
- Sección "Cerradas" de `harness/IDEAS.md`: lo que ya se probó y con qué número murió. No se vuelve a proponer sin un motivo nuevo.
- Estudios de los equipos top que toquen el tema (`/mnt/project-files/analysis/`).

## Huecos (de la ficha, el número nuestro y el del rival)

| hueco | nosotros | rival | mapas donde pesa |
|---|---|---|---|
| | | | |

## Ideas

Una fila por idea. Sin hipótesis medible no entra en el tablero.

| idea (un solo cambio) | tipo | hueco que ataca | hipótesis (qué número, de cuánto a cuánto, en qué mapas) | riesgo (qué puede empeorar) | quién |
|---|---|---|---|---|---|
| | farm/fight/macro/bug | | | | |

## Orden

1. ...   (razón: el hueco más grande / la más barata de probar / desbloquea otras)
2. ...
3. ...

Al terminar: `python3 tools/idea.py add "..." --kind ... --source "brainstorm <fecha>" --hypothesis "..." --owner ...` por cada
idea de la lista, en ese orden; máximo 3 en desarrollo por persona.
