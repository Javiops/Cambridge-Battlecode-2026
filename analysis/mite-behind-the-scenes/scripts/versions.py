import json,collections,sys
MITE='ee83f5e5-bcad-4923-86b4-b79ea6083d2e'
names={'ee83f5e5-bcad-4923-86b4-b79ea6083d2e':'Mite','1890540d-1ffc-4847-adbf-d0d08772f268':'Intercontinental Fish','197f3952-fd35-499a-9a01-4abdf3196600':'hello'}
lad={t['teamId']:t for t in json.load(open('ladder.json'))['teams']}
G=[json.loads(l) for l in open('groups.jsonl')]
print('groups',len(G),'from',G[-1]['createdAt'],'to',G[0]['createdAt'])
def team_report(tid):
    rows=[]
    for g in G:
        for s in g['sides']:
            if s['teamId']==tid:
                opp=[x for x in g['sides'] if x['teamId']!=tid][0]
                rows.append((g['createdAt'],g['kind'],s.get('version'),s.get('submissionId'),opp['teamName'],lad.get(opp['teamId'],{}).get('rank'),s['wins'],opp['wins']))
    rows.sort()
    kinds=collections.Counter(r[1] for r in rows)
    vers=collections.OrderedDict()
    for r in rows:
        if r[2] is not None: vers.setdefault(r[2],[r[0],r[0],0,0,0,0]); v=vers[r[2]]; v[1]=r[0]; v[2]+=1; v[3]+= r[6]>r[7]; v[4]+= (r[1]=='unranked'); 
    print(f"\n### {lad.get(tid,{}).get('name',tid)} (rank {lad.get(tid,{}).get('rank')}): {len(rows)} groups {dict(kinds)}; versions seen {len(vers)}")
    for v,(a,b,n,w,u) in vers.items(): print(f"  version {v}: {a[5:16]} -> {b[5:16]}  groups {n} (unranked {u}) won {w}")
    unr=[r for r in rows if r[1]=='unranked']
    opp=collections.Counter((r[4],r[5]) for r in unr)
    print('  unranked opponents:',opp.most_common(12))
    byhour=collections.Counter(r[0][:13] for r in rows); print('  groups per hour:',sorted(byhour.items())[-30:])
for tid in [MITE,'1890540d-1ffc-4847-adbf-d0d08772f268','197f3952-fd35-499a-9a01-4abdf3196600']+sys.argv[1:]: team_report(tid)
