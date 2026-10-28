# idlecr.py TAG: classify every "[v11-idle] reason=capture-reward" line against the decoded state
import json,gzip,glob,collections,sys,zipfile,re
W='/tmp/claude-0/w'; T=sys.argv[1]
C=collections.Counter(); EX=[]
for f in sorted(glob.glob(f'{W}/dec/{T}/*.json.gz')):
    b=f.split('/')[-1][:-8]; side=b[-1]; us=0 if side=='a' else 1; D=json.load(gzip.open(f))
    out=zipfile.ZipFile(f'{W}/ws/rep/{T}/{b}.repl26a').read(f'team-{side}.stdout').decode(errors='replace')
    n_team=len([c for c in D['rounds'][0]['c'] if c[1]==us])
    name2idx={}
    for m in re.finditer(r'\[init\] (\w+) melee=\d ally=(\d+)',out): name2idx[m.group(1)]=int(m.group(2))+us*n_team
    tiles=collections.defaultdict(list)
    for k in D['camps']: tiles[k[2]].append((k[3],k[4]))
    cen={g:t[0] for g,t in tiles.items()}
    ctc=collections.defaultdict(list)
    for g,t,r in D['ctc']: ctc[r].append((g,t))
    cur={}; curat={}
    for row in D['rounds']:
        for g,t in ctc.get(row['r'],[]): cur[g]=t
        curat[row['r']]=dict(cur)
    P={row['r']:{c[0]:c for c in row['c']} for row in D['rounds']}
    GS={row['r']:row['gs'] for row in D['rounds']}
    for m in re.finditer(r'\[v11-idle\] r=(\d+) who=(\w+) grp=(\d+) target=(-?\d+) reason=capture-reward',out):
        r=int(m.group(1)); who=m.group(2); g=int(m.group(3)); tg=int(m.group(4))
        if r>600 or r not in P or r+1 not in P: continue
        i=name2idx.get(who)
        if i is None: C['noname']+=1; continue
        c=P[r][i]; c2=P[r+1][i]
        gs=GS[r].get(str(g)); holder=curat[r].get(g,2)
        on=(c[3],c[4]) in tiles[g]
        mate_on=any((x[3],x[4]) in tiles[g] for x in P[r].values() if x[1]==us and x[0]!=i and x[9])
        moved=(c[3],c[4])!=(c2[3],c2[4])
        foes=sum(1 for x in P[r].values() if x[1]!=us and x[9] and max(abs(x[3]-c[3]),abs(x[4]-c[4]))<=6)
        d=min(max(abs(c[3]-t[0]),abs(c[4]-t[1])) for t in tiles[g])
        hits=any(k.startswith(f'{i}>') for k in D['ck'].get(str(r),{}))
        key=(f'gs={gs}', 'holder='+('us' if holder==us else 'them' if holder==1-us else 'none'), 'on' if on else 'mate_on' if mate_on else 'nobody_on', 'moved' if moved else 'hit' if hits else 'still', 'foe' if foes else 'nofoe')
        C[key]+=1
        if key[2]=='nobody_on' and key[3]=='still' and len(EX)<30: EX.append((b,r,who,g,tg,d,c[3],c[4],int(c[5]),cen[g],[(x[0],x[3],x[4]) for x in P[r].values() if x[1]==us and x[9] and x[0]!=i]))
tot=sum(C.values()); print('total',tot)
for k,v in C.most_common(40): print(v, f'{100*v/tot:.1f}%', k)
print('--- examples nobody_on & still')
for e in EX: print(e)
