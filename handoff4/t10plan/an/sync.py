# sync.py TAG: gold-group captures (gold>=20, r<=600) of our side. Hitting phase = first hit (episode <=15 apart) -> group dead
# (first round gs==2, else last hit). Per hitting round: number of distinct hitters of ours. Arrival spread: for each of our
# champions that hit the group during the capture, its first hit round minus the block's first hit round. Also prints the v12
# gates: hitting-phase mean/median, rounds first hit -> capture, captures/600, caps per game.
import json,gzip,glob,collections,sys
W='/home/user/ws'; T=sys.argv[1]
H=collections.Counter(); hit_rounds=0; phases=[]; durs=[]; spreads=[]; nmem=[]; ngames=0; ncaps=0; fourhit=0
first_vs_arrive=[]
for f in sorted(glob.glob(f'{W}/dec/{T}/*.json.gz')):
    us=0 if f.endswith('_a.json.gz') else 1; D=json.load(gzip.open(f)); ngames+=1
    team={c[0]:c[1] for c in D['rounds'][0]['c']}
    grp={k[0]:k[2] for k in D['camps']}; gg={}
    for k in D['camps']: gg[k[2]]=max(gg.get(k[2],0),k[6] or 0)
    big={g for g,v in gg.items() if v>=20}
    hits=collections.defaultdict(lambda: collections.defaultdict(set))
    for r,dd in D['ck'].items():
        r=int(r)
        for k,v in dd.items():
            a,ci=map(int,k.split('>')); g=grp.get(ci)
            if g in big and team.get(a)==us: hits[g][r].add(a)
    R={row['r']:row for row in D['rounds']}
    caps={g:r for g,t,r in D['caps'] if t==us and g in big and r<=600}
    for g,r0 in caps.items():
        rs=sorted(r for r in hits[g] if r<=r0)
        if not rs: continue
        ep=[rs[-1]]
        for r in reversed(rs[:-1]):
            if ep[-1]-r<=15: ep.append(r)
            else: break
        first=min(ep); last=max(ep)
        dead=None
        for r in range(first,r0+1):
            if r in R and R[r].get('gs',{}).get(str(g))==2: dead=r; break
        if dead is None: dead=last+1
        ncaps+=1; durs.append(r0-first); phases.append(dead-first)
        fa={}
        for r in range(first,dead):
            n=len(hits[g].get(r,())); H[min(n,4)]+=1; hit_rounds+=1
            if n>=4: fourhit+=1
            for a in hits[g].get(r,()): fa.setdefault(a,r)
        nmem.append(len(fa))
        for a,r in fa.items(): spreads.append(r-first)
        if len(fa)>=2: first_vs_arrive.append(max(fa.values())-first)
def stat(x): x=sorted(x); return 'mean %.1f median %d n=%d'%(sum(x)/max(1,len(x)), x[len(x)//2] if x else 0, len(x))
print(T,'games',ngames,'gold captures',ncaps,'(%.2f/game)'%(ncaps/max(1,ngames)))
print(' hitting phase (first hit -> group dead):',stat(phases))
print(' first hit -> capture:',stat(durs))
print(' hitters per hitting round:',' '.join('%d:%.1f%%'%(k,100*H[k]/max(1,hit_rounds)) for k in range(5)),'(rounds',hit_rounds,')')
print(' members that hit per capture:',stat(nmem))
print(' arrival spread (member first hit - block first hit):',stat(spreads), 'last arrival:',stat(first_vs_arrive))
sp=collections.Counter(min(s,10) for s in spreads); print('  spread hist',' '.join('%d:%d'%(k,sp[k]) for k in sorted(sp)))
