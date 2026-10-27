# loc.py TAG: decode rep/TAG (r0-200) and print pack metrics for side A's bot (team 0 in *_a, team 1 in *_b)
import json, gzip, sys, os, collections, subprocess, glob
W='/tmp/claude-0/w'; T=sys.argv[1]; R0,R1=int(os.environ.get('R0',21)),int(os.environ.get('R1',150))
out=W+'/decl/'+T; os.makedirs(out,exist_ok=True)
env=dict(os.environ, MAXR=os.environ.get('MAXR','200'), CAMBC_VIS_WASM=W+'/champ/handoff/replay2/v2_0_0-hWOQ1R8f.wasm')
fs=sorted(glob.glob(W+'/ws/rep/'+T+'/*.repl26a'))
todo=[f for f in fs if not os.path.exists(out+'/'+os.path.basename(f)+'.json.gz')]
if todo:
  args=[]; [args.extend([f,out+'/'+os.path.basename(f)+'.json.gz']) for f in todo]
  subprocess.run(['xargs','-P4','-n2','python3',W+'/viewer/ext.py'],input='\n'.join(args),text=True,env=env,stdout=subprocess.DEVNULL)
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
S={0:collections.Counter(),1:collections.Counter()}; ng=0
for f in fs:
  g=out+'/'+os.path.basename(f)+'.json.gz'
  if not os.path.exists(g): continue
  D=json.load(gzip.open(g)); ng+=1; us=0 if f.endswith('_a.repl26a') else 1
  R=D['rounds']; team={c[0]:c[1] for c in R[0]['c']}
  spc={}
  for t in (0,1):
    p=[(c[3],c[4]) for c in R[0]['c'] if c[1]==t]; spc[t]=(sum(x for x,_ in p)/len(p),sum(y for _,y in p)/len(p))
  cg={k[0]:k[2] for k in D['camps']}
  for i,rd in enumerate(R):
    r=rd['r']
    if r<R0 or r>R1: continue
    al=[c for c in rd['c'] if c[9]]
    for t in (0,1):
      k=0 if t==us else 1
      mine=[c for c in al if c[1]==t]
      for c in mine:
        if cheb((c[3],c[4]),spc[t])<=4: continue
        dn=min([cheb((c[3],c[4]),(o[3],o[4])) for o in mine if o[0]!=c[0]] or [99])
        S[k]['fr']+=1; S[k]['nn2']+=dn<=2; S[k]['nn4']+=dn<=4
    hits=collections.defaultdict(set)
    for key in D['ck'].get(str(r),{}):
      a,c=key.split('>'); hits[int(a)].add(cg.get(int(c)))
    for a,gs in hits.items():
      k=0 if team[a]==us else 1
      S[k]['hit']+=1; S[k]['co']+=any(b!=a and team[b]==team[a] and (hits[b]&gs) for b in hits)
    if i>0:
      for c in rd['c']:
        pc=[x for x in R[i-1]['c'] if x[0]==c[0]][0]
        k=0 if team[c[0]]==us else 1
        if not c[9]: S[k]['deadr']+=1
        if c[9] or not pc[9]: continue
        S[k]['death']+=1
        a8=sum(1 for x in R[max(0,i-4)]['c'] if x[9] and x[1]==c[1] and x[0]!=c[0] and cheb((x[3],x[4]),(pc[3],pc[4]))<=8)
        S[k]['alone_death']+=a8==0
  elkn=collections.Counter(k[2] for k in D['camps'] if k[1]==1)
  for gid,t,r in D['caps']:
    if R0<=r<=R1 and t in (0,1):
      S[0 if t==us else 1]['caps']+=1
      if elkn[gid]>=2: S[0 if t==us else 1]['elk2']+=1
  sg=[rd for rd in R if rd['r']==R1]
  if sg and sg[0].get('sg'): S[0]['gems']+=sg[0]['sg'][us]; S[1]['gems']+=sg[0]['sg'][1-us]
print(T,'games',ng,'r%d-%d'%(R0,R1))
for k in (0,1):
  s=S[k]; fr=max(1,s['fr'])
  print(' ',['A','B'][k],'ally<=2 %.2f <=4 %.2f cofarm %.2f deaths/g %.2f alone-deaths/g %.2f deadrounds/g %.0f caps/g %.1f elk2/g %.2f gems@R1 %.1f'%(
    s['nn2']/fr,s['nn4']/fr,s['co']/max(1,s['hit']),s['death']/ng,s['alone_death']/ng,s['deadr']/ng,s['caps']/ng,s['elk2']/ng,s['gems']/ng))
