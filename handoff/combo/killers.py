# killers.py INDEX.json BOT OUT.json: our deaths r151-300 with the enemy champions within 4 one round before (type, hp), plus summary items per side
import sys,os,json,collections,subprocess
from concurrent.futures import ThreadPoolExecutor
RD='/home/user/cambridge-battlecode-2026/handoff/replay2'
IDX,BOT,OUT=sys.argv[1:4]; D=os.path.dirname(IDX)
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
def one(e):
    p=subprocess.run(['node',RD+'/replaydump_pc.js',os.path.join(D,e['file'])],capture_output=True,text=True,timeout=3000,env=dict(os.environ,CAMBC_VIS_WASM=RD+'/v2_0_0-hWOQ1R8f.wasm'))
    rows={};summ=None
    for l in p.stdout.splitlines():
        if not l.startswith('{'): continue
        d=json.loads(l)
        if d.get('summary'): summ=d
        elif 'champions' in d and not d.get('draft'): rows.setdefault(d['round'],d)
    if not rows: return None
    ours=0 if e['side']=='a' else 1; out=[]
    for r in range(152,301):
        if r not in rows or r-1 not in rows: continue
        prev={c['index']:c for c in rows[r-1]['champions']}
        for c in rows[r]['champions']:
            if c['team']!=ours or c['alive'] or not prev[c['index']]['alive']: continue
            pc=prev[c['index']]
            en=[o for o in prev.values() if o['team']!=ours and o['alive'] and cheb((pc['x'],pc['y']),(o['x'],o['y']))<=4]
            al=[o for o in prev.values() if o['team']==ours and o['alive'] and o['index']!=pc['index'] and cheb((pc['x'],pc['y']),(o['x'],o['y']))<=4]
            out.append({'r':r,'me':pc['typeName'],'gems':pc['gems'],'en':[(o['typeName'],o['health'],o['maxHealth']) for o in en],'na':len(al)})
    st=summ and summ.get('statistics')
    return {'file':e['file'],'rival':e.get('rival'),'res':e['result'],'map':e.get('map'),'deaths':out,'stats':st,'ours':ours}
I=[e for e in json.load(open(IDX)) if e['bot']==BOT]
with ThreadPoolExecutor(4) as ex: res=[r for r in ex.map(one,I) if r]
json.dump(res,open(OUT,'w')); print('games',len(res))
