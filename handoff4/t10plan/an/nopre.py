# nopre.py TAG: for every capture of a gold group (gold>=20, r<=600) take the rounds from the first hit (episode of hits
# <=15 rounds apart) to the capture; classify each round with 0 hitters of ours by what the block members near the camp
# (<=6 of a camp tile) were doing, from the stdout episode lines ([v9-retreat]/[v9-fight]/[v11-retreat] persist per
# champion until no rival within 8) and the [v11-idle] lines of that round.
import json,gzip,glob,collections,sys,zipfile,re
W='/tmp/claude-0/w'; T=sys.argv[1]
C=collections.Counter(); tot=0; zero=0; durs=[]
LINE=re.compile(r'\[(v9-retreat|v9-fight|v11-retreat|v11g-nopreempt|v11-idle)\] r=(\d+) who=(\w+)(.*)')
for f in sorted(glob.glob(f'{W}/dec/{T}/*.json.gz')):
    b=f.split('/')[-1][:-8]; side=b[-1]; us=0 if side=='a' else 1; D=json.load(gzip.open(f))
    out=zipfile.ZipFile(f'{W}/ws/rep/{T}/{b}.repl26a').read(f'team-{side}.stdout').decode(errors='replace')
    n_team=len([c for c in D['rounds'][0]['c'] if c[1]==us])
    name2idx={}
    for m in re.finditer(r'\[init\] (\w+) melee=\d ally=(\d+)',out): name2idx[m.group(1)]=int(m.group(2))+us*n_team
    ev=collections.defaultdict(list)   # (idx) -> [(r,kind,rest)]
    idle=collections.defaultdict(dict) # r -> idx -> reason
    for m in LINE.finditer(out):
        k,r,who,rest=m.group(1),int(m.group(2)),m.group(3),m.group(4); i=name2idx.get(who)
        if i is None: continue
        if k=='v11-idle':
            mm=re.search(r'reason=(\S+)',rest); idle[r][i]=mm.group(1) if mm else '?'
        else: ev[i].append((r,k))
    tiles=collections.defaultdict(list); grp={}
    for k in D['camps']: tiles[k[2]].append((k[3],k[4])); grp[k[0]]=k[2]
    gg={}
    for k in D['camps']: gg[k[2]]=max(gg.get(k[2],0),k[6] or 0)
    big={g for g,v in gg.items() if v>=20}
    P={row['r']:{c[0]:c for c in row['c']} for row in D['rounds']}
    hits=collections.defaultdict(lambda: collections.defaultdict(set))
    for r,dd in D['ck'].items():
        r=int(r)
        for k,v in dd.items():
            a,ci=map(int,k.split('>')); g=grp.get(ci)
            if g in big and a in name2idx.values(): hits[g][r].add(a)
    # per champion per round: fstate reconstruction (persist until no foe within 8)
    def foes_within(r,c,d):
        return sum(1 for x in P[r].values() if x[1]!=us and x[9] and max(abs(x[3]-c[3]),abs(x[4]-c[4]))<=d)
    fstate={}
    for i in name2idx.values():
        st=None; evs=sorted(ev[i]); j=0
        for r in sorted(P):
            while j<len(evs) and evs[j][0]<=r: st=evs[j][1]; j+=1
            c=P[r].get(i)
            if c is None or not c[9]: st=None
            elif st and foes_within(r,c,8)==0 and (j>=len(evs) or evs[j-1][0]!=r): st=None
            fstate[(i,r)]=st
    caps={g:r for g,t,r in D['caps'] if t==us and g in big and r<=600}
    for g,r0 in caps.items():
        rs=sorted(r for r in hits[g] if r<=r0)
        if not rs: continue
        ep=[rs[-1]]
        for r in reversed(rs[:-1]):
            if ep[-1]-r<=15: ep.append(r)
            else: break
        first=min(ep); durs.append(r0-first)
        for r in range(first,r0+1):
            if r not in P: continue
            tot+=1
            if hits[g].get(r): continue
            zero+=1
            near=[c for c in P[r].values() if c[1]==us and c[9] and min(max(abs(c[3]-t[0]),abs(c[4]-t[1])) for t in tiles[g])<=6]
            if not near: C['nobody<=6']+=1; continue
            # reward on the ground (group dead, waiting)?
            gs=D['rounds'][r]['gs'].get(str(g)) if 'gs' in D['rounds'][r] else None
            if gs==2: C['reward-wait']+=1; continue
            sts=[fstate.get((c[0],r)) for c in near]
            ids=[idle[r].get(c[0]) for c in near]
            foe=any(foes_within(r,c,6) for c in near)
            if 'v9-retreat' in sts: C['v9-retreat'+('/foe6' if foe else '/nofoe6')]+=1
            elif 'v11-retreat' in sts: C['v11-retreat'+('/foe6' if foe else '/nofoe6')]+=1
            elif 'v9-fight' in sts: C['v9-fight'+('/foe6' if foe else '/nofoe6')]+=1
            elif 'v11g-nopreempt' in sts: C['nopreempt']+=1
            elif any(x=='rally-hold' for x in ids): C['rally-hold']+=1
            elif any(x and x.startswith('capture') for x in ids): C['capture-idle']+=1
            elif any(x=='solo-hold' for x in ids): C['solo-hold']+=1
            elif foe: C['foe6-nolog']+=1
            else:
                mv=any((P[r+1][c[0]][3],P[r+1][c[0]][4])!=(c[3],c[4]) for c in near if r+1 in P and c[0] in P[r+1])
                C['other-moving' if mv else 'other-still']+=1
print(T,'caps',len(durs),'mean dur %.1f'%(sum(durs)/max(1,len(durs))),'median',sorted(durs)[len(durs)//2] if durs else 0,'rounds',tot,'zero-hitter %d (%.1f%%)'%(zero,100*zero/max(1,tot)))
for k,v in C.most_common(): print('  %-22s %6d %5.1f%% of zero  %5.1f%% of all'%(k,v,100*v/max(1,zero),100*v/max(1,tot)))
