"""Collect every match group our team played (public API, no login): one row per game in data/games.jsonl,
full group JSON in data/groups/<id>.json, map ids in data/maps.json. Optional --replays downloads replay bundles.
Usage: python3 collect.py [--replays] [--all]   (default: stop at the first page with no new group)"""
import json, os, sys, time, urllib.request
from common import *
os.makedirs(os.path.join(DATA, 'groups'), exist_ok=True)
DRAFT = ['ryth','vesper','vendetta','cassi_issac','stellar','prism','marcella','willow','ren','varg','tavi']
games_p = os.path.join(DATA, 'games.jsonl'); maps_p = os.path.join(DATA, 'maps.json')
seen = {g['group'] for g in load_jsonl(games_p)}
maps = json.load(open(maps_p)) if os.path.exists(maps_p) else {}
want_replays = '--replays' in sys.argv; everything = '--all' in sys.argv
ladder = {t['teamId']: t for t in api('/ladder')['teams']}
before = None; new = 0; stop = False
while not stop:
    page = api(f'/match-groups?scope=all&team={US}' + (f'&before={before}' if before else ''))
    groups = page.get('groups') or []
    if not groups: break
    fresh = 0
    for g in groups:
        if not any(s['teamId'] == US for s in g['sides']): continue
        if g['id'] in seen or g['status'] != 'finished': continue
        time.sleep(0.5)
        d = api(f"/match-groups/{g['id']}")
        json.dump(d, open(os.path.join(DATA, 'groups', g['id'] + '.json'), 'w'))
        side = next(s for s in g['sides'] if s['teamId'] == US); opp = next(s for s in g['sides'] if s['teamId'] != US)
        with open(games_p, 'a') as out:
            for m in d.get('matches') or []:
                st = m.get('statistics') or {}; teams = st.get('teams') or [{}, {}]
                mine = 0 if side['side'] == 'a' else 1
                if m.get('map') and m.get('mapId'): maps[m['map']] = m['mapId']
                row = dict(group=g['id'], match=m['id'], at=g['createdAt'], kind=g['kind'], opp=opp['teamName'], opp_id=opp['teamId'],
                           opp_rank=ladder.get(opp['teamId'], {}).get('rank'), map=m.get('map'), side=side['side'], rounds=m.get('rounds'),
                           result='win' if (st.get('outcome') == ('teamA' if mine == 0 else 'teamB')) else ('loss' if st.get('outcome') in ('teamA','teamB') else st.get('outcome')),
                           gems=teams[mine].get('submittedGems'), opp_gems=teams[1-mine].get('submittedGems'),
                           draft=[DRAFT[i] for i in teams[mine].get('draftPicks') or []], opp_draft=[DRAFT[i] for i in teams[1-mine].get('draftPicks') or []],
                           faults=st.get('botFaults'), replay=m.get('replayUrl'))
                out.write(json.dumps(row) + '\n'); fresh += 1
                if want_replays and m.get('replayUrl'):
                    rp = os.path.join(DATA, 'replays', m['id'] + '.zip'); os.makedirs(os.path.dirname(rp), exist_ok=True)
                    if not os.path.exists(rp):
                        time.sleep(1); urllib.request.urlretrieve(BASE + m['replayUrl'], rp)
        seen.add(g['id']); new += 1
    if fresh == 0 and not everything: stop = True
    last = groups[-1]; before = f"{last['createdAt']}_{last['id']}"
    time.sleep(0.5)
json.dump(maps, open(maps_p, 'w'), indent=1)
log(f'collect: {new} new groups, {len(seen)} total, maps known {len(maps)}')
