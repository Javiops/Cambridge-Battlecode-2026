"""How close are we to the top 10?  Same per-team indicators for: top-10 vs top-10 games (online/data/top10_1022 summaries),
our online games (games.jsonl + sidefix, summaries) and local panel games (compacted JSONs, compact.py with TL timelines).
  g150 g400      earnedGold of the team at r150 / r400
  gm150 gm400    collectedGems at r150 / r400
  sp150          spentGold at r150 (buy timing)
  t300           first round the team has spent 300 gold (buy timing; 1000 if never)
  d150 d400      champion deaths before r150 / r400
  clr400         camp groups cleared before r400
  cap20          round of the first 20+ gem group capture (1000 if none)
usage:
  python3 likeness.py profile                      -> writes likeness_ref.json: top10 profile (all/winners) and ours online
  python3 likeness.py gate BASE CAND [RIV,RIV]      -> local CAND-BASE delta per indicator as % of the gap to the top 10"""
import json,glob,os,sys,math,statistics as st
sys.path.insert(0,'/mnt/project-files/analysis/map-macro-v96-1021/scripts')
D='/mnt/project-files/online/data'; HERE=os.path.dirname(os.path.abspath(__file__))
REF=os.path.join(HERE,'likeness_ref.json')  # next to the script
KEYS=['g150','g400','gm150','gm400','sp150','t300','d150','d400','clr400','cap20']
GOOD={'g150':1,'g400':1,'gm150':1,'gm400':1,'sp150':1,'t300':-1,'d150':-1,'d400':-1,'clr400':1,'cap20':-1}
def tl(runs,r):
    t=0
    for x in runs:
        t+=x['duration']
        if t>r: return float(x['value'])
    return float(runs[-1]['value'])
def first_reach(runs,v):
    t=0
    for x in runs:
        if float(x['value'])>=v: return t
        t+=x['duration']
    return 1000
def prof(d,us):
    T=lambda m,r: sum(tl(t['runs'],r) for t in d['championTimelines'] if t['metric']==m and t['owner']['team']==us)
    p={'g150':T('earnedGold',150),'g400':T('earnedGold',400),'gm150':T('collectedGems',150),'gm400':T('collectedGems',400),'sp150':T('spentGold',150)}
    # team spentGold curve: sum of champion curves sampled every 10 rounds
    sp=[t['runs'] for t in d['championTimelines'] if t['metric']=='spentGold' and t['owner']['team']==us]
    p['t300']=next((r for r in range(0,1000,10) if sum(tl(x,r) for x in sp)>=300),1000)
    ev=lambda k:[x for e in d['events'] if e['kind']==k and isinstance(e.get('owner'),dict) and e['owner'].get('team')==us for x in e['entries']]
    dr=[x['timestamp']['round'] for x in ev('death')]
    p['d150']=sum(r<150 for r in dr); p['d400']=sum(r<400 for r in dr)
    p['clr400']=len({(x['timestamp']['round'],(x.get('target') or {}).get('id')) for x in ev('campClear') if x['timestamp']['round']<400})
    caps={}
    for x in ev('gemCollection'):
        if x.get('context')!='campGroup': continue
        k=(x['timestamp']['round'],(x.get('target') or {}).get('id')); caps[k]=caps.get(k,0)+int(x['value'])
    p['cap20']=min([r for (r,_),v in caps.items() if v>=20]+[1000])
    return p
def summ(L):
    return {k:{'mean':st.mean(x[k] for x in L),'sd':st.pstdev(x[k] for x in L)} for k in KEYS} | {'n':len(L)}
def team_owner_fix(d):
    # online summaries: owner has id only sometimes; map id -> team via roster
    team={c['id']:c['team'] for c in d['roster']['champions']}
    for t in d['championTimelines']:
        o=t['owner']; o.setdefault('team',team.get(o.get('id')))
    for e in d['events']:
        o=e.get('owner')
        if isinstance(o,dict) and 'team' not in o: o['team']=team.get(o.get('id'))
    return d
def profile():
    from dec import load
    top=[];topw=[]
    for f in glob.glob(f'{D}/top10_1022/summaries/*.json'):
        d=team_owner_fix(load(f))
        for us in ('teamA','teamB'):
            p=prof(d,us); top.append(p)
            if d['match']['outcome']==us: topw.append(p)
    fix={}
    for l in open('/mnt/project-files/analysis/overnight-1021/sidefix/rows_v110plus.jsonl'):
        r=json.loads(l); fix[r['match']]=r
    ours={};seen=set()
    for l in open(f'{D}/games.jsonl'):
        try: g=json.loads(l)
        except Exception: continue
        v=g.get('version')
        if v not in (122,132) or g['result'] not in ('win','loss'): continue
        r=fix.get(g['match']); side=r['tside'] if r else g['side']
        k=(v,g['opp_id'],g['map'],side,g['rounds'],g['gems'],g['opp_gems'])
        if k in seen: continue
        seen.add(k)
        p0=f"{D}/summaries/{g['match']}.json"
        if not os.path.exists(p0): continue
        try: d=team_owner_fix(load(p0))
        except Exception: continue
        rk=g.get('opp_rank') or 999
        band='top50' if rk<=50 else 'r51-100' if rk<=100 else 'r100+'
        ours.setdefault(f'v{v}',[]).append(prof(d,'teamA' if side=='a' else 'teamB'))
        ours.setdefault(f'v{v}_{band}',[]).append(prof(d,'teamA' if side=='a' else 'teamB'))
    out={'top10':summ(top),'top10_winners':summ(topw)}
    for k,L in ours.items():
        if len(L)>=30: out[k]=summ(L)
    json.dump(out,open(REF,'w'),indent=1)
    print(f"{'':16s}"+''.join(f'{k:>8s}' for k in KEYS)+'      n')
    for name,s in out.items(): print(f'{name:16s}'+''.join(f"{s[k]['mean']:8.0f}" if s[k]['mean']>=20 else f"{s[k]['mean']:8.2f}" for k in KEYS)+f"{s['n']:7d}")
def gate(base,cand,rivs,ours_key=None):
    R=json.load(open(REF)); top=R['top10']; ours=R[ours_key or sorted(k for k in R if k.startswith('v') and '_' not in k)[-1]]
    def load_local(b):
        out={}
        for riv in rivs:
            for f in glob.glob(f'res/cal_{b}_{riv}/[AB]_*.json'):
                d=json.load(open(f))
                if not any(t['metric']=='collectedGems' for t in d['championTimelines']): continue
                out[riv+'/'+os.path.basename(f)]=prof(d,'teamA' if os.path.basename(f)[0]=='A' else 'teamB')
        return out
    B=load_local(base); C=load_local(cand); k=sorted(set(B)&set(C)); n=len(k)
    if not n: print('no paired games with likeness timelines (rerun with the new compact.py)'); return
    print(f"{cand} vs {base}, {n} paired local games ({','.join(rivs)}); gap = top10 - ours online ({ours['n']} games)")
    print(f"{'':7s}{'top10':>8s}{'ours':>8s}{'gap':>8s} | {'base':>8s}{'cand':>8s}{'delta':>8s}{'se':>7s} {'gap closed':>10s}")
    score=[]
    for key in KEYS:
        t=top[key]['mean']; o=ours[key]['mean']; gap=t-o
        d=[C[x][key]-B[x][key] for x in k]; md=st.mean(d); se=st.stdev(d)/math.sqrt(n) if n>1 else 0
        frac=md/gap if abs(gap)>1e-9 else 0
        sig=abs(md)>2*se
        flag=('toward' if frac>0 else 'AWAY') if sig else ''
        if abs(gap)>0.15*top[key]['sd']: score.append(max(-1,min(1,frac)))
        print(f"{key:7s}{t:8.1f}{o:8.1f}{gap:+8.1f} | {st.mean(B[x][key] for x in k):8.1f}{st.mean(C[x][key] for x in k):8.1f}{md:+8.2f}{se:7.2f} {100*frac:+9.0f}% {flag}")
    print(f"LIKENESS: mean gap closed {100*st.mean(score):+.0f}% over {len(score)} indicators where we differ from the top 10 by > 0.15 sd"
          "  (local rivals are not the top 10: read the direction, not the size)")
if __name__=='__main__':
    if sys.argv[1]=='profile': profile()
    else: gate(sys.argv[2],sys.argv[3],(sys.argv[4] if len(sys.argv)>4 else 'pHuntF,rRushHunt').split(','))
