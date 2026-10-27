# t5b_income.py SET : gold income sources r<=300 both sides: capture gold by kind (rewardGold of the group), kill gold (100 x enemy deaths)
import sys,glob,pickle,os,collections
sys.path.insert(0,'/tmp/claude-0/ff/gem'); from capseq import analyse
from cmpwin2 import ok
pref=sys.argv[1]; files=glob.glob(f'/tmp/claude-0/ff/gem/cache/{pref}__*.r300h.pkl')
S={'us':collections.Counter(),'t5':collections.Counter()}; n=0
for f in files:
    rows=pickle.load(open(f,'rb'))
    if not rows or not ok(rows): continue
    b=os.path.basename(f); us=0 if '_A_' in b else 1; n+=1
    ggold={}; 
    for c in rows[0]['camps']: ggold[c['group']]=ggold.get(c['group'],0)+c.get('rewardGold',0)
    deaths={0:0,1:0}; prev={}
    for r in rows:
        if r['round']>300: break
        for ch in r['champions']:
            k=(ch['team'],ch['index']); p=prev.get(k)
            if p and p['alive'] and not ch['alive']: deaths[ch['team']]+=1
            prev[k]=ch
    for who,t in (('us',us),('t5',1-us)):
        caps,_=analyse(rows,t,300)
        for c in caps:
            if c['r']<=300: S[who]['cap_'+c['kind'][:8]]+=ggold.get(c['g'],0); S[who]['cap_total']+=ggold.get(c['g'],0)
        S[who]['kill_gold']+=100*deaths[1-t]; S[who]['deaths']+=deaths[t]
print(pref,'clean',n)
for who in ('us','t5'):
    d=S[who]; print(f"  {who}: capture gold r<=300 /game {d['cap_total']/n:.0f} (" + ', '.join(f"{k[4:]} {v/n:.0f}" for k,v in d.items() if k.startswith('cap_') and k!='cap_total') + f"); kill gold {d['kill_gold']/n:.0f}; deaths {d['deaths']/n:.2f}; est. total {(d['cap_total']+d['kill_gold'])/n:.0f}")
