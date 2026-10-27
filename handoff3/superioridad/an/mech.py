import json, gzip, sys, os, collections, math
W='/tmp/claude-0/w'
idx=json.load(open(W+'/assets/pcassets/replays_t5b/index.json'))
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
R0,R1=int(os.environ.get('R0',21)),int(os.environ.get('R1',100))
bots=sys.argv[1:] or ['e1']
for bot in bots:
  S={0:collections.Counter(),1:collections.Counter()}  # 0 = us, 1 = top5
  H={0:collections.defaultdict(list),1:collections.defaultdict(list)}
  ng=0
  for e in idx:
    if e['bot']!=bot: continue
    f=W+'/dec/'+bot+'/'+os.path.basename(e['file']).replace('.repl26a','.json.gz')
    if not os.path.exists(f): continue
    D=json.load(gzip.open(f)); ng+=1
    us=0 if e['side']=='a' else 1
    rounds=D['rounds']
    spawn={c[0]:(c[3],c[4]) for c in rounds[0]['c']}
    team={c[0]:c[1] for c in rounds[0]['c']}
    sp={t:[spawn[i] for i in spawn if team[i]==t] for t in (0,1)}
    spc={t:(sum(p[0] for p in sp[t])/len(sp[t]),sum(p[1] for p in sp[t])/len(sp[t])) for t in (0,1)}
    prevdead=set()
    prev_contact=set()
    for rd in rounds:
      r=rd['r']
      if r<R0 or r>R1: 
        prevdead={c[0] for c in rd['c'] if not c[9]}; continue
      al=[c for c in rd['c'] if c[9]]
      pos={c[0]:(c[3],c[4]) for c in al}
      for t in (0,1):
        k=0 if t==us else 1
        mine=[c for c in al if c[1]==t]
        # field champs: farther than 3 from own spawn centre
        fld=[c for c in mine if cheb((c[3],c[4]),spc[t])>4]
        for c in fld:
          dn=min([cheb((c[3],c[4]),(o[3],o[4])) for o in mine if o[0]!=c[0]] or [99])
          S[k]['fr']+=1
          for th in (2,4,6,10):
            if dn<=th: S[k]['nn%d'%th]+=1
          # half: closer to own spawn than enemy?
          de=cheb((c[3],c[4]),spc[1-t]); do=cheb((c[3],c[4]),spc[t])
          if de<do: S[k]['enemyhalf']+=1
      # contacts: cross pairs within 4
      contact=set()
      for a in al:
        for b in al:
          if a[1]==0 and b[1]==1 and cheb((a[3],a[4]),(b[3],b[4]))<=4: contact.add(a[0]); contact.add(b[0])
      # components via dist<=6 links among all champs, seeded by contact
      if contact:
        comp={}
        ids=[c[0] for c in al]
        par={i:i for i in ids}
        def fd(i):
          while par[i]!=i: par[i]=par[par[i]]; i=par[i]
          return i
        for a in al:
          for b in al:
            if a[0]<b[0] and cheb((a[3],a[4]),(b[3],b[4]))<=5: par[fd(a[0])]=fd(b[0])
        groups=collections.defaultdict(list)
        for i in ids: groups[fd(i)].append(i)
        for g in groups.values():
          if not (set(g)&contact): continue
          new = not (set(g)&prev_contact)
          if not new: continue
          for t in (0,1):
            k=0 if t==us else 1
            n=sum(1 for i in g if team[i]==t); m=len(g)-n
            # wider: own alive within 10 of component centroid
            cx=sum(pos[i][0] for i in g)/len(g); cy=sum(pos[i][1] for i in g)/len(g)
            n10=sum(1 for c in al if c[1]==t and cheb((c[3],c[4]),(cx,cy))<=10)
            m10=sum(1 for c in al if c[1]!=t and cheb((c[3],c[4]),(cx,cy))<=10)
            st='up' if n>m else ('even' if n==m else 'down')
            S[k]['ep']+=1; S[k]['ep_'+st]+=1
            S[k]['ep10_'+('up' if n10>m10 else ('even' if n10==m10 else 'down'))]+=1
            # location: closer to own spawn?
            do=cheb((cx,cy),spc[t]); de=cheb((cx,cy),spc[1-t])
            S[k]['ep_ownhalf']+=do<de
            if st=='up': S[k]['up_ownhalf']+=do<de
            if st=='down': S[k]['down_ownhalf']+=do<de
            H[k]['nm'].append((n,m,n10,m10))
      prev_contact=contact
      # deaths
      for c in rd['c']:
        if not c[9] and c[0] not in prevdead:
          k=0 if team[c[0]]==us else 1
          S[k]['death']+=1
          # local numbers at death (previous positions approximated by current alive)
      prevdead={c[0] for c in rd['c'] if not c[9]}
  print('==',bot,'games',ng,'rounds',R0,R1)
  for k,name in ((0,'us'),(1,'top5')):
    s=S[k]; fr=max(1,s['fr']); ep=max(1,s['ep'])
    print(name, 'per game: ep %.2f up %.2f even %.2f down %.2f | ep10 up %.2f even %.2f down %.2f | deaths %.2f'%(
      s['ep']/ng,s['ep_up']/ng,s['ep_even']/ng,s['ep_down']/ng,s['ep10_up']/ng,s['ep10_even']/ng,s['ep10_down']/ng,s['death']/ng))
    print('   field rounds/g %.0f  ally within 2 %.2f 4 %.2f 6 %.2f 10 %.2f  enemyhalf %.2f | ep on own half %.2f up-own %.2f down-own %.2f'%(
      fr/ng, s['nn2']/fr,s['nn4']/fr,s['nn6']/fr,s['nn10']/fr,s['enemyhalf']/fr, s['ep_ownhalf']/ep, s['up_ownhalf']/max(1,s['ep_up']), s['down_ownhalf']/max(1,s['ep_down'])))
