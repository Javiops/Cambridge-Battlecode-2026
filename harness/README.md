# Harness de desarrollo: cómo pasa una idea a ser bot

Cuatro etapas, cada una con una puerta con números. Nada entra en la siguiente etapa sin pasar la puerta, y todo
lo que pasa por aquí queda apuntado en el tablero ([IDEAS.md](IDEAS.md)) con su etapa y su resultado.

```
 1. brainstorm  ──►  2. desarrollo + test local  ──►  3. online (horas, ranked + 30 retos/hora)  ──►  4. disección
    ideas con            una idea = una rama,            A/B emparejado contra los mismos             ficha de métricas
    hipótesis            tools/gate.py decide             30 equipos, online/lfl.py decide              y propuestas ──► 1.
```

Todo son órdenes de una línea que ya existen en el repo; este documento dice cuándo se lanza cada una, qué número
tiene que salir para seguir y dónde se guarda lo que produce.

## Reglas de la casa

1. **Una idea, una rama, un cambio.** Rama `idea/I012-nombre-corto`, editando el bot actual en su sitio
   (`bots/study28/src`, nunca una copia nueva en `bots/`: así el diff del PR es el cambio y nada más). Para probar la
   idea contra la base, `gate.py` exporta sola la versión de `main` (`python3 tools/gate.py bots/study28 main ...`).
2. **El bot online solo cambia con una idea en etapa `local-ok`**, apuntada en el tablero, y como mucho una vez por
   hora (cada hora online es una muestra de 150 partidas; dos cambios en la misma hora no se pueden separar).
3. **Lo que decide es la puerta, no la sensación.** Un resultado sin su `gate.txt` (local) o sin su salida de
   `lfl.py` (online) no es un resultado. Los números de las puertas están abajo; si una idea no los alcanza, se queda
   en su etapa o se cierra como `rechazada` con el número que la cerró.
4. **El trabajo del compañero no se toca.** Cada uno trabaja en su rama y pasa sus ideas por la misma puerta; las
   ideas se combinan en la etapa 2 (ver "combinaciones"), nunca editando la rama de otro.
5. **Todo al tablero.** `python3 tools/idea.py add|set` en cada cambio de etapa. El tablero es lo que lee el
   coordinador para el resumen de la hora y lo que mira cualquiera para saber en qué estamos.
6. **Máximo 3 ideas en `desarrollo`/`test-local` por persona.** Con más, nadie termina ninguna.

## Etapa 1: brainstorm

**Entra:** la última ficha de disección (`online/data/dissect/<versión>/ficha.md`, etapa 4), la salida de
`lfl.py` de la última idea online, los estudios de los equipos top (`/mnt/project-files/analysis/`, resumen en
[current-state/](../current-state/README.md)) y lo que ya se probó (sección "Cerradas" del tablero: no repetir).

**Sale:** ideas en el tablero con hipótesis medible. Plantilla: [templates/brainstorm.md](templates/brainstorm.md).

```bash
python3 tools/idea.py add "Dos campeones por campamento en mapas de pelea" --kind fight \
    --source "ficha corners fix 15/10: 22% de golpes sin aliado a 8" \
    --hypothesis "golpes recibidos sin aliado a 8 del 22% al 12%; muertes/partida de 5.5 a 4.5 en corners/collision/packs"
```

Reglas: cada idea nombra **qué número de la ficha mueve y cuánto** (si no se puede medir, no es una idea, es una
opinión); dice **en qué mapas** aplica; es **un solo cambio** (una regla, un umbral, un interruptor). Una
combinación de ideas es otra idea, y se abre solo cuando sus partes ya tienen resultado.

**Puerta para pasar a desarrollo:** hipótesis con número, tipo (`farm`/`fight`/`macro`/`bug`), alguien asignado
(`--owner`). El que la coge la pasa a `desarrollo` con su rama.

## Etapa 2: desarrollo y test local

Un "subagente" es quien coge la idea: una persona o un hilo de Claude. Recibe el brief de
[templates/brief.md](templates/brief.md) (idea, hipótesis, bot base, puerta que tiene que pasar, qué entregar) y
no se sale de él: hacer que **su** idea funcione, no mejorar el bot en general.

```bash
git checkout -b idea/I012-dos-por-campo main
python3 tools/idea.py set I012 --stage desarrollo --branch idea/I012-dos-por-campo --owner Javi
#   ... editar bots/study28/src (switch P_* en params.h si es un umbral: tools/variante.sh sirve para probar valores)
python3 tools/gate.py bots/study28 main --kind fight --idea I012        # la puerta; ~1-3 min con 4 núcleos
```

`gate.py` corre por fases, de la más barata a la más cara, y para en cuanto el resultado está claro:

| fase | qué juega | para si | tiempo (4 núcleos, caché caliente) |
|---|---|---|---|
| 1 seguridad | 9 oficiales x 2 lados + combustible en lanes/corners/collision | fallos del bot > 0, partida rota, o +30 turnos sin combustible sobre la base | 20 s |
| 2 mapas nuevos | hold60 + dev200 (+ `--extra fresh300`) barajados, en tandas de 40, mapas ganados **por los dos lados** | peor con p<0.05 (cualquiera); mejor con p<0.01 (farm) | 10 s por tanda |
| 3 panel | spar11/12/16 (los únicos rivales locales que matan como online) en oficiales + gen | las partidas que cambian van en contra con p<0.05 = **veto** | 60 s |
| 4 contraejemplos | lista de los mapas nuevos perdidos por los dos lados, con la orden para verlos | siempre se escribe | 0 |

**Puerta a `local-ok`:**

| tipo | mapas nuevos (fase 2) | seguridad | panel |
|---|---|---|---|
| `farm` / `macro` | a favor con **p<0.05** (unos +6 mapas netos en 44 decididos, +10 en 100) | limpia | sin veto |
| `fight` | **no peor** (p≥0.05): local no puede juzgar una regla de pelea (es self-play, ver `cambc-online-ab`) | limpia | sin veto |
| `bug` | no peor | limpia y el bug ya no se reproduce en su contraejemplo | sin veto |

El veredicto sale solo (`PASA` / `NO PASA` y por qué) y queda en `out/gate/<cand>_vs_<base>/gate.txt`,
`result.json` y `contraejemplos.md`; con `--idea` se apunta en el tablero.

Reglas de la fase:
- **Contraejemplos antes de celebrar.** Antes de pasar a `local-ok` se miran los 3 peores contraejemplos con
  `cambc view` y se escribe una línea por cada uno en el doc de la idea (por qué pierde ahí y si importa).
- **Tiempo.** La caché (`out/ab-cache`, `out/wasmtime-cache`) hace que la base y el panel no se repitan: el segundo
  candidato cuesta solo sus partidas. `--max-maps 80` para una primera mirada; la puerta completa para decidir.
  Nunca se ajusta un umbral mirando hold60/dev200 (son la comprobación sellada); para ajustar, `maps_gen` o `--extra`.
- **Seguridad** = fallos del bot (`botFaults`), partidas rotas, combustible (`tools/replaydump.js` cuenta los turnos
  tipo 26), y el bot no escanea todos los campamentos o campeones por turno (memoria `cambc-fuel-budget`).
- **Combinaciones.** Una combinación (dos switches, dos ramas fusionadas) pasa la misma puerta **contra la mejor de
  sus partes**, no contra la base: si no gana a la mejor parte, se queda con la parte.
- **Lo que local no ve**: cómo pelean los equipos top. Por eso una regla de pelea con `PASA` local está en `local-ok`,
  no en `aceptada`; la decide la etapa 3.

**Entrega de la etapa:** PR con el diff del bot + `docs/<I012-nombre>.md` según
[templates/resultado.md](templates/resultado.md) (hipótesis, cambio, tabla de la puerta, contraejemplos mirados). El
PR no se fusiona hasta la decisión online (etapa 3), salvo `bug` e `infra`.

## Etapa 3: online (varias horas, ranked + 30 retos por hora)

Solo entra una idea en `local-ok`. Quien sube es siempre una persona (subir y activar en la web es una acción en
vivo): el bot se empaqueta, se sube, se activa y se registra la versión en el mismo minuto.

```bash
cambc bundle bots/study28 --output /mnt/project-files/bot/mybot_I012.zip   # 1. zip (en el repo, en la rama de la idea)
#   2. subir y ACTIVAR en 2026a.battlecode.co.uk (persona)
python3 online/version.py "v38 = I012 dos por campo"                        # 3. desde ese minuto las partidas son de I012
python3 tools/idea.py set I012 --stage online --version "v38"
```

El bucle de retos (`online/loop.py --top 30`, o la tarea programada de las :46 UTC que ya corre) gasta los 30 grupos
de la hora contra los mismos 30 equipos del top; `collect.py` baja los resultados. **Protocolo A/B:** la candidata y
la base se alternan hora a hora (A, B, A, B...), mínimo **2 horas cada una** (unas 300 partidas y ~200 parejas
rival+mapa compartidas); cada batch se compara en cuanto llega:

```bash
cd online && python3 collect.py && python3 lfl.py --a "I012" --b "study27" --idea I012
```

`lfl.py` cuenta solo las parejas (rival, mapa, lado) jugadas con las dos versiones (el motor es determinista: la
pareja es un experimento controlado) y hace el test de signos sobre las que cambian de resultado. El porcentaje
bruto de un batch **no vale** (hoy fue del 25% al 41% sin tocar el bot: cambia el sorteo de rivales).

**Puerta:**

| resultado de `lfl.py` | decisión |
|---|---|
| A mejor con p<0.05 | `aceptada`: la rama se fusiona en `main` (rename + diff, nunca copia nueva), queda como bot online |
| A peor con p<0.05 | `rechazada` con el número; vuelve la base a la web en la siguiente hora |
| sin decidir tras 3 horas de cada una (6 batches) | `rechazada` como "no cambia nada" salvo que sea `farm` con `PASA` local claro: entonces `aceptada` como neutra (el farmeo sí se mide bien en local) |

Mientras tanto, los ranked de la ventana (unos 20 por hora) son solo una comprobación de que no se hunde: con 20
partidas por hora no deciden nada. Mirar también `faults` de `games.jsonl`: un fallo del bot online es `rechazada`
al momento, sea cual sea el marcador.

Reglas: no se sube otra idea mientras una está en etapa 3 (se mezclarían las muestras); si la cookie caduca
(`challenge.py` da 401), la persona la renueva (README de `online/`) y la hora perdida no cuenta.

## Etapa 4: disección y nuevas ideas

Cuando una idea termina su etapa 3 (o cada mañana con la versión activa), la ficha:

```bash
cd online && python3 collect.py && python3 dissect.py --version "I012" --ref "study27" --idea I012
```

`dissect.py` baja las repeticiones que faltan, las decodifica (unos 25 s por partida nueva, 4 a la vez, con caché) y
escribe `data/dissect/<versión>-<fecha>/ficha.md`: la misma métrica para nosotros y para el rival en las mismas
partidas (muertes y cómo morimos, rondas muerto/inactivo, capturas por ronda-campeón, contacto antes del primer golpe,
aperturas en solitario, hechizos, combustible), por mapa y por nivel de rival, con la columna de la versión anterior
si se pide `--ref`. La ficha termina en **Propuestas**: los huecos más grandes respecto al rival, en frases que van
directas a `idea.py add`. Con eso se vuelve a la etapa 1.

Para preguntas más finas (por qué morimos en corners, qué hace el rival en lanes) el workspace que deja `dissect.py`
(`selected.json`, `steps/`, `mapsj/`) es el mismo formato que usan los scripts de
`/mnt/project-files/analysis/v35-dissection-2026-10-15/scripts_*` (`WS=<carpeta>`); el análisis largo se guarda en
`/mnt/project-files/analysis/<tema>-<fecha>/README.md` y se enlaza desde la idea.

## Quién hace qué

| | brainstorm | desarrollo + local | online | disección |
|---|---|---|---|---|
| Javi | decide qué ideas entran y su orden; asigna | sus ideas por la puerta | sube, activa, registra la versión; decide con `lfl.py` | lee la ficha |
| compañero | propone con hipótesis | sus ideas por la misma puerta, en su rama | igual, cuando tiene el bot activo | |
| hilos de Claude | proponen desde la ficha y los estudios | un hilo por idea con el brief; entrega PR + doc + gate.txt | el hilo del bucle manda los retos y pasa `lfl.py` cada hora | `dissect.py` y las preguntas finas |
| coordinador | | resume el tablero en el proyecto (ideas por etapa, última que cambió) | avisa cuando `lfl.py` decide | |

## Dónde vive cada cosa

| qué | dónde |
|---|---|
| tablero de ideas | `harness/ideas/I###.json` (uno por idea, se fusiona sin conflictos) y `harness/IDEAS.md` (generado: `idea.py board`) |
| bot actual | `bots/study28/src` en `main`; versión online en `online/data/versions.jsonl` |
| puerta local | `tools/gate.py`, resultados en `out/gate/<cand>_vs_<base>/` (gate.txt, result.json, contraejemplos.md); A/B suelto: `tools/ab.py` |
| mapas | `maps/` oficiales (cambc init), `maps_gen` (entrenamiento), `maps_hold60` + `maps_dev200` (sellados, deciden), `/mnt/project-files/arena/maps/fresh300` (`--extra`) |
| rivales de panel | `bots/spar11`, `spar12`, `spar16` |
| online | `online/` (collect, challenge, loop, report, lfl, version, dissect); datos en `online/data/` (en la nube: `/mnt/project-files/online/data/`, `games.jsonl`, `hourly.md`, `versions.jsonl`) |
| zips subidos | `/mnt/project-files/bot/mybot_<idea>.zip` |
| fichas de disección | `online/data/dissect/<versión>-<fecha>/ficha.md` |
| análisis largos | `/mnt/project-files/analysis/<tema>-<fecha>/README.md` |
| doc de cada versión | `docs/<I###-nombre>.md` (plantilla `harness/templates/resultado.md`) |
| memoria del equipo (lecciones) | memoria del proyecto (`cambc-eval-method`, `cambc-online-ab`, `cambc-fuel-budget`...) |

## Montar el entorno (una vez)

```bash
pip install cambc && cambc init --yes          # SDK, toolchain, 9 mapas oficiales en maps/
cambc build bots/study28 && cambc build bots/spar11 bots/spar12 bots/spar16
python3 tools/gate.py bots/study28 bots/study25 --kind farm --max-maps 40   # prueba: ~40 s, debe decir "a favor pero sin decidir"
```
En la nube, si `cambc init` no puede bajar la toolchain (certificado), se descarga a mano en `~/.cache/cambc/`
(`wasi-sdk-33`, `cmake-3.31.8-linux-x86_64`, `ninja-1.12.1-linux-x86_64`) y se repite.
