# c34_pack.py SET : how packed each side farms: share of alive champion-rounds (r1-300) with >=1 / >=2 / >=3 living allies within 10,
# by result; and the same within 6. The o106 squad pricing fires only when 2+ allies are within 10.
import sys,glob,pickle,os,json,re,collections,statistics as st
sys.path.insert(0,'/tmp/claude-0/ff/gem'); from cmpwin2 import ok
pref=sys.argv[1]; bot=pref.split('_',1)[1]
idx={os.path.basename(g['file']):g for g in json.load(open('/tmp/claude-0/ff/c34/index.json')) if g['bot']==bot}
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
C=collections.defaultdict(collections.Counter)
for f in glob.glob(f'/tmp/claude-0/ff/gem/cache/{pref}__*.r300h.pkl'):
    rows=pickle.load(open(f,'rb'))
    if not rows or not ok(rows): continue
    b=os.path.basename(f); us=0 if '_A_' in b else 1; name=re.sub(rf'^{pref}__{pref}_[AB]_','',b).replace('.r300h.pkl','')
    g=idx.get(name)
    if not g: continue
    for r in rows:
        if r['round']<1 or r['round']>300: continue
        for t in (0,1):
            chs=[ch for ch in r['champions'] if ch['team']==t and ch['alive']]
            who='us' if t==us else 'riv'
            for ch in chs:
                n10=sum(1 for o in chs if o is not ch and cheb((o['x'],o['y']),(ch['x'],ch['y']))<=10)
                n6=sum(1 for o in chs if o is not ch and cheb((o['x'],o['y']),(ch['x'],ch['y']))<=6)
                c=C[(g['result'],who)]; c['n']+=1; c['a10_1']+=n10>=1; c['a10_2']+=n10>=2; c['a10_3']+=n10>=3; c['a6_1']+=n6>=1; c['a6_2']+=n6>=2
for k in sorted(C):
    c=C[k]; n=c['n']
    print(f"{pref} {k[0]:4s} {k[1]:3s}: alive champ-rounds {n}; allies within 10: >=1 {100*c['a10_1']/n:.0f}%, >=2 {100*c['a10_2']/n:.0f}%, >=3 {100*c['a10_3']/n:.0f}% | within 6: >=1 {100*c['a6_1']/n:.0f}%, >=2 {100*c['a6_2']/n:.0f}%")
