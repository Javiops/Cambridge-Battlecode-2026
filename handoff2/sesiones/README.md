# Sesiones locales del 25 y 26-10 (PC del usuario, app de escritorio)

Todas se abrieron desde la sesión coordinadora, trabajan en `C:\Users\Javier\Cambc2026` y van en modo auto. Para escribirles: SendMessage con `to` = su id `local_…`. Para reabrirlas: con el enlace `claude://claude.ai/epitaxy/<id>` desde la app. Sus transcripciones no están en git (ver `../HANDOFF.md`).

## Coordinadora (esta sesión)
- **Qué hizo:**
  - repartir y dirigir las líneas;
  - el análisis ronda a ronda frente al top 5 (scripts en `lab\coord\`);
  - desde el 26-10 a mediodía, por orden del usuario, trabajar ella misma la pelea: o200-o213, `fight2.h`, el barrido de parámetros (`lab\coord\sweep\`) y la clonación de comportamiento (`bc_*.py`).
- **Dónde está todo:**
  - memoria del proyecto: `C:\Users\Javier\.claude\projects\C--Users-Javier-Cambc2026\memory\`, copiada en `../memory/`;
  - plan y estado: `cambc-plan-c97-1025.md`;
  - hallazgos de mecánica: `cambc-vesper-step-reset-1026.md`.

## ML: optimizar y aprender la pelea del bot (UPV) — `local_a95718dc-d977-4619-839a-31ea3332d097`
- **Encargo** (orden del usuario del 26-10 hacia las 15:45): apostar por ML, siguiendo un plan sin iterarlo.
  1. CMA-ES sobre 105 variables continuas y 87 categóricas, contra un pool.
  2. Sparring del top 5 por imitación.
  3. Red de pelea entrenada por evolución.
  4. Juicio online en t5b a través del loop.
- **Ficheros:** `lab\ml\` (`INFORME.md`, `PITCH_UPV.md`, `runner.py`, `build.py`, `space.py`, `es.py`, `es_net.py`, `imit\`, `cpp\pol.h`, `db\games.sqlite`).
- **Estado a las 20:00:**
  - fase 1 en p1c (p1 falló por mutaciones demasiado fuertes);
  - fase 3 en n1;
  - la imitación no transfiere: el clon de acciones gana 7-13 de 140 a E1;
  - Q offline: 71 de 140, por debajo de co_v7 (79);
  - empaquetó `ml q1d10`, sin enviarlo.
- **Pendiente:** saber cuánto cómputo da la UPV (núcleos, GPU, sistema, acceso).

## Loop online en el PC — `local_aa12b548-0edc-4d79-b52c-8c72c9ed3efb`
- **Es la única sesión que toca el sitio** (subidas, activaciones, retos) y la única que baja repeticiones.
- **Ficheros:** `lab\loop\` (`README.md`, `INFORME.md`, `queue.py`, `cand.py`, `post.py`, `cmp_ref.py`, `fetch_replays.py`, `mk_t5b.py`, `ml_t5vs.py`); registros en `lab\loop\data\`; repeticiones en `lab\loop\replays\`.
- **Formato de prueba:**
  - cada candidata se juega sola en los grupos fijados de la brújula t5b (25 grupos, top 5) o en una cadena c3x (los 15 de delante);
  - se compara partida a partida con la referencia de kvvl;
  - un control de kvvl cada dos candidatas;
  - después, v164 vuelve a quedar activa.
- **Estado:** cola vacía, v164 activa. Bajó las 715 partidas del top 5 contra otros para la sesión ML: `lab\eval\t10out\ml_t5vs_1.json`, con un segundo pase en curso.

## Peleas sobre la base determinista — `local_61ed6f3b-ad46-45d2-9cf5-eb0540f864cc`
- **Qué hizo:** bisección de muertes en campamento (hitpass culpable), c95shop, o104 cf4, arranque (o105), t10pv (o106), foco o107/o108, corte o109, aliado o110 y controlador o111 (`fight_ctl.h`, `ARQUITECTURA_PELEA.md`).
- **Ficheros:** `lab\peleas4\` (banco `run.py`, `opts\`, `bots\`, `zips\`, `res\`, `fronts.py`, `idle2.py`, `rivwin.py`).
- **Estado:** en espera. Por orden del coordinador no toca el controlador (lo tomó el coordinador). Sus instrucciones del banco están en su último mensaje: mkzip.sh, run.py, sum4.py y fuelturns4.py.

## Evaluador de nuestras partidas — `local_a91af4ae-a0ed-4c17-a15d-c2d0f7a95f01`
- **Qué hizo:**
  - metas r1-100 a partir de los resúmenes (`sumchain.py`) y macro150;
  - hueco de oro por ventanas (`wingap`);
  - análisis de las parejas que cambian en las cadenas c30-c33 (las decide quién muere más en r1-300);
  - corrigió las listas de `loopdec.py` para que nunca pierdan partidas.
- **Ficheros:** `lab\eval\` (`INFORME.md`, `runs\`, `online2\`, `t10dec\`, `t10out\`).
- **Estado:** en espera.

## Análisis del top 10 — `local_96101b90-5ab6-46c1-8557-bbb277293da3`
- **Qué hizo:**
  - causa de las muertes tempranas: veredicto fijo y P_OUTNUM = 0;
  - invasiones en r101-300;
  - peleas igualadas: la conversión 14 % frente a 49 %;
  - el herido que se salva: ellos se van al 0,53 con 0,85 aliados y hacen recall;
  - juez online `juez_t5b.py`, más `wounded.py` y `eqbrief.py`.
- **Ficheros:** `lab\top10\` (`scripts\`, `out\`); sus notas `top10_*.md` están en la carpeta de notas compartidas.
- **Estado:** en espera.

## Farmeo y macro sobre la base determinista — `local_cbdea81d-6258-4a48-acbd-287381cebc06`
- **Qué hizo:**
  - c95go45 (peso del oro en la apertura);
  - E1 = o100 (daño recibido ×0,5), la mejor base;
  - E2 (trío al alce), descartada;
  - o135 rwb (vigilar la reaparición de los alces), efecto pequeño;
  - e1focon100 (E1 hasta r100 en cercanos), aparcada;
  - análisis del oro sin gastar: no lo guardamos.
- **Ficheros:** `lab\farmeo\` (`INFORME.md`, `zips\`).
- **Estado:** en espera.

## Banco del PC (Juez 2) — `local_f455491e-5c80-4da3-b2e5-1c78a3b8a765`
- **Qué es:** el banco J2 de 800 partidas del motor 1.0.3 (`lab\j2\`). Con el motor 2.0.0 ya no sirve; el banco válido es `lab\peleas4\run.py` sobre `lab4`.
- **Estado:** en espera desde las 05:00 del 26-10.
