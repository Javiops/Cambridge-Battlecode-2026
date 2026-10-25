# vin-v1 (Vesper entra y dispara), sobre b28 (fuelfit-b28.zip, rama jeb4pf)

Causa medida (turn.py: acciones de cada turno con --every-step, r30-300, cercanos; 40 partidas top 10 vs 18 nuestras online):
Vesper con el rival más cercano a 4 (una más que su alcance 3) ataca en el 22% de sus turnos (top 10) y en el 12% (nosotros).
Habilidades de Vesper: k0 = reinicio de ataque, k1 = carga (dash). En esos turnos el top 10 hace paso + reinicio + disparo
(39 de 97 turnos con habilidad) o carga + disparo (34); la nuestra carga para alejarse (13 de 18).
Contexto (dmg.py/dagg.py): daño a campeones por ronda de pelea, top 10 33 frente a nuestro 27; Vesper 40 frente a 28.

- **b28-vin1** = b28 + `vin_patch.py SRC 1`: a 4 del objetivo, con vida >= 50% y el reinicio listo: paso a una casilla a <= 3
  no más amenazada que la actual, reinicio, disparo.
- **b28-vin2** = b28 + `vin_patch.py SRC 2`: lo mismo y, sin reinicio, carga a una casilla a <= 3 (no más amenazada) y disparo.

52 partidas locales frente a b28 (golpes de Vesper a 4: ataque 8 -> 15% / 18%, golpe a campeón 0 -> 6% / 9%; a 2-3: 67 -> 70 / 71%):
vin1 -3 de 7 cambiadas, vin2 +2 de 8 (ruido a este tamaño). Sin lecturas de fuel.
spf_patch.py (hechizo antes de apartarse) no cambia nada: Vesper no tiene hechizo de daño.
