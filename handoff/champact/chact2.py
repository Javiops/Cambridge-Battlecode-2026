#!/usr/bin/env python3
"""chact.py SRC OUT.json : per champion type, r1-150: rounds by activity (dead, spawn = own spawn area/start tiles,
fight = enemy champion within 3, camp = within 2 of a live camp, walk = moved, idle), gems gained (positive gem deltas),
and groups cleared with the champion within 3 at the clear, by group kind (elk, gem, gold, wolf, mixed) and by company
(our champions within 3 at the clear incl. itself). SRC: t10f (top10 vs top10 r300 jsonl, both sides) or a local res dir."""
import sys,json,os,collections,zipfile,tempfile,glob
sys.path.insert(0,"/home/user/cambridge-battlecode-2026/handoff/replay2"); from dump2 import dump, cheb
from concurrent.futures import ProcessPoolExecutor
BAD=('quadrants','concentrated_wealth')
def P(c): return (c['x'],c['y'])
def kind(ts):
    ts=set(t.split('_')[0] for t in ts)
    if ts=={'elk'}: return 'elk'
    if 'elk' in ts and 'gem' in ts: return 'elk+gem'
    if ts=={'gem'}: return 'gem'
    if ts=={'gold'}: return 'gold'
    if 'wolf' in ts: return 'wolf*'
    return '+'.join(sorted(ts))
def one(a):
    src,teams=a
    try:
        if src.endswith('.jsonl'): R=[json.loads(l) for l in open(src)]
        else:
            d=tempfile.mkdtemp(dir=os.environ['TMPD'])
            with zipfile.ZipFile(src) as f: f.extract('replay.repl26a',d)
            R=dump(d+'/replay.repl26a'); os.remove(d+'/replay.repl26a'); os.rmdir(d)
    except Exception: return None
    byr={}
    for r in R: byr.setdefault(r['round'],r)
    r0=byr.get(1) or R[0]
    gk={}; gt=collections.defaultdict(set)
    for k in r0['camps']: gt[k['group']].add(k['typeName'])
    for g in gt: gk[g]=kind(gt[g])
    start={c['index']:P(c) for c in r0['champions']}
    out=collections.Counter(); prev=None
    for rd in range(1,151):
        r=byr.get(rd)
        if not r: continue
        C=[c for c in r['champions'] if c['alive'] and c['x']>=0]
        alive_g=collections.defaultdict(int)
        for k in r['camps']:
            if k['alive']: alive_g[k['group']]+=1
        for c in r['champions']:
            if c['team'] not in teams: continue
            t=c['typeName']; out[(t,'n')]+=1
            if not c['alive'] or c['x']<0: out[(t,'dead')]+=1; continue
            p=P(c); pc=prev.get(c['index']) if prev else None
            if pc and c['gems']>pc['gems']: out[(t,'gems')]+=c['gems']-pc['gems']
            if cheb(p,start[c['index']])<=2: a='spawn'
            elif any(cheb(p,P(f))<=3 for f in C if f['team']!=c['team']): a='fight'
            elif any(k['alive'] and cheb(p,P(k))<=2 for k in r['camps']): a='camp'
            elif pc and pc['x']>=0 and P(pc)!=p: a='walk'
            else: a='idle'
            out[(t,a)]+=1
        if prev is not None:
            for g,n in prev_alive.items():
                if n>0 and alive_g.get(g,0)==0:
                    cells=[(k['x'],k['y']) for k in prev_raw if k['group']==g]
                    for c in C:
                        if c['team'] not in teams: continue
                        if any(cheb(P(c),q)<=3 for q in cells):
                            comp=sum(1 for o in C if o['team']==c['team'] and any(cheb(P(o),q)<=3 for q in cells))
                            out[(c['typeName'],'cap',gk.get(g,'?'))]+=1; out[(c['typeName'],'capn',min(comp,3))]+=1
        prev={c['index']:c for c in r['champions']}; prev_alive=alive_g; prev_raw=r['camps']
    return {'|'.join(map(str,k)):v for k,v in out.items()}
def jobs(src):
    if src=='t10f':
        L=json.load(open('/mnt/project-files/analysis/top10-fresh-1025/sel_1025.json'))['t10']; D=os.environ['T10F']
        return [(D+'/'+g['match']+'.r300.jsonl',(0,1)) for g in L if not any(b in g['map'] for b in BAD) and os.path.exists(D+'/'+g['match']+'.r300.jsonl')]
    return [(z,(0,) if os.path.basename(z).startswith('A_') else (1,)) for z in sorted(glob.glob(src+'/*/*.repl26a')) if not any(b in z for b in BAD)]
if __name__=='__main__':
    T=collections.Counter(); g=0
    with ProcessPoolExecutor(4) as ex:
        for o in ex.map(one,jobs(sys.argv[1])):
            if o: g+=1; T.update(o)
    json.dump({'games':g,'T':T},open(sys.argv[2],'w')); print(sys.argv[1],g)
