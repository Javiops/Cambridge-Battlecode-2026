# fuelfit o03: an attack or an ability use can kill a visible champion mid-turn, so the vis_champions key also counts
# those actions (dm_use() ticks g_kill at every .attack( / .use( site).
import sys,glob,re
d=sys.argv[1]
for f in glob.glob(d+'/*.cpp')+glob.glob(d+'/*.h'):
    s=open(f,newline='').read(); o=s
    s=re.sub(r'(?<![\w\.])((?:me|ab|abs\[k\]|ability|lock|a|c)(?:\[k\])?)\.(use|attack)\(', lambda m: f'dm_use({m.group(1)}).{m.group(2)}(', s)
    if s!=o: open(f,'w',newline='').write(s)
p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,a; s=s.replace(a,b)
rep("int g_ward_n = 0;\nconst std::vector<bc::champion>& vis_champions(bc::team side) {\n    static int r[2] = {-1, -1}, kx[2], ky[2], kw[2];",
"""int g_ward_n = 0, g_kill = 0;
template <class T> T& dm_use(T& x) { ++g_kill; return x; }
template <class T> const T& dm_use(const T& x) { ++g_kill; return x; }
const std::vector<bc::champion>& vis_champions(bc::team side) {
    static int r[2] = {-1, -1}, kx[2], ky[2], kw[2], kk[2];""")
rep("    if (r[i] == round && kx[i] == X(mp) && ky[i] == Y(mp) && kw[i] == g_ward_n) return val[i];","    if (r[i] == round && kx[i] == X(mp) && ky[i] == Y(mp) && kw[i] == g_ward_n && kk[i] == g_kill) return val[i];")
rep("    r[i] = round; kx[i] = X(mp); ky[i] = Y(mp); kw[i] = g_ward_n;","    r[i] = round; kx[i] = X(mp); ky[i] = Y(mp); kw[i] = g_ward_n; kk[i] = g_kill;")
open(p,'w',newline='').write(s)
