# Test de mecanismo (método de process-audit-1023 §3), 23-oct

Obligatorio para todo candidato antes de panel17 y antes de la cola online (usuario 09:09: "aplica el método a todos los hilos").

## Cómo se corre
```
bash /mnt/project-files/analysis/local-filter-1021/scripts/runmech.sh WORKDIR bundles/<cand>.zip <cand> '\[tag\]'
```
- 80 partidas contra pHuntF (el veto de farmeo) y 80 contra rRushHunt (el rival duro más parecido a la banda online; t10shop le gana el 72%).
  - Son los 40 mapas del sitio x 2 lados por rival: 160 partidas emparejadas, unos 7 min con 4 jobs. Probado de punta a punta.
  - Para usar otros rivales: `RIVS="pHuntF rRushHunt pPoke"`.
- Base por defecto: t10shop-v2 (V17). Usa `BASE=nightpack-v1` para lo que vaya apilado sobre nightpack.
  - Las bases están en `base-results-mech/` y no se vuelven a jugar.
  - También están fixpack, shootfirst y gemrace-v4, como referencia.
- El 4º argumento es la regex de la etiqueta que imprime la regla nueva (`[tpc]`, `[wd]`, `[rally]`...). La línea debe llevar `r<ronda>`.
  - Sin etiqueta no hay contador, y sin contador la ficha está incompleta.
- Scripts en `scripts/`:
  - `mechgate.py BASE CAND`: el juez. Con `RIV=pHuntF,rRushHunt` junta los pares de los dos rivales.
  - `mechcount.py REGEX DIR`: el contador. Lee team-a/b.stdout de los replays antes de borrarlos.
  - `compact.py`: ahora guarda los eventos de muerte, kill, fuelExhausted, campClear y gemCollection, recortados (40-90 KB por partida).
  - Los JSON compactados con la versión vieja no tienen esos eventos: el juez los ignora.

## Qué informa
Para cada candidato, emparejado partida a partida contra la base:
- Resultado: net, cambiadas y barra.
- Los 6 indicadores de efecto secundario:

| indicador | qué es | malo si |
|---|---|---|
| gold400 | oro ganado por el equipo en r400 | baja |
| deaths | muertes de campeón por partida (también las de campamento) | sube |
| vdeaths | muertes de Vesper por partida | sube |
| fuel | turnos sin combustible por partida, más la **cola**: partidas con 30+ cortes | sube |
| cap20 | ronda de nuestra primera captura de grupo de 20+ gemas (si no hay, 1000) | llega más tarde |
| clears400 | grupos limpiados antes de r400 | baja |

- El contador: disparos por partida, partidas con 0 disparos y reparto por fase (r<100 / 100-400 / 400+).
- PUERTA:
  - FAIL si un indicador empeora más de 2 errores estándar emparejados y además más que su suelo. Suelos: oro 1%, muertes 0.4/g, Vesper 0.15/g, fuel 15%, cap20 15 rondas, limpiezas 0.5.
  - "watch" si empeora más de 1 error estándar.
  - La cola de combustible avisa si el candidato tiene 2 o más partidas con 30+ cortes que la base.
- CLOSE: con menos de 300 partidas emparejadas, una línea queda "sin resolver". Nunca se cierra con este test solo.

## Calibración con los candidatos que fallaron online (base t10shop-v2, 160 g = pHuntF + rRushHunt)
| cand. | net | gold400 | muertes | Vesper | fuel (cola 30+) | cap20 | limp.@400 | puerta | online |
|---|---|---|---|---|---|---|---|---|---|
| fixpack-v1 (cutguard) | -1 | -0.7% | +0.20 | +0.03 | -11% (9 vs 7, watch) | -6 | +0.1 | pass | -1; fuel 4.7->6.2 |
| shootfirst-v1 | +4 | +3.2% | -0.03 | -0.11 | **+24% watch** (11 vs 7, watch) | -17 | +0.4 | pass | +1; Vesper +0.2 |
| gemrace-v4 | +5 | **-4.4% FAIL** | +0.02 | +0.07 | +2% | -22 | **-0.7 FAIL** | **FAIL** | +5,-3; oro lejanos -12%, limpiezas -10% |
| nightpack-v1 | **+9** | +1.8% | -0.14 | -0.01 | +11% (**12 vs 7, watch**) | -22 | +0.6 | pass | (sin jugar) |

Por rival:
- **fixpack:** vs rRushHunt oro -6.4%, muertes +0.9 y Vesper +0.34 (todo watch). Vs rD (80 más) muertes +1.0, cap20 +22 y limpiezas -0.7 (watch). Vs pHuntF, nada.
- **shootfirst:** vs rRushHunt Vesper +0.17 (igual que online, +0.2), pero vs pHuntF -0.40.
- **nightpack:** contador `[tpc]|[wd]` 5.7 disparos por partida contra pHuntF; 0 en 59 de 80 partidas; el 81% después de r400.

**Qué caza y qué no:**
- **Lo caza:** gemrace, en los mismos dos indicadores que online (oro@400 y limpiezas). Es la clase que más hemos repetido (gemrace v1..v7).
- **No lo caza:** el bucle de cutguard. No aparece en local en 400 partidas (pHuntF, rRushHunt, rD); los cortes medios bajan.
  - Online era una cola rara: mediana 0, unas pocas partidas con 200+ cortes.
  - Por eso existe el indicador de cola y por eso el contador es obligatorio: la congelación de la partida a0efb96f solo se ve en el replay.
- **shootfirst:** el signo de Vesper solo sale contra rRushHunt. pHuntF no castiga a una Vesper clavada (no hace poke).
  - Reglas de Vesper o de huida: añadir pPoke a RIVS.
- **Aviso para el hilo API:** nightpack sube la cola de cortes de combustible, 12 partidas contra 7.
  - Online idletpc ya mostraba cortes 5.2->8.1 en mapas lejanos.
  - Antes de apilar nada más sobre nightpack, mirar en qué partidas se corta y si es por los cristales de teletransporte.
  - Partidas con 30+ cortes: sobre todo lanes (164 contra 74 vs rRushHunt), yellow_brick_road (70 contra 22) y big_world (30 contra 16).
  - Ningún resultado cambia por eso en estas 160 partidas.

## Control online (punto 7 del método), lo que pasa el filtro al loop con cada candidato
- **Subconjunto de control** = partidas donde la regla no actúa. Primero por contador: replays online con 0 disparos en team-a.stdout. Si no hay contador, por clase: mapas cercanos/lejanos según mapfeat40, o draft rival sin el campeón que activa la regla.
- Si el control se mueve 5 pares o más entre base y candidato, el lote es deriva y no se juzga.
- Efecto esperado < +6/120 (panel17 < +80/800): no va solo a un lote. Se apila, y la pila se prueba junta vs pHuntF antes del lote (punto 8; sfflp).
