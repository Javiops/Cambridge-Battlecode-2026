# o81 mfocus: Marcella compra poder de hechizo (sobre fuelfit-b32, 25-10)

`python3 o81_mfocus.py SRC V` (V = P_MSHOP). Solo cambia el plan de tienda de marcella.h; sin fuel, sin bucles, sin printf.

Por qué: el hechizo 2 x Focus de Marcella hace siempre 120 en las nuestras; el top 10 123 / 163 / 255 en r30-100 / r100-200 /
r200-300. Fragmentos de la Marcella del top 10 a r300 (mstat.py): fuerza 4,7, vida 5,6, focus 5,1 de 13,5; la nuestra (b32):
fuerza 1,9, vida 4,7, focus 0,2 de 6,5.

| variante | plan | focus r300 / r400 | vida r400 | daño a monstruos r400 | oro r400 | victorias (312, b32 = 244) |
|---|---|---|---|---|---|---|
| b32 | Treasure-h, Jungle-s, Bruiser-h x2, Durab-h, Bruiser-f x2 | 0,2 / 0,9 | 7,5 | 4645 | 381 | 244 |
| 1 | Treasure-f en vez de Treasure-h | 4,1 / 5,6 | 4,2 | 4999 | 424 | 236 (+25 -33) |
| 2 | 1 + Bruiser-f antes que Bruiser-h | 5,1 / 7,8 | 2,2 | 5020 | 431 | 241 (+31 -34) |
| 3 | Treasure-s (comparación) | 0,2 / 0,9 | 3,5 | 5232 | 391 | 233 (+25 -36) |

Lo que se deja de comprar: vida (Treasure-h 5 fragmentos = 500 hp). Sonda +20 sobre la variante 1: 0/52 cambian.
El mecanismo se mueve (focus como el top 10, +8% daño a monstruos y +11% oro a r400), pero las victorias no: 2 es la mejor (-3, ruido).

## Daño por golpe en pelea (mstep.py, cada acción con daño a un campeón, r30-300)
| | básico r30-150 / r150-300 | hechizo r30-150 / r150-300 | hechizos por partida r<150 |
|---|---|---|---|
| top 10 (81 online) | 45 / 56 | 128 / 200 | 2,2 |
| b32 (312 local) | 44 / 48 | 117 / 116 | 3,6 |
| o81 v2 (focus) | 44 / 48 | 133 / **196** | 3,5 |
| o81 v3 (Treasure-s) | 47 / **59** | 117 / 116 | 3,5 |

Las dos variantes cierran la brecha de daño por golpe (v2 el hechizo, v3 el básico) y ninguna gana partidas (241 y 233 frente a 244):
el daño por golpe de Marcella no es la palanca mientras se pague con vida. Línea cerrada.
