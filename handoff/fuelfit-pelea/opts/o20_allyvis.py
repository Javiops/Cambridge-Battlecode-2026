# fuelfit o20 (pelea): vis_champions(ally) was rebuilt (~2.7k: champion_tiles + champion_at per champion) after every
# action of ours (g_kill) and every ward, like the enemy list. Our own champions are always in our vision and our
# actions cannot kill or hide one of them, so the ally list now keys on the round and our own tile only (our tile
# sets the list order, we are in it). Positions / health are still read live from each handle.
# Checked: a debug build compared the cached ally list with a fresh one on every call (52 games, 0 mismatches), and
# same.py 52/52 on the replays.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
a="    if (r[i] == round && kx[i] == X(mp) && ky[i] == Y(mp) && kw[i] == g_ward_n && kk[i] == g_kill) return val[i];"
assert s.count(a)==1
s=s.replace(a,"    if (r[i] == round && kx[i] == X(mp) && ky[i] == Y(mp) && (i == 0 || (kw[i] == g_ward_n && kk[i] == g_kill))) return val[i];  // fuelfit o20: allies ignore our actions")
open(p,'w',newline='').write(s)
