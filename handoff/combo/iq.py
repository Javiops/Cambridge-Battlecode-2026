import sys,os,json
sys.path.insert(0,'/home/user/cambridge-battlecode-2026/handoff/replay2'); from dump2 import dump, cheb
IDX=sys.argv[1]; RIV=sys.argv[2]; D=os.path.dirname(IDX)
I=[e for e in json.load(open(IDX)) if e['bot']=='e1foco' and e['rival']==RIV]
def P(c): return (c['x'],c['y'])
for e in I:
    R=dump(os.path.join(D,e['file']),camps=True,timeout=2400); byr={}
    for r in R: byr.setdefault(r['round'],r)
    ours=0 if e['side']=='a' else 1
    r0=byr[min(byr)]
    sp={t:[P(c) for c in r0['champions'] if c['team']==t] for t in (0,1)}
    spc={t:(sum(x for x,y in sp[t])//len(sp[t]),sum(y for x,y in sp[t])//len(sp[t])) for t in (0,1)}
    half=lambda p: 'ours' if cheb(p,spc[ours])<cheb(p,spc[1-ours]) else 'theirs'
    print(f"== {e['map']} {e['result']} spawn us {spc[ours]} them {spc[1-ours]}")
    # invasion: rounds 120-300 where 2+ enemies are in our half
    inv=[]
    for r in range(120,301):
        if r not in byr: continue
        en=[c for c in byr[r]['champions'] if c['team']!=ours and c['alive'] and half(P(c))=='ours']
        inv.append(len(en))
    first=[120+i for i,n in enumerate(inv) if n>=2][:1]
    print('  first round with 2+ enemies in our half:',first,' max',max(inv) if inv else 0)
    for r in range(151,301):
        if r not in byr or r-1 not in byr: continue
        prev={c['index']:c for c in byr[r-1]['champions']}
        for c in byr[r]['champions']:
            if c['team']!=ours or c['alive'] or not prev[c['index']]['alive']: continue
            pc=prev[c['index']]; p=P(pc)
            line=[f"  r{r} {pc['typeName']} at {p} ({half(p)} half, {cheb(p,spc[ours])} from our spawn) gems {pc['gems']}"]
            for b in (10,5,1):
                rr=byr.get(r-b)
                if not rr: continue
                C={x['index']:x for x in rr['champions']}; me=C[c['index']]
                if not me['alive']: continue
                mp=P(me)
                en=[x for x in C.values() if x['team']!=ours and x['alive'] and cheb(mp,P(x))<=6]
                al=[x for x in C.values() if x['team']==ours and x['alive'] and x['index']!=c['index']]
                camps=[k for k in rr.get('camps',[]) if k.get('alive')]
                def act(x):
                    q=P(x); d=cheb(q,mp); nc=min([cheb(q,(k['x'],k['y'])) for k in camps] or [99])
                    return f"{x['typeName'][:4]} d{d} hp{int(100*x['health']/x['maxHealth'])}{' camp' if nc<=2 else ''}"
                line.append(f"t-{b}: me hp{int(100*me['health']/me['maxHealth'])} foes<=6 {len(en)} [{','.join(x['typeName'][:4] for x in en)}] | allies: "+'; '.join(act(x) for x in al))
            print('\n     '.join(line))
