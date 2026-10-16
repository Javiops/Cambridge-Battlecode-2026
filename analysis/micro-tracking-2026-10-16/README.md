# Memoria por campeón para la micro (P_TRACK) — 2026-10-16

Base: v52 = `bot/mybot_teammate_fixes3_mapdraft.zip` (sin tocar). Cambios: `track.h` nuevo + 5 enganches
(`track_on_v52.patch`). Con `P_TRACK 0` las 170 partidas del panel son **idénticas** a v52 (0 cambios).

## 1. Qué usa v52 hoy en cada turno

| Dato | ¿Lo usa? | Dónde |
|---|---|---|
| Enemigos que **este** campeón ve ahora: casilla, vida, distancia, gemas, canalizando | Sí | lista `foes` (main.cpp) |
| Si el enemigo se aleja (comparado con la ronda anterior, solo si lo vio la ronda anterior) | Sí | P_NOCHASE |
| Alcance del enemigo, dash listo | Sí | `fight::reach` (paso seguro, kite) |
| Fuerza, foco y hechizos listos del enemigo | Solo para elegir casilla | P_VOLLEY (`threat_of`, enemigos a ≤10) |
| Aliados que **este** campeón ve: casilla y vida | Sí | favourable, ENGAGE2, front_line, kite, safe_step |
| Enemigo que se sale de nuestra visión | **No**: desaparece al turno siguiente | — |
| Enemigos muertos / cuántos vivos | **No** | — |
| Aliados fuera de visión | **No** (position() lanza error) | solo la reclamación de campamento en memoria compartida |
| Decidir pelea por daño (no solo vida) | **No**: compara suma de vida (ENGAGE2 74%) y número de cuerpos | — |

Medido (17 mapas del sitio contra sp_castera, 44.000 turnos de campeón):
- La visión es **por campeón**, unas 8 casillas de radio (~200 casillas).
- Un campeón ve a sus aliados vivos solo el **35%** de los turnos.
- En el 14% de los turnos con un enemigo a ≤8 hay además otro enemigo visto hace ≤3 rondas que ya no vemos.
- Al morir teníamos de media 1,9 enemigos visibles a ≤8 y solo 0,2 "fantasmas": casi nunca morimos por un enemigo que no veíamos.
- `is_alive()` de los enemigos funciona fuera de visión: sabemos cuántos están muertos.

## 2. El rastreador (`track.h`, P_TRACK 1)

Memoria privada de cada campeón (sus variables globales duran toda la partida):
- **Por enemigo** (orden del roster, máx. 8): última casilla y ronda vista (ronda actual = visible ahora), vida, vida máxima, fuerza, foco, alcance, gemas, daño/ronda estimado (fuerza + foco×1,5/8, se refresca cada 10 rondas), vivo/muerto y ronda de la muerte.
- **Por aliado**: última casilla y ronda vista, vida, vida máxima, a distancia o no, daño/ronda, vivo.
- Ayudas: `enemies_near(c, r)` (visibles + fantasmas de ≤3 rondas), `allies_near(c, r)` (yo + aliados vistos hace ≤2 rondas), poder de Lanchester (vida total × daño total), `isolated()`, `remembered_allies()`.
- Coste: ~3-5k de combustible por turno (de 100k).

Aliados más allá de la visión: la memoria compartida tiene 8 bytes y están todos usados (0-4 reclamaciones de campamento,
5-6 grupo/respawn, 7 ayuda/peligro). Compartir posiciones obliga a quitar algo: p.ej. reclamaciones a 6 bits (ya existe para
6 cuerpos) liberaría ~1 byte, que da 1 aliado por ronda a resolución 8×8 casillas. Hoy la reclamación de campamento ya dice
**adónde va** cada aliado; no lo he cambiado porque no ha salido ninguna ganancia que lo justifique.

## 3. Usos medidos (panel de especialistas, 17 mapas del sitio × 2 lados × 5 rivales = 170 partidas)

| Versión | Ganadas /170 | Cambios vs v52 (gana-pierde) |
|---|---|---|
| v52 | 121 (71,2%) | — |
| P_TRACK 0 | 121 | 0-0 (idéntica) |
| solo rastreador (P_TRACK 1, sin usos) | 118 | 22-25 |
| pelear por poder Lanchester, umbral 100% (P_TRACK_FAV 100) | 119 | 23-25 |
| ídem umbral 140% | 120 | 26-27 |
| enemigo aislado que matamos en ≤3 rondas (P_TRACK_ISO 3) | 117 | 22-26 |
| ídem ≤5 rondas | 118 | 25-28 |
| **retirarse hacia aliados recordados** (P_TRACK_RET 6) | **125 (73,5%)** | 24-20 (p=0,65); vs solo rastreador 10-3 (p=0,09) |

Ruido del panel: ±5-9 partidas al recompilar. **Ningún uso supera el ruido.** El mejor, retirarse hacia aliados
recordados, gana +4 a v52 y +7 al rastreador solo; menos muertes contra sp_farm (8,8 → 7,9) pero más contra sp_casterh (10,1 → 12,5).
El rastreador solo cuesta 3 partidas (más muertes contra sp_casterh: 10,1 → 13,0), probablemente por combustible.

Conclusión: la información que faltaba (enemigos fuera de visión) rara vez está cerca cuando morimos, así que tenerla
no cambia las peleas. Lo que más prometía es usar la memoria de aliados para retirarse; solo se puede juzgar online.

## 4. 2026-10-16 20:10: la versión "retirarse hacia aliados recordados", coste de combustible (el usuario pidió implementarla si no es cara)

Versión ligera (`track.h` actual): con solo P_TRACK_RET guarda solo aliados, y solo en turnos con un enemigo a la vista o visto hace ≤10 rondas.
- Coste del rastreador en esos turnos: ~3,3-4,4k de media, máx. 7,6k (de 100k); 0 en turnos tranquilos.
- Turnos perdidos por quedarse sin combustible (paso 26), 17 mapas × 2 lados contra sp_castera: **v52 106, ligera 149 (+43, +40%)**;
  sobre todo lanes 19→36, corners 8→24, rushbait-v2 2→9 (`fuel_k26.txt`).
- Panel de mapas del sitio: ligera **120/170** (v52 121, cambios 19-20): el +4 de la primera versión era ruido (`p3.txt`).

Veredicto: no se fusiona. Más turnos perdidos por combustible y ninguna ganancia medible.

## 5. 2026-10-16 20:30: arreglo de combustible de v52 (P_ROSTER + P_OCMEMO) y retirada sin coste

Perfil (P_FUELPROF, 12 partidas): en los turnos que se quedaban sin combustible el culpable era `other_captures`
(48k de media en los turnos pesados, hasta 4 llamadas por turno). Dentro, `bc::champions(team)` cuesta 3-23k por llamada.
- **P_ROSTER 1**: las listas de campeones se leen una vez por partida (los identificadores no cambian).
- **P_OCMEMO 1**: other_captures se calcula una vez por (ronda, grupo, casilla).
- Con combustible ilimitado (`--fuel 100000000`) las partidas son **idénticas a v52 en 34/34** (resultado, ronda, gemas y muertes por campeón): mismas decisiones.
- Turnos perdidos por combustible, 17 mapas × 2 lados contra sp_castera: **v52 106 → 12** (monolith 51 → 0, lanes 19 → 8, stampede 14 → 0, corners 8 → 2).
- Retirada hacia aliados recordados reescrita sin coste: reutiliza las casillas que safe_step ya leyó (sin llamadas a la API): 105 turnos perdidos (= v52).
- Panel de mapas del sitio (170): v52 121, arreglo 118 (cambios 14-17), arreglo + retirada **123** con **20** turnos perdidos. Todo dentro del ruido (±5-9).

Ficheros: `fuelfix_on_v52.patch`, `fuelfix_ret_on_v52.patch` (incluye track.h); zips `bot/mybot_v52_fuelfix.zip`, `bot/mybot_v52_fuelfix_ret.zip`.
