---
name: cambc-fuelfit-state-1025
description: 10-25 12:05 UTC fuelfit current state and user rule - keep iterating on the deterministic base (b28+), send to the loop ONLY a significant PC-confirmed improvement; b27 already measured online (c19 -7), do not resend
metadata:
  type: project
  modified: 2026-10-25T09:45:00.000Z
---
Estado fuelfit (base determinista) a 25-10 11:45 UTC. Detalle anterior en [[cambc-fuelfit-1025]].

- b32 (b15 + o68 v2 P_MP_HOLE=2) = base determinista actual; PC pad 0/800, J2 +14.2; online cadena 20 vs kvvl v164: -1 total, cercanos -5 (27 parejas cambiadas). USER 10:38 UTC ordeno mandarla al loop; USER 10:17: TODOS los hilos trabajan sobre la base determinista.
- b35 (+o74 ajuste turno 1) y b37 (+o75 tienda diferida): caben en turno 1 en 23/26 mapas cercanos (antes: primera accion r3 en casi todos). PC: J2 +16.4/+14.6, cercanos 155/153 de 200, vs kvvl directo 45/45/38 de 80 (no significativo), pad+20 4/23 partidas cambiadas (borde del turno 1). PC recomienda b35.
- Analisis online c19 (b27 vs V20) + c20 (b32 vs kvvl), repeticiones decodificadas: los deterministas mueren ANTES en cercanos: primera muerte mediana r66 vs r87 (c20), r52 vs r120 (c19); muertes extra r100-300 en peleas contra campeones rivales, en inferioridad y con gemas; gemas entregadas a r300 58 vs 76. NO es separacion del grupo (clusters iguales), ni acarreo de gemas, ni campamentos. El panel local (rivales = nuestro linaje) no lo reproduce (muertes <=r300 b32 1.96 vs kvvl 1.88).
- Pieza unica comprobable online: arranque r1 (b35) -> propuesta cadena 21 = b35. Zips: handoff/fuelfit/ en rama claude/project-thread-jeb4pf (fuelfit-b35.zip sha 537b38c9...).
- 12:30 UTC: la perdida cercana es MICRO: muertes en modo farm/fight-camp (online 12 vs 3; proxy LOCAL medible con handoff/fuelfit/tools/deathmode.py: kvvl 13, b32 21, b35 22 en 52 partidas). No es posicion/contacto, ni turnos cortados, ni dashers lejos. Propuesto al PC medir el proxy a 800 g. o76 (warm-up fuera del turno 1, b38) aparcado: turno 2 sube a 83-100k. Commit 967877c.
- 12:04 UTC ONLINE b35 (cadena 21 implicita, 24 grupos c20): vs kvvl -4 (cercanos 44/76 vs kvvl 52, b32 47; lejanos 20/44 = b32 identicas). Arrancar en r1 NO arregla cercanos online. b35 descartada como candidato; la pista es fight-camp.
- Pendiente: mapas aun en r3 (monolith, quadrants, lost_world, yellow_brick_road, the_farm, elk_arena, boss_battle, corners, stampede); hitpass o70 genera errores "Unit is not in vision" (~113/partida, inocuos).
