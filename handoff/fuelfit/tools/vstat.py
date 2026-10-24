# vstat.py RESDIR [RESDIR2] : per-champion early monster damage + team state@300 (us - them), near/mid maps
import json,sys,glob,os,collections,math
def tl(runs,R):
    t=0;v=0.0
    for x in runs:
        if t>=R: break
        v=float(x['value']); t+=x['duration']
    return v
def first(runs):
    t=0
    for x in runs:
        if float(x['value'])>0: return t
        t+=x['duration']
    return 9999
def load(d):
    out={}
    for f in glob.glob(d+'/*/*.json'):
        J=json.load(open(f)); side=os.path.basename(f)[0]; us='teamA' if side=='A' else 'teamB'
        row=collections.defaultdict(float)
        for T in J['championTimelines']:
            o=T['owner']; k='us' if o['team']==us else 'th'
            if T['metric']=='monsterDamageDone':
                for R in (20,40,100,300): row[f'md{R}_{k}']+=tl(T['runs'],R)
                if k=='us': row['n_'+o['name']]=1; row['f_'+o['name']]=first(T['runs']); row['m20_'+o['name']]=tl(T['runs'],20); row['m40_'+o['name']]=tl(T['runs'],40)
            if T['metric'] in ('earnedGold','deaths'):
                row[f"{T['metric']}300_{k}"]+=tl(T['runs'],300)
        for T in J['teamTimelines']:
            if T.get('metric','submittedGems')=='submittedGems':
                row['s300_'+('us' if T['owner']==us else 'th')]=tl(T['runs'],300)
        row['win']=J['match']['outcome']==us
        out[f.split(d)[1]]=row
    return out
W=[0.64,1.71,0.07,0.64,-0.04]
def a14(r):
    x=[(r['s300_us']-r['s300_th'])/100,(r['earnedGold300_us']-r['earnedGold300_th'])/1000,(r['deaths300_th']-r['deaths300_us'])/3,(r['md300_us']-r['md300_th'])/10000,1]
    return sum(a*b for a,b in zip(W,x))
for d in sys.argv[1:]:
    D=load(d); n=len(D)
    def m(k): v=[r[k] for r in D.values() if k in r]; return sum(v)/max(1,len(v))
    print(f'{d}: n={n} WR {m("win"):.2f}  team md net r20 {m("md20_us")-m("md20_th"):+.0f} r40 {m("md40_us")-m("md40_th"):+.0f} r100 {m("md100_us")-m("md100_th"):+.0f} r300 {m("md300_us")-m("md300_th"):+.0f} | gold300 {m("earnedGold300_us")-m("earnedGold300_th"):+.0f} deaths300 {m("deaths300_us")-m("deaths300_th"):+.2f} gems300 {m("s300_us")-m("s300_th"):+.1f} | a14 {sum(a14(r) for r in D.values())/n:+.3f}')
    names=sorted({k[2:] for r in D.values() for k in r if k.startswith('n_')})
    for nm in names:
        fs=sorted(r['f_'+nm] for r in D.values() if 'f_'+nm in r)
        print(f'   {nm:14s} first hit med r{fs[len(fs)//2]}  md@20 {m("m20_"+nm):.0f}  md@40 {m("m40_"+nm):.0f}')
