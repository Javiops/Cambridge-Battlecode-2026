import json,os,glob,subprocess,collections,sys
import pandas as pd
S=os.path.dirname(os.path.abspath(__file__))
sel=[]
for f in glob.glob(S+'/beh/steps/*.c.jsonl'):
    if os.path.getsize(f)<50000: continue
    m=os.path.basename(f)[:-8]; bot,opp,mp,side=m.rsplit('_',3)
    sel.append(dict(match=m,team=bot+'_vs_'+opp,side=side,map=mp))
json.dump(sel,open(S+'/beh/sel.json','w'))
subprocess.run([sys.executable,S+'/build_dataset.py',S+'/beh/steps',S+'/beh/sel.json','/mnt/project-files/analysis/top2-dissection-2026-10-15/data/mapsj',S+'/out_beh'],check=True,capture_output=True)
d=pd.read_csv(S+'/out_beh/turns.csv'); d=d[d.team_tag!='opp']; d['bot']=d.team_tag.str.split('_vs_').str[0]
c=d[d.near_en_dist<=5]
out=pd.DataFrame({'contact_turns':c.groupby('bot').size(),'ally_within2_share':(c.near_ally_dist<=2).groupby(c.bot).mean().round(3),
                  'died10_contact':c.groupby('bot').died10.mean().round(3)})
res=collections.defaultdict(collections.Counter)
for f in glob.glob(S+'/beh/steps/*.c.jsonl'):
    if os.path.getsize(f)<50000: continue
    m=os.path.basename(f)[:-8]; bot,opp,mp,side=m.rsplit('_',3); me=0 if side=='a' else 1
    prev=None; deaths=[0,0]; last=None
    for l in open(f):
        o=json.loads(l)
        if o['t']!='round': continue
        al={x[0]:(x[1],x[9]) for x in o['champs']}
        if prev:
            for i,(t,a) in al.items():
                if prev[i][1] and not a: deaths[t]+=1
        prev=al; last=o
    r=res[bot]; r['games']+=1; r['deaths']+=deaths[me]; r['kills']+=deaths[1-me]; r['wins']+=last['sub'][me]>last['sub'][1-me]
    r['gems']+=last['sub'][me]; r['rounds']+=last['r']
g=pd.DataFrame(res).T; g['gems_per_100r']=(g.gems/g.rounds*100).round(1)
print(out.join(g[['games','wins','deaths','kills','gems_per_100r']]).to_string())
