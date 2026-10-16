import sys, os, glob, json, hashlib, subprocess, collections
sys.path.insert(0,'/home/user/cambridge-battlecode-2026/tools'); import ab
os.chdir('/home/user/cambridge-battlecode-2026')
base, cand, P = sys.argv[1], sys.argv[2], sys.argv[3]
opps=[f'bots/{P}sp_{n}' for n in 'castera casterh hunt centre farm'.split()]
ver=subprocess.run([ab.CLI,'--version'],capture_output=True,text=True,env=ab.ENV).stdout.strip()
maps=sorted(glob.glob('maps/*.map26a'))
h={b:ab.sha(ab.wasm_of(b)) for b in [base,cand]+opps}
def get(b,o,m,side):
    hm=hashlib.sha256((ab.sha(m)+ver).encode()).hexdigest()[:8]
    x,y=(b,o) if side=='A' else (o,b)
    r=json.load(open(f'out/ab-cache/{h[x]}_{h[y]}_{hm}.json')); me=0 if side=='A' else 1
    return r['outcome']==('teamA' if me==0 else 'teamB'), r['gems'][me], r['deaths'][me], r['deaths'][1-me]
pm=collections.defaultdict(lambda:[0,0,0,0,0,0,0])
for m in maps:
  for o in opps:
    for s in 'AB':
      a=get(base,o,m,s); c=get(cand,o,m,s); k=os.path.basename(m)[:-7]; t=pm[k]
      t[0]+= c[0] and not a[0]; t[1]+= a[0] and not c[0]; t[2]+=c[1]-a[1]; t[3]+=c[2]-a[2]; t[4]+=c[3]-a[3]; t[5]+=1
print(f'{cand} vs {base} on {P}: map  won-lost  dgems/game  dour_deaths  dtheir_deaths')
for k,t in sorted(pm.items()): print(f'  {k:14s} {t[0]:2d}-{t[1]:<2d}  {t[2]/t[5]:+7.0f} {t[3]/t[5]:+6.1f} {t[4]/t[5]:+6.1f}')
