"""gold@r400 + deaths per game from local replays res/cal_BOT_RIVAL/{A,B}_map.repl26a (BOT = team 0 in A_, 1 in B_).
gold@r400 = sum over our champions of positive per-round increases of held gold up to round 400 (earned gold;
spending shows as decreases and is ignored). Cached in res/cal_BOT_RIVAL/g400.json.
usage (in out/panel): python3 ../../panel/scripts/gold400.py BASE CAND...  (PAN=pA,pB to limit the rivals)"""
import json, subprocess, sys, os, glob, math, statistics as st
from concurrent.futures import ThreadPoolExecutor
DUMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools', 'replaydump.js')
def one(path):
    p=subprocess.Popen(['node',DUMP,path],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
    prev={}; earn={0:0,1:0}; deaths={0:0,1:0}; alive={}
    for line in p.stdout:
        d=json.loads(line)
        if 'round' not in d: continue
        r=d['round']
        for c in d.get('champions') or []:
            k=(c['team'],c['index'])
            if r<=400:
                g=c.get('gold',0); 
                if k in prev and g>prev[k]: earn[c['team']]+=g-prev[k]
                prev[k]=g
            if alive.get(k,True) and not c['alive'] and c['typeName']!='Issac': deaths[c['team']]+=1
            alive[k]=c['alive']
    p.wait(); return earn,deaths
def tag_data(bot,riv):
    d=f'res/cal_{bot}_{riv}'; cache=f'{d}/g400.json'
    C=json.load(open(cache)) if os.path.exists(cache) else {}
    todo=[f for f in glob.glob(f'{d}/*.repl26a') if os.path.basename(f) not in C and os.path.exists(f[:-7]+'json')]
    with ThreadPoolExecutor(4) as ex:
        for f,(e,dt) in zip(todo,ex.map(one,todo)):
            t=0 if os.path.basename(f).startswith('A_') else 1
            C[os.path.basename(f)]={'g400':e[t],'g400_foe':e[1-t],'deaths':dt[t]}
    json.dump(C,open(cache,'w')); return C
def win(bot,riv,f):
    j=json.load(open(f'res/cal_{bot}_{riv}/{f[:-7]}json')); t=0 if f.startswith('A_') else 1
    w=j.get('winner', j.get('result',{}).get('winner') if isinstance(j.get('result'),dict) else None)
    return w
if __name__=='__main__':
    base,cands=sys.argv[1],sys.argv[2:]; pan=os.environ.get('PAN','pA,pB,pC,pInv,pD,pF,pE,pG,pM').split(',')
    B={r:tag_data(base,r) for r in pan}
    print(f"base {base}: g400 mean "+' '.join(f"{r}:{st.mean(v['g400'] for v in B[r].values()):.0f}" for r in pan))
    for c in cands:
        dg=[];dd=[]
        for r in pan:
            Cd=tag_data(c,r)
            for f,v in Cd.items():
                if f in B[r]: dg.append(v['g400']-B[r][f]['g400']); dd.append(v['deaths']-B[r][f]['deaths'])
        n=len(dg); bg=sum(B[r][f]['g400'] for r in pan for f in B[r])/max(1,sum(len(B[r]) for r in pan))
        low=[x for x,y in zip(dd,dg) if y<=-200]
        corr=st.correlation(dg,dd) if n>2 and st.pstdev(dg)>0 and st.pstdev(dd)>0 else float('nan')
        print(f"{c}: n={n} dgold@r400 {st.mean(dg):+.0f} ({100*st.mean(dg)/bg:+.1f}%), ddeaths {st.mean(dd):+.2f}, "
              f"games gold<=-200: {len(low)} (ddeaths there {st.mean(low) if low else 0:+.2f}), corr(dg,dd) {corr:+.2f}")
