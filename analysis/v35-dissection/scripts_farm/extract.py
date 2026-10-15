# usage: python3 -I extract.py [match ...]  -> writes out/<match>.json with everything the farm questions need, for BOTH teams.
import sys, json, math, collections, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
OUT=os.environ.get('FARM_OUT',S+'/ws2/scripts_farm/out'); os.makedirs(OUT,exist_ok=True)
def run(rec):
    G=Game(rec); mp=G.map; t=G.t; R=G.R; order=G.order
    alltiles={}
    for g,info in G.groups.items():
        for p in info['tiles']: alltiles[p]=g
    nch=len(G.own)
    r0=R[order[0]]
    st={c[0]:dict(gems=c[7],gold=c[8],hp=c[5],mhp=c[6],pos=(c[3],c[4]),alive=c[9]) for c in r0['champs']}
    ch={}
    for c in r0['champs']:
        i=c[0]
        ch[i]=dict(i=i,team='us' if c[1]==t else 'opp',ty=c[2],captures=[],tributes=[],recalls=[],deaths=[],respawns=[],buys=[],killgains=[],
                   states=collections.Counter(),moves=0,camphits=0,champhits=0,tanked_hits=0,tanked_dmg=0,ranged_d=collections.Counter(),
                   segs=[],passes=0,bag_since=[] ,earned=0, firstcap=None)
    spawn_alt={}
    for tm in (0,1): spawn_alt[tm]=min(near_d(mp,mp['dAlt'],x,y) for x,y in mp['sp'][tm])
    # camp state
    camp_alive={c[0]:c[5] for c in r0['camps']}; camp_pos={c[0]:(c[2],c[3]) for c in r0['camps']}
    grp_alive_r={g:0 for g in G.groups}   # round the group (re)spawned
    first_hit={}; attackers=collections.defaultdict(lambda:collections.defaultdict(float)); tank=collections.defaultdict(collections.Counter)
    caps=[]; resp=collections.defaultdict(list); gdeath=collections.defaultdict(list)
    cur_trib={}; cur_rec={}; pending_passes={}
    seg={i:dict(start=st[i]['pos'],steps=0,r0=0) for i in ch}
    last_purpose={i:dict(r=0,pos=st[i]['pos']) for i in ch}
    sub=[]
    def group_of_pos(p):
        if p in alltiles: return alltiles[p]
        return min(G.groups,key=lambda g:min(cheb(p,q) for q in G.groups[g]['tiles']))
    for r in order:
        snap=R[r]
        acted=collections.defaultdict(set)
        dead_now={i for i in ch if not st[i]['alive']}
        prev_camp_alive=dict(camp_alive)
        for e in G.ev[r]:
            a=e.get('a'); ak=e['ak']; k=e['k']
            if ak==1 and a in ch:
                acted[a].add(k)
                if k==11: cur_rec[a]=dict(r0=r,gems=st[a]['gems'],hp=st[a]['hp'],mhp=st[a]['mhp'],gold=st[a]['gold'],pos=st[a]['pos'],done=None)
                if k==12:
                    cur_trib[a]=dict(r0=r,gems=st[a]['gems'],pos=st[a]['pos'],done=None,bag=0,oldest=None,newest=None)
                    bs=ch[a]['bag_since']
                    if bs: cur_trib[a]['oldest']=r-bs[0]; cur_trib[a]['newest']=r-bs[-1]; cur_trib[a]['ncap']=len(bs)
                    ch[a]['tributes'].append(cur_trib[a])
                if k==20 and a in cur_trib and cur_trib[a]['done'] is None: cur_trib[a]['cancel']=r
                if k in (5,6):
                    for kf in e.get('keff',[]):
                        if kf.get('hp',0)<0 and kf['i'] in G.camp_group:
                            g=G.camp_group[kf['i']]; key=(g,grp_alive_r[g]); first_hit.setdefault(key,r); attackers[key][a]+=-kf['hp']; ch[a]['camphits']+=1
                            if k==5: ch[a]['ranged_d'][cheb(e['apos'],camp_pos[kf['i']])]+=1
                    for x in e.get('eff',[]):
                        if x.get('hp',0)<0 and x['i'] in ch and x['i']!=a: ch[a]['champhits']+=1
            if ak==2:
                for x in e.get('eff',[]):
                    if x.get('hp',0)<0 and x['i'] in ch:
                        ch[x['i']]['tanked_hits']+=1; ch[x['i']]['tanked_dmg']+=-x['hp']
                        g=G.camp_group.get(a)
                        if g is not None: tank[(g,grp_alive_r[g])][x['i']]+=-x['hp']
            for kf in e.get('keff',[]):
                if 'alive' in kf and kf['i'] in G.camp_group:
                    camp_alive[kf['i']]=kf['alive']
                    if kf['alive']==1 and 'pos' in kf: camp_pos[kf['i']]=(kf['pos'][2],kf['pos'][3])
                if 'pos' in kf and kf['i'] in camp_pos and kf.get('alive',1): camp_pos[kf['i']]=(kf['pos'][2],kf['pos'][3])
            for x in e.get('eff',[]):
                i=x['i']
                if i not in ch: continue
                if 'pos' in x:
                    x0,y0,x1,y1=x['pos']; st[i]['pos']=(x1,y1)
                    if x.get('alive')==1 and st[i]['alive']==0:
                        pass
                    elif ak==1 and a==i and k==4:
                        if max(abs(x1-x0),abs(y1-y0))<=1: ch[i]['moves']+=1; seg[i]['steps']+=1
                        else:
                            seg[i]=dict(start=(x1,y1),steps=0,r0=r); last_purpose[i]=dict(r=r,pos=(x1,y1))
                            if (x1,y1) in mp['sp'][G.teamof[i]] and i in cur_rec and cur_rec[i]['done'] is None:
                                cur_rec[i]['done']=r; ch[i]['recalls'].append(cur_rec.pop(i))
                if 'alive' in x:
                    if x['alive']==0 and st[i]['alive']==1:
                        ch[i]['deaths'].append(dict(r=r,gems=st[i]['gems'],gold=st[i]['gold'],pos=st[i]['pos'],terr=None))
                        ch[i]['bag_since']=[]
                        if i in cur_trib and cur_trib[i]['done'] is None: cur_trib[i]['died']=r
                        if i in cur_rec and cur_rec[i]['done'] is None: cur_rec[i]['died']=r; ch[i]['recalls'].append(cur_rec.pop(i))
                    if x['alive']==1 and st[i]['alive']==0:
                        ch[i]['respawns'].append(r); seg[i]=dict(start=st[i]['pos'],steps=0,r0=r); last_purpose[i]=dict(r=r,pos=st[i]['pos'])
                    st[i]['alive']=x['alive']
                if 'hpnow' in x: st[i]['hp']=x['hpnow']
                if 'maxhp' in x: st[i]['mhp']+=x['maxhp']
                if 'gold' in x:
                    if x['gold']>0: ch[i]['earned']+=x['gold']
                    if k==13 and ak==1 and a==i and x['gold']<0:
                        ch[i]['buys'].append(dict(r=r,gold=-x['gold'],maxhp=x.get('maxhp',0),dead=int(not st[i]['alive']),onspawn=int(st[i]['pos'] in mp['sp'][G.teamof[i]]),before=st[i]['gold'],hp=st[i]['hp'],mhp=st[i]['mhp']))
                    st[i]['gold']+=x['gold']
                if 'gems' in x:
                    if x['gems']>0 and ak==0 and e['ph']==7:
                        # capture: which group died this round nearest to champion
                        p=st[i]['pos']; died=[g for g in G.groups if any(prev_camp_alive[c] and not camp_alive[c] for c in G.camp_group if G.camp_group[c]==g)]
                        g=min(died,key=lambda g:min(cheb(p,q) for q in G.groups[g]['tiles'])) if died else group_of_pos(p)
                        gi=G.groups[g]
                        # nearest-camp test from last purpose point
                        lp=last_purpose[i]; cand=[]
                        for g2,inf in G.groups.items():
                            if inf['gems']<=0 or 'monolith' in inf['types']: continue
                            # alive at last purpose round?
                            rr=lp['r']; sn=R[rr] if rr in R else snap
                            alive2=any(c[5] for c in sn['camps'] if G.camp_group[c[0]]==g2)
                            if not alive2 and g2!=g: continue
                            d=G.gd(g2)[lp['pos'][1]][lp['pos'][0]] if lp['pos'][0]>=0 else 10**6
                            cand.append((d,g2))
                        cand.sort(); rank=next((n for n,(d,g2) in enumerate(cand) if g2==g),None)
                        dsel=next((d for d,g2 in cand if g2==g),None); dnear=cand[0][0] if cand else None
                        key=(g,grp_alive_r[g])
                        att=attackers.get(key,{}); fh=first_hit.get(key)
                        near=sum(1 for cc in snap['champs'] if cc[1]==G.teamof[i] and cc[9] and cheb((cc[3],cc[4]),p)<=4)
                        tk=tank.get(key,collections.Counter()); tank_i=tk.most_common(1)[0][0] if tk else None
                        rec_c=dict(i=i,team=ch[i]['team'],r=r,g=g,jg=gi['jg'],gems=x['gems'],gold=x.get('gold',0),hp=gi['hp'],ggems=gi['gems'],terr=gi['terr'],dOwn=gi['dOwn'],
                                   pos=p,dAlt=mp['dAlt'][p[1]][p[0]] if p[0]>=0 else None,spawnAlt=spawn_alt[G.teamof[i]],
                                   natt=len(att),dur=(r-fh) if fh is not None else None,near=near,att=[G.typeof[j] for j in att],dmg=sum(att.values()),
                                   tank=G.typeof[tank_i] if tank_i is not None else None,tank_dmg=sum(tk.values()),since_up=r-grp_alive_r[g],
                                   rank=rank,ncand=len(cand),dsel=dsel,dnear=dnear,gems_before=st[i]['gems'],recall=None)
                        ch[i]['captures'].append(rec_c); caps.append(rec_c); ch[i]['bag_since'].append(r)
                        if ch[i]['firstcap'] is None: ch[i]['firstcap']=r
                        last_purpose[i]=dict(r=r,pos=p)
                        # walking segment end
                        sg=seg[i]; d=bfs_cached(mp,sg['start'])[p[1]][p[0]] if sg['start'][0]>=0 else -1
                        if d>=0 and d<10**6 and (sg['steps']>0 or d>0): ch[i]['segs'].append((sg['steps'],d))
                        seg[i]=dict(start=p,steps=0,r0=r)
                    elif x['gems']>0: ch[i]['killgains'].append(dict(r=r,gems=x['gems']))
                    elif x['gems']<0 and k==18:
                        if i in cur_trib and cur_trib[i]['done'] is None: cur_trib[i]['done']=r; cur_trib[i]['bag']=-x['gems']
                        else: ch[i]['tributes'].append(dict(r0=None,gems=st[i]['gems'],pos=st[i]['pos'],done=r,bag=-x['gems']))
                        ch[i]['bag_since']=[]
                        p=st[i]['pos']; sg=seg[i]; d=bfs_cached(mp,sg['start'])[p[1]][p[0]] if sg['start'][0]>=0 else -1
                        if d>=0 and d<10**6 and (sg['steps']>0 or d>0): ch[i]['segs'].append((sg['steps'],d))
                        seg[i]=dict(start=p,steps=0,r0=r); last_purpose[i]=dict(r=r,pos=p)
                    st[i]['gems']+=x['gems']
            # group deaths/respawns
            if ak==0 and e['ph']==7:
                for g in G.groups:
                    cs=[c for c in G.camp_group if G.camp_group[c]==g]
                    if any(prev_camp_alive[c] for c in cs) and not any(camp_alive[c] for c in cs): gdeath[g].append(r)
            if ak==0 and e['ph']==1 and k==1:
                for kf in e.get('keff',[]):
                    if kf.get('alive')==1 and kf['i'] in G.camp_group:
                        g=G.camp_group[kf['i']]
                        if not resp[g] or resp[g][-1]!=r: resp[g].append(r); grp_alive_r[g]=r; first_hit.pop((g,r),None)
        # per-round state + altar passes
        sub.append(snap['sub'])
        for cc in snap['champs']:
            i=cc[0]; c=ch[i]
            if not cc[9]: c['states']['dead']+=1; continue
            if i in cur_trib and cur_trib[i]['done'] is None and cur_trib[i].get('cancel') is None and cur_trib[i].get('died') is None and r-cur_trib[i]['r0']<=math.ceil(cur_trib[i]['gems']/10)+1: s='tribute'
            elif i in cur_rec and cur_rec[i]['done'] is None and r-cur_rec[i]['r0']<=5: s='recall'
            elif 13 in acted[i]: s='shop'
            elif (5 in acted[i] or 6 in acted[i]):
                hitcamp=any(kf.get('hp',0)<0 and kf['i'] in G.camp_group for e in G.ev[r] if e['ak']==1 and e.get('a')==i for kf in e.get('keff',[]))
                hitch=any(x.get('hp',0)<0 and x['i'] in ch and x['i']!=i for e in G.ev[r] if e['ak']==1 and e.get('a')==i for x in e.get('eff',[]))
                s='camp' if hitcamp else ('fight' if hitch else ('walk' if 4 in acted[i] else 'cast_other'))
            elif 4 in acted[i]: s='walk'
            elif 12 in acted[i] or 18 in acted[i]: s='tribute'
            elif 11 in acted[i]: s='recall'
            else: s='idle'
            c['states'][s]+=1
            # altar pass: adjacent to an altar with >=10 gems, not tributing
            if s not in ('tribute','recall','dead') and st[i]['gems']>=10 and mp['dAlt'][cc[4]][cc[3]]==0:
                pending_passes.setdefault(i,r)
            else:
                if i in pending_passes:
                    r_pass=pending_passes.pop(i)
                    started=any(tb.get('r0') is not None and r_pass<=tb['r0']<=r+1 for tb in c['tributes'])
                    if not started: c['passes']+=1
        # timeout stale tribute/recalls
        for i,tb in list(cur_trib.items()):
            if tb['done'] is None and r-tb['r0']>math.ceil(max(tb['gems'],1)/10)+3: tb['interrupted']=True; cur_trib.pop(i)
        for i,rc in list(cur_rec.items()):
            if rc['done'] is None and r-rc['r0']>7: rc['interrupted']=True; ch[i]['recalls'].append(cur_rec.pop(i))
    # mark captures followed by a recall start within 3 rounds (and a tribute after arrival before another capture)
    for i,c in ch.items():
        recs=sorted([rc['r0'] for rc in c['recalls']]); tribs=sorted([tb['done'] for tb in c['tributes'] if tb['done']])
        for n,cp in enumerate(c['captures']):
            nxt=c['captures'][n+1]['r'] if n+1<len(c['captures']) else 10**6
            rr=[x for x in recs if cp['r']-5<=x<=cp['r']+3]
            cp['recall']=bool(rr)
            cp['trib_before_next']=any(cp['r']<x<nxt for x in tribs)
        c['states']=dict(c['states']); c['ranged_d']=dict(c['ranged_d']); c.pop('bag_since',None)
        c['gems_end']=st[i]['gems']; c['gold_end']=st[i]['gold']
        c['tributes']=[tb for tb in c['tributes']]
    # summary items
    if G.summary:
        for cs in G.summary['stats']['champions']:
            i=cs['index']
            if i in ch:
                ch[i]['items']={ITEMS[n]:v for n,v in enumerate(cs['itemsBought']) if v}
                ch[i]['consumables']=cs['consumablesBought']; ch[i]['earnedGold']=cs['earnedGold']; ch[i]['spentGold']=cs['spentGold']
                ch[i]['collectedGems']=cs['collectedGems']; ch[i]['submittedGems']=cs['submittedGems']; ch[i]['monsterDamageDone']=cs['monsterDamageDone']
    out=dict(match=rec['match'],map=rec['map'],opp=rec['opp'],orank=rec['orank'],tier=tier(rec['orank']),res=rec['res'],score=rec['score'],oscore=rec['oscore'],rounds=order[-1],nch=nch,t=t,
             draft=rec['draft'],odraft=rec['odraft'],sub=sub,champs=list(ch.values()),groups={g:{k:(sorted(v) if isinstance(v,set) else v) for k,v in inf.items()} for g,inf in G.groups.items()},
             gdeath=dict(gdeath),resp=dict(resp),spawn_alt=spawn_alt)
    json.dump(out,open(f'{OUT}/{rec["match"]}.json','w'))
_bc={}
def bfs_cached(mp,p):
    key=(mp['file'],p)
    if key not in _bc: _bc[key]=bfs(mp,[p])
    return _bc[key]
if __name__=='__main__':
    ids=sys.argv[1:]
    for rec in SEL:
        if ids and rec['match'] not in ids: continue
        if not os.path.exists(WS+'/steps/%s.c.jsonl'%rec['match']): continue
        if os.path.exists(f'{OUT}/{rec["match"]}.json') and not ids: continue
        try: run(rec)
        except Exception as ex:
            import traceback; traceback.print_exc(); print('FAIL',rec['match'])
