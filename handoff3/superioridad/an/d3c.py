import json, gzip, sys, os, collections
W='/tmp/claude-0/w'
idx=json.load(open(W+'/assets/pcassets/replays_c34/index.json'))
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
TN={0:'Ryth',1:'Ves',2:'Vend',3:'Cas',4:'Iss',5:'Stel',6:'Pri',7:'Mar',8:'Wil',9:'Ren',10:'Varg',11:'Tavi',12:'HoR'}
bot=sys.argv[1]; d=sys.argv[2] if len(sys.argv)>2 else 'dec3'
WIN=[(21,100),(101,150),(151,300)]
S={(k,w):collections.Counter() for k in (0,1) for w in range(3)}; ng=0
for e in idx:
  if e['bot']!=bot: continue
  if len(sys.argv)>3 and e['result']!=sys.argv[3]: continue
  f=W+'/'+d+'/c34'+bot+'/'+os.path.basename(e['file']).replace('.repl26a','.json.gz')
  if not os.path.exists(f): continue
  D=json.load(gzip.open(f)); ng+=1; us=0 if e['side']=='a' else 1
  R=D['rounds']; team={c[0]:c[1] for c in R[0]['c']}
  spc={}
  for t in (0,1):
    p=[(c[3],c[4]) for c in R[0]['c'] if c[1]==t]; spc[t]=(sum(x for x,_ in p)/len(p),sum(y for _,y in p)/len(p))
  for i in range(1,len(R)):
    r=R[i]['r']
    w=[j for j,(a,b) in enumerate(WIN) if a<=r<=b]
    if not w: continue
    w=w[0]
    for c in R[i]['c']:
      k=0 if team[c[0]]==us else 1
      s=S[(k,w)]
      if not c[9]: s['deadr']+=1; continue
      pc=[x for x in R[i-1]['c'] if x[0]==c[0]][0]
    for c in R[i]['c']:
      pc=[x for x in R[i-1]['c'] if x[0]==c[0]][0]
      if c[9] or not pc[9]: continue
      k=0 if team[c[0]]==us else 1; s=S[(k,w)]
      s['death']+=1
      dch=dcamp=0
      for rr in range(r-3,r+1):
        for key,v in D['cc'].get(str(rr),{}).items():
          if key.split('>')[1]==str(c[0]): dch+=v
        for key,v in D['kc'].get(str(rr),{}).items():
          if key.split('>')[1]==str(c[0]): dcamp+=v
      s['by_camp']+= dcamp>dch
      st=R[max(0,i-4)]['c']; me=[x for x in st if x[0]==c[0]][0]
      a6=sum(1 for x in st if x[9] and x[1]==c[1] and x[0]!=c[0] and cheb((x[3],x[4]),(me[3],me[4]))<=6)
      f6=sum(1 for x in st if x[9] and x[1]!=c[1] and cheb((x[3],x[4]),(me[3],me[4]))<=6)
      s['alone']+=a6==0; s['outnum']+=f6>a6+1
      s['gems']+=pc[7]
      st10=R[max(0,i-10)]['c']; m10=[x for x in st10 if x[0]==c[0]][0]
      na=min([cheb((x[3],x[4]),(m10[3],m10[4])) for x in st10 if x[9] and x[1]==c[1] and x[0]!=c[0]] or [30])
      s['na10']+=min(na,30); s['na10_le3']+=na<=3
      s['enemyside']+= cheb((pc[3],pc[4]),spc[1-c[1]])<cheb((pc[3],pc[4]),spc[c[1]])
      s['t_'+TN[c[2]]]+=1
print(bot,ng)
for w,(a,b) in enumerate(WIN):
  for k in (0,1):
    s=S[(k,w)]; dd=max(1,s['death'])
    print('r%d-%d %-4s deaths/g %.2f deadrounds/g %.0f | by camp %.2f alone(<=6) %.2f outnumbered %.2f on enemy side %.2f gems carried %.1f nearest-ally-10r %.1f (<=3 %.2f) | %s'%(a,b,['us','top5'][k],s['death']/ng,s['deadr']/ng,s['by_camp']/dd,s['alone']/dd,s['outnum']/dd,s['enemyside']/dd,s['gems']/dd,s['na10']/dd,s['na10_le3']/dd,
      ' '.join('%s %.2f'%(t[2:],v/ng) for t,v in sorted(s.items()) if t.startswith('t_'))))
