import json,sys,os,collections,statistics as st
sys.argv=[sys.argv[0],'x','x','/mnt/project-files/analysis/top2-dissection-2026-10-15/data/mapsj','x']
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'build_dataset.py')).read().split('def process')[0])
def cheb(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
def run(steps,games,tagmap=None):
    out=[]
    by=collections.defaultdict(list)
    for g in games: by[g['match']].append(g)
    for m,recs in by.items():
        p=os.path.join(steps,m+'.c.jsonl')
        if not os.path.exists(p) or os.path.getsize(p)<50000: continue
        tag={0 if r['side']=='a' else 1:r['team'] for r in recs}
        info=mapinfo(recs[0]['map'])
        snaps,evs=load(p); R=max(snaps)
        ch={r:{c[0]:c for c in snaps[r]['champs']} for r in snaps}
        team={c[0]:c[1] for c in snaps[0]['champs']}
        last_rec={}
        for r in sorted(evs):
            pre=ch.get(r-1)
            if not pre: continue
            for e in evs[r]:
                if e['ak']==1 and e['ph']==10 and e['k']==11:
                    i=e['a']; t=team[i]
                    if tuple(e['apos']) in info['sp'][t]: continue
                    if last_rec.get(i,-9)>=r-1: last_rec[i]=r; continue  # retry of the same attempt
                    last_rec[i]=r
                    c=pre[i]; pos=(c[3],c[4])
                    ens=[j for j,x in pre.items() if team[j]!=t and x[9]]
                    ne=min([cheb(pos,(pre[j][3],pre[j][4])) for j in ens],default=99)
                    done=0
                    for rr in range(r+1,min(r+9,R)+1):
                        x=ch.get(rr,{}).get(i)
                        if x and x[9] and (x[3],x[4]) in info['sp'][t]: done=1;break
                    died=any(not ch.get(rr,{}).get(i,[0]*10)[9] for rr in range(r,min(r+10,R)+1) if rr in ch)
                    out.append(dict(tag=tag.get(t,'opp'),hp=c[5]/c[6],gems=c[7],near=ne,dsp=info['dsp'][t][pos[1]][pos[0]],dalt=info['dalt'][pos[1]][pos[0]],done=done,died=int(died),round=r))
        # deaths and champion-rounds
        for t in (0,1):
            cr=sum(1 for r in ch for i,x in ch[r].items() if team[i]==t and x[9])
            dth=0; lost=0
            for r in ch:
                if r-1 in ch:
                    for i,x in ch[r].items():
                        if team[i]==t and ch[r-1][i][9] and not x[9]: dth+=1; lost+=ch[r-1][i][7]
            out.append(dict(tag=tag.get(t,'opp'),kind='life',cr=cr,deaths=dth,lost=lost))
    return out
import pandas as pd
top=json.load(open('/mnt/project-files/analysis/top2-dissection-2026-10-15/data/selected.json'))
us=json.load(open('ours/selected_us_ok.json'))
a=run('st/steps',top)+run('ours/steps2',us)
d=pd.DataFrame(a)
life=d[d.get('kind')=='life'].groupby('tag')[['cr','deaths','lost']].sum()
rec=d[d.get('kind')!='life']
cnt=rec.groupby('tag').size()
life['recalls']=cnt; life['recalls_per_1000cr']=(life.recalls/life.cr*1000).round(2); life['deaths_per_1000cr']=(life.deaths/life.cr*1000).round(2); life['gems_lost_per_death']=(life.lost/life.deaths).round(1)
print(life)
print(rec.groupby('tag')[['hp','gems','near','dsp','dalt','done','died']].describe(percentiles=[.5]).round(2).T.to_string())
rec['hb']=pd.cut(rec.hp,[0,.3,.5,.7,.9,1.01]); print(pd.crosstab(rec.hb,rec.tag,normalize='columns').round(2))
rec['nb']=pd.cut(rec.near,[0,4,6,8,12,99]); print(pd.crosstab(rec.nb,rec.tag,normalize='columns').round(2))
print(rec.pivot_table(index='nb',columns='tag',values='done',aggfunc='mean',observed=False).round(2))
rec.to_csv('recalls.csv',index=False)
