# Traspaso del proyecto Cambridge Battlecode 2026 (segundo)

Escrito el 26-10-2026 a las 20:05 (hora de Madrid, reloj del PC) por la sesión coordinadora del escritorio en el PC del usuario. Sustituye al traspaso del 25-10 (`handoff/HANDOFF.md`), que sigue valiendo como historia. Está en español porque el usuario escribe en español.

Qué hay en esta carpeta (`handoff2/`):

- `HANDOFF.md`: este documento.
- `memory/`: copia íntegra de la memoria del proyecto tal como está hoy en el PC. `memory/MEMORY.md` es el índice. **Léela entera antes de empezar**: son reglas del usuario y aprendizajes, y valen como si los dijera él.
- `sesiones/README.md`: resumen de cada sesión local de estos dos días (qué hizo, dónde dejó sus ficheros, en qué punto quedó y su id para reabrirla).

No contiene cookies, contraseñas ni tokens. Las transcripciones de las sesiones **no** se exportan: en la de la coordinadora el usuario pegó una vez la cookie del sitio, y por eso ninguna transcripción va a git.

---

## 1. Objetivo y calendario

- **Objetivo:** **top 10** en el torneo del **4-11-2026**. El bot tiene que estar terminado el **3-11**, y **desde el 30-10 no se empiezan ideas nuevas**.
- **Puesto:** 82º el 26-10 por la tarde, con kvvl (v164) activo en ranked. En el ranked solo se juegan rivales cercanos; perder elo probando candidatos no importa.
- **Sitio:** 2026a.battlecode.co.uk. **Desde el 26-10 hacia las 00:15 el motor es 2.0.0** (CLI `cambc` 4.0.0). Trae objetos nuevos (84 tipos), nerfs a nuestro draft (Vesper, Marcella, HoR, Ryth) y un pool de 70 mapas. Todas las referencias medidas con el motor 1.0.3 están anuladas. Detalle en `memory/cambc-patch-2-0-0-1026.md`.
- **Cuota online:** 50 grupos por hora en ventana móvil; un grupo son 5 partidas.

## 2. Reglas del usuario (lo nuevo de estos dos días; el resto está en `memory/` con su fecha)

- **Idioma y horas:** español, con horas de Madrid según el reloj del PC (desde el 25-10, UTC+1).
- **Informes:**
  - pocos («no me comentes tanto, todo tuyo»): solo veredictos online, decisiones suyas o problemas;
  - no escribir «sigo» en cada mensaje;
  - **solo contar lo confirmado**; si no se sabe, «no lo sé».
- **Causas, no síntomas** (25-10): buscar la variable oculta que hace que las decisiones del top 10 les funcionen.
- **Regla de copiar X** (25-10): si copiamos X del top 5 y no funciona, X no era el problema. Hay que ir a fondo, no a lo superficial.
- **Promoción** (25-10 19:18): una candidata solo se promueve si pasa la barra en el loop online contra **los 15 equipos de delante**, y con palabras del usuario. Barra: (a favor − en contra) ≥ 2·√(partidas cambiadas).
- **Juez:** online es el juez. El banco local solo sirve para descartar builds rotos o predecir, y está **sesgado** (ver sección 5).
- **26-10 por la tarde:**
  - «tryhardea esto, hazlo tú, no lo mandes a otro hilo»;
  - después «shoot big», rehacer el módulo de pelea entero y coordinado;
  - por último: **«manda un hilo con un plan detallado, no voy a iterar sobre el plan, tiene que gamblear a que ML funcione»**. Eso es la sesión ML de la sección 4.
- **El usuario está de muy mal humor con el progreso.** Dos días de arreglos que no se notan online. No le prometas resultados; dale cifras online.

Seguridad (obligatorio):

- **Cookie del sitio:** está en `C:\Users\Javier\.cambc_cookie`. Todas las sesiones la leen con `session_cookie()` de `lab\loop\common.py`. **Nunca se imprime, se copia ni se sube.** Claude no la escribe en ficheros: si hay que renovarla, la guarda el usuario.
- **Solo la sesión «Loop online en el PC» cambia el estado del sitio** (subidas, activaciones, retos) y **solo ella baja repeticiones**. Las demás se lo piden por SendMessage, con la ruta del zip, el sha256, los bytes y el marcador en stdout. Los resúmenes por API (`lab\eval\sumchain.py`) sí puede leerlos cualquiera.
- **Git:** nada de push sin que lo pida el usuario. No tocar la rama de `C:\Users\Javier\Cambc2026\repo` (granja GA antigua).

## 3. Estado a las 20:00 del 26-10

**En ranked:** kvvl v164 (`k_vvl_mgwp`, sha256 ae22c3f2…). No se ha promovido nada.

**La brújula del top 5 (t5b):** 25 grupos fijados contra los 5 primeros (125 partidas), motor 2.0.0. La referencia de kvvl es **5-120**. Como el sitio es determinista, cada candidata se juega sola en esos grupos y se compara partida a partida.

| Candidata (versión del sitio) | Qué es | t5b | Frente a kvvl | Frente a E1 |
|---|---|---|---|---|
| kvvl v164 | bot en ranked | 5-120 | — | — |
| c95hl150 | c95shop + oro hasta r150 | 5-120 | 0 | — |
| c95go45 (v181) | c95shop + peso del oro 0,45 en la apertura | 7-118 | +2 | — |
| go45sup (v182) | go45 + superioridad local | 5-120 | 0 | — |
| **go45e1 = E1 (v183)** | go45 + o100 (daño recibido ×0,5 en choose_target) | **11-114** | +6 (barra 8) | base |
| **e1foco (v184)** | E1 + punto de disparo único o96/o107/o108 | **14-111** | **+9 (barra 8,2): PASA** | +3 (4-1) |
| e1corte (v185) | E1 + corte o95 para todos | 10-115 | +5 | −1 |
| e1fctl (v186) | E1 + controlador de pelea de Peleas | 7-118 | +2 | −4 |
| co_v7 (v187) | E1 + o201 + o205 + o206 + o207 (coordinador) | 8-117 | +3 | −3 |
| e1hp (v188) | E1 + o213 (Marcella y Vendetta compran vida primero) | 7-118 | +2 | −4 |

**e1foco contra los 15 de delante** (puestos 67-81, cadenas c30-c33, 285 parejas): 116-169 frente al 122-163 de kvvl. A favor 41, en contra 47: **−6, barra 18,8 → no pasa.** Entrega más gemas, pero las parejas que cambian las decide quién muere más en r1-300. No se promueve.

**El diagnóstico que queda en pie** (juez online `lab\top10\scripts\juez_t5b.py`, E1 frente al top 5):

| Medida | Nosotros (E1) | Top 5 |
|---|---|---|
| Peleas igualadas: mata / muere por pelea (r21-100) | 0,29 / 0,67 | 0,67 / 0,29 |
| Daño que acaba en una baja | 21 % | 45-51 % |
| El herido (quien más daño recibe) muere | 39 % | 12 % |
| Muere después de irse | 22 % | 7 % |
| Aliados a ≤4 al irse | 0,49 | 0,83 |
| Muertes r101-300 por partida | 2,36 | 0,69 |
| Oro de bajas en contra (r1-300) | 291 | 78 |

- El 52 % de nuestras muertes son en inferioridad. Con un aliado a ≤5, morimos el 15-20 %; ellos, el 3 %.
- Por ronda de contacto hacemos casi el mismo daño. Los porcentajes de golpe, el uso de habilidades y los cambios entre entrar y salir (14,7 frente a 14,8 por 100 rondas) son parecidos.
- Su vida máxima es mayor desde r200, por los objetos. El escudo de su HoR absorbe 2.651 por partida y el del nuestro 1.142.
- **Ninguna de las piezas probadas ha movido el 3 a 1** (ver sección 6). La causa sigue sin aislar.

## 4. Lo que está en marcha: la sesión ML (la apuesta del usuario)

Sesión **«ML: optimizar y aprender la pelea del bot (UPV)»**, id `local_a95718dc-d977-4619-839a-31ea3332d097`. Trabaja en `C:\Users\Javier\Cambc2026\lab\ml\`:
- registro: `INFORME.md`;
- petición de cómputo para la UPV: `PITCH_UPV.md`;
- detalle: `memory/cambc-ml-lab-1026.md`.

La UPV va a dejar instalaciones para ML. Aún no se sabe cuántos núcleos ni GPU; el usuario dijo «asume un buen escenario». Todo es portable a Linux (`setup_linux.sh`, variables ML_*).

**Infraestructura:**
- `runner.py`: partidas en paralelo con resultados en sqlite. Las partidas son deterministas y se juegan una sola vez.
- `build.py`: vector de parámetros → `params.h` + `ml_gen.h` → WASM, con unos 15 s por build y caché.
- `space.py`: 105 variables continuas y 87 categóricas (planes de tienda por campeón y draft).
- Base `mlv7`: co_v7 con 12 constantes de pelea expuestas.

**Fases:**
- **Fase 1 (CMA-ES):**
  - Pool de 6 rivales (e1, co_v7, kvvl, rTop1, c95shop, e1fctl), 420 partidas por candidata y 10 mapas reservados.
  - La generación 0 (p1) salió mal: mediana 0,41 frente a 0,57 del vector por defecto. Se relanzó como p1b y luego p1c, con mutaciones más suaves y los parámetros del escudo de HoR.
  - Unos 75 minutos por generación en este PC (2,6 partidas por segundo).
- **Fase 2 (imitación del top 5) — no transfiere:**
  - Datos: 2,4 M muestras, 1,3 M del top 5, más las 715 partidas del top 5 contra otros equipos que bajó el loop (`lab\eval\t10out\ml_t5vs_1.json`).
  - Una MLP acierta el movimiento el 46 % de las veces (la clase más frecuente, el 35 %).
  - El clon de acciones gana 7-13 de 140 partidas a E1; la postura clonada, 21-39. El sparring «rT5» no entra al pool.
- **Q offline:** recompensa = bajas − muertes a 10 rondas, R² 0,41. Lo mejor dentro del bot (con sesgo hacia farmear) gana 71 de 140 a E1, por debajo de co_v7 (79). Empaquetó `ml q1d10`, pero no lo mandó al loop.
- **Fase 3 (OpenAI-ES sobre la red de pelea):** n1 en marcha desde la tarde, arrancando de los pesos de imitación.
- **Fase 4:** las candidatas van a la brújula t5b a través del loop. A las 20:00 todavía no ha mandado ninguna.

**Siguiente paso de la nueva sesión:** reabrir la sesión ML, leer su `INFORME.md` y dejarla seguir. Pídele los datos de la UPV al usuario en cuanto los tenga.

## 5. Herramientas y datos en el PC (`C:\Users\Javier\Cambc2026\`)

Todo vive en el PC; no está en git salvo este traspaso.

- **Python:**
  - `lab3\Scripts\python.exe`: Python 3.14, que hace de intérprete para los scripts;
  - `lab4\Scripts\cambc.exe`: CLI 4.0.0 del motor 2.0.0;
  - `lab4\viewer\ext.py`: decodificador de repeticiones al formato dec2 (rondas, posiciones, vida, cooldowns, daño por actor, tipos de acción).
  - Ejecuta los scripts con `-I`.
- **Loop online** (`lab\loop\`):
  - scripts: `queue.py` (cola), `cand.py` (candidata sola en grupos fijados), `post.py` (vuelta a v164 + control), `fetch_replays.py`, `cmp_ref.py`, `mk_t5b.py`;
  - datos y registros: `data\`, con `t5b_<tag>.out`;
  - repeticiones: `replays\t5b\<tag>\`, con `team-?.stdout`, `.fuel`, `.debug` y `replay.repl26a`;
  - informe: `INFORME.md`.
- **Evaluación** (`lab\eval\`):
  - `sumchain.py` (resúmenes por API → `online2\<cadena>\<tag>\`);
  - `loopdec.py` (decodifica → `t10dec\`, listas `t10out\loop_<cadena>_<tag>.json`);
  - informes en `runs\` e `INFORME.md`.
- **Análisis del top 10** (`lab\top10\scripts\`): `juez_t5b.py` (juez online de peleas, una tabla), `wounded.py`, `eqbrief.py`, `fronts`…
- **Banco local** (`lab\peleas4\`):
  - `run.py BOT RIVALES --all --jobs 14 [--rounds R --logs RE --keep]`;
  - `sum4.py --pair`, `dec2local.py`, `fuelturns4.py`, `mlog_patch.py` (registro de modo por ronda);
  - parches en `opts\`, bots en `bots\`, wasm en `wasm\`, zips en `zips\`.
  - Hace 140 partidas completas en unos 90 s con 14 procesos.
- **Scripts del coordinador** (`lab\coord\`):
  - contraste partida a partida con el top 5: `canhit.py`, `spots.py`, `dps.py`, `reinf.py`, `killers.py`, `travel_dash.py`, `dashengage.py`, `recalls.py`, `builds2.py` (objetos del motor 2.0.0);
  - traza ronda a ronda: `r100.py`, `ftrace.py`, `gtrace.py`;
  - filas para clonar comportamiento: `bc_extract.py`, `bc_tree.py`;
  - parches propios en `opts\` (o200-o213, `fight2.h`); zips en `zips\`.
- **Farmeo** (`lab\farmeo\`): zips c95go45* e `INFORME.md`.
- **Banco J2 antiguo** (`lab\j2\`, motor 1.0.3): ya no vale para el 2.0.0.

**Sesgos del banco local, medidos:**
- Todos los rivales locales salen de nuestro código. Incluso rTop1, que es V18 + D1 + D2.
- E1 gana el 79 % de los mapas medios en local, así que casi cualquier cambio sale «peor en medios» (regresión a la media).
- Las comparaciones contra la propia base se explotan a sí mismas: co_cA ganó 86 de 140 a co_v4 pero solo 78 a E1.
- Varias mejoras locales no se notaron online (o108, corte), y otras locales negativas no fueron peores online.

## 6. Hallazgos y piezas de estos dos días (qué se probó y qué pasó)

**Reglas del motor confirmadas** (en `memory/cambc-vesper-step-reset-1026.md` y `cambc-ml-lab-1026.md`):
- **Movimiento y ataque:**
  - un campeón a distancia **o se mueve o ataca** en un turno;
  - el reinicio de ataque (habilidad de Vesper) devuelve el ataque tras el paso, y el dash lo conserva;
  - el cuerpo a cuerpo puede dar paso y golpe;
  - alcance básico: 1 el cuerpo a cuerpo, 3 los de distancia; el dash llega a 2 casillas.
- **Turnos y visión:**
  - dentro de una ronda los campeones juegan por orden de índice;
  - un bot no puede leer a aliados fuera de su visión.
- **Recursos y determinismo:**
  - memoria compartida de 8 bytes, casi llena (reclamaciones, caché y peligro);
  - combustible: unos 100k por turno; el primer turno, 2x; el del draft, 100x;
  - el bot es determinista: `fuel_ok` es un stub y no lee el combustible.

**Pruebas online contra el top 5** (todas en la tabla de la sección 3):
- **c95go45 / E1:** valorar más los grupos ricos (alce + gemas) en la apertura y abaratar el daño que reciben; es lo único que mejoró la brújula. E1 iguala al top 5 en daño a alce + gemas + oro en r1-100.
- **e1foco:** pasó la brújula del top 5, pero no los 15 de delante. El mecanismo de foco no cambió online: convergencia de 79 % a 82 %. Su +3 sobre E1 es compatible con suerte.
- **Sin efecto en el resultado:**
  - corte de los heridos (o109): el herido sigue muriendo el 35 %;
  - controlador de pelea (o111): baja las muertes, pero hunde los disparos de Vesper;
  - mecánicas copiadas en co_v7: Vesper da el paso con reinicio + disparo (de 3 % a 8 % de disparos a alcance+1; el top 5 tiene 19 %), HoR viaja con el dash (de 0,3 a 9,1 por partida), y el cuerpo a cuerpo abre y remata con dash (de 19 a 36 por 1.000 rondas; ellos, ~80);
  - compras de vida (o213): la vida máxima ya está igual que la suya.

**Probado solo en local y descartado:**
- arranque desde r1: el primer golpe no cambia;
- trío al alce: más muertes por campamento;
- foco de equipo (o107/o108): no sube el foco en local;
- retirada hacia aliados (o110): de 27 a 88 en local;
- pv durante toda la partida: deja peleas ganadas (5-29 en medios);
- módulo fight2 hecho de cero por el coordinador: pierde contra E1, 49-67 de 140;
- capas de ayuda (o211) y cobertura (o212): neutras;
- barrido de 37 parámetros de pelea: nada fuera del ruido. Quitar horfocus, team-fight o bcf empeora mucho, así que esas reglas sí sirven.

**Contraste de decisiones, mismas situaciones** (`lab\coord\bc_contrast.py`):
- con ventaja de vida cerca, el top 5 se acerca entre 6 y 12 puntos más que nosotros;
- igualado o por detrás, se va más;
- su herido no huye si su equipo va ganando;
- a 3-4 casillas, sus campeones a distancia pegan el 39 % de las rondas y los nuestros el 20 %.

## 7. Sesiones locales (detalle en `sesiones/README.md`)

Todas en `C:\Users\Javier\Cambc2026`, en modo auto, arrancadas por la coordinadora. A las 20:00 solo trabaja la sesión ML; el resto está en espera.

| Sesión | Id | Estado |
|---|---|---|
| ML: optimizar y aprender la pelea del bot (UPV) | local_a95718dc-d977-4619-839a-31ea3332d097 | En marcha (fases 1 y 3). Es la apuesta. |
| Loop online en el PC | local_aa12b548-0edc-4d79-b52c-8c72c9ed3efb | Cola vacía, v164 activa. Único que toca el sitio. |
| Peleas sobre la base determinista | local_61ed6f3b-ad46-45d2-9cf5-eb0540f864cc | En espera; no toca el controlador por orden del coordinador. |
| Evaluador de nuestras partidas | local_a91af4ae-a0ed-4c17-a15d-c2d0f7a95f01 | En espera (sumchain, wingap, metas r1-100). |
| Análisis del top 10 | local_96101b90-5ab6-46c1-8557-bbb277293da3 | En espera (juez_t5b, herido, invasiones). |
| Farmeo y macro sobre la base determinista | local_cbdea81d-6258-4a48-acbd-287381cebc06 | En espera (E1, e1focon100 aparcada). |
| Banco del PC (Juez 2) | local_f455491e-5c80-4da3-b2e5-1c78a3b8a765 | En espera; J2 del motor 1.0.3, sin uso. |

## 8. Zips clave y sha256

| Bot | Ruta | sha256 |
|---|---|---|
| kvvl v164 (ranked) | rama `claude/project-thread-dxkoko` `handoff/chain14/k_vvl_mgwp.zip`; fuente en `lab\j2\bots\k_vvl_mgwp` | ae22c3f2f80036acdda43a19c167c41c6e436077b127296c4dc157bf393c9787 |
| b35nohp | `lab\ffp\new-b35nohp.zip` | 84dedecf2480331d861da60900b6b57572978562e2e72d3f177a92061ad7b40b |
| c95shop | `lab\peleas\cut\c95shop.zip` | 51b22054aa1628ccfa73dd43e64002a818330218805df720588b01b767f4bbf9 |
| c95go45 | `lab\farmeo\zips\farmeo-c95go45.zip` | 7fbe33699f6e429130a6daa3771e8930bf5e03f6bd593772ba1b0c068b1543dc |
| **E1 = go45e1** (base de todo lo nuevo) | `lab\farmeo\zips\farmeo-c95go45e1.zip`; fuente en `lab\peleas4\bots\e1\src` | f967edfebc33692490a54033ef575908f96e82fc905b7f9e5a413e80b24187ed |
| **e1foco** (la mejor en t5b) | `lab\peleas4\zips\e1foco.zip` | 659ded194f6ae8c5122001fca9de8366583740dd51819e0d52c9df34dd975873 |
| e1corte | `lab\peleas4\zips\e1corte.zip` | 5659cf497e7ec990ce5260b3cc72acb19a4d7befd32629b677c565c336b2a8f8 |
| e1fctl | `lab\peleas4\zips\e1fctl.zip` | cf1e7432ac6802202a4369c772f7e7bc407fb658f00615d49a94f1d2afb68733 |
| co_v7 | `lab\coord\zips\co_v7.zip`; fuente en `lab\peleas4\bots\co_v7\src` | 425b705a4505bd1c39d0e91ec0c5bfbc9acbbd2f83fee4ea390ccd72fd421b02 |
| e1hp | `lab\coord\zips\e1hp.zip` | 6d9737c65064300835454e8c4ad9ec5e40f8a9862982c4ab2b147bc1e0f4b2fb |

Antes de subir un zip, se añade un marcador a la línea `[fuelfit]` de `main.cpp` (`lab\coord\tagzip.py`). El loop comprueba el sha256, el tamaño, que los 27 ficheros fuente del sitio sean idénticos a los del zip y que el marcador salga en el stdout de la primera partida.

## 9. Cómo seguir

1. Lee `memory/` entera, empezando por `MEMORY.md`, `cambc-vesper-step-reset-1026.md`, `cambc-ml-lab-1026.md`, `cambc-plan-c97-1025.md` y `cambc-patch-2-0-0-1026.md`.
2. Si sigues en el mismo PC: las sesiones de la sección 7 siguen ahí. Reabre la coordinadora o crea una nueva, y continúa con la sesión ML (su `INFORME.md`).
3. Si estás en otra cuenta o en la nube:
   - todo lo de `lab\` está solo en el PC; pide al usuario Remote Control o que suba lo que necesites;
   - la cookie la tiene que poner el usuario en `C:\Users\Javier\.cambc_cookie`;
   - el loop solo funciona en el PC.
4. Siguiente decisión del usuario: qué candidata de ML va a la brújula t5b y, si pasa, a los 15 de delante. Hasta entonces, kvvl v164 sigue en ranked.
5. Fechas: ideas nuevas hasta el **30-10**, bot final el **3-11**.
