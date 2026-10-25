# Traspaso del proyecto Cambridge Battlecode 2026

Escrito el 25-10-2026 a las 13:00 UTC (14:00 en Madrid) para que una sesión nueva, en otra cuenta, siga exactamente desde aquí. Está en español porque el usuario escribe en español.

Qué hay en esta carpeta del repo (`handoff/` en la rama `claude/project-thread-880vzg`):

- `HANDOFF.md`: este documento.
- `memory/`: copia íntegra de la memoria del proyecto (214 ficheros, 1,1 MB). `memory/MEMORY.md` es el índice. La memoria del proyecto no viaja a otra cuenta, así que esta copia es la única.
- `threads/`: cada hilo del proyecto exportado a un `.md` (76 hilos, unos 8.600 mensajes) y el chat del proyecto en `threads/00_chat-del-proyecto.md`. `threads/README.md` es el índice, con estado, fechas y número de mensajes.

No contiene cookies, contraseñas ni tokens.

---

## 1. Objetivo y calendario

- **Objetivo del usuario:** acabar en el **top 10**. El resultado final sale de un **torneo aparte el 4-11-2026**, no del elo del ladder. Por eso el elo que se pierde probando candidatos online no importa (regla del usuario del 18-10).
- **Fechas:** bot terminado el **3-11-2026**. Desde el **30-10 no se empiezan ideas nuevas**. Subida final el 2-11, con el 3-11 de margen.
- **Puesto:** ha oscilado entre el 52 y el 78 del ladder estos días (52º con 1899 el 24-10 a las 21:34 UTC; 67º el 25-10 de madrugada). El usuario espera un salto grande, no piezas de +1%.
- **Sitio:** 2026a.battlecode.co.uk. Motor 1.0.3 (paquete `cambc` 3.0.5; la wheel está en la carpeta del proyecto). Pool de 40 mapas. Cuota de partidas no ranked: 50 grupos por hora; un lote son 25 grupos de 5 mapas.

## 2. Reglas del usuario (resumen; el detalle con fecha está en `memory/`)

Forma de trabajar:
- Escribe en español. Es medallista de olimpiadas y programador competitivo: quiere razonamiento serio, no relleno.
- Dar las horas en **hora de Madrid** (desde el 25-10 es UTC+1).
- **Solo contar lo que esté confirmado** por el último mensaje de un hilo, con su hora. Si no se sabe, decir "no lo sé". Nunca adivinar (se enfadó por esto el 22-10 y el 23-10).
- No cerrar ni resolver hilos por iniciativa propia.
- Ningún hilo debe quedarse parado. El loop online informa cada 15 minutos; si calla más de 20 minutos durante un lote, el coordinador lo persigue.
- Ciclo estándar sin preguntar: revisar, buscar la causa profunda, arreglar, filtro local, loop online.
- Causas de sistema entero; razonar por **características de mapa**, no por mapas concretos. Cambios **ambiciosos** y agrupados en candidatos combinados; lo más prometedor primero.
- Ficha de mecanismo obligatoria antes de juez local u online. No cerrar una línea con menos de 300 partidas.
- El código de cada campeón vive en su `<campeón>.h` (desde v20c, PR #47).
- Versionado en GitHub: una versión nueva es un cambio sobre la carpeta del bot actual (`git mv`), no una copia nueva, para que se vea el diff.
- Borrar repeticiones con las que no trabaje ningún Claude. La carpeta del proyecto tiene un límite de 50.000 ficheros y 10 GB, y cuando se llena las escrituras se pierden sin error.
- El usuario tiene permiso permanente para que se actualicen las bases del filtro local a cada base promovida, y ofrece su PC (C:\Users\Javier\Cambc2026).

Reglas del loop online (las más recientes mandan):
- **25-10 12:08 UTC:** **online es el juez** de cada pieza determinista. El juez local (J2) queda como predicción. Aun así, en local una candidata tiene que ganar al menos cara a cara a kvvl (v164): "no vamos a ser top 10 si nuestro bot no puede al menos derrocar al que tenemos actual".
- **25-10 11:48 UTC:** no relanzar siempre la base. Se manda **solo la candidata** sobre los grupos fijados de la última cadena y se compara con las partidas de la base ya jugadas. Funciona porque **las partidas online son deterministas** (comprobado el 24-10: 60 pares duplicados idénticos). Si las partidas de mapas lejanos dejan de ser idénticas, es que un rival cambió de bot.
- **25-10 12:12 UTC:** rivales = los **15 equipos justo por delante** (antes 25). Tras b15 se hace una única tirada de referencia de kvvl en esos 15 grupos (cadena 21) y luego cada candidata sola en ellos (unas 3 por hora).
- La candidata solo está activa durante su lote; al acabar vuelve **kvvl (v164)**, que está en ranked hasta que el usuario diga otra cosa.
- Comprobaciones de cada subida: el tamaño coincide con el zip local, la versión no queda cancelada, se espera a que compile y se active, y se busca el contador de la pieza en el stdout de la primera partida. Una sola copia del script de envío (hubo duplicados el 24-10).
- Barra para aprobar: (a favor − en contra) ≥ 2·√(partidas cambiadas). El usuario puede promover por debajo de la barra.
- Tras cada lote se bajan automáticamente las repeticiones de las parejas que cambian.
- **25-10 10:17 UTC:** todos los hilos construyen y miden sus piezas **sobre la base determinista**, no solo el hilo que la hace.

## 3. Estado actual (25-10, 12:50 UTC)

**Bots:**
- **Base promovida V20 = v139 "v6d"** (V19 + bcf-v3 solo para entrar en pelea + richcap-v2), promovida por el usuario el 23-10 a las 19:33 UTC. Zip: `/mnt/project-files/bundles/v6d.zip` (sha256 d4fa1cc5…).
- **En ranked: kvvl = v164** (`k_vvl_mgwp`: v20c-vk + v20c-vco + lshop-v1c + mgwp). Zip en la rama `claude/project-thread-dxkoko`, `handoff/chain14/k_vvl_mgwp.zip` (sha256 ae22c3f2…). Online: +1 en la cadena 14 y +4 en la 15 frente a V20. El torneo Sprint 2 sigue con V20 inscrita; el usuario dijo que no es relevante.
- **Bot determinista (línea principal desde el 24-10).** Problema: kvvl/V20 leen el fuel restante para decidir, así que cualquier recompilación cambia el 96% de las partidas y ninguna pieza se puede medir. El hilo "Encontrar la causa real del estancamiento" lo arregla con "fuelfit": que el peor turno quepa en el fuel para que ninguna decisión lea el fuel. Versiones b3…b37 en `claude/project-thread-jeb4pf`, `handoff/fuelfit/` (README, `opts/`, `applyopts.sh`, `SHA256SUMS`). También hay `kvvl-det8` (fuel simulado con un contador) en `handoff/det/`, que el usuario pidió no subir online.

**Resultados online del bot determinista** (todo en los 24 grupos fijados de la cadena 20, 120 partidas, comparado con kvvl):

| Versión | Cercanos (de 76) | Lejanos (de 44) | Neto frente a kvvl |
|---|---|---|---|
| kvvl v164 | 52 | 16 | — |
| b15 | 45 | 22 | −1 |
| b32 | 47 | 20 | −1 |
| b35 | 44 | 20 | −4 |

Además b27 ("V21") dio −7 frente a V20 en la cadena 19 (cercanos 32 frente a 37 de 81). Lo mismo en todas: **los deterministas ganan en lejanos y pierden en cercanos**, y lo que estropea los cercanos ya está en b15.

**Diagnóstico actual** (hilos de estancamiento y del PC, 25-10 12:00-12:20 UTC): la pérdida en cercanos es de **micro**. Los deterministas mueren peleando el campamento cuando llega el rival (modo fight-camp: 12 muertes frente a 3 de kvvl en c20), mueren antes (primera muerte en r66 frente a r87) y con gemas encima. El indicador local `handoff/fuelfit/tools/deathmode.py` lo reproduce en 800 partidas del Juez 2 (fight-camp en cercanos: kvvl 75, b15 91, b26 111, b32 109, b35 111). Sube en dos saltos:
1. kvvl → b15 (+16): entre fuelfit-a1 y b15 (b10, b12 = o52-o56 de farmeo, o13/o35).
2. b15 → b26 (+20): hitpass v6 (b24hp) y o59/o63. Sospechoso principal: **hitpass**, que decide cuándo seguir pegando al campamento.

**Siguiente paso (bisección):** ya están los zips `fuelfit-b26nohp`, `fuelfit-b35nohp` (hitpass apagado) y `fuelfit-b12` (commit 55d807d, 12:21 UTC). Plan: medirlos en el PC con deathmode y cara a cara contra kvvl, junto con b3 y det8 contra kvvl, y luego mandar online la que arregle fight-camp, sola en los 15 grupos de delante. En ese momento el loop esperaba cuota para la tirada de referencia de kvvl en los 15 de delante (cadena 21, prevista a las 13:53 hora de Madrid).

**Aviso:** a las 12:47 UTC del 25-10 la organización llegó a su **límite de gasto de uso extra**, y el hilo del loop se paró a mitad de turno con ese error. Seguramente le pasó lo mismo a otros hilos. El uso incluido del plan se renueva en unos 2 días (el error lo sitúa hacia el 27-10). En la cuenta nueva no hay nada en marcha: hay que relanzarlo todo.

## 4. Ramas y zips (repo `Javiops/cambridge-battlecode-2026`)

| Rama | Último commit | Qué contiene |
|---|---|---|
| `claude/project-thread-jeb4pf` | 55d807d (25-10 12:21 UTC) | Bot determinista: `handoff/fuelfit/` (fuelfit-a1, b3…b37, b26nohp, b35nohp, b12, `SHA256SUMS`, `opts/`, `tools/`, `sdk_costs.md`), `handoff/det/` (kvvl-det8, FICHA), `handoff/vendetta/` (vopen ve/vf). |
| `claude/project-thread-dxkoko` | 4b29e4d (25-10 10:37 UTC) | Puente con el PC: `bundles/` (kvvl-hitpass-v2, pelea-pA, pelea-v1a/b), `handoff/chain14/` (k_vvl_mgwp = kvvl, k_allwp = kall), `handoff/b32-fight/` (bd2c, bd4c, vin1, vin2 sobre b32), `handoff/buddy/`, `handoff/vin/`, `handoff/pelea/`, `handoff/pc/`, `handoff/pw3/`, `handoff/mgwp/`, `handoff/opening/`, `handoff/focus/`. |
| `claude/project-thread-jhnqzy` | 13ecf1a (25-10 12:45 UTC) | Farmeo sobre la base determinista: `handoff/fuelfit-farm/` (NOTES.md, zips incoming50-b35 y nohold-b35). |
| `main` | 9900461 (18-10) | Historial anterior (PR #37). El código de V20 y kvvl no está en main, sino en los zips. |
| `claude/project-thread-880vzg` | esta rama | Este traspaso. |

Hay unas 60 ramas más, antiguas (GA, estudios, compañero de equipo); se ven con `git ls-remote origin`.

sha256 de los zips clave (lista completa en cada `SHA256SUMS`):
- kvvl v164 `k_vvl_mgwp.zip`: ae22c3f2f80036acdda43a19c167c41c6e436077b127296c4dc157bf393c9787
- kall `k_allwp.zip`: 65e807d06e77b2b4a76f97c7df434410e8fa250ecad625aa1512947c16571bd0
- V20 `v6d.zip` (carpeta del proyecto): d4fa1cc51fd00724e89d4d460d6f861f95b09b4151078f7600977a2c9fb76ba8
- kvvl-det8: 897e84ee06f5248b053e648e94d2e0735e7b39b6773397db73a6ad2773240e7e
- b15: d314e7e40384b39e69f10467a3e5703c88c993d4d3aba064177f15e560178f9c
- b27 (V21): c285f4fa476b987487b493a8cbd700fbcd5e5ccce1f334b571664a47c50cee8d
- b32: 76d0a735cf3b6bd985cbcb3f627d2ac50146bf63765eb0708974f428d6e5014b
- b35: 537b38c92992ed4d8eac973a04985484f397ac8cfc70848fdc909d37f1cc683d
- b26nohp: 06ab527642ad4e7666e1e4eeccab4008bec3a0f4034353d395782662fea53c70
- b35nohp: 84dedecf2480331d861da60900b6b57572978562e2e72d3f177a92061ad7b40b
- b12: 4d212c40fab17b7449757e20c3f8ed6e3eb69a6ab79a2d035f238d16b5fc6cc4
- kvvl-hitpass-v2 (dxkoko 1bb5840): 6b2049d556b526ad23cd72487f633abd134ee175b8a2017adfccd8e41f19f8df

Linaje de bases: v96 goldval → v98 horfocus → v102 mate-dash → v105 stallfix → v110 need2 → v117 marc-bfill (V15) → v120 t10draft-v2 (V16) → v122 t10shop-v2 (V17) → v132 nightpack-v2 (V18) → v136 pack-v1w (V19) → v139 v6d (V20). Online, v140-v173 son candidatos (v164 = kvvl, v172 = b32, v173 = b35).

## 5. Dónde están los datos

Carpeta del proyecto `/mnt/project-files/` (9,3 GB, unos 41.900 ficheros):
- `bundles/` (30 MB, 324 zips): todos los bots subidos o probados.
- `bot/` (59 MB): fuentes y zips por versión (p. ej. `bot/far-b32/b35-fnc.zip`).
- `online/`: scripts del loop (`common.py`, `send_batch.py`, `draw_batch.py`, `collect.py`, `fetch_replays.py`, `fetch_summaries*.py`, `dissect*.py`, `judge.py`) y `online/data/` (803 MB): `games.jsonl`, `versions.jsonl`, `challenges.jsonl`, `loop_config.json` (`fight_rank_mode` = `ahead15`), `group_versions.json`, `groups/` (grupos fijados), `chain*_10xx/`, `c19_b27_changed37/`, `c20_b32_changed27/`, `t10_vs_band_1024/` (158 MB), `top10_1022/`, `replays/` (526 MB).
- `analysis/` (8,4 GB): análisis por línea. Lo vivo: `top10-micro-1023/dec300/` (40 partidas top 10 descifradas hasta r300), `top10-fresh-1025/`, `far-maps-1023/README.md`, `bc-top10-1023/`, `local-filter-1021/` (999 MB), `chain*-102x/` (unos 6 GB de repeticiones de cadenas).
- `docs/`, `harness/`, `tools/` (74 MB), `arena/` (56 MB), `next-pc/`, `next-strategy/`, `archive/MANIFEST.md`.
- La wheel `cambc-3.0.5-py3-none-manylinux_2_28_x86_64.whl`.

Fuera del proyecto:
- **PC Windows del usuario**, `C:\Users\Javier\Cambc2026\`: archivo definitivo de datos viejos en `archive\` (old2/, sum2/, mac/, con sha256 verificados). Ahí corre el Juez 2 de 800 partidas en unos 5 minutos, por Remote Control (hilo "Iterar rápido con el PC al 100%").
- **Repo privado `Javiops/cambc-archive`**: puente entre las sesiones en la nube y el PC (ficheros de menos de 100 MB). El PC tiene `gh` con sesión de Javiops, sin Python, y `core.autocrlf=true` (cuidado con los checksums de texto).
- **Mac** (`/Users/javier/Downloads/bot2_osc_dash_survival_v1/cambc-archive/`): primera copia del archivo, ya duplicada en el PC.
- **Datos públicos de partidas**: la API del sitio. En `draft` los ids no coinciden con `champion_type`: draft 0 ryth, 1 vesper, 2 vendetta, 3 cassi e issac, 4 stellar, 5 prism, 6 marcella, 7 willow, 8 ren, 9 varg, 10 tavi, 11 hor.

## 6. Método del loop y herramientas

- **Sesión del sitio:** el loop lee la cookie de navegador de `CAMBC_COOKIE`, del fichero de `CAMBC_COOKIE_FILE` o de `~/.cambc_cookie` (`online/common.py`). **No está en el repo ni en la carpeta del proyecto.** En la cuenta nueva, el usuario tiene que iniciar sesión otra vez y dar la cookie solo al hilo del loop. Nunca se adjunta ni se copia en otros sitios.
- **Red:** el entorno en la nube tiene que permitir el dominio 2026a.battlecode.co.uk (el 13-10 el usuario creó un entorno con ese dominio permitido). En la cuenta nueva hay que configurar un entorno igual.
- **Formato actual:** cada candidata sola en los grupos fijados (15 rivales justo por delante), comparada partida a partida con la referencia ya jugada. `pinq.sh` y `cmp_ref.py` estaban en el contenedor del hilo del loop, que es temporal; si no aparecen en `online/`, hay que reescribirlos a partir de `send_batch.py` y `judge.py`.
- **Juez local J2:** `scripts/judge2.py` (panel duro, lejanos ×0,42, rPun5 a-d), correlación 0,80 con online en 8 piezas viejas. Solo sirve para descartar builds rotos o predecir. Banco del PC: `pad.py` / `diffcount.py` (sonda +20 instrucciones = cuántas partidas cambian con ruido de fuel).
- **Herramientas fuelfit** (`handoff/fuelfit/tools/` en jeb4pf): `subq.sh`, `same.py` (repeticiones idénticas byte a byte), `divloc.py` (ronda de divergencia), `restarts.py`, `deathmode.py` (muertes por modo), perfiles de fuel. El simulador admite fuel ilimitado (`--fuel-quantum`) para comprobaciones de identidad exacta.
- **Reglas para portar una pieza al determinista:** no leer fuel (`fuel_ok` es un stub), nada de trabajo nuevo en el turno 1 (en muchos mapas ya está en el tope de 200k), nada de BFS en r2 en mapas grandes, trabajo pesado en rondas fijas. Con fuel ilimitado, una función bool que se sale sin `return` provoca un trap de wasm y el motor reinicia al campeón.

## 7. Líneas abiertas por hilo

| Hilo | Estado y siguiente paso |
|---|---|
| **Encontrar la causa real del estancamiento** (dueño del bot determinista) | Bisección de fight-camp: b26nohp, b35nohp y b12 subidos. Siguiente: medirlos en el PC y mandar online la que baje las muertes fight-camp en cercanos. Pendiente: mapas que aún empiezan en r3 (monolith, quadrants, lost_world, yellow_brick_road, the_farm, elk_arena, boss_battle, corners, stampede). |
| **Dissect the top 2 teams** (loop online, único con la cookie) | b15 juzgada (−1). Pasaba a 15 rivales: referencia kvvl (cadena 21) y luego candidatas solas. Bajando 80 partidas públicas del top 10 para "Comprobar si las stats…". Se paró por el límite de gasto a las 12:47 UTC. |
| **Iterar rápido con el PC al 100%** (Remote Control en el PC) | Muertes por modo medidas (tabla de la sección 3). En cola: bd4c, vin2, incoming50, b35-fnc y la bisección b12/b26nohp/b35nohp. El PC no puede escribir a otros hilos; los resultados pasan por el coordinador. |
| **Farmeo y macro del bot** | Causa nueva: el modelo de coste de `choose_target` cobra el doble de daño del real y descarta grupos de alces con gemas (1,1 frente a 2,3 por partida del top 10). Pieza o70 (daño modelado al 50%) sobre b35: neutra en local, más alces y menos muertes tempranas. Probando 35%. teamopen cerrada. |
| **Acotar el fuel / Mejorar cada campeón en su fichero** | Marcella: tienda del hechizo y daño por golpe cerrados (no ganan). Pidió siguiente frente. |
| **Copiar las decisiones del top 10** | vin2 (Vesper entra y dispara) neutra en 312 cercanas (−5 de 69); vin1 +1; bd2c −4. Usa dec300. |
| **Por qué perdemos en mapas lejanos** | Pieza o82 farnochase (sin persecución en equipo en lejanos antes de r400), neutra en local, enviada al PC frente a b35 (`bot/far-b32/b35-fnc.zip`). |
| **Comprobar si las stats del top 10 están anticuadas** | El top 10 ha cambiado (Claudus Maximus 2º, Mite 4º…) y el draft dominante también (Tavi 46%, Vendetta 80%; Ryth baja al 29% y gana el 42%; el nuestro lleva Ryth). Recalculando referencias con partidas de hoy. |
| **Qué hace mejor el top 10** (hilo guía del objetivo) | Referencia: el top 10 entra en peleas superando en 2 el 36-43% de las veces y nosotros el 12-21%; daño por ronda de pelea 33 frente a 27. |
| **Análisis de partidas con la API de Claude** | Pipeline de análisis de repeticiones; sin tarea activa. |
| **How Carson starts a bot** | Tuvo la cookie del sitio en su día: no copiar nada de ahí. |

Líneas cerradas (no reabrir sin datos nuevos): recortar muertes, escuadras y reclutar, territorio y mantener campamento, gemas primero en lejanos, bigrush, apertura, rally, ejecución de peleas, macro de farmeo en general, parejas y soledad, objetivo de HoR, retirarse en inferioridad, pelea-v1 (todas neutras o negativas online), vkite (+6 en 370), vcarry-open (+14 en 500, barra 22,8), monoguard (+6 en 250). idlerush está aparcada por el usuario.

## 8. Cómo arrancar en la cuenta nueva

1. Conectar GitHub (Javiops) y dar acceso a `Javiops/cambridge-battlecode-2026` y `Javiops/cambc-archive`.
2. Crear un entorno en la nube con 2026a.battlecode.co.uk en los dominios permitidos.
3. Subir a la carpeta del proyecto nuevo lo de la sección 9, como mínimo `online/` y `bundles/`.
4. Copiar `handoff/memory/*.md` a la memoria del proyecto nuevo, o pedir al primer hilo que la lea entera.
5. Empezar por el hilo del bot determinista (bisección de fight-camp) y relanzar el loop con la cookie nueva, siguiendo la regla de los 15 de delante.
6. Activar el Remote Control del PC para el Juez 2.
