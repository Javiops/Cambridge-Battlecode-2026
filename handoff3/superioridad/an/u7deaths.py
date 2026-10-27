import json,gzip,os,collections,sys
W='/tmp/claude-0/w'
idx=json.load(open(W+'/assets/pcassets/replays_c34/index.json'))
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
TN={0:'Ryth',1:'Ves',2:'Vend',3:'Cas',4:'Iss',5:'Stel',6:'Pri',7:'Mar',8:'Wil',9:'Ren',10:'Varg',11:'Tavi',12:'HoR'}
u={(e['map'],e['rival'],e['side']):e for e in idx if e['bot']=='u7'}
f={(e['map'],e['rival'],e['side']):e for e in idx if e['bot']=='e1foco'}
sel=sys.argv[1]  # lostonly / all
def load(bot,e):
  return json.load(gzip.open(W+'/dec3/c34'+bot+'/'+os.path.basename(e['file']).replace('.repl26a','.json.gz')))
def deaths(D,us):
  R=D['rounds']; out=[]
  sp=[(c[3],c[4]) for c in R[0]['c'] if c[1]==us]; spc=(sum(x for x,_ in sp)/len(sp),sum(y for _,y in sp)/len(sp))
  for i in range(1,len(R)):
    r=R[i]['r']
    if r<151 or r>300: continue
    for c in R[i]['c']:
      if c[1]!=us: continue
      pc=[x for x in R[i-1]['c'] if x[0]==c[0]][0]
      if c[9] or not pc[9]: continue
      # trigger history over previous 10 rounds
      trig=0; first=None; hist=[]
      for j in range(max(1,i-10),i):
        st=R[j]['c']; me=[x for x in st if x[0]==c[0]][0]
        if not me[9]: continue
        fo=sum(1 for x in st if x[9] and x[1]!=us and cheb((x[3],x[4]),(me[3],me[4]))<=6)
        al=1+sum(1 for x in st if x[9] and x[1]==us and x[0]!=c[0] and cheb((x[3],x[4]),(me[3],me[4]))<=6)
        na=min([cheb((x[3],x[4]),(me[3],me[4])) for x in st if x[9] and x[1]==us and x[0]!=c[0]] or [99])
        nf=min([cheb((x[3],x[4]),(me[3],me[4])) for x in st if x[9] and x[1]!=us] or [99])
        hist.append((R[j]['r'],fo,al,na,nf,int(100*me[5]/me[6]),cheb((me[3],me[4]),spc)))
      # consecutive trigger rounds
      run=0;mx=0
      for h in hist:
        run = run+1 if h[1]>=h[2]+1 else 0; mx=max(mx,run)
      out.append((r,TN[c[2]],mx,hist))
  return out
tot=collections.Counter()
for k in u:
  ue,fe=u[k],f[k]
  if sel=='lost' and not (ue['result']=='loss' and fe['result']=='win'): continue
  us=0 if ue['side']=='a' else 1
  du=deaths(load('u7',ue),us); df=deaths(load('e1foco',fe),us)
  tot['g']+=1; tot['du']+=len(du); tot['df']+=len(df)
  tot['du_trig']+=sum(1 for d in du if d[2]>=2); tot['df_trig']+=sum(1 for d in df if d[2]>=2)
  if sel=='lost':
    print('==',k,'deaths r151-300 u7',len(du),'e1foco',len(df))
    for r,t,mx,h in du:
      print('  u7 r%d %s trig-run %d | last rounds (r,foes6,allies6,nearAlly,nearFoe,hp%%,homeDist):'%(r,t,mx), ' '.join('%d:%d/%d a%d f%d %d%% h%d'%x for x in h[-6:]))
print(dict(tot))
