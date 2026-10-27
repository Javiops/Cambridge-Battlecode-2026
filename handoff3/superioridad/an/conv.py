import json, gzip, sys, os, collections
W='/tmp/claude-0/w'
idx=json.load(open(W+'/assets/pcassets/replays_t5b/index.json'))
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
R0,R1=int(os.environ.get('R0',40)),int(os.environ.get('R1',150))
bot=sys.argv[1]; ng=0
S={0:collections.Counter(),1:collections.Counter()}
for e in idx:
  if e['bot']!=bot: continue
  f=W+'/dec/'+bot+'/'+os.path.basename(e['file']).replace('.repl26a','.json.gz')
  if not os.path.exists(f): continue
  D=json.load(gzip.open(f)); ng+=1; us=0 if e['side']=='a' else 1
  R=D['rounds']; byr={rd['r']:rd for rd in R}
  last={}  # (a,b) pair last contact round
  for rd in R:
    r=rd['r']
    if r<R0 or r>R1: continue
    al=[c for c in rd['c'] if c[9]]
    for a in al:
      if a[1]!=us: continue
      for b in al:
        if b[1]==us: continue
        if cheb((a[3],a[4]),(b[3],b[4]))>4: continue
        key=(a[0],b[0]); new = r-last.get(key,-99)>10; last[key]=r
        if not new: continue
        # episode start for both a (us) and b (them): count allies of each within 4 now and within 4 of the contact point at r+3; allies 5-10 away now
        cp=((a[3]+b[3])/2,(a[4]+b[4])/2)
        for me,k in ((a,0),(b,1)):
          t=me[1]
          n0=sum(1 for c in al if c[1]==t and cheb((c[3],c[4]),cp)<=4)
          m0=sum(1 for c in al if c[1]!=t and cheb((c[3],c[4]),cp)<=4)
          mid=sum(1 for c in al if c[1]==t and 4<cheb((c[3],c[4]),cp)<=10)
          r3=byr.get(r+3)
          if not r3: continue
          n3=sum(1 for c in r3['c'] if c[9] and c[1]==t and cheb((c[3],c[4]),cp)<=4)
          S[k]['ep']+=1; S[k]['n0']+=n0; S[k]['m0']+=m0; S[k]['n3']+=n3; S[k]['mid']+=mid
          S[k]['up0']+=n0>m0; S[k]['down0']+=n0<m0
          if mid: S[k]['midep']+=1; S[k]['gain_mid']+=n3-n0
          me3=[c for c in r3['c'] if c[0]==me[0]][0]
          S[k]['stay']+= me3[9] and cheb((me3[3],me3[4]),cp)<=4
          if n0<m0: S[k]['down_stay']+= me3[9] and cheb((me3[3],me3[4]),cp)<=4
print(bot,ng,R0,R1)
for k in (0,1):
  s=S[k]; ep=max(1,s['ep'])
  print(['us','top5'][k],'pair-contacts/g %.1f  at start own<=4 %.2f foe<=4 %.2f up %.2f down %.2f | allies 5-10 away %.2f; when any, gain in 3 rounds %.2f | stay %.2f, stay when down %.2f'%(
    s['ep']/ng,s['n0']/ep,s['m0']/ep,s['up0']/ep,s['down0']/ep,s['mid']/ep,s['gain_mid']/max(1,s['midep']),s['stay']/ep,s['down_stay']/max(1,s['down0'])))
