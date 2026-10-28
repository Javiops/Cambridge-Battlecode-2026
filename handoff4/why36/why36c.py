# why36c.py: big groups (>=40 gems) in c34 games: who damages them, who captures, bodies at capture, stolen/abandoned attempts
import json,gzip,os,collections,sys
W='/tmp/claude-0/w'
T=json.load(open(f'{W}/combo.json'))
import os as _o
CH=_o.environ.get('CH')
T=[x for x in T if not CH or x['chain']==CH]
DIR={'t10plan4o2':'on_t10plan4o2','e1foco':'e1foco'}
RES=sys.argv[1] if len(sys.argv)>1 else 'loss'
def ch(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
S=[collections.Counter(),collections.Counter()]; n=0; typ=collections.Counter()
for x in T:
    if x['bot'] not in DIR or x['result']!=RES: continue
    f=f"{W}/dec/{x['dec']}/"+os.path.basename(x['file']).replace('.repl26a','.json.gz')
    if not os.path.exists(f): continue
    D=json.load(gzip.open(f)); us=0 if x['side']=='a' else 1; n+=1
    team={c[0]:c[1] for c in D['rounds'][0]['c']}
    grp={}; gv={}; gpos=collections.defaultdict(list); gt=collections.defaultdict(list)
    for k in D['camps']: grp[k[0]]=k[2]; gv[k[2]]=max(gv.get(k[2],0),k[5] or 0); gpos[k[2]].append((k[3],k[4])); gt[k[2]].append(k[1])
    big={g for g,v in gv.items() if v>=40}
    for g in big: typ[tuple(sorted(gt[g]))]+=1
    # per round damage per team to each big group
    dmg=collections.defaultdict(lambda: collections.defaultdict(float))  # (g) -> (team,r)->dmg
    for r,dd in D['ck'].items():
        for k,v in dd.items():
            a,ci=map(int,k.split('>'))
            g=grp.get(ci)
            if g in big and a in team: dmg[g][(team[a],int(r))]+=v
    caps=sorted((r,g,t) for g,t,r in D['caps'] if g in big)
    R={row['r']:row for row in D['rounds']}
    last={g:0 for g in big}
    for r,g,t in caps:
        if t not in (0,1): continue
        i=0 if t==us else 1
        w=[(tt,rr,v) for (tt,rr),v in dmg[g].items() if last[g]<rr<=r]
        own=sum(v for tt,rr,v in w if tt==t); oth=sum(v for tt,rr,v in w if tt!=t)
        st=min([rr for tt,rr,v in w if tt==t] or [r])
        row=R.get(r-1) or R.get(r)
        bodies=sum(1 for c in row['c'] if c[1]==t and c[9] and min(ch((c[3],c[4]),p) for p in gpos[g])<=4) if row else 0
        foes=sum(1 for c in row['c'] if c[1]!=t and c[9] and min(ch((c[3],c[4]),p) for p in gpos[g])<=8) if row else 0
        S[i]['caps']+=1; S[i]['bodies']+=bodies; S[i]['dur']+=r-st; S[i]['val']+=gv[g]
        S[i]['stolen']+= oth>=own*0.5 and oth>0   # other team did >=1/3 of damage
        S[1-i]['lostwork']+=oth; S[i]['foesnear']+=foes
        last[g]=r
    # abandoned work: damage by a team on big group in windows that ended without any capture by anyone before game end
    for g in big:
        for (tt,rr),v in dmg[g].items():
            if rr>last[g] and tt in (0,1): S[0 if tt==us else 1]['wasted']+=v
    for (g,(tt,rr)),v in [((g,k),v) for g in dmg for k,v in dmg[g].items()]:
        if tt in (0,1): S[0 if tt==us else 1]['bigdmg']+=v
print(f'{RES} n={n} games; us / rival per game')
for k in ['caps','val','bigdmg','wasted','lostwork']:
    print(f'  {k:9s} {S[0][k]/n:8.2f} / {S[1][k]/n:8.2f}')
for k in ['bodies','dur','stolen','foesnear']:
    print(f'  per cap {k:9s} {S[0][k]/max(1,S[0]["caps"]):6.2f} / {S[1][k]/max(1,S[1]["caps"]):6.2f}')
print('big group types (camp types)',typ.most_common(6))
