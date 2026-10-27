import json, gzip, sys, os, collections
W='/tmp/claude-0/w'
idx=json.load(open(W+'/assets/pcassets/replays_t5b/index.json'))
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
R0,R1=int(os.environ.get('R0',21)),int(os.environ.get('R1',100))
bot=sys.argv[1]
S={0:collections.Counter(),1:collections.Counter()}; ng=0
for e in idx:
  if e['bot']!=bot: continue
  f=W+'/dec/'+bot+'/'+os.path.basename(e['file']).replace('.repl26a','.json.gz')
  if not os.path.exists(f): continue
  D=json.load(gzip.open(f)); ng+=1; us=0 if e['side']=='a' else 1
  team={c[0]:c[1] for c in D['rounds'][0]['c']}
  cg={k[0]:k[2] for k in D['camps']}
  ggold={k[2]:0 for k in D['camps']}
  for r in range(R0,R1+1):
    hits=collections.defaultdict(set)
    for key in D['ck'].get(str(r),{}):
      a,c=key.split('>'); hits[int(a)].add(cg.get(int(c)))
    for a,gs in hits.items():
      k=0 if team[a]==us else 1
      S[k]['hitr']+=1
      co=any(b!=a and team[b]==team[a] and (hits[b]&gs) for b in hits)
      S[k]['co']+=co
  # captures by team in r21-100 and group value
  for g,t,r in D['caps']:
    if R0<=r<=R1 and t in (0,1):
      S[0 if t==us else 1]['caps']+=1
for k in (0,1):
  s=S[k]; print(['us','top5'][k],'camp-hit champ-rounds/g %.1f  co-farm same group %.2f  captures/g %.2f'%(s['hitr']/ng,s['co']/max(1,s['hitr']),s['caps']/ng))
