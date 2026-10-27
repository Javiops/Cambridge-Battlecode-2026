# Superioridad (10-27): candidata u7 sobre e1foco limpio

u7 = e1foco (sha 659ded19) + aa (opts/aa.py, P_AA_GW 100) + awb (opts/awb.py, P_AW_FROM 151, P_AW_R 6, P_AW_PERS 2).
- aa: flee() lleva al herido hacia el aliado sano visible (>=40% de vida, sin recall) a 2-10 casillas, que no esté más
  cerca del rival y esté >=2 más cerca de casa; si no hay ninguno, va a casa como antes.
- awb: desde r151, si los rivales a <=6 son >= aliados a <=6 (contándome) + 1 durante 2 rondas seguidas, se va hacia
  el aliado visible a <=12 o se aparta (safe_step / flee). No se activa si el rival a su alcance muere con nuestro golpe.
Marcadores stdout: "[sup] aw1 own0 p2 r151 R6 AR6 N2 M1" y "[sup] aa1 H2 R10 GR3 GW100".
Diagnóstico (c34, e1foco vs puestos 56-70, r151-300, derrotas): morimos 1,82/partida vs 0,76; 55% en inferioridad
(rival 17%); 77% en nuestra mitad. t5b vs top 5: 1,79 vs 0,61.
Filtro local 2.0.0 (70 mapas x 2 lados): vs kvvl 79-61 (e1foco 74-66, nulo 71); vs e1foco 69-71;
rHunt/rTop1/rD 113/105/96 = 314/420 (e1foco 329). u1 (solo aa): 82-58, 65-75, 317.
Cerradas: parejas fijas pk (vs kvvl 67-81 sobre E1), huida hacia cualquier aliado (panel 268), convocatoria a alces
dobles cv (panel 300-301), apilar sobre o101.
