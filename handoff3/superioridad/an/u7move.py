import json,gzip,os,collections
W='/tmp/claude-0/w'
idx=json.load(open(W+'/assets/pcassets/replays_c34/index.json'))
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
S={'u7':collections.Counter(),'e1foco':collections.Counter()}
for bot in S:
  for e in idx:
    if e['bot']!=bot: continue
    D=json.load(gzip.open(W+'/dec3/c34'+bot+'/'+os.path.basename(e['file']).replace('.repl26a','.json.gz')))
    us=0 if e['side']=='a' else 1; R=D['rounds']; s=S[bot]
    for i in range(1,len(R)):
      r=R[i]['r']
      if r<153 or r>300: continue
      for c in R[i]['c']:
        if c[1]!=us or not c[9]: continue
        def st(j):
          cc=[x for x in R[j]['c'] if x[0]==c[0]][0]
          if not cc[9]: return None
          fo=sum(1 for x in R[j]['c'] if x[9] and x[1]!=us and cheb((x[3],x[4]),(cc[3],cc[4]))<=6)
          al=1+sum(1 for x in R[j]['c'] if x[9] and x[1]==us and x[0]!=c[0] and cheb((x[3],x[4]),(cc[3],cc[4]))<=6)
          nf=min([cheb((x[3],x[4]),(cc[3],cc[4])) for x in R[j]['c'] if x[9] and x[1]!=us] or [99])
          return cc,fo,al,nf
        a=st(i-2); b=st(i-1)
        if not a or not b: continue
        if not (a[1]>=a[2]+1 and b[1]>=b[2]+1): continue
        # triggered state at i-1 (2 rounds in a row): what happens at i
        now=[x for x in R[i]['c'] if x[0]==c[0]][0]
        s['trig']+=1
        s['moved']+= (now[3],now[4])!=(b[0][3],b[0][4])
        nf=min([cheb((x[3],x[4]),(now[3],now[4])) for x in R[i]['c'] if x[9] and x[1]!=us] or [99])
        s['away']+= nf>b[3]; s['incontact']+= b[3]<=1
        s['nf_le2']+=b[3]<=2
        # dies within 10 rounds?
        dead=any(not [x for x in R[k]['c'] if x[0]==c[0]][0][9] for k in range(i,min(len(R),i+10)))
        s['die10']+=dead
        if b[3]<=2: s['die10_close']+=dead
        else: s['die10_far']+=dead; s['far']+=1
for bot,s in S.items():
  t=max(1,s['trig'])
  print(bot,'triggered champion-rounds %d | moved %.2f, nearest foe grows %.2f | at trigger foe<=2 %.2f | die<=10r %.2f (foe<=2: %.2f, foe>2: %.2f)'%(s['trig'],s['moved']/t,s['away']/t,s['nf_le2']/t,s['die10']/t,s['die10_close']/max(1,s['nf_le2']),s['die10_far']/max(1,s['far'])))
