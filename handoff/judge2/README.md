# Juez 2: un juez local que refleja mejor el online (10-24)

Pedido por el usuario (10-24 08:54): que el entorno local refleje los resultados online.

## Qué es
J2 = 100·(cercanos + medios + 0,42·lejanos)/n_duro + 100·neto_castigadores/n_cast   (por cada 100 partidas emparejadas, frente a V20)
- **Panel duro** (480 partidas): rTop1, rD, rF, rHunt, mV19 (=V19 pack-v1w), mV10d (=v10d). Las victorias en lejanos pesan 0,42 (en local están ~2,4 veces infladas).
- **Castigadores** (320 partidas): rPun5 (v20c-vk con build de daño puro, retrocede en inferioridad a ≤6, sin retirada) y 3 variantes mínimas (rPun5b/c/d: P_OUTNUM 5/7, retroceso por 2). Pillan las piezas que ganan en local muriendo más.
- **Lectura**: online ≈ 0,8 × J2 por cada 100. Barra de J2 ≈ 4-8. Comparar candidatos entre sí: la tanda base online mueve todo ±4.

## Las 800 partidas
10 rivales × 40 mapas del pool (maps/) × 2 lados. Lado A: `cand rival mapa`; lado B: `rival cand mapa`. Clase de mapa por d_spawn de mapfeat40.json: cercano <35, medio <60, lejano el resto (12/16/14 mapas → 120/192/168 partidas del panel duro).
Las 800 partidas base de V20 (v6d) ya están jugadas: base_v6d_outcomes.json (clave `rival/[AB]_mapa` → equipo ganador). El motor es determinista: la misma pareja da la misma partida.

## Uso (necesita `cambc` 3.0.5 / motor 1.0.3 en el PATH)
```
bash run_judge2.sh /ruta/a/bot.zip NOMBRE [JOBS]     # o una carpeta que contenga src/
```
Crea work/, juega lo que falte (salta lo ya jugado), borra las repeticiones y llama a `judge2_local.py work/res/NOMBRE`.
Comprobación: v20c-vco da `J2 +3.9/100 (bar 8.2) = hard +0.8 [near -2 mid +3 far +7] + pun +3.1 (+10/320)`.

## Fuentes incluidas
- bots/v6d = V20 (v139), base de las partidas base. bots/v20c = V20 reorganizado por campeón (base de las piezas nuevas).
- bots/rTop1 rD rF rHunt mV19 mV10d rPun5 rPun5b rPun5c rPun5d: rivales.

## Validación
1. 8 piezas antiguas con efecto online grande, cada una contra su base: marc-bfill +20/100 online, stallfix +9, t10draft +6, need2 +6, elksplit 0, goldw40 −6, mega-far −6, value −7,5.

| juez | r con online | signos |
|---|---|---|
| panel duro (480) | 0,55 | 5/8 |
| panel duro con lejanos ×0,42 | 0,66 | 4/8 |
| castigadores (320) | 0,84 | 6/8 |
| **Juez 2** | **0,80** | 5/8 |

   - Ejemplo: marc-bfill J2 +21,4 (online +20). mega-far gana +20 en lejanos en local y pierde online. goldw40/value solo los pillan los castigadores.
   - Fallos: need2 (+6 online, −4 local) y stallfix (+9 online, +5 local).
2. Las 12-13 piezas jugadas online sobre V20 (vkite, vco, fvk, fgw33, fvkls, nofs, kq, fo2r, vkls, lshop, vgoldfar, vkvcols, v7d) no validan nada: su dispersión online (varianza 12) es menor que el ruido de una tanda de 120 (15).

## Por qué el local se separaba del online (perfil V20, 745 partidas online de las cadenas 3-8)
- Los rivales online farmean mucho más: 184-214 gemas a r400 frente a 97-166 de los locales; online hay pocas partidas igualadas a r800 (8-21% frente a 20-50%).
- En cercanos las piezas de Vesper salen negativas en local y positivas online (+20 gemas por partida online).
- No se puede hacer un rival "rico" editando mapas: el motor espeja los campamentos. Rivales que evitan pelear farmean menos.
