# rdeath.py INDEX.json BOT OUT.json: every champion death r1-400 on both sides, with the context 1 and 5 rounds before
import sys,os,json,collections
sys.path.insert(0,'/home/user/cambridge-battlecode-2026/handoff/replay2'); from dump2 import dump, cheb
from concurrent.futures import ProcessPoolExecutor
IDX,BOT,OUT=sys.argv[1:4]; D=os.path.dirname(IDX)
def P(c): return (c['x'],c['y'])
def one(e):
    try: R=dump(os.path.join(D,e['file']),camps=False,timeout=1500)
    except Exception: return None
    if not R: return None
    ours=0 if e['side']=='a' else 1
    byr={}
    for r in R: byr.setdefault(r['round'],r)
    rs=sorted(byr); out=[]; alive_prev={}
    for r in rs:
        if r>400: break
        C=byr[r]['champions']
        for c in C:
            i=c['index']
            if alive_prev.get(i) and not c['alive']:
                ctx={}
                for back in (1,5,10):
                    rr=byr.get(r-back)
                    if not rr: continue
                    cc=[x for x in rr['champions'] if x['index']==i][0]
                    if not cc['alive']: continue
                    al=[x for x in rr['champions'] if x['team']==c['team'] and x['index']!=i and x['alive']]
                    en=[x for x in rr['champions'] if x['team']!=c['team'] and x['alive']]
                    ctx[back]={'hp':cc['health']/cc['maxHealth'],'na4':sum(cheb(P(cc),P(x))<=4 for x in al),'nf4':sum(cheb(P(cc),P(x))<=4 for x in en),
                               'nf6':sum(cheb(P(cc),P(x))<=6 for x in en),'dal':min([cheb(P(cc),P(x)) for x in al] or [99]),'den':min([cheb(P(cc),P(x)) for x in en] or [99]),
                               'gems':cc['gems'],
                               'first':int(bool(en) and all(min(cheb(P(cc),P(y)) for y in en)<=min(cheb(P(x),P(y)) for y in en) for x in al))}
                out.append({'r':r,'type':c['typeName'],'us':c['team']==ours,'ctx':ctx})
            alive_prev[i]=c['alive']
    return {'file':e['file'],'res':e['result'],'deaths':out}
I=[e for e in json.load(open(IDX)) if e['bot']==BOT]
res=[]
with ProcessPoolExecutor(4) as ex:
    for o in ex.map(one,I):
        if o: res.append(o)
json.dump(res,open(OUT,'w')); print('games',len(res))
