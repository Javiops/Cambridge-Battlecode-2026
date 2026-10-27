# mapgroups.py : one replay per map -> group table {map: {group_id: {gems, gold, kinds, cx, cy}}}; verifies campClear ids against positions  (group reward = per-camp value, the engine pays it once per capture; an earlier version summed it over camps)
import sys,json,glob,os,collections,statistics as st
sys.path.insert(0,'/tmp/claude-0/ff/replay2'); from dump2 import dump, cheb
out={}
for pat in ('/tmp/claude-0/ff/ws4/res/o1b_n80/*/A_*.repl26a','/tmp/claude-0/ff/ws4/res/new30_o1b/rTop1/A_*.repl26a','/tmp/claude-0/ff/ws4/res/o4b_n80/*/A_*.repl26a','/tmp/claude-0/ff/ws4/res/far_o1b/*/A_*.repl26a'):
    for f in sorted(glob.glob(pat)):
        m=os.path.basename(f)[2:-8]
        if m in out: continue
        rows=dump(f)
        if not rows: print('no rows',m); continue
        g=collections.defaultdict(list)
        for c in rows[0]['camps']: g[c['group']].append(c)
        out[m]={str(k):{'gems':max(c['rewardGems'] for c in cs),'gold':max(c['rewardGold'] for c in cs),'members':len(cs),'kinds':sorted(set(c['typeName'] for c in cs)),'cx':st.mean(c['spawnX'] for c in cs),'cy':st.mean(c['spawnY'] for c in cs)} for k,cs in g.items()}
        # verify: campClear entries (x,y) within 3 of the group centre of the same id
        j=json.load(open(f[:-8]+'.json')); ok=bad=0
        for e in j['events']:
            if e['kind']!='campClear': continue
            for en in e['entries']:
                gi=str(en['target']['id']); 
                if gi in out[m] and cheb((en['x'],en['y']),(out[m][gi]['cx'],out[m][gi]['cy']))<=3: ok+=1
                else: bad+=1
        print(m, len(out[m]),'groups; campClear id check ok',ok,'bad',bad, flush=True)
json.dump(out,open('/tmp/claude-0/ff/gem/cache/mapgroups.json','w')); print('maps',len(out))
