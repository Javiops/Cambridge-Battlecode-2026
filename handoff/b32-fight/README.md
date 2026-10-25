# Piezas de pelea sobre b32 (fuelfit-b32.zip, jeb4pf, sha 76d0a735…)

- **b32-vin2** = b32 + `handoff/vin/vin_patch.py SRC 2` (Vesper a alcance+1: paso + reinicio + disparo, o carga + disparo).
- **b32-vin1** = b32 + `vin_patch.py SRC 1` (solo paso + reinicio + disparo).
- **b32-bd4c** = b32 + `bd_patch.py SRC 250` + `handoff/buddy/bd_resync.py SRC` (x2.5 y el seguidor reelige cuando su líder cambia de reclamación). Local -1/9; sonda 0 cambios.
- **b32-bd2c** = b32 + `handoff/buddy/bd_patch.py SRC 150` (el seguidor toma el campamento de su líder).

Sin lecturas de fuel; nada nuevo en el arranque (vin solo en peleas, bd en choose_target a partir de r30).
Sonda +20 (bucle de run_game): 52/52 replays idénticas en las tres.
52 partidas locales frente a b32: vin2 +5 de 9 cambiadas (umbral 6.0), vin1 +1/7, bd2c -4/10.
