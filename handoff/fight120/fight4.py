# fight4.py INDEX.json BOT OUT.json: even contact episodes r21-200, both sides, per champion: targeting, abilities, exits
import sys,os,json,collections,subprocess
sys.path.insert(0,'/home/user/cambridge-battlecode-2026/handoff/replay2'); from dump2 import dump, cheb
from concurrent.futures import ProcessPoolExecutor
RD='/home/user/cambridge-battlecode-2026/handoff/replay2'
IDX,BOT,OUT=sys.argv[1:4]; D=os.path.dirname(IDX)
def P(c): return (c['x'],c['y'])
def deltas(path):
    p=subprocess.run(['node',RD+'/replaydump_pc.js',path,'--deltas'],capture_output=True,text=True,timeout=2400,env=dict(os.environ,CAMBC_VIS_WASM=RD+'/v2_0_0-hWOQ1R8f.wasm'))
    return [json.loads(l) for l in p.stdout.splitlines() if l.startswith('{')]
def one(e):
    path=os.path.join(D,e['file'])
    try:
        R=dump(path,camps=False,timeout=2400); Dl=deltas(path)
    except Exception: return None
    if not R or not Dl: return None
    ours=0 if e['side']=='a' else 1
    byr={}
    for r in R: byr.setdefault(r['round'],r)
    team={c['index']:c['team'] for c in R[0]['champions']}; typ={c['index']:c['typeName'] for c in R[0]['champions']}
    hits=collections.defaultdict(list); abil=collections.defaultdict(set)  # (round)->[(actor,target,dmg)], round->set(actors casting)
    for d in Dl:
        if d.get('ak')!=1: continue
        r=d['r']; a=d['ai']
        if d['k']==6: abil[r].add(a)
        for i,x in d.get('dc',[]):
            if x<0 and team.get(i) is not None and team.get(i)!=team.get(a): hits[r].append((a,i,-x,d['k']))
    T=collections.Counter()
    def add(side,t,m,v=1): T[f"{side}|{t}|{m}"]+=v
    state={}  # idx -> episode dict
    for r in range(21,201):
        if r not in byr: continue
        C={c['index']:c for c in byr[r]['champions']}
        for i,c in C.items():
            side='us' if c['team']==ours else 'them'; t=typ[i]
            ep=state.get(i)
            if not c['alive']:
                if ep and ep['cls']=='even': add(side,t,'dead'); 
                state.pop(i,None); continue
            al=[o for o in C.values() if o['team']==c['team'] and o['alive']]
            en=[o for o in C.values() if o['team']!=c['team'] and o['alive']]
            near=[o for o in en if cheb(P(c),P(o))<=3]
            hpf=c['health']/c['maxHealth']
            if ep is None:
                if not near: continue
                na=sum(cheb(P(c),P(o))<=4 for o in al); nf=sum(cheb(P(c),P(o))<=4 for o in en)
                cls='even' if na==nf else ('up' if na>nf else 'down')
                ep={'cls':cls,'start':r,'quiet':0,'hurt':False,'hurtr':None}; state[i]=ep
                if cls=='even': add(side,t,'ep')
            if ep['cls']!='even':
                ep['quiet']=0 if near else ep['quiet']+1
                if ep['quiet']>=3: state.pop(i,None)
                continue
            # even episode round
            add(side,t,'rounds')
            if i in abil.get(r,()): add(side,t,'abil_rounds'); 
            if i in abil.get(r,()) and r-ep['start']<=1: add(side,t,'abil_first2')
            my=[h for h in hits.get(r,[]) if h[0]==i]
            dmg=sum(h[2] for h in my); add(side,t,'dmg',dmg)
            taken=sum(h[2] for h in hits.get(r,[]) if h[1]==i); add(side,t,'taken',taken)
            en4=[o for o in en if cheb(P(c),P(o))<=4]
            if my and en4:
                tg=max(my,key=lambda h:h[2])[1]
                lo=min(en4,key=lambda o:o['health']); nr=min(en4,key=lambda o:cheb(P(c),P(o)))
                add(side,t,'hit_rounds'); add(side,t,'tgt_lowhp',int(tg==lo['index'])); add(side,t,'tgt_nearest',int(tg==nr['index']))
                if len(en4)>=2: add(side,t,'hit_rounds_multi'); add(side,t,'tgt_lowhp_multi',int(tg==lo['index']))
                mates=set(h[0] for h in hits.get(r,[]) if h[1]==tg and h[0]!=i and team[h[0]]==c['team'])
                add(side,t,'focus_shared',int(bool(mates)))
            if hpf<0.5 and not ep['hurt']: ep['hurt']=True; ep['hurtr']=r; add(side,t,'hurt')
            ep['quiet']=0 if near else ep['quiet']+1
            if ep['quiet']>=3:
                add(side,t,'exit'); add(side,t,'exit_hp',hpf)
                if ep['hurt']: add(side,t,'hurt_exit')
                state.pop(i,None)
        # kills: enemy deaths within 4 of an even-episode champion
        nxt=byr.get(r+1)
        if nxt:
            N={c['index']:c for c in nxt['champions']}
            for j,c in C.items():
                if c['alive'] and not N[j]['alive']:
                    for i,ep in state.items():
                        if ep['cls']=='even' and team[i]!=c['team'] and C[i]['alive'] and cheb(P(C[i]),P(c))<=4:
                            add('us' if team[i]==ours else 'them',typ[i],'kills')
    return dict(T)
I=[e for e in json.load(open(IDX)) if e['bot']==BOT]
T=collections.Counter(); g=0
with ProcessPoolExecutor(4) as ex:
    for o in ex.map(one,I):
        if o: T.update(o); g+=1
json.dump({'games':g,'T':T},open(OUT,'w')); print('games',g)
