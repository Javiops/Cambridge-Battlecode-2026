# Fuentes de las fusiones del PC (hilo «Iterar rápido con el PC al 100%», 10-24)

Fusiones a tres bandas con lab/j2/combo.py, base kvvl (k_vvl_mgwp, handoff/chain14). Juez 2 frente a V20 / mapas de reserva:
| zip | piezas | J2 | reserva |
|---|---|---|---|
| pA.zip | kvvl + vkite-v3 + mstick-v1 (= bundles/pelea-pA.zip) | +16,7 | +16,8 |
| pA_ve.zip | pA + vopen-ve | +1,7 | +16,2 |
| pA_v1a.zip | pA + pelea-v1a | −5,1 | +11,8 |
| pA_ve_v1a.zip | pA + vopen-ve + pelea-v1a | −26,5 | — |
Comprobado en pA_ve y pA_ve_v1a: vendetta::open_k aparece 2 veces (declaración + uso) y vop_best/g_vop 4 veces, igual que en kvvl-vopen-ve: la fusión no duplica ni pierde los ganchos de choose_target_impl.
