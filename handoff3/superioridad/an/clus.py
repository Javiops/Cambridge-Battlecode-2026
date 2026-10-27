import json, gzip, sys, os, collections
W='/tmp/claude-0/w'
idx=json.load(open(W+'/assets/pcassets/replays_t5b/index.json'))
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
R0,R1=int(os.environ.get('R0',21)),int(os.environ.get('R1',100)); L=int(os.environ.get('L',3))
TN={0:'Ryth',1:'Ves',2:'Vend',3:'Cas',4:'Iss',5:'Stel',6:'Pri',7:'Mar',8:'Wil',9:'Ren',10:'Varg',11:'Tavi',12:'HoR'}
bot=sys.argv[1]
CS={0:collections.Counter(),1:collections.Counter()}; PT={0:collections.Counter(),1:collections.Counter()}
ALONE={0:collections.Counter(),1:collections.Counter()}; TOT={0:collections.Counter(),1:collections.Counter()}
ng=0
for e in idx:
  if e['bot']!=bot: continue
  f=W+'/dec/'+bot+'/'+os.path.basename(e['file']).replace('.repl26a','.json.gz')
  if not os.path.exists(f): continue
  D=json.load(gzip.open(f)); ng+=1; us=0 if e['side']=='a' else 1
  rounds=D['rounds']
  for rd in rounds:
    if rd['r']<R0 or rd['r']>R1: continue
    for t in (0,1):
      k=0 if t==us else 1
      m=[c for c in rd['c'] if c[1]==t and c[9]]
      par={c[0]:c[0] for c in m}
      def fd(i):
        while par[i]!=i: i=par[i]
        return i
      for a in m:
        for b in m:
          if a[0]<b[0] and cheb((a[3],a[4]),(b[3],b[4]))<=L: par[fd(a[0])]=fd(b[0])
      g=collections.defaultdict(list)
      for c in m: g[fd(c[0])].append(c)
      sizes=tuple(sorted((len(v) for v in g.values()),reverse=True))
      CS[k][sizes]+=1
      for v in g.values():
        for c in v:
          TOT[k][TN[c[2]]]+=1
          if len(v)==1: ALONE[k][TN[c[2]]]+=1
        if len(v)==2: PT[k]['+'.join(sorted(TN[c[2]] for c in v))]+=1
print(bot,ng,'link',L)
for k in (0,1):
  n=sum(CS[k].values())
  print(['us','top5'][k],' '.join('%s:%.2f'%(''.join(map(str,s)),v/n) for s,v in CS[k].most_common(8)))
  print('  alone frac', ' '.join('%s %.2f(%d)'%(t,ALONE[k][t]/TOT[k][t],TOT[k][t]//ng) for t in TOT[k]))
  print('  pairs', ' '.join('%s %.1f'%(p,v/ng) for p,v in PT[k].most_common(8)))
