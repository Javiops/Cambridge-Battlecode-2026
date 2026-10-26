---
name: cambc-top10-eco-1023
description: 10-23 top10-vs-top10 economy vs v122: same gold, gems -31% because we take 4.5 more tiny captures and fewer 20+/40+; Vesper is the weakest farmer; open-pack failed
metadata:
  type: project
---
Map thread 10-23 ~12:20 UTC (analysis/top10-micro-1023/eco-plan/README.md; scripts curves.py/champ.py/caps.py read summaries events gemCollection/buyItem).
- top10 (45 t10-t10 summaries 10-22) vs 600 v122: gold r400 1889 vs 1799; gems 21/44/72/100/224 vs 9/28/47/67/155 (r50..400); monster dmg -17..-23%.
- Same capture count (21.8 vs 23.9 by r400) but 12.3 vs 8.5 gems/capture: we take +4.5 captures <6 gems, 2.6 vs 3.6 of 20-39, 0.4 vs 0.9 of 40+ = -69 gems = whole gap. All map classes, mid worst (first 20+ r456 vs r324). Even top10 losers (11.5) > our winners (8.6).
- Vesper: gems150 19 vs 8, gold400 547 vs 316; same hit rounds but wolves 80% vs 56%, elk 9% vs 34%; buys Durability Str vs top10 Treasure/Power Str.
- Mirror teams (Bamboo etc) open packed near; top10 does NOT (first hit r37, 17 tiles, 0.9 mates). open-pack (opk) mech test FAIL clears -3.9% net -7: parked.
- User 10-23 11:37: reference = top10 vs top10, not mid-table rivals.
Related: [[cambc-map-class-1022]] [[cambc-games-side-bug-1023]]
- 13:30 vespcap (Vesper captures first, P_CAPPRIO+cap_rank vesper=0): v2 (CAPPRIO 2) BEST: runmech 240 net -3, gold400 +4.4%, Vesper deaths -31%, Vesper gold share 16%->40% (top10 32%), likeness +16%; bundles/vespcap-v2.zip b41e1109, sheet bot/vespcap-v2/FICHA.md -> API pack-v2. v1 deaths +0.85; v3 (d<=1, no foe 5) gold +1.8% likeness 0. richcap-v1 (tiny x0.5) FAIL gold -11% deaths +29%. vtreas alone failed twice (shop).
- 15:50 ONLINE v133 pack-v2w (with vespcap-v2) vs v132, 90 pairs: WR 58 vs 48%, Vesper share 0.41 vs 0.17 (as local), gold400 +8%, clears same, gems/capture unchanged 9.4; near +18pts mid +21 far -7 (n33). richcap-v2 (gold_w 0.45 from r150, 20+ clusters shareable) runmech 240 pass net +5 gems400 +8% gold -1.3% watch; bundles/richcap-v2.zip. Script analysis/overnight-1021/chain-1023/chain_eco.py (chain1 lists analysis/chain1-1023).

10-23 17:15 chain_eco vs V19 (v136, paired same groups; table chain-1023/table_v136.txt, now with deaths): vespcap (v133/v134) +2.4 Vesper caps taken from HoR/Ren, gold +4-6%, WR ≈ equal, melee deaths NOT up (Vesper deaths down) -> extra gold doesn't convert. FAR is the hole for every version (v136 far WR ~24%, d400 only 1.4: economy loss, gpc 8.4 & 64% tiny caps vs top10 12.3). v135 pack-v3b 69% vs 44% (n=32, far 5/9 vs 2/9).
10-23 18:55 FAR line (analysis/far-1023/): farswap NOT the cause (far WR v122 42, v132 50, v136 44). far-v1 (no P_HALF on far) -1/-6/-8 local (gems down); far-v2 (cycle cap) -3 deaths +0.81 FAIL. gdiag (instrumented V19, 14 far maps vs rTop1): rich guarded groups (12+ gems) chosen 3%, outscored 87% (half by <6-gem camps); heal-trip term = 63% median of priced rounds. Counterfactual: gold_w .45 -> 11% flips, inc x0.3 -> 36%, both 42%. -> richwolf-v1 (inc x0.4 if gems>=20, team>=2, hp>=70%).
10-23 19:40 richwolf-v1 (cheaper heal term) on v7d -17, deaths +0.91 (filter thread) -> heal term is REAL for 1-2 champs. Rich (20+) captures decoded: T10 r<=250 2.81/team-game vs us 1.68, r251-400 2.17 vs 1.48, r400+ equal; T10 squad 2.31 (36% 3+) vs 1.97, less camp dmg/champ (279 vs 329) with less mhp. Lever = 3-champ squads on rich guarded groups before r300 (far-v3 idea). v10f (richcap far-only) -1: keep richcap everywhere.
10-23 20:15 GUARDED-GROUP SELECTION AXIS CLOSED (5 tries): squad3-v1 on V20 (price 20+ gem guarded groups as 3-champ job before r300, wait for 3rd) -39, gold -26%, deaths +3.4, d150 +0.69; v1b (no wait, 30+, <r250) -31, deaths +3.4. Our champs die in rich guarded camps early -> gap is camp-fighting (dmg/kite/items), not choice. FICHA bot/squad3-v1/. Diag tool: instrumented [gdiag] build, scripts /tmp only.
10-23 20:25 SMALL CAPTURES CLOSED: decoded r150-400 T10 small(<6) 1.67 rich(20+) 3.26 total 9.1 vs us 3.17/2.18/8.7 -> small replace rich 1:1 (fillers, walk 9 vs 14). smallcap-v1 on V20 (unguarded <6 gems x0.6/x0.3 r150-400): -3 / -9, gems +6/+9 but gold -2.7/-8%, deaths +0.55/+1.2. Retry squad3-v1b + smallcap x0.6 only after a camp-fight (bcf/shop) candidate lowers camp damage taken.
USER RULE 10-23 20:35 (via API thread): per-champion behaviour may be coded while the draft stays the same; every rule tied to champion type, falling back to generic if that champion is absent.
USER RULE 10-23 20:36: champion-specific behaviour lives in <champion_name>.h, not main.cpp (thread "Un fichero por campeón" refactors V20).
10-24 00:00 MID r400-800 (far-1023/mid48.py, clash.py; 27 t10 vs 27 ours decoded): we fight 30% more rounds; clashes 59% at camps for both (not camp choice); in our losses clashes start EQUAL (1.72 vs 1.54 champs, hp 84 vs 82) yet 0.65 vs 0.15 deaths/clash (t10 losers 0.40) -> fight execution/power, not map. No map piece.
10-24 00:10 CLASH POWER: in mid r400-800 clashes we start with MORE max hp (2060 vs 1940), same buys, same focus (0.64), but deal ~600 champ dmg/15r win or lose vs t10 winners 875; we win only when rival hits weakly (422). = damage gap (§8.2 hp builds), not execution. HoR in 44% lost / 47% won clashes.

## 10-24 ~04:30 UTC stuck rich groups (map thread), analysis/far-1023/stuck/
- Not a path/reach bug: idle-near-camp (2-5 tiles, no hp drop) v139 364/game vs t10 401 on same maps. Local [fz] build: 69% = fight-camp on a neighbour group, 10% capture elsewhere; rally/need-heal/probe/unreach <1%.
- Real gap = more rich groups untouched to r800 in our games (4.78 vs 3.92), mostly elk+gem(+gold) on swirl/shortcut/collision = farm thread's guarded-group line.
- Chain 5 (n=125): v150 vkite -5, v151 fo2r 0, v152 vkls -6.
- 10-24 06:20 chain 6 (n=125): v153 lshop-v1c +3-6 (far 0-5, eco = base), v154 vgoldfar +6-5 (Vesper far r800 maxhp 1326->1396, held gold 39->47, alive 88->92%), v155 vco +16-15. None passes. Elk+gem untouched groups (own-side elk+gem no wolves) handed to farm thread: analysis/far-1023/stuck/ELKGEM.md.
