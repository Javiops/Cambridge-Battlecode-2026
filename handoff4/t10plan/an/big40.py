# big40.py: attempts on 40+ gem groups in online losses (c34+c36): bodies, damage taken, deaths, duration, outcome, us vs rival
import json,gzip,os,collections,sys
W='/tmp/claude-0/w'; T=json.load(open(f'{W}/combo.json')); RES=sys.argv[1] if len(sys.argv)>1 else 'loss'
S=[collections.Counter(),collections.Counter()]; n=0; firstb=[[],[]]
for x in T:
    if x['result']!=RES: continue
    f=f"{W}/dec/{x['dec']}/"+os.path.basename(x['file']).replace('.repl26a','.json.gz')
    if not os.path.exists(f): continue
    D=json.load(gzip.open(f)); us=0 if x['side']=='a' else 1; n+=1
    team={c[0]:c[1] for c in D['rounds'][0]['c']}
    grp={k[0]:k[2] for k in D['camps']}; gv={}
    for k in D['camps']: gv[k[2]]=max(gv.get(k[2],0),k[5] or 0)
    big={g for g,v in gv.items() if v>=40}
    hits=collections.defaultdict(lambda: collections.defaultdict(set))  # (team,g) -> r -> champs
    for r,dd in D['ck'].items():
        r=int(r)
        if r>600: continue
        for k,v in dd.items():
            a,ci=map(int,k.split('>')); g=grp.get(ci)
            if g in big and a in team: hits[(team[a],g)][r].add(a)
    taken=collections.defaultdict(float)  # (team,g,r)
    for r,dd in D['kc'].items():
        r=int(r)
        if r>600: continue
        for k,v in dd.items():
            ci,b=map(int,k.split('>')); g=grp.get(ci)
            if g in big and b in team: taken[(team[b],g,r)]+=v
    caps=collections.defaultdict(list)
    for g,t,r in D['caps']:
        if g in big: caps[g].append((r,t))
    dead_r=collections.defaultdict(list)
    prev={}
    for row in D['rounds']:
        for c in row['c']:
            p=prev.get(c[0])
            if p and p[9] and not c[9]: dead_r[c[0]].append(row['r'])
        prev={c[0]:c for c in row['c']}
    for (t,g),rs in hits.items():
        i=0 if t==us else 1
        rr=sorted(rs); eps=[]; cur=[rr[0]]
        for r in rr[1:]:
            if r-cur[-1]<=15: cur.append(r)
            else: eps.append(cur); cur=[r]
        eps.append(cur)
        for ep in eps:
            a,b=ep[0],ep[-1]; champs=set().union(*(rs[r] for r in ep))
            S[i]['att']+=1; S[i]['bodies']+=len(champs); S[i]['dur']+=b-a
            S[i]['maxsim']+=max(len(rs[r]) for r in ep)
            firstb[i].append(len(rs[a]))
            S[i]['taken']+=sum(taken.get((t,g,r),0) for r in range(a,b+1))
            S[i]['deaths']+=sum(1 for c in champs for d in dead_r[c] if a<=d<=b+3)
            oc=[(r,tt) for r,tt in caps[g] if a<=r<=b+10]
            res='own' if any(tt==t for r,tt in oc) else ('other' if oc else 'none')
            S[i]['res_'+res]+=1
            if res=='own': S[i]['own_bodies']+=len(champs); S[i]['own_dur']+=b-a; S[i]['own_taken']+=sum(taken.get((t,g,r),0) for r in range(a,b+1))
print(f'{RES} n={n}: attempts on 40+ groups r<=600 (us / rival)')
for k in ['att','res_own','res_other','res_none']: print(f'  {k:10s} per game {S[0][k]/n:.2f} / {S[1][k]/n:.2f}')
for k in ['bodies','maxsim','dur','taken','deaths']: print(f'  per attempt {k:8s} {S[0][k]/S[0]["att"]:.2f} / {S[1][k]/S[1]["att"]:.2f}')
for k in ['own_bodies','own_dur','own_taken']: print(f'  per success {k:10s} {S[0][k]/max(1,S[0]["res_own"]):.1f} / {S[1][k]/max(1,S[1]["res_own"]):.1f}')
for i in (0,1):
    c=collections.Counter(min(b,3) for b in firstb[i]); print('  bodies hitting on the first round', ['us','rival'][i], sorted(c.items()))
