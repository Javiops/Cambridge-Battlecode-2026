import json, glob, collections
lad=json.load(open('../ladder.json'))['teams']; rank={t['teamId']:t['rank'] for t in lad}
TOP={'ee83f5e5-bcad-4923-86b4-b79ea6083d2e':'mite','a4350547-b7a1-47b1-9031-4f7f084ad0d8':'uni'}
rows=[]
for f in glob.glob('groups/*.json'):
    for m in json.load(open(f))['matches']:
        if m['status']!='finished': continue
        for i,s in enumerate(m['sides']):
            if s['teamId'] in TOP:
                o=m['sides'][1-i]
                rows.append(dict(match=m['id'],team=TOP[s['teamId']],side=s['side'],map=m['map'],opp=o['teamName'],orank=rank.get(o['teamId'],99),res=s['result'],score=s['score'],oscore=o['score'],rounds=m['rounds'],created=m['createdAt'],
                  draft=m['statistics']['teams'][i]['draftPicks'] if m.get('statistics') else None))
json.dump(rows,open('all_matches.json','w'))
sel=[]; seen=set()
by=collections.defaultdict(list)
for r in rows: by[(r['team'],r['map'])].append(r)
for k,v in sorted(by.items()):
    v.sort(key=lambda r:(r['orank'],r['created']))
    used=set(); n=0
    for r in v:
        if r['opp'] in used: continue
        used.add(r['opp']); sel.append(r); n+=1
        if n>=6: break
    w=sum(r['res']=='win' for r in v); print(k, len(v), f'{w}-{len(v)-w}', [ (r['opp'][:8],r['res'][0]) for r in sel[-n:]])
json.dump(sel,open('selected.json','w')); print(len(sel), len({r['match'] for r in sel}))
