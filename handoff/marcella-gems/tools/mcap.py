import json,glob,sys,os,collections
sys.path.insert(0, "/mnt/project-files/analysis/farm-route-1021/capkind"); from capkind_light import dump
from concurrent.futures import ProcessPoolExecutor
def one(a):
    summ,rep,tn=a
    try: s=json.load(open(summ)); rows=dump(rep)
    except Exception: return None
    if not rows: return None
    kinds=collections.defaultdict(set)
    for c in rows[0]['camps']: kinds[c['group']].add(c['typeName'])
    kind={g:'+'.join(sorted(t)) for g,t in kinds.items()}
    out=collections.Counter()
    for e in s['events']:
        if e['kind']!='gemCollection' or e['owner']['team']!=tn: continue
        nm=e['owner']['name']
        for x in e['entries']:
            r=x['timestamp']['round']
            if r>=150: continue
            g=x['target'].get('id'); k=kind.get(g,'?')
            out[(nm,k,'n')]+=1; out[(nm,k,'gems')]+=int(float(x['value']))
    return out
w=sys.argv[1]
if w=='t10':
    L=json.load(open('/mnt/project-files/online/data/t10_vs_band_1024/index.json'))['games']; R='/mnt/project-files/online/data/replays/'
    J=[(g['summary'],R+g['match']+'.zip','teamA' if g['side']=='a' else 'teamB') for g in L if not g.get('far') and g.get('summary') and '6' in g['draft'] and os.path.exists(R+g['match']+'.zip')]
else: J=[(f[:-5]+'.json',f[:-5]+'.repl26a','teamA' if os.path.basename(f).startswith('A_') else 'teamB') for f in glob.glob(w+'/*/*.json')]
T=collections.Counter(); n=0
with ProcessPoolExecutor(4) as ex:
    for o in ex.map(one,J):
        if o is None: continue
        n+=1; T.update(o)
print(w,n)
by=collections.defaultdict(list)
for (nm,k,f),v in T.items():
    if f=='n': by[nm].append((T[(nm,k,'gems')]/n,v/n,k))
for nm,l in by.items():
    l.sort(reverse=True); print(f"{nm:14s} tot gems {sum(x[0] for x in l):5.1f} caps {sum(x[1] for x in l):4.2f} | "+'  '.join(f"{k}: {c:.2f}x {g:.1f}g" for g,c,k in l[:5]))
K=collections.Counter(); G=collections.Counter()
for (nm,k,f),v in T.items():
    kk='elk+gem' if ('elk' in k and 'gem' in k) else 'wolf+gem' if ('wolf' in k and 'gem' in k) else 'gem_cluster' if k=='gem_cluster' else 'other'
    if f=='n': K[kk]+=v/n
    else: G[kk]+=v/n
print('TEAM r<150 captures/gems:', '  '.join(f"{k} {K[k]:.2f}x {G[k]:.1f}g" for k in K))
