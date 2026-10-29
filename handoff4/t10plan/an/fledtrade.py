# per death r30-150 class (death15 EX), damage the dying champion dealt to champions in its last 10 rounds, and dmg received
import sys,os,json,gzip,collections,subprocess
d=sys.argv[1]; idx=sys.argv[2]
env=dict(os.environ,EX='1')
out=subprocess.run(['python3','an/death15.py',d,'--index',idx],capture_output=True,text=True,env=env).stdout.splitlines()
ex=[l.split() for l in out if l.endswith(('chase','dash','ranged','stayed','alone','allies','1foe','late')) and '.json.gz' in l]
side={x['file']:(0 if x['side']=='a' else 1) for x in json.load(open(idx))}
bot=os.path.basename(d.rstrip('/'))
TYPES=['Ryth','Vesper','Vendetta','Cassi','Issac','Stellar','Prism','Marcella','Willow','Ren','Varg','Tavi','HoR']
S=collections.defaultdict(lambda:[0,0,0,0]); cache={}
for fn,r,t,cat in ex:
    r=int(r)
    if fn not in cache: cache[fn]=json.load(gzip.open(os.path.join(d,fn)))
    D=cache[fn]; us=side[f"{bot}/{fn.replace('.json.gz','.repl26a')}"]
    byr={rr['r']:{c[0]:c for c in rr['c']} for rr in D['rounds']}
    me=[i for i,c in byr[r-1].items() if c[1]==us and TYPES[c[2]]==t and c[9] and not byr[r][i][9]]
    if not me: continue
    me=me[0]
    dealt=sum(x[3] for x in D['cc'] if x[1]==me and r-10<=x[0]<=r)
    got=sum(x[3] for x in D['cc'] if x[2]==me and r-10<=x[0]<=r)
    s=S[cat]; s[0]+=1; s[1]+=dealt; s[2]+=got; s[3]+=byr[r-10][me][5] if r-10 in byr and byr[r-10][me][9] else 0
for k,v in S.items(): print(k,'n',v[0],'dealt10',round(v[1]/v[0]),'got10',round(v[2]/v[0]),'hp@-10',round(v[3]/v[0]))
