"""Mechanism counts from local replays res/TAG/{A,B}_map.repl26a (cand = team 0 in A_, team 1 in B_).
Per team: mid gold-only captures before r300, gem-only-group captures, rounds with 2+ live rivals in own half
(invasion exposure), champion deaths in own half / total. Output JSON per game."""
import json, subprocess, sys, os, glob, math, collections
from concurrent.futures import ThreadPoolExecutor
DUMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools', 'replaydump.js')
def one(path):
    p = subprocess.Popen(['node', DUMP, path, '--camps'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    spawn=None; state={}; team={}; cen={}; kinds={}; alive={}; lastp={}; names={}
    R={t: collections.Counter() for t in (0,1)}; gemonly_map=False; last_r=-1
    for line in p.stdout:
        d=json.loads(line)
        if 'round' not in d: continue
        r=d['round']
        ch=d.get('champions') or []
        if spawn is None and ch:
            spawn={t:(sum(c['x'] for c in ch if c['team']==t)/max(1,sum(1 for c in ch if c['team']==t)), sum(c['y'] for c in ch if c['team']==t)/max(1,sum(1 for c in ch if c['team']==t))) for t in (0,1)}
        if spawn is None: continue
        own=lambda t,x,y: math.dist((x,y),spawn[t]) < math.dist((x,y),spawn[1-t])
        if r!=last_r:
            last_r=r
            for t in (0,1):
                inv=sum(1 for c in ch if c['team']!=t and c['alive'] and own(t,c['x'],c['y']) and math.dist((c['x'],c['y']),spawn[1-t])>6)
                if inv>=2: R[t]['inv2_rounds']+=1
                if inv>=3: R[t]['inv3_rounds']+=1
        for c in ch:
            k=(c['team'],c['index'])
            if alive.get(k,True) and not c['alive'] and c['typeName']!='Issac':
                lx,ly=lastp.get(k,(c['x'],c['y']))
                R[c['team']]['deaths']+=1; R[c['team']]['deaths_own']+=own(c['team'],lx,ly)
            if c['alive']: lastp[k]=(c['x'],c['y'])
            alive[k]=c['alive']
        if 'camps' not in d: continue
        groups=collections.defaultdict(list)
        for k in d['camps']: groups[k['group']].append(k)
        for g,ks in groups.items():
            cen.setdefault(g,(sum(k['spawnX'] for k in ks)/len(ks), sum(k['spawnY'] for k in ks)/len(ks)))
            gems=max(k['rewardGems'] for k in ks); gold=max(k['rewardGold'] for k in ks)
            kinds.setdefault(g,(gems,gold)); names.setdefault(g,'+'.join(sorted(set(k['typeName'] for k in ks))))
            if gems>0 and gold<=0 and not any('Monolith' in k['typeName'] for k in ks): gemonly_map=True
            st=ks[0]['groupStateName']; ct=[k['captureTeam'] for k in ks if k['captureTeam'] in (0,1)]
            if st=='reward_available' and ct: team[g]=ct[0]
            if state.get(g)=='reward_available' and st!='reward_available' and g in team:
                t=team.pop(g); c=cen[g]; gm,gd=kinds[g]
                do=math.dist(c,spawn[t]); df=math.dist(c,spawn[1-t])
                mid=abs(do-df)<=6
                R[t]['caps']+=1
                if 'elk' in names.get(g,'').lower():
                    R[t]['elk_caps']+=1
                    if r<400: R[t]['elk_r400']+=1
                if gm<=0 and gd>0:
                    R[t]['goldonly_caps']+=1
                    if r<300: R[t]['goldonly_r300']+=1
                    if r<300 and mid: R[t]['mid_goldonly_r300']+=1
                    if r>=300: R[t]['goldonly_late']+=1
                if gm>0 and gd<=0: R[t]['gemonly_caps']+=1
            state[g]=st
    p.wait()
    return {'gemonly_map':gemonly_map, 0:dict(R[0]), 1:dict(R[1])}
def run(tag):
    fs=sorted(glob.glob(f'res/{tag}/*.repl26a'))
    with ThreadPoolExecutor(4) as ex: out=list(ex.map(one,fs))
    res={}
    for f,o in zip(fs,out):
        b=os.path.basename(f)[:-8]; c=0 if b.startswith('A_') else 1
        res[b]={'gemonly_map':o['gemonly_map'],'cand':o[c],'base':o[1-c]}
    json.dump(res,open(f'res/{tag}_mech.json','w'))
    return res
def show(tag,res):
    n=len(res); keys=['elk_caps','elk_r400','caps','mid_goldonly_r300','goldonly_r300','goldonly_late','gemonly_caps','inv2_rounds','inv3_rounds','deaths','deaths_own']
    s={k:[sum(v[side].get(k,0) for v in res.values())/n for side in ('cand','base')] for k in keys}
    print(tag, 'n',n, ' '.join(f"{k} {a:.1f}/{b:.1f}" for k,(a,b) in s.items()))
if __name__=='__main__':
    for t in sys.argv[1:]: show(t, run(t))
