# night23.py: (2) near maps capture throughput per body; (3) far maps per-50-round profile; top-10 winners vs our online c34 bots
import json,gzip,os,collections,sys
W='/tmp/claude-0/w'
near=set(open('/tmp/claude-0/-home-user-cambridge-battlecode-2026/3dc070b2-a00b-5e31-ba97-59618d5276fa/scratchpad/near.txt').read().split())
BAD=set('anvil boss_battle concentrated_wealth crater dunes galaxy gato_gemcombat2 gato_gemcombat5 gold_rush guardians lost_world packs quadrants quarry ribs the_line treasure_box vault'.split())
def games_t10(sel):
    for x in json.load(open(f'{W}/assets/pcassets/replays_t10/index.json')):
        if not sel(x['map']): continue
        b=os.path.basename(x['file']).replace('.repl26a','.json.gz'); f=f'{W}/dec/t10fix/'+b; fix=True
        if not os.path.exists(f):
            if x['map'] in BAD: continue
            f=f'{W}/dec/t10/'+b; fix=False
        if not os.path.exists(f): continue
        D=json.load(gzip.open(f)); us=D['meta']['outcome']-1
        if us in (0,1): yield x['map'],D,us
def games_on(bot,d,sel):
    for x in json.load(open(f'{W}/c34index.json')):
        if x['bot']!=bot or not sel(x['map']): continue
        f=f'{W}/dec/{d}/'+os.path.basename(x['file']).replace('.repl26a','.json.gz')
        if os.path.exists(f): yield x['map'],json.load(gzip.open(f)),(0 if x['side']=='a' else 1)
ch=lambda a,b:max(abs(a[0]-b[0]),abs(a[1]-b[1]))
def cls(gty,gv,g):
    t=gty[g]
    if 5 in t or 4 in t: return 'boss'
    if 1 in t: return 'elk'
    if 0 in t: return 'wolf'
    return 'gold' if gv[g]<=0 else 'cluster'
def prof(it,NB=12):
    A=collections.defaultdict(lambda:collections.Counter()); n=0; maps=collections.Counter()
    for m,D,us in it:
        n+=1; maps[m]+=1
        gt=collections.defaultdict(list); gty=collections.defaultdict(set); gv={}
        for k in D['camps']: gt[k[2]].append((k[3],k[4])); gty[k[2]].add(k[1]); gv[k[2]]=k[5]
        tiles=[t for v in gt.values() for t in v]
        sp=None; esp=None; prev={}
        for row in D['rounds']:
            r=row['r']
            if r>=600: break
            b=r//50; cs=[c for c in row['c'] if c[1]==us]
            if sp is None: sp=[(c[3],c[4]) for c in cs]; esp=[(c[3],c[4]) for c in row['c'] if c[1]!=us]
            al=[c for c in cs if c[9]]
            for c in cs:
                p=prev.get(c[0])
                if p and p[9] and not c[9]: A[b]['deaths']+=1
                if p and p[9] and c[9] and c[8]<p[8]: A[b]['banked']+=p[8]-c[8]
                prev[c[0]]=c
            for c in al:
                q=(c[3],c[4]); ds=min(ch(q,s) for s in sp)
                if ds<=4: continue
                A[b]['off']+=1
                A[b]['ally4']+=any(e is not c and ch(q,(e[3],e[4]))<=4 for e in al)
                A[b]['own']+=min(ch(q,s) for s in sp)<min(ch(q,s) for s in esp)
                A[b]['camp']+=any(ch(q,t)<=2 for t in tiles)
        for g,t,r in D['caps']:
            if t==us and r<600: A[r//50]['cap_'+cls(gty,gv,g)]+=1; A[r//50]['caps']+=1
    return A,n,maps
if sys.argv[1]=='2':
    S=lambda m:m in near
    for tag,it in (('top10 W',games_t10(S)),('v4o2 online',games_on('t10plan4o2','on_t10plan4o2',S)),('e1foco online',games_on('e1foco','e1foco',S))):
        A,n,maps=prof(it); tot=collections.Counter()
        for b in range(0,8): tot.update(A[b])
        print(f"{tag}: {n} games, {len(maps)} maps; r0-400 captures/game {tot['caps']/n:.1f}, champion-rounds at a camp/game {tot['camp']/n:.0f}, captures per 100 camp-rounds {100*tot['caps']/max(tot['camp'],1):.2f}, ally<=4 {tot['ally4']/tot['off']:.0%}, deaths/game {tot['deaths']/n:.1f}")
else:
    S=lambda m:m not in near
    out={}
    for tag,it in (('top10 W',games_t10(S)),('e1foco online',games_on('e1foco','e1foco',S))):
        A,n,maps=prof(it); out[tag]=(A,n); print(f'{tag}: {n} games, {len(maps)} maps')
    print('| r | ally<=4 t10/e1f | own half | at camp | deaths/game | caps/game | gold/cluster/wolf/elk/boss caps per game t10 | e1f | gems banked/game |')
    print('|---|---|---|---|---|---|---|---|---|')
    for b in range(12):
        (a,na),(e,ne)=out['top10 W'],out['e1foco online']
        f=lambda X,k,d:X[b][k]/max(X[b][d],1)
        ty=lambda X,nn:'/'.join(f"{X[b]['cap_'+k]/nn:.1f}" for k in ('gold','cluster','wolf','elk','boss'))
        print(f"| {b*50}-{b*50+49} | {f(a,'ally4','off'):.0%}/{f(e,'ally4','off'):.0%} | {f(a,'own','off'):.0%}/{f(e,'own','off'):.0%} | {f(a,'camp','off'):.0%}/{f(e,'camp','off'):.0%} | {a[b]['deaths']/na:.2f}/{e[b]['deaths']/ne:.2f} | {a[b]['caps']/na:.1f}/{e[b]['caps']/ne:.1f} | {ty(a,na)} | {ty(e,ne)} | {a[b]['banked']/na:.0f}/{e[b]['banked']/ne:.0f} |")
