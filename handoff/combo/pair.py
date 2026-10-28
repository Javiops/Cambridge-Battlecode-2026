import sys,os,json,collections
sys.path.insert(0,'/home/user/cambridge-battlecode-2026/handoff/replay2'); from dump2 import dump, cheb
from concurrent.futures import ProcessPoolExecutor
D='/tmp/claude-0/-home-user-cambridge-battlecode-2026/76ec8910-3410-5095-ba5f-885fa2d39df3/scratchpad/c34/pcassets/replays_c34'
L=json.load(open(sys.argv[1]))
def summ(path,ours):
    R=dump(os.path.join(D,path),camps=False,timeout=2400); byr={}
    for r in R: byr.setdefault(r['round'],r)
    deaths=[]; prev={}
    for r in sorted(byr):
        for c in byr[r]['champions']:
            if prev.get(c['index']) and not c['alive'] and c['team']==ours: deaths.append((r,c['typeName']))
            prev[c['index']]=c['alive']
    g=lambda r: byr[r]['submittedGems'] if r in byr else None
    return byr,deaths,{r:g(r) for r in (150,300,500,800)}, max(byr)
def one(x):
    k,fe,fo=x; ours=0 if k[2]=='a' else 1
    be,de,ge,fe_=summ(fe,ours); bo,do,go,fo_=summ(fo,ours)
    div=None
    for r in sorted(set(be)&set(bo)):
        a=[(c['x'],c['y'],c['alive']) for c in be[r]['champions'] if c['team']==ours]; b=[(c['x'],c['y'],c['alive']) for c in bo[r]['champions'] if c['team']==ours]
        if a!=b: div=r; break
    return {'k':k,'div':div,'de':de,'do':do,'ge':ge,'go':go,'ours':ours,'end':(fe_,fo_)}
with ProcessPoolExecutor(4) as ex: res=list(ex.map(one,L))
json.dump(res,open(sys.argv[2],'w'))
for o in res:
    ours=o['ours']
    f=lambda g: {r:(v[ours],v[1-ours]) if v else None for r,v in g.items()}
    print(o['k'][0],o['k'][1],'div r',o['div'],'| e1foco deaths',len([d for d in o['de'] if d[0]<=400]),'o120c',len([d for d in o['do'] if d[0]<=400]),'| gems e1foco',f(o['ge']),'o120c',f(o['go']))
    print('    first deaths e1foco',o['de'][:6]); print('    first deaths o120c ',o['do'][:6])
