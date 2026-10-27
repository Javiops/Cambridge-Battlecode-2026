import json, gzip, sys, os, collections
W='/tmp/claude-0/w'
idx=json.load(open(W+'/assets/pcassets/replays_t5b/index.json'))
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
R0,R1=int(os.environ.get('R0',21)),int(os.environ.get('R1',100))
TN={0:'Ryth',1:'Ves',2:'Vend',3:'Cas',4:'Iss',5:'Stel',6:'Pri',7:'Mar',8:'Wil',9:'Ren',10:'Varg',11:'Tavi',12:'HoR'}
bot=sys.argv[1]
S={0:collections.Counter(),1:collections.Counter()}
ng=0
for e in idx:
  if e['bot']!=bot: continue
  f=W+'/dec/'+bot+'/'+os.path.basename(e['file']).replace('.repl26a','.json.gz')
  if not os.path.exists(f): continue
  D=json.load(gzip.open(f)); ng+=1; us=0 if e['side']=='a' else 1
  R=D['rounds']; team={c[0]:c[1] for c in R[0]['c']}
  ck=D['ck']
  for i in range(1,len(R)):
    r=R[i]['r']
    if r<R0 or r>R1: continue
    for c in R[i]['c']:
      pc=[x for x in R[i-1]['c'] if x[0]==c[0]][0]
      if c[9] or not pc[9]: continue
      k=0 if team[c[0]]==us else 1
      # look 6 rounds back: first round any foe within 4
      j=i-1
      while j>0 and R[j-1]['r']>=r-15:
        me=[x for x in R[j-1]['c'] if x[0]==c[0]][0]
        if not me[9]: break
        if not any(x[9] and x[1]!=me[1] and cheb((x[3],x[4]),(me[3],me[4]))<=4 for x in R[j-1]['c']): break
        j-=1
      st=R[j]['c']; me=[x for x in st if x[0]==c[0]][0]
      a4=sum(1 for x in st if x[9] and x[1]==me[1] and x[0]!=me[0] and cheb((x[3],x[4]),(me[3],me[4]))<=4)
      a8=sum(1 for x in st if x[9] and x[1]==me[1] and x[0]!=me[0] and cheb((x[3],x[4]),(me[3],me[4]))<=8)
      f4=sum(1 for x in st if x[9] and x[1]!=me[1] and cheb((x[3],x[4]),(me[3],me[4]))<=4)
      f8=sum(1 for x in st if x[9] and x[1]!=me[1] and cheb((x[3],x[4]),(me[3],me[4]))<=8)
      # was it hitting camps in the 3 rounds before contact start
      farming=any(k2.split('>')[0]==str(c[0]) for rr in range(R[j]['r']-3,R[j]['r']+1) for k2 in ck.get(str(rr),{}))
      S[k]['d']+=1; S[k]['a4_%d'%min(a4,2)]+=1; S[k]['f4_%d'%min(f4,3)]+=1
      S[k]['alone8']+= a8==0; S[k]['farming']+=farming; S[k]['hp']+=me[5]/me[6]
      S[k]['len']+=r-R[j]['r']; S[k]['typ_'+TN[c[2]]]+=1
print(bot,ng)
for k in (0,1):
  s=S[k]; d=max(1,s['d'])
  print(['us','top5'][k],'deaths/g %.2f | at contact start: ally<=4 0:%.2f 1:%.2f 2+:%.2f  noally<=8 %.2f foes<=4 1:%.2f 2:%.2f 3+:%.2f | farming %.2f hp %.2f len %.1f'%(
   s['d']/ng,s['a4_0']/d,s['a4_1']/d,s['a4_2']/d,s['alone8']/d,s['f4_1']/d,s['f4_2']/d,s['f4_3']/d,s['farming']/d,s['hp']/d,s['len']/d))
  print('   ',' '.join('%s %.2f'%(t[4:],v/ng) for t,v in s.items() if t.startswith('typ_')))
