import sys,glob,os,zipfile,tempfile,collections
sys.path.insert(0,'/home/user/cambridge-battlecode-2026/handoff/replay2'); from dump2 import dump
from concurrent.futures import ProcessPoolExecutor
def one(z):
    side=0 if os.path.basename(z).startswith('A_') else 1
    d=tempfile.mkdtemp(dir=os.environ['TMPD'])
    with zipfile.ZipFile(z) as f: f.extract('replay.repl26a',d)
    R=dump(d+'/replay.repl26a',camps=False); os.remove(d+'/replay.repl26a'); os.rmdir(d)
    if not R: return None
    out=collections.Counter(); prev={}
    for r in R:
        for c in r['champions']:
            if c['team']!=side: continue
            t=c['typeName']; i=c['index']
            if not c['alive']: prev.pop(i,None); continue
            out[(t,'alive')]+=1
            if i in prev:
                for k in (0,1):
                    if c['cd'][k]>prev[i][k]: out[(t,'cast%d'%k)]+=1
            prev[i]=c['cd']
    return out
Z=sorted(glob.glob(sys.argv[1]+'/*/*.repl26a'))[:int(sys.argv[2])]
T=collections.Counter(); n=0
with ProcessPoolExecutor(4) as ex:
    for o in ex.map(one,Z):
        if o: T.update(o); n+=1
for t in sorted(set(k[0] for k in T)):
    a=T[(t,'alive')]; print(t,'casts per 1000 alive rounds', round(1000*T[(t,'cast0')]/a,1), round(1000*T[(t,'cast1')]/a,1))
