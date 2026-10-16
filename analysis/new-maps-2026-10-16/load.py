# Shared loaders: per-game rows (one per team per game) from match-group detail files.
import json, glob, os
D = os.path.dirname(os.path.abspath(__file__)) + '/../data'
MAPS = json.load(open('/mnt/project-files/online/data/maps.json'))
MAPNAME = {v: k for k, v in MAPS.items()}
NEW = ['stampede', 'pilgrimage', 'ambush', 'eight', 'contest', 'fragment', 'swirl', 'rushbait_v2']
DRAFT = ['ryth', 'vesper', 'vendetta', 'cassi', 'stellar', 'prism', 'marcella', 'willow', 'ren', 'varg', 'tavi']
TYPE = ['ryth', 'vesper', 'vendetta', 'cassi', 'issac', 'stellar', 'prism', 'marcella', 'willow', 'ren', 'varg', 'tavi']
ITEMS = [l.strip() for l in open('/mnt/project-files/analysis/data/items.txt')]
US = '292625c5-0f3a-49f0-a08a-9757b8f58658'

def rows(files):
    out = []
    for f in files:
        d = json.load(open(f)); grp = d['group']
        sides = {s['side']: s for s in grp['sides']}
        for m in d['matches']:
            st = m.get('statistics')
            if not st or m.get('status') != 'finished': continue
            mp = MAPNAME.get(m['mapId'], m['mapId'][:8])
            for t, side in ((0, 'a'), (1, 'b')):
                o = 1 - t
                ch = [c for c in st['champions'] if c['team'] == t]
                oc = [c for c in st['champions'] if c['team'] == o]
                win = st['outcome'] == ('teamA' if t == 0 else 'teamB')
                out.append(dict(group=grp['id'], match=m['id'], at=grp['createdAt'], kind=grp['kind'], map=mp, side=side,
                    team=sides[side]['teamName'], tid=sides[side]['teamId'], opp=sides['b' if side == 'a' else 'a']['teamName'],
                    win=win, rounds=st['round'], gems=st['teams'][t]['submittedGems'], ogems=st['teams'][o]['submittedGems'],
                    draft=[DRAFT[i] for i in st['teams'][t]['draftPicks']], odraft=[DRAFT[i] for i in st['teams'][o]['draftPicks']],
                    kills=sum(c['kills'] for c in ch), deaths=sum(c['deaths'] for c in ch),
                    gold=sum(c['earnedGold'] for c in ch), ogold=sum(c['earnedGold'] for c in oc),
                    mdmg=sum(c['monsterDamageDone'] for c in ch), cdmg=sum(c['championDamageDone'] for c in ch),
                    collected=sum(c['collectedGems'] for c in ch),
                    champs=[dict(type=TYPE[c['type']], gold=c['earnedGold'], kills=c['kills'], deaths=c['deaths'],
                                 gems=c['submittedGems'], col=c['collectedGems'], mdmg=c['monsterDamageDone'], cdmg=c['championDamageDone'],
                                 items={ITEMS[i]: n for i, n in enumerate(c['itemsBought']) if n}) for c in ch],
                    faults=st['botFaults'][t]))
    return out

def top_rows():
    return rows(sorted(glob.glob(D + '/details/*.json')))

def our_rows(since='2026-10-16T03:40'):
    gids = {json.loads(l)['group'] for l in open('/mnt/project-files/online/data/games.jsonl') if json.loads(l)['at'] >= since}
    fs = ['/mnt/project-files/online/data/groups/%s.json' % g for g in sorted(gids)]
    fs = [f for f in fs if os.path.exists(f)]
    r = [x for x in rows(fs) if x['tid'] == US and x['at'] >= since]
    return r
