# Tablero de ideas

Generado por `python3 tools/idea.py board` el 2026-10-15T22:02Z. Pipeline y puertas: [harness/README.md](README.md).

## En curso

| id | idea | tipo | etapa | quién | bot / rama / PR | último resultado |
|---|---|---|---|---|---|---|
| I004 | Arreglo de corners: no volver solos, huir antes (study27 + corners fix) | fight | online | Javi | study27 + corners fix | local corners 16-0; online lfl: 24 vs 17 en 206 parejas (p=0.35), corners 7 vs 7: sin decidir tras 4 batches |
| I009 | Barrido con el hechizo de área en el borde (AoE sweep, dash cooldowns) | fight | local-ok | Fran | fran/study27-combat-micro / PR #11 | local 92-55 sobre el bot combinado (zip bot/mybot_study27_corners_combat.zip); pendiente de subir y lfl online |
| I010 | P_RECALL_PCT 50 (recall con la bolsa al 50%) | farm | local-ok | Javi |  | local 91-58; pendiente de subir y confirmar online que no empeora |
| I017 | Arreglos de la auditoría de study28 (bucle de recall, byte de peligro, desatasco) | bug | test-local | Javi | PR #9 | local empate (es un arreglo, no una mejora); zip bot/mybot_study28_fixes.zip |
| I011 | Banco de pruebas de la macro de Mite fija por mapa (P_MITEMACRO) | infra | desarrollo | Javi | claude/project-thread-cn0ial / PR #12 | PR #12 abierto |
| I014 | Políticas de farmeo y banca conectadas (study27 economy) | farm | desarrollo | Fran | fran/study27-economy / PR #13 | PR #13 abierto; pasar por gate.py --kind farm |
| I015 | Farmeo seguro y cambios de corners v39 | fight | desarrollo | Fran | fran/study27-safe-farming / PR #10 | PR #10 abierto; pasar por gate.py --kind fight |
| I016 | No abandonar la captura a aliados canalizando | bug | desarrollo | Fran | fran/study28-tested-fixes / PR #8 | PR #8 abierto |
| I012 | Segunda vuelta de farmeo en mapas de carrera (expanse, rows) | farm | idea | Javi |  | frente abierto, sin rama |
| I013 | Farmear en nuestra mitad cuando estamos en inferioridad | macro | idea | Javi |  | frente abierto, sin rama |
| I018 | La apertura de la pelea: no andar hacia un grupo visible antes del primer golpe | fight | idea | Javi |  | dimensión sin probar; ninguna regla de hoy la tocó |

## Cerradas

| id | idea | tipo | etapa | quién | bot / rama / PR | resultado |
|---|---|---|---|---|---|---|
| I001 | Recall sobre las casillas de captura en todos los mapas (study25, P_CAPRECALL 2) | farm | aceptada | Javi | PR #1 / v35 lineage | local dev 88-34, hold 19-12 vs v30; en study26/27 online |
| I002 | Apilar en campamentos de 3000+ hp, repartir en los pequeños (study27) | farm | aceptada | Javi | PR #4 / v36 = study27 | online: apilar funciona en mapas con campamentos 3000+; es el bot online desde las 15:36 |
| I003 | Cancelar tributos y recalls condenados (study28, P_CHANCANCEL 60) | fight | rechazada | Javi | PR #6 / v37 = study28 | local dev200 24-5 vs study27, online emparejado igual (14 vs 18 en 58 parejas), ranked 36%: vuelta a study27 15:36 |
| I005 | Dos campeones por campamento como Mite (msquad) | fight | rechazada | Javi |  | local: 6% más lento farmeando y el panel de lanzadores le gana más (66-13 vs 78-11): veto |
| I006 | Final de rows: guardar cada bolsa cuando alguien está a 150 de 1000 | farm | rechazada | Javi |  | sin cambio en ningún mapa; rows banca en 404 vs 401 y pierde el espejo por los dos lados |
| I007 | Nivel de peligro 0-1 para decidir la huida (P_DLEVEL) | fight | rechazada | Javi |  | sin victoria local; 2/3 de las muertes siguen siendo huyendo |
| I008 | Desempates simétricos por lado (P_SYM) | bug | rechazada | Javi |  | lados iguales en 37/44 mapas pero 4% más lento y 107/212 vs study27: el hueco es caos, no sesgo |

## Por etapa

- **idea**: 3 (I012, I013, I018)
- **desarrollo**: 4 (I011, I014, I015, I016)
- **test-local**: 1 (I017)
- **local-ok**: 2 (I009, I010)
- **online**: 1 (I004)
- **aceptada**: 2 (I001, I002)
- **rechazada**: 5 (I003, I005, I006, I007, I008)
- **pausada**: 0
