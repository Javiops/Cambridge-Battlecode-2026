import sys, json, collections, pandas as pd, numpy as np, os
OUT=sys.argv[1]; STEPS=sys.argv[2]
d=pd.read_csv(f'{OUT}/turns.csv')
# death rounds from snapshots
deaths={}
for m in d.match.unique():
    alive={}; dr=collections.defaultdict(list)
    for line in open(os.path.join(STEPS,m+'.c.jsonl')):
        x=json.loads(line)
        if x['t']!='round': continue
        for c in x['champs']:
            a=c[9]
            if alive.get(c[0],1) and not a: dr[c[0]].append(x['r'])
            alive[c[0]]=a
    deaths[m]=dr
def died_between(m,i,a,b):
    return any(a<=r<=b for r in deaths[m].get(i,[]))
# dps per type: mean damage per row when attacking a champion
dps=d[d.dealt0>0].groupby('type').dealt0.mean().to_dict()
d=d.sort_values(['match','champ','round'])
eps=[]
for (m,i),g in d.groupby(['match','champ'],sort=False):
    rs=g['round'].values; cut=np.where(np.diff(rs)>3)[0]+1
    for seg in np.split(np.arange(len(g)),cut):
        e=g.iloc[seg]
        if e.near_en_dist.min()>4: continue
        fi=np.where(e.near_en_dist.values<=6)[0][0]
        F=e.iloc[fi]; end=e['round'].iloc[-1]; start=F['round']
        died=died_between(m,i,start,end+3)
        ens=set()
        for s in e.en_ids.iloc[fi:]: ens|=set(int(z) for z in str(s).split(';'))
        kills=sum(died_between(m,j,start,end+3) for j in ens)
        after=e.iloc[fi:]
        # first hitter from this champion's view in the episode
        fd=after[after.dealt0>0]['round'].min(); ft=after[after.tch0>0]['round'].min()
        fd=fd if fd==fd else 1e9; ft=ft if ft==ft else 1e9
        first = 'none' if fd==1e9 and ft==1e9 else ('us' if fd<ft else ('them' if ft<fd else 'tie'))
        def pw(types,hps):
            return sum(hps)*sum(dps.get(t,0) for t in types)
        at=[F.type]+([] if pd.isna(F.ally_types) else str(F.ally_types).split(';'))
        et=[] if pd.isna(F.en_types) else str(F.en_types).split(';')
        hp_us=F.hp+F.ally_hp6; hp_en=max(1,F.en_hp6)
        dps_us=sum(dps.get(t,0) for t in at); dps_en=max(1e-6,sum(dps.get(t,0) for t in et))
        eps.append(dict(match=m,map=F['map'],champ=i,tag=F.team_tag,type=F.type,melee=F.melee,start=start,dur=end-start+1,
            died=int(died),kills=kills,
            out='L' if died and not kills else ('W' if kills and not died else ('T' if died else 'N')),
            hp=F.hp,hp_frac=F.hp_frac,maxhp=F.maxhp,gems=F.gems,dist=F.near_en_dist,
            n_ally2=F.n_ally2,n_ally3=F.n_ally3,n_ally4=F.n_ally4,n_ally6=F.n_ally6,n_en4=F.n_en4,n_en6=F.n_en6,
            num_diff=1+F.n_ally6-F.n_en6, hp_ratio6=(hp_us)/hp_en, dps_ratio6=dps_us/dps_en,
            power_ratio=(hp_us*dps_us)/(hp_en*dps_en) if F.n_en6>0 else 9,
            ready_me=int(F.own_casts_last8==0), ally_ready=F.ally_ready, en_ready=F.en_ready,
            first=first, team_alive=F.n_team_alive, opp_alive=F.n_opp_alive, d_altar=F.d_altar, d_spawn=F.d_spawn,
            retreat_share=(after.action3=='retreat').mean(), engage_share=(after.action3=='engage').mean(),
            min_hpfrac=after.hp_frac.min(), max_en6=after.n_en6.max(), n_en8=F.n_en8, en_hp8=F.en_hp8, ally_hp8=F.ally_hp8, n_ally8=F.n_ally8, max_ally6=after.n_ally6.max(), early_ret=int((after.action3.iloc[:3]=='retreat').mean()>=0.5), early_eng=int((after.action3.iloc[:3]=='engage').mean()>=0.5), death_while_ret=int(died and after.action3.iloc[-3:].eq('retreat').any()),
            dealt=after.dealt0.sum(), taken=after.tch0.sum(), round=start))
E=pd.DataFrame(eps); E.to_csv(f'{OUT}/episodes.csv',index=False)
print(json.dumps({k:round(v,1) for k,v in dps.items()}))
print(E.groupby('tag').out.value_counts(normalize=True).unstack().round(3)); print(E.tag.value_counts())
