# fuelfit o35 (altar fields by map size; after o32): br_static_step built P_BRC_PER = 2 altar fields a turn from round 3; each
# field is a compute with cap 400, ~24k on a 100x100 map, so rounds 3-7 there cost 20-48k on top of the first
# choose_target (farm thread profile). Now one field a turn when the map has more than 2500 tiles (and 2 otherwise).
# Expected exact (same argument as o32: every caller needs gems > 0, which no champion has that early); checked with
# same.py on the 56 far games.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
a="    for (int k = 0; k < P_BRC_PER && g_brs.built < static_cast<int>(s.altars.size()); ++k) {"
assert s.count(a)==1
s=s.replace(a,"""    static const int per = (static_cast<long>(bc::map::width()) * static_cast<long>(bc::map::height()) > 2500) ? 1 : P_BRC_PER;  // fuelfit o35
    for (int k = 0; k < per && g_brs.built < static_cast<int>(s.altars.size()); ++k) {""")
open(p,'w',newline='').write(s)
