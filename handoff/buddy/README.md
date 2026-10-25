# buddy-v1 (hilo «llegar juntos a las peleas»), sobre b27 (fuelfit-b27.zip, jeb4pf 76c4f20)

Causa medida (posiciones reales, r30-150, mapas cercanos; form.py / offcamp.py / walk3.py sobre decodes r300):

| | top 10 (40 p.) | puestos 30-60 | b27 online (18 p.) | b27 local (52 p.) |
|---|---|---|---|---|
| en campamento, en pareja (<=3) | 61% | 73% | 62% | 59% |
| caminando, en pareja | 55% | 57% | 37% | 39% |
| caminando sin gemas, en pareja | 56% | 62% | 37% | 41% |
| grupos (aliados encadenados a <=3) | 2.6 | 2.3 | 3.0 | 2.9 |
| rondas de pelea a +2 | 25% | 27% | 16% | 16% |

En el campamento estamos igual; nos separamos al caminar entre campamentos. Cada campeón elige su campamento solo.

Piezas (sin lecturas de fuel; coste: un claim_value por elección):
- **bd2c** = b27 + `bd_patch.py SRC 150`: los seguidores (puestos 1, 3, 4 del roster) valoran x1.5 el grupo que reclama su líder
  (0, 2, 3), saltándose el tope de reparto y la regla de racimo en solitario.
- **bd4c** = b27 + `bd_patch.py SRC 250` + `bd_resync.py SRC`: x2.5 y el seguidor vuelve a elegir cuando su líder cambia de reclamación.
- bw_patch.py (caminar hacia el compañero visible): sin efecto, no se envía.

52 partidas locales (sub52), frente a b27: bd2c +2 real 15.8 -> 19.5%, caminando en pareja 39 -> 42%, resultado -1/9;
bd4c +2 17.2%, caminando 44%, compañero a <=3 25 -> 37% (puestos 2-3), resultado -1/13. Ruido a este tamaño: hace falta el PC.
