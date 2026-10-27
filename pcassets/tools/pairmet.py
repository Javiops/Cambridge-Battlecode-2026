r"""pairmet.py CHAIN TAG [--vs TAG2]: per-pair state metrics of a candidate against the reference (or TAG2's cand games) on the
same pinned games, from replays\<CHAIN>\<TAG>\ (fetch_replays --all) decoded with lab4\viewer\ext.py (cached in
replays\<CHAIN>\_dec\). Our side = the team-<side> files in the bundle.
Metrics (our team): deaths r1-150 / r151-300, gems (submitted + carried) at r150 / r300, kills r151-300.
Usage: python -I pairmet.py c34 o101 --vs e1foco"""
import gzip, json, os, re, subprocess, sys, zipfile
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.join(H, '..', '..', 'lab4', 'viewer', 'ext.py'); PY = sys.executable
a = sys.argv[1:]; chain, tag = a[0], a[1]; vs = a[a.index('--vs') + 1] if '--vs' in a else None
DEC = os.path.join(H, 'replays', chain, '_dec3'); os.makedirs(DEC, exist_ok=True)     # _dec3: ctc + fixed camp spawn/reward (replaydump 28-10)

def games(t, who):
    d = os.path.join(H, 'replays', chain, t); out = {}
    for f in json.load(open(os.path.join(d, 'index.json')))['files']:
        if f['who'] != who or not f.get('file'): continue
        key = f['file'][len(who) + 1:]; out[key] = (os.path.join(d, f['file']), f['match'], f['result'])
    return out

def dec(zp, mid):
    gz = os.path.join(DEC, mid + '.json.gz')
    if not os.path.exists(gz): subprocess.run([PY, '-I', EXT, zp, gz], check=True, capture_output=True, timeout=900)
    side = {m.group(1) for n in zipfile.ZipFile(zp).namelist() for m in [re.match(r'team-([ab])\.', n)] if m}.pop()
    return gz, 0 if side == 'a' else 1

def met(gz, us):
    d = json.load(gzip.open(gz)); R = {r['r']: r for r in d['rounds']}
    def gems(r):
        while r not in R and r > 0: r -= 1
        if r not in R: return None
        x = R[r]; return (x['sg'] or [0, 0])[us] + sum(c[7] for c in x['c'] if c[1] == us)
    dth = {1: 0, 2: 0}; kil = 0; k100 = 0; d100 = 0; ves = 0; prev = None
    for r in sorted(R):
        if r > 300: break
        if prev:
            pa = {c[0]: c for c in prev['c']}
            for c in R[r]['c']:
                p = pa.get(c[0])
                if p and p[9] and not c[9]:
                    if c[1] == us:
                        dth[1 if r <= 150 else 2] += 1; ves += c[2] == 1; d100 += 21 <= r <= 100
                    else:
                        kil += r > 150; k100 += 21 <= r <= 100
        prev = R[r]
    # reward claims of our team by group class (camp types: 0 hp1350 wolf?, 1 hp2400 elk?, 2/3 hp120 small, 4 hp20000, 5 hp5000)
    gt = {}
    for c in d['camps']: gt.setdefault(c[2], set()).add(c[1]); gg = {c[2]: c[5] for c in d['camps']}
    def cls(g):
        t = gt.get(g, set())
        return 'goldonly' if not gg.get(g) else 'boss' if 4 in t or 5 in t else 'elk' if 1 in t else 'wolf' if 0 in t else 'small'
    cl = {f'cl_{k}': 0 for k in ('goldonly', 'boss', 'elk', 'wolf', 'small')}
    for g, t, r in d['caps']:
        if t == us and r <= 600: cl['cl_' + cls(g)] += 1
    extra = cl
    # jackpot (farm rule 27-10): group whose summed rewardGems >= 50% of the map's; captures = its reward claims by team
    val = {}
    for c in d['camps']: val[c[2]] = val.get(c[2], 0) + (c[5] or 0)
    tot = sum(val.values()); big = max(val, key=val.get) if val else None
    if big is None or not tot or val[big] < tot / 2:
        return dict(extra, d150=dth[1], d300=dth[2], k300=kil, k100=k100, d100=d100, ves=ves, g150=gems(150), g300=gems(300),
                    jp=False, jp_us=None, jp_them=None, jp_first=None, jp_us_n=None, jp_them_n=None, jc_us_n=None, jc_them_n=None)
    ev = [cp for cp in d['caps'] if cp[0] == big and cp[1] in (0, 1)]                 # reward claims
    tc = [cp for cp in d.get('ctc', []) if cp[0] == big and cp[1] in (0, 1)]          # captureTeam changes to a team
    first = {t: next((cp[2] for cp in tc if cp[1] == t), None) for t in (0, 1)}
    return dict(extra, d150=dth[1], d300=dth[2], k300=kil, k100=k100, d100=d100, ves=ves, g150=gems(150), g300=gems(300),
                jp=True, jp_us=first[us], jp_them=first[1 - us], jp_first=bool(tc) and tc[0][1] == us,
                jp_us_n=sum(cp[1] == us for cp in tc), jp_them_n=sum(cp[1] != us for cp in tc),
                jc_us_n=sum(cp[1] == us for cp in ev), jc_them_n=sum(cp[1] != us for cp in ev))

A = games(tag, 'cand'); B = games(vs, 'cand') if vs else games(tag, 'ref')
keys = sorted(set(A) & set(B))
def one(k):
    out = []
    for zp, mid, res in (A[k], B[k]):
        gz, us = dec(zp, mid); out.append(dict(met(gz, us), win=res == 'win'))
    return k, out
with ThreadPoolExecutor(6) as ex: rows = list(ex.map(one, keys))
lab = vs or 'kvvl'
def avg(i, f):
    v = [r[1][i][f] for r in rows if r[1][i][f] is not None]
    if f in ('jp_us', 'jp_them'): return sorted(v)[len(v) // 2] if v else float('nan')     # median round
    return sum(v) / len(v) if v else float('nan')
print(f'{chain}: {tag} vs {lab}, {len(rows)} pairs (our team, per game)')
for f, n in (('k100', 'kills r21-100'), ('d100', 'deaths r21-100'), ('ves', 'Vesper dth r1-300'), ('d150', 'deaths r1-150'), ('d300', 'deaths r151-300'), ('k300', 'kills r151-300'), ('g150', 'gems r150'), ('g300', 'gems r300'), ('jp', 'jackpot map'), ('jp_us', 'jackpot 1st cap us'), ('jp_them', 'jackpot 1st cap them'), ('jp_first', 'jackpot ours first'), ('jp_us_n', 'jackpot captures us'), ('jp_them_n', 'jackpot captures them'), ('jc_us_n', 'jackpot claims us'), ('jc_them_n', 'jackpot claims them'), ('cl_goldonly', 'claims gold-only r600'), ('cl_wolf', 'claims wolf r600'), ('cl_elk', 'claims elk r600'), ('cl_small', 'claims small r600'), ('cl_boss', 'claims boss r600'), ('win', 'wins')):
    print(f'  {n:16s} {tag} {avg(0, f):6.2f}   {lab} {avg(1, f):6.2f}')
json.dump([dict(game=k, cand=x[0], base=x[1]) for k, x in rows], open(os.path.join(H, 'data', 'chains', chain, f'pairmet_{tag}_vs_{lab}.json'), 'w'), indent=0)
