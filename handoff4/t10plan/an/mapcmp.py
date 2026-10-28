# mapcmp.py OURTAG: per map, carry captures r<400 per game by class (cluster>=50 gems 'rich', cluster<50, gold-only, wolf, elk, boss):
# top-10 winners (index.json, t10fix decode; old t10 decode only on maps the PC fix did not touch) vs our local replays (both sides)
import json,gzip,os,sys,glob,collections
W='/tmp/claude-0/w'; P=f'{W}/assets/pcassets'
BAD=set('anvil boss_battle concentrated_wealth crater dunes galaxy gato_gemcombat2 gato_gemcombat5 gold_rush guardians lost_world packs quadrants quarry ribs the_line treasure_box vault'.split())
K=('rich','poor','gold','wolf','elk','boss')
def caps(D,us):
    gt=collections.defaultdict(list); gty=collections.defaultdict(set); gv={}
    for k in D['camps']: gt[k[2]].append((k[3],k[4])); gty[k[2]].add(k[1]); gv[k[2]]=(k[5],k[6])
    def cls(g):
        t=gty[g]
        if 5 in t or 4 in t: return 'boss'
        if 1 in t: return 'elk'
        if 0 in t: return 'wolf'
        return 'gold' if gv[g][0]<=0 else 'rich' if gv[g][0]>=50 else 'poor'
    R={row['r']:row for row in D['rounds']}; C=collections.Counter()
    for g,t,r in D['caps']:
        if t!=us or r>=400 or r not in R: continue
        if any(c[2] in (1,7) and c[9] and min(max(abs(c[3]-x),abs(c[4]-y)) for x,y in gt[g])<=1 for c in R[r]['c'] if c[1]==us): C[cls(g)]+=1
    return C
T=collections.defaultdict(lambda:[collections.Counter(),0]); O=collections.defaultdict(lambda:[collections.Counter(),0])
for x in json.load(open(f'{P}/replays_t10/index.json')):
    m=x['map']; b=os.path.basename(x['file']).replace('.repl26a','.json.gz')
    f=f'{W}/dec/t10fix/'+b
    if not os.path.exists(f):
        if m in BAD: continue
        f=f'{W}/dec/t10/'+b
    if not os.path.exists(f): continue
    D=json.load(gzip.open(f)); us=D['meta']['outcome']-1
    if us not in (0,1): continue
    T[m][0].update(caps(D,us)); T[m][1]+=1
for f in glob.glob(f'{W}/dec/{sys.argv[1]}/*.json.gz'):
    b=os.path.basename(f)[:-8]; m=b[:-2]; us=0 if b.endswith('_a') else 1
    O[m][0].update(caps(json.load(gzip.open(f)),us)); O[m][1]+=1
print('| map | n top10 | top10 '+'/'.join(K)+f' | {sys.argv[1]} '+'/'.join(K)+' |'); print('|---|---|---|---|')
tt=collections.Counter(); oo=collections.Counter(); nt=no=0
for m in sorted(set(T)&set(O)):
    (ct,n),(co,k)=T[m],O[m]
    print(f'| {m} | {n} | '+'/'.join(f'{ct[c]/n:.1f}' for c in K)+' | '+'/'.join(f'{co[c]/k:.1f}' for c in K)+' |')
    for c in K: tt[c]+=ct[c]/n; oo[c]+=co[c]/k
    nt+=1
print(f'| mean over {nt} common maps | | '+'/'.join(f'{tt[c]/nt:.2f}' for c in K)+' | '+'/'.join(f'{oo[c]/nt:.2f}' for c in K)+' |')
