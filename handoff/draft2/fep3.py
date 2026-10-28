#!/usr/bin/env python3
"""fep2.py RESDIR OUT.json : contact episodes r21-100 (engine 2.0.0 local bundles), BOTH sides (our = side of the bundle).
Episode: a champion with an enemy champion within 3; it ends after 2 rounds with none (or death). At onset:
na = allies within 4 (incl. me), nf = enemies within 4: even (na==nf), up (na>nf), down (na<nf). During the episode
and up to 2 rounds after: enemy deaths within 4 of me (kills, shared), my death. Also: hurt = my hp fell below 50% in
the episode; died-after-leaving = death within 10 rounds after the episode ended, with no enemy within 3 at death-1."""
import sys,json,os,collections,zipfile,tempfile,glob
sys.path.insert(0,"/home/user/cambridge-battlecode-2026/handoff/replay2"); from dump2 import dump, cheb
from concurrent.futures import ProcessPoolExecutor
def P(c): return (c['x'],c['y'])
def one(a):
    z,ours=a if isinstance(a,tuple) else (a,0 if os.path.basename(a).startswith('A_') else 1)
    if zipfile.is_zipfile(z):
        d=tempfile.mkdtemp(dir=os.environ['TMPD'])
        with zipfile.ZipFile(z) as f: f.extract('replay.repl26a',d)
        R=dump(d+'/replay.repl26a',camps=False,timeout=1200); os.remove(d+'/replay.repl26a'); os.rmdir(d)
    else: R=dump(z,camps=False,timeout=1200)
    if not R: return None
    byr={}
    for r in R: byr.setdefault(r['round'],r)
    out=collections.Counter(); ep={}; ended={}
    def close(i,e,lab):
        k=(lab,e['t'],e['cls'])
        out[k+('ep',)]+=1; out[k+('kills',)]+=e['kills']; out[k+('dead',)]+=e['dead']
        if e['hurt']: out[k+('hurt',)]+=1; out[k+('hurtdead',)]+=e['dead']
    for rd in range(21,111):
        r=byr.get(rd)
        if not r: continue
        prev=byr.get(rd-1)
        A=[c for c in r['champions'] if c['alive'] and c['x']>=0]
        died=[c for c in r['champions'] if not c['alive'] and prev and any(q['index']==c['index'] and q['alive'] for q in prev['champions'])]
        PP={q['index']:q for q in prev['champions']} if prev else {}
        for c in r['champions']:
            i=c['index']; lab='us' if c['team']==ours else 'them'
            if i in ep:
                e=ep[i]
                for dd in died:
                    if dd['team']!=c['team'] and dd['index'] not in e['seen'] and i in PP and PP[i]['x']>=0 and cheb(P(PP[i]),P(PP[dd['index']]))<=4:
                        e['kills']+=1; e['seen'].add(dd['index'])
                if not c['alive']:
                    e['dead']=1; close(i,e,lab); del ep[i]; continue
                if c['health']<0.5*c['maxHealth']: e['hurt']=1
                F=[f for f in A if f['team']!=c['team'] and cheb(P(c),P(f))<=3] if c['x']>=0 else []
                if F: e['quiet']=0
                else:
                    e['quiet']+=1
                    if e['quiet']>=3: close(i,e,lab); ended[i]=(rd,lab,e['t']); del ep[i]
                continue
            if i in ended and not c['alive'] and PP.get(i,{}).get('alive'):
                r0,lb,t=ended.pop(i)
                if rd-r0<=10:
                    pc=PP[i]; nf=any(f['team']!=c['team'] and f['alive'] and f['x']>=0 and cheb(P(pc),P(f))<=3 for f in prev['champions'])
                    out[(lb,t,'ALL','after_dead')]+=1; out[(lb,t,'ALL','after_dead_nofoe')]+=not nf
            if not c['alive'] or c['x']<0 or rd>100: continue
            F=[f for f in A if f['team']!=c['team'] and cheb(P(c),P(f))<=3]
            if not F: continue
            na=sum(1 for a in A if a['team']==c['team'] and cheb(P(c),P(a))<=4); nf=sum(1 for f in A if f['team']!=c['team'] and cheb(P(c),P(f))<=4)
            cls='even' if na==nf else 'up' if na>nf else 'down'
            ep[i]=dict(t=c['typeName'],cls=cls,kills=0,dead=0,hurt=int(c['health']<0.5*c['maxHealth']),quiet=0,seen=set())
            out[(lab,c['typeName'],'ALL','left')]+=0
    for i,e in ep.items():
        lab='us' if [c for c in R[0]['champions'] if c['index']==i][0]['team']==ours else 'them'; close(i,e,lab)
    return {'|'.join(k):v for k,v in out.items()}
if __name__=='__main__':
    if sys.argv[1].endswith('.json'):  # index.json (t5b): {bot, file, side} ; optional argv[3] = bot filter
        base=os.path.dirname(sys.argv[1]); L=json.load(open(sys.argv[1]))
        J=[(os.path.join(base,x['file']),0 if x.get('side','a')=='a' else 1) for x in L if len(sys.argv)<4 or x['bot']==sys.argv[3]]
    else: J=sorted(glob.glob(sys.argv[1]+'/*/*.repl26a'))
    T=collections.Counter(); g=0
    with ProcessPoolExecutor(4) as ex:
        for o in ex.map(one,J):
            if o: g+=1; T.update(o)
    json.dump({'games':g,'T':T},open(sys.argv[2],'w')); print(g)
