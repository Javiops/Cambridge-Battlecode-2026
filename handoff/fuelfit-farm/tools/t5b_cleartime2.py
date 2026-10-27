# t5b_cleartime.py SET : real clear time of elk groups (both teams, r<=300): rounds from the capturing team's continuous presence within 3
# of the group (arrival) to the capture, champions of that team within 3 at capture, by group strength. Compare with the bot's model.
import sys,glob,pickle,os,collections,statistics as st
sys.path.insert(0,'/tmp/claude-0/ff/gem'); from capseq import cheb
from cmpwin2 import ok
pref=sys.argv[1]; HI=int(os.environ.get("HI","300"))
files=glob.glob(f'/tmp/claude-0/ff/gem/cache/{pref}__*.r300h.pkl')
STR={'elk':60,'wolf':20,'monolith':200,'golem':120}
R=collections.defaultdict(list); n=0
for f in files:
    rows=pickle.load(open(f,'rb'))
    if not rows or not ok(rows): continue
    b=os.path.basename(f); us=0 if '_A_' in b else 1; n+=1
    r0=rows[0]; groups=collections.defaultdict(list)
    for c in r0['camps']: groups[c['group']].append(c)
    for g,cs in groups.items():
        kinds=[c['typeName'] for c in cs]
        if 'elk' not in kinds: continue
        cen=(st.mean(c['spawnX'] for c in cs), st.mean(c['spawnY'] for c in cs)); sg=sum(STR.get(k,0) for k in kinds)
        prev=None
        for ri,r in enumerate(rows):
            if r['round']>HI: break
            ct=next((c['captureTeam'] for c in r['camps'] if c['group']==g),None)
            if prev is not None and prev not in (0,1) and ct in (0,1):
                t=ct; who='us' if t==us else 't5'
                # arrival: walk back while some champion of team t is within 3
                # arrival with kiting allowed: walk back while a champion of team t was within 5 in at least one of the last GAP rounds
                GAP=int(os.environ.get('GAP','6')); j=ri-1; last=ri-1
                while j>0:
                    if any(c['team']==t and c['alive'] and cheb((c['x'],c['y']),cen)<=5 for c in rows[j]['champions']): last=j
                    elif last-j>=GAP: break
                    j-=1
                dur=ri-1-last
                nin=max(sum(1 for c in rr['champions'] if c['team']==t and c['alive'] and cheb((c['x'],c['y']),cen)<=3) for rr in rows[max(0,ri-5):ri])
                R[(who,min(sg,140),min(nin,3))].append(dur); R[(who,min(sg,140),'all')].append(dur); R[(who,'all','all')].append(dur)
            prev=ct
print(pref,'clean',n,'elk captures r<=300 (both halves)')
for who in ('us','t5'):
    for sg in (60,80,100,120,140):
        row=[]
        for k in (1,2,3,'all'):
            L=R.get((who,sg,k),[])
            row.append(f"{k}:{len(L)} med {st.median(L):.0f}" if L else f"{k}:0")
        if R.get((who,sg,'all')): print(f"  {who} str {sg}{'+' if sg==140 else ''} clear rounds by champions within 3 at capture -> "+' | '.join(row))
    L=R[(who,'all','all')]; print(f"  {who} all: {len(L)} captures, median {st.median(L):.0f}, mean {st.mean(L):.1f}")
