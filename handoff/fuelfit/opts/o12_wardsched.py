# fuelfit o12 (changes decisions a little): the ward search runs only on even rounds. Its fixed part (chebyshev draw,
# four bitboard ops, the vision query, two positions lists) is 5-8k and it ran every turn the cooldown was over; with
# the candidates (o10) it was 8-15k in heavy turns. Wards last many rounds, so placing one a round later costs little.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
a="    if (!has_bush || !fuel_ok(P_WARD_FUEL)) return;\n"
assert s.count(a)==1
s=s.replace(a,a+"    if (static_cast<int>(bc::round_number()) % 2) return;  // fuelfit o12: even rounds only\n")
open(p,'w',newline='').write(s)
