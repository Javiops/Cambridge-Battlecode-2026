# v11an.py TAG [BASE]: v9an + block cohesion (>=3 of ours within 4 of each other, % of rounds r50-600), 1-vs-N deaths
# (victim with <2 allies within 4 and >=2 rivals within 6) and rounds first hit -> capture of gold groups (gold >= 20) r<=600.
# v9an.py TAG [BASE]: mechanism numbers of rep/TAG (ours = the bot in column A of _a games, B of _b games), decoded in dec/TAG.
# With BASE: first divergence round against dec/BASE (positions), games identical through r29, and fuel markers from stdout.
import json, gzip, os, sys, re, zipfile, collections
W = '/tmp/claude-0/w'
T = sys.argv[1]; B = sys.argv[2] if len(sys.argv) > 2 else None
ch = lambda a, b: max(abs(a[3] - b[3]), abs(a[4] - b[4]))
def load(tag, b):
    return json.load(gzip.open(f'{W}/dec/{tag}/{b}.json.gz'))
def game(D, us):
    R = D['rounds']
    gv = {}
    for k in D['camps']: gv[k[2]] = max(gv.get(k[2], 0), k[5] or 0)
    caps = [(g, t, r) for g, t, r in D['caps'] if t == us and r <= 600]
    big = sum(1 for g, t, r in caps if gv.get(g, 0) >= 40)
    capgems = sum(gv.get(g, 0) for g, t, r in caps)
    spawn = None
    prev = {}
    d = d3 = 0; al4 = al4n = 0; dead_r = 0; coh = cohn = 0; d1n = 0
    grp = {k[0]: k[2] for k in D['camps']}; ggold = {}
    for k in D['camps']: ggold[k[2]] = max(ggold.get(k[2], 0), k[6] or 0)
    goldg = {g for g, v in ggold.items() if v >= 20}
    hits = collections.defaultdict(lambda: collections.defaultdict(set))
    for rr, dd in D['ck'].items():
        rr = int(rr)
        if rr > 600: continue
        for kk, v in dd.items():
            a, ci = map(int, kk.split('>')); g = grp.get(ci)
            if g in goldg and a in {c[0] for c in R[0]['c'] if c[1] == us}: hits[g][rr].add(a)
    gcaps = {g: r for g, t, r in D['caps'] if t == us and g in goldg and r <= 600}
    durs = []
    for g, rs in hits.items():
        rr = sorted(rs); eps = []; cur = [rr[0]]
        for r in rr[1:]:
            if r - cur[-1] <= 15: cur.append(r)
            else: eps.append(cur); cur = [r]
        eps.append(cur)
        for ep in eps:
            if g in gcaps and ep[0] <= gcaps[g] <= ep[-1] + 10: durs.append(gcaps[g] - ep[0])
    g300 = g600 = None
    for row in R:
        r = row['r']
        cs = [c for c in row['c'] if c[1] == us]
        if spawn is None and cs:
            spawn = (sum(c[3] for c in cs) / len(cs), sum(c[4] for c in cs) / len(cs))
        if r == 300 and row.get('sg') is not None: g300 = row['sg'][us] if isinstance(row['sg'], list) else row['sg']
        if r == 600 and row.get('sg') is not None: g600 = row['sg'][us] if isinstance(row['sg'], list) else row['sg']
        if 50 <= r <= 600:
            alive = [c for c in cs if c[9]]
            field = [c for c in alive if max(abs(c[3] - spawn[0]), abs(c[4] - spawn[1])) > 3]
            if len(field) >= 3:
                cohn += 1
                if any(sum(1 for o in field if o is not c and ch(o, c) <= 4) >= 2 for c in field): coh += 1
            for c in alive:
                if max(abs(c[3] - spawn[0]), abs(c[4] - spawn[1])) <= 3: continue
                al4n += 1
                if any(o is not c and ch(o, c) <= 4 for o in alive): al4 += 1
        if 150 < r <= 600:
            dead_r += sum(1 for c in cs if not c[9])
            for c in cs:
                p = prev.get(c[0])
                if p and p[9] and not c[9]:
                    d += 1
                    if sum(1 for a in prev.values() if a[1] != us and a[9] and ch(a, p) <= 6) >= 3: d3 += 1
                    if sum(1 for a in prev.values() if a[1] != us and a[9] and ch(a, p) <= 6) >= 2 and sum(1 for a in prev.values() if a[1] == us and a[9] and a[0] != p[0] and ch(a, p) <= 4) < 2: d1n += 1
        prev = {c[0]: c for c in row['c']}
    return dict(caps=len(caps), big=big, capgems=capgems, deaths=d, d3=d3, al4=al4, al4n=al4n, g300=g300 or 0, g600=g600 or 0, dead_r=dead_r, coh=coh, cohn=cohn, d1n=d1n, gdur=sum(durs), gdn=len(durs))
S = collections.Counter(); n = 0; wins = 0
ident = 0; divs = []; fuelm = 0; fuelm_b = 0; lines = collections.Counter()
log = open(f'{W}/ws/res/{T}.log', errors='replace').read()
for fn in sorted(os.listdir(f'{W}/ws/rep/{T}')):
    if not fn.endswith('.repl26a'): continue
    b = fn[:-8]; side = b[-1]; us = 0 if side == 'a' else 1
    try: D = load(T, b)
    except Exception: continue
    n += 1
    for k, v in game(D, us).items(): S[k] += v
    z = zipfile.ZipFile(f'{W}/ws/rep/{T}/{fn}')
    out = z.read(f'team-{side}.stdout').decode(errors='replace')
    for m in re.finditer(r'\[v(?:9|11)-(\w+)\]', out): lines[m.group(1)] += 1
    fuelm += len(re.findall(r'mode=low-fuel|farm=fuel-wait', out))
    if B:
        try:
            Db = load(B, b)
            div = None
            for x, y in zip(D['rounds'], Db['rounds']):
                if [(c[0], c[3], c[4]) for c in x['c']] != [(c[0], c[3], c[4]) for c in y['c']]: div = x['r']; break
            if div is None: ident += 1
            else: divs.append((b, div))
            zb = zipfile.ZipFile(f'{W}/ws/rep/{B}/{fn}')
            fuelm_b += len(re.findall(r'mode=low-fuel|farm=fuel-wait', zb.read(f'team-{side}.stdout').decode(errors='replace')))
        except Exception as e: pass
m = re.findall(r'WIN \((\w+)\)', log)
print(f'{T}: games {n}, wins (log) {sum(1 for w in m if w == T.rstrip("k").rstrip("e") or w.startswith(T[:2]))}/{len(m)}')
print(f'  allies<=4 off-spawn r50-600: {100*S["al4"]/max(1,S["al4n"]):.1f}%')
print(f'  deaths r151-600: {S["deaths"]/n:.2f} (with 3+ rivals<=6: {S["d3"]/n:.2f}); dead champion-rounds r151-600: {S["dead_r"]/n:.0f}')
print(f'  captures<=600: {S["caps"]/n:.2f}; 40+ gem groups: {S["big"]/n:.2f}; capture gems: {S["capgems"]/n:.0f}')
print(f'  block cohesion (>=3 within 4 of each other, rounds with 3+ in the field, r50-600): {100*S["coh"]/max(1,S["cohn"]):.1f}%; 1-vs-N deaths r151-600: {S["d1n"]/n:.2f}')
print(f'  gold-group (20+ gold) captures<=600 with a hit episode: {S["gdn"]/n:.2f}/game, rounds first hit->capture mean {S["gdur"]/max(1,S["gdn"]):.1f}')
print(f'  gems banked r300: {S["g300"]/n:.0f}; r600: {S["g600"]/n:.0f}')
print(f'  v9 lines per game: ' + ' '.join(f'{k}={v/n:.1f}' for k, v in sorted(lines.items())))
print(f'  fuel markers (low-fuel/fuel-wait status lines): {fuelm}' + (f' (base {fuelm_b})' if B else ''))
if B:
    early = [(b, d) for b, d in divs if d < 30]
    print(f'  vs {B}: identical through r700: {ident}; diverging before r30: {len(early)} {early[:10]}; first divergence median: {sorted(d for _, d in divs)[len(divs)//2] if divs else None}')
