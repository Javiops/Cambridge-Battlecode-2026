"""Mechanism test (process-audit-1023 §3.5): CAND vs BASE, paired by game, against one rival (default pHuntF, 80 games).
Six side-effect gauges for OUR team, from the (compacted) result JSONs:
  gold@400   earnedGold summed over our champions at r400            (bad if down)
  deaths     champion deaths per game                                  (bad if up)
  vdeaths    Vesper deaths per game                                    (bad if up)
  fuel       fuelExhausted turns per game                              (bad if up)
  cap20      round of our first camp-group capture worth 20+ gems (none = 1000)   (bad if later)
  clears400  camp groups we cleared before r400                        (bad if down)
plus result net (wins-losses of CAND minus BASE) and the mechanism counter if res/cal_CAND_RIV/counter.json exists (mechcount.py).
A gauge FAILS when it moves the bad way by more than 2 paired standard errors AND more than its floor
(gold 1%, deaths 0.4/g, vdeaths 0.15/g, fuel 15%, cap20 15 rounds, clears 0.5); WATCH when more than 1 SE.
usage: python3 mechgate.py BASE CAND [CAND...]   (env RIV=pHuntF or RIV=pHuntF,rRushHunt to pool 160 games)"""
import json,glob,os,sys,math,statistics as st
RIVS=os.environ.get('RIV','pHuntF').replace(' ',',').split(',')   # several rivals = pooled pairs
RIV='+'.join(RIVS)
def tl(runs,r):
    t=0
    for x in runs:
        t+=x['duration']
        if t>r: return float(x['value'])
    return float(runs[-1]['value'])
def gauges(f):
    d=json.load(open(f)); us='teamA' if os.path.basename(f)[0]=='A' else 'teamB'
    if not any(e['kind']=='fuelExhausted' for e in d['events']): return None   # compacted by the old compact.py: no gauges
    g={'win':1 if d['match']['outcome']==us else 0}
    g['gold400']=sum(tl(t['runs'],400) for t in d['championTimelines'] if t.get('metric')=='earnedGold' and t['owner']['team']==us)
    ours=lambda e: e['owner'].get('team')==us
    ev=lambda k: [(e['owner'].get('name'),x) for e in d['events'] if e['kind']==k and ours(e) for x in e['entries']]
    dth=ev('death')   # owner = the champion that died, entry = its killer (champion or camp)
    g['deaths']=len(dth); g['vdeaths']=sum(1 for n,x in dth if (n or '').startswith('Vesper'))
    g['fuel']=len(ev('fuelExhausted'))
    caps={}
    for n,x in ev('gemCollection'):
        if x.get('context')!='campGroup': continue
        k=(x['timestamp']['round'],x['target'].get('id')); caps[k]=caps.get(k,0)+int(x['value'])
    big=[r for (r,_),v in caps.items() if v>=20]; g['cap20']=min(big+[1000])
    g['clears400']=len({(x['timestamp']['round'],x['target'].get('id')) for n,x in ev('campClear') if x['timestamp']['round']<400})
    return g
def load(bot):
    out={}
    for R in RIVS:
      for f in glob.glob(f'res/cal_{bot}_{R}/[AB]_*.json'):
        try: g=gauges(f)
        except Exception: continue
        if g: out[R+'/'+os.path.basename(f)]=g
    return out
# name, bad direction (+1 = up is bad), floor (absolute, or relative if rel)
SPEC=[('gold400',-1,0.01,True),('deaths',1,0.4,False),('vdeaths',1,0.15,False),('fuel',1,0.15,True),('cap20',1,15,False),('clears400',-1,0.5,False)]
def counter(bot):
    out={}
    for R in RIVS:
        p=f'res/cal_{bot}_{R}/counter.json'
        if os.path.exists(p): out.update({R+'/'+k:v for k,v in json.load(open(p)).items()})
    return out or None
def judge(B,C,name):
    k=sorted(set(B)&set(C)); n=len(k)
    if not n: print(name,'no paired games with gauges'); return
    w=sum(C[x]['win']-B[x]['win'] for x in k); ch=sum(1 for x in k if C[x]['win']!=B[x]['win'])
    print(f"{name} vs base on {RIV}: n={n}  net {w:+d} (changed {ch}, bar {2*math.sqrt(max(ch,1)):.1f})  WR {sum(C[x]['win'] for x in k)/n:.0%} vs {sum(B[x]['win'] for x in k)/n:.0%}")
    fails=[]
    for g,bad,floor,rel in SPEC:
        b=[B[x][g] for x in k]; c=[C[x][g] for x in k]; d=[c[i]-b[i] for i in range(n)]
        mb=st.mean(b); md=st.mean(d); se=(st.stdev(d)/math.sqrt(n)) if n>1 else 0
        fl=floor*abs(mb) if rel else floor
        s='ok'
        if bad*md>max(2*se,fl): s='FAIL'; fails.append(g)
        elif bad*md>max(se,fl/2): s='watch'
        pct=f' ({100*md/mb:+.1f}%)' if mb else ''
        print(f"  {g:9s} base {mb:8.1f}  cand {st.mean(c):8.1f}  d {md:+8.2f}{pct:10s} se {se:6.2f}  {s}")
    tb=sum(1 for x in k if B[x]['fuel']>=30); tc=sum(1 for x in k if C[x]['fuel']>=30)
    print(f"  fuel tail games with 30+ cuts: base {tb}  cand {tc}" + ("  WATCH (runaway cut loop?)" if tc>tb+1 else ""))
    cc=counter(name)
    if cc:
        v=[cc.get(x,{}).get('n',0) for x in k]; ph=[sum(cc.get(x,{}).get('ph',[0,0,0])[i] for x in k) for i in range(3)]; tot=max(1,sum(ph))
        print(f"  counter   {st.mean(v):.1f} fires/game, games with 0: {sum(1 for x in v if x==0)}/{n}, phase r<100/100-400/400+: {' / '.join(f'{100*p/tot:.0f}%' for p in ph)}")
    else: print("  counter   none (the rule must print a status-line tag; run mechcount.py before compacting)")
    print(f"  GATE: {'FAIL '+','.join(fails) if fails else 'pass'}" + ("" if n>=80 else f"  (only {n} games: mechanism test needs 80 per rival)"))
    print(f"  CLOSE: {'can close' if n>=300 else 'unresolved below 300 paired games: a line is never closed on this alone'}")
if __name__=='__main__':
    B=load(sys.argv[1])
    for c in sys.argv[2:]: judge(B,load(c),c)
