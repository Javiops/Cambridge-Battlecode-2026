# vopen-v1: Vendetta abre el farmeo junto al spawn (pelea-v1, parte Vendetta)

Base: kvvl (k_vvl_mgwp, v164; zip handoff/chain14/k_vvl_mgwp.zip de claude/project-thread-dxkoko). Código en vendetta.h (`vendetta::open_k`), una llamada en `choose_target_impl` y el contador.

## Dato (online, cercanos)
Top 10 frente a los mismos rivales: Vendetta golpea su primer campamento en r6 y lleva 534 de daño a monstruos a r20; la nuestra r24 y 160. Nadie compra antes de r40 y el daño por golpe es igual, así que la diferencia es dónde y cuándo empieza. La elección puntúa valor/rondas, y los grupos grandes a 15-17 casillas ganan a los pequeños junto al spawn. Por mapa el hueco está en elkring (r3 frente a r18), quadrants (r5 frente a r25), starfish, gem_fields y monolith.

## Regla
Solo Vendetta, hasta la ronda P_VOP_UNTIL (30), en mapas con camino spawn-spawn < P_VOP_MAX: los grupos a más de P_VOP_D (6) casillas de camino valen score × (6/travel)^2. Los demás campeones conservan su apertura (opening-near-v1 sobre los tres pesados perdía oro a r300).
- **ve** (recomendada): P_VOP_MAX 60, es decir, todos los mapas salvo los lejanos con farswap; solo grupos con gemas.
- **vf**: ve, pero también grupos solo de oro.

Contador en la línea de estado de Vendetta: `vop=N/R`, con N = elecciones que cambió y R = ronda de su primer golpe básico (−1 si aún no ha golpeado). Va por VM: solo la línea de Vendetta lo lleva.

## Prueba local (312 partidas cada una: 26 mapas no lejanos × 2 lados × 6 rivales del panel duro, motor 1.0.3)
| | Vendetta primer golpe (mediana) | Vendetta daño r20 / r40 | Daño de equipo neto r20 / r100 / r300 | Oro r300 | Gemas r300 | a14 r300 | Neto frente a kvvl |
|---|---|---|---|---|---|---|---|
| kvvl | r19 | 167 / 664 | −88 / +25 / +1372 | +235 | +19,1 | +0,59 | – |
| va (cercanos <35) | r18 | 273 / 878 | −16 / +158 / +1535 | +235 | +18,7 | +0,60 | −5 (69 cambiadas, barra 16,6) |
| **ve** | **r14** | **392 / 1014** | +41 / +192 / +1934 | +252 | +22,8 | **+0,68** | −1 (71, 16,9) |
| vf | r11 | 473 / 1094 | +86 / +223 / +1944 | +236 | +23,7 | +0,66 | −5 (75, 17,3) |

Variantes descartadas: vb (D4, hasta r20) a14 +0,43, neto −16; vc (exponente 1) +0,53, −7; vd (D4, exp 3, hasta r40) +0,46, −12.
ve es la primera pieza de apertura que mejora el estado a r300 en local (oro +17, gemas +3,7, daño +560). Va como acompañante de pelea-v1, no sola.

Ficheros: kvvl-vopen-ve.zip, kvvl-vopen-vf.zip (cambc bundle), diff_ve_vs_kvvl.patch, diff_vf_vs_ve.patch, SHA256SUMS.
