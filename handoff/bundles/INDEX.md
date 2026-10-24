# Piezas desde V20 (bundles de 23-oct 19:30 en adelante)

V20 = v139 = **v6d** (V19 + bcf-v3 engage + richcap-v2). **v20c** = la misma V20 refactorizada en un `.h` por campeón; las piezas `*-c` / `v20c-*` van sobre v20c, el resto sobre V20 (v6d) salvo que se diga.

Columnas, por pieza:
- **Duro**: resultado en el panel duro contra V20, neto sobre 480 partidas (barra de 11 a 22).
- **J2**: Juez 2 por cada 100 partidas (barra de 4 a 8; online ≈ 0,8 × J2).
- **Online**: neto de victorias por pares frente a la base de la misma tanda. En V20, todo el online cae dentro del ruido (±10 sobre 125).

Hay 78 zips copiados tal cual de /mnt/project-files/bundles, sin cookies ni credenciales. Las fichas están en /mnt/project-files/bot/<pieza>/FICHA.md cuando existen.

## Tandas y paquetes
- `v20-5.zip`: paquete de la cadena 3 (base V20 más mejoras 1-5).
- `v20c.zip`: V20 refactorizada, un fichero por campeón (PR #47). Es idéntica a V20 y es la base de todo lo nuevo.

## Vesper (vkite y familia)
- `v20-vk.zip` (vkite-v1): Vesper dispara primero y luego hace el dash. Duro +10 (gana en lejanos, pierde en cercanos); J2 +5,8. Online, cadenas 3/4/5: +5/+7/−5; en total +6/370 = ruido.
- `v20c-vk.zip`: vkite-v1 portado a vesper.h sobre v20c (ce731e13). Es la base de la cadena 5.
- `v20-vk1f.zip`: vkite solo en lejanos. Duro +8 (lejanos +19).
- `v20c-vk2.zip`: variante vk2 sobre v20c. En V20, la v2 dio −9 en duro.
- `v20c-kq.zip`: V20 más contadores [kq] (solo registro, mismo comportamiento). Sirve de suelo de ruido online: −4/125 (14 cambiados); J2 −4,3.

## Lejanos: peso del oro y farmeo
- `fargw-v2.zip`, `v20-fgw.zip`: peso del oro en lejanos de r400 a r800. Duro +5 (todo en lejanos), pero más muertes en lejanos (+0,44).
- `v20-fgw33.zip`, `v20c-fgw33.zip`: igual con gold_w 0,33. Duro +5 sin el coste en muertes; runmech +4. J2 −2,4. Online cadena 3: +3.
- `v20-vf33.zip`, `v20c-vf33.zip`: fgw33 + vcapfar. Duro −1: no suman.
- `v20c-fgw33-vk1f.zip` (fvk): fgw33 + vkite en lejanos. Duro +16 (barra 13,3), el primer PASA sobre V20; J2 +0,5. Online: +5 (cadena 3) y −1 (cadena 4).
- `v20c-fgw33-vk1f-fp4.zip` / `-fp6.zip`: fvk + farplan. Duro −11 / −13, con más muertes. Cerradas.
- `v20c-fgw33-nofs.zip` (nofs): fgw33 sin farswap (HoR en lejanos, no Ren). Duro −1; J2 −0,2. Online cadena 4: −2.
- `v20-hor.zip`: V20 sin farswap. Duro −8, todo en lejanos.
- `v9d-fgw.zip`: v9d + fgw, en la base de V19.
- `vgold-c.zip`, `vgold-c-r500.zip`, `vgold-c-w70.zip`: Vesper prioriza oro. Duro +3 / −5 / −3. fargem ≤ 0: más oro, no más gemas.
- `vgold-far-c.zip`: lo mismo solo en lejanos. Duro 0; J2 −2,8. Online cadena 6: +1 (Vesper +22% de oro a r800, mismas victorias).
- `vgold-far-vk.zip`: vgold-far sobre v20c-vk. No recomendado.
- `vrich-c.zip`: grupos ricos para Vesper. Duro −10.
- `vcapt-c.zip`: capturas de Vesper. Duro −5.
- `vcapl-v1.zip`: captura tardía. Duro 0; aparcada.
- `v20c-vk-fo2r.zip` (fo2r): v20c-vk + farout (vuelve a base en lejanos de r400 en adelante si van 2 en contra). Duro −7 frente a vk; J2 +2,2. Online cadena 5: 0 (28 cambiados).
- `v20c-vk-fo2r-fp4.zip`: fo2r + fp4. Duro −10; no se usó.
- `hfarm-v1.zip`, `hfarm-v1b.zip`, `hfarm-v2.zip`, `hfarm-v2b.zip`: HoR farmea primero, o emblemas de farmera del top 10. Duro −30 / −20 / −23 / −23. Cerradas.
- `teamclear-v1.zip`, `teamclear-v1b.zip`: los grupos custodiados se valoran como despejados por 1,8 campeones. Duro −22. Cerradas.
- `ownrich-v1.zip`: el primero en elegir el grupo rico propio no paga la penalización de compañía. runmech −5, más muertes. Cerrada.

## Tienda tardía (lshop)
- `lshop-v1.zip`: tienda tardía sobre V20. Duro +4 (muertes −0,26).
- `lshop-v1c.zip`: la misma sobre v20c (hook late_mix). Duro +7; J2 +2,0. Online cadena 6: −3.
- `lshop-v1c-r250.zip` / `-r600.zip`: la misma empezando en r250 / r600. Duro +4 / +5.
- `lshop-v2.zip`, `lshop-v2c.zip`, `lshop-v3c.zip`: más Strength. Duro v2 −16 y v3c −2: más Strength perjudica.
- `v20c-vk-ls.zip` (vkls): v20c-vk + lshop-v1c. Duro +1 frente a vk; J2 +5,7. Online cadena 5: −6.

## vco (Vesper lleva el oro en la apertura)
- `v20c-vco.zip` (vcarry-open, P_VCARRY_UNTIL 200): Duro +8; J2 +3,9; oro del equipo a r300 +7,5%. Online cadenas 6/7/8: +1/+9/+3; en total +14/500 en 4 tandas. Cerrada porque la ganancia de gemas no es estable.
- `v20c-vk-vco-ls.zip` (vkvcols): paquete vk + vco + ls. J2 +2,9. Online cadena 7: +6.

## Peleas y muertes
- `bcflate-v2.zip`, `bcflate-v2L.zip`, `bcflate-v2R.zip`: a partir de r400, bcf solo entra en 2 contra 1 claro. Duro −14 / −19 / −14. Cerradas.
- `gf2-small60.zip`, `gf2-sq3b.zip`: guardfirst (hilo bcf, prueba de mapas). No hay resultado anotado.
- `hshield-v1.zip`: escudo de HoR con hp < 85%. Duro −18 sobre V20. Cerrada.
- `recallcut-v1.zip`, `recallcut-v1b.zip`: perseguir al rival que se retira a base. Duro −23 / −11. Cerradas.
- `laterecall-v1.zip`, `-v1b`, `-v2`, `-v3`, `-v3e`: volver a base tarde en lejanos cuando hay contacto. v3 +0 y v3e −4 en duro; +2/80 contra rPun5. No hay resultado anotado para v1/v2.
- `vendstand-v1.zip`: Vendetta no retrocede a distancia 2 cuando está sana. Duro −12. Cerrada.
- `vendbuy-v1.zip`, `vendbuy-v1b.zip`: Vendetta compra Power-S. Duro −26 / −5. Cerradas.
- `dmg-v1c.zip`, `dmgm-c.zip`: compras de daño. Duro −9 / −18. Cerradas.
- `mcgo-v1.zip`, `mcf-v1.zip`, `mcgof-v1.zip`: Marcella hace burst con Focus y se va (go), o Bruiser-f antes (f), o ambas (gof). Duro −20 / −14; gof sin resultado anotado. Cerradas en esta forma.
- `dfirst-v1.zip`, `dmon-v1.zip`: orden de emblemas (Durab-h 3.º / Monster-h). Duro −17 / −19. Cerradas.
- `v20c-hr.zip`: curación al volver a base con hp < 40%. Duro −2 = ruido.

## Primeras 150 rondas: soledad, parejas y monolito (10-24)
- `monoguard-v1.zip`, `-v1b`, `-v1c` (mg1): no despertar el monolito gold_rush mientras el grupo no pueda con él. v1c (87e46a7d) es la buena. Hilo de muertes en campamento.
- `pfg.zip`, `v20c-pfg.zip`: los campamentos sin un aliado que los reclame a menos de 6 valen ×0,4 entre r30 y r150, excepto los de solo oro. Duro −10 (cercanos −5); se juzga online por soledad y muertes.
- `v20c-mg1c-pfg.zip`: monoguard-v1c + pfg. Cadena 11.
- `v20c-mg1c-pw3-waitpair.zip` (mgwp): mg1c + pw3 (posición estimada del aliado y caminar con él) + esperar a la pareja. Duro +1 = neutro. Las fuentes de pw3 y mgwp están en la rama claude/project-thread-dxkoko (handoff/pw3, handoff/mgwp).

## Otras
- `v20-draft.zip`: draft tavi vesper ryth prism vendetta. Duro −117. Se construyó sobre un mapeo de ids equivocado; descartada.
