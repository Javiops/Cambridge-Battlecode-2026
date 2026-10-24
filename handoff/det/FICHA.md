# kvvl-det v8: kvvl con fuel determinista

**Qué es.** kvvl (v164) con una sola diferencia: `fuel_ok()` ya no lee el fuel que queda. Lee un contador `g_dm` que solo depende del estado de la partida. Las decisiones ya no se reparten de otra manera cada vez que una pieza cambia el gasto de instrucciones.

**Por qué.** Al recompilar, cambia el fuel que se gasta en cada turno desde el primero. Con eso, algunos `fuel_ok()` dan otro resultado desde r2, y los pares online de la cadena 16 se separaban en r3 (mediana). En local, kvvl con 20 instrucciones inútiles por turno cambia 248 de 312 partidas y el resultado de 43. En el PC, pelea-v10 (kvvl con un contador) cambia 771 de 800 y el ganador de 233.

**Cómo funciona** (`main.cpp`, bloque `det-fuel`):
- **Por sección:** cada sección de `play_turn` (marcas `FP`) cobra `DM_BASE[sección][enemigos a menos de 10]`.
- **Por comprobación:** cada `fuel_ok` cobra `DM_CALL` (400).
- **Trabajo caro:** si una comprobación deja pasar trabajo caro, cobra ese trabajo con `fuel_okc(need, charge)`. Por ejemplo: elegir objetivo 24 500, entrar a pelear 16 500, persecución 14 500, línea de estado 20 600, búsqueda de camino 4 800.
- **Compras:** cada compra cobra 70 000 después de hacerla.
- **Calibrado:** el contador está ajustado para que, por término medio, cada sección cueste lo mismo que el fuel real (52 partidas).
- **Veto del fuel real:** solo actúa por debajo de 9000, en los turnos muy pesados. Se cuenta en la línea de estado como `dm=contador/vetos`.

**Resultados en local** (312 partidas: 26 mapas no lejanos x 6 rivales duros x 2 lados):

| | kvvl | det8 |
|---|---|---|
| victorias | 71% | 71% (neto +1 en 121 cambiadas) |
| a14@300 | +0.591 | +0.571 |
| oro@300 | +235 | +222 |
| gemas@300 | +19.1 | +18.9 |
| +20 instr./turno: partidas cambiadas | 248 | 172 |
| … de ellas antes de r300 | 105 | 33 |
| … ganador cambiado | 43 | 18 |

**Todavía no es 0.** Los cambios que quedan vienen del veto del fuel real en turnos pesados (unos 130 por partida para 4 campeones). Hay una versión que cobra más (v4) y casi no cambia nada (16 de 312, 0 ganadores), pero es mucho más floja: el contador corta trabajo que kvvl sí hace. Sigo con v9, que busca quitar ese resto sin perder fuerza.

**Cómo portar una pieza:**
1. Aplica su diff encima de esta base.
2. Si añade un bucle o una búsqueda cara bajo `fuel_ok(n)`, cámbialo por `fuel_okc(n, coste)`, con el coste medio de una pasada.
3. No uses `bc::fuel_remaining()` en ninguna decisión.

**Ficheros:** `kvvl-det8.zip` (src/), `diff_det8_vs_kvvl.patch`, `SHA256SUMS`.
