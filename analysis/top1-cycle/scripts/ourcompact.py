import json, sys, os, glob
# usage: ourcompact.py OUTROOT TAG TEAMNAME  -> compact_TAG/*.json with sel = side a
root, tag, tname = sys.argv[1:4]; od = f'compact_{tag}'; os.makedirs(od, exist_ok=True)
for dd in sorted(glob.glob(f'{root}/*/')):
    mp = os.path.basename(dd.rstrip('/')); f = dd + 'dump.jsonl'
    rounds = []; groups = None; gstate = {}; gev = []; summ = None; first = None
    for l in open(f):
        r = json.loads(l)
        if r.get('summary'): summ = r; continue
        if first is None: first = r
        if groups is None:
            groups = {}
            for c in r['camps']:
                g = groups.setdefault(c['group'], {'tiles': [], 'gems': c.get('rewardGems'), 'gold': c.get('rewardGold'), 'respawn': c.get('respawnDelay'), 'types': [], 'hp': 0})
                g['tiles'].append((c['spawnX'], c['spawnY'])); g['types'].append(c['typeName']); g['hp'] += c['maxHealth']
        st = {c['group']: (c['groupStateName'], c['captureTeam']) for c in r['camps']}
        for g, s in st.items():
            if gstate.get(g) != s: gev.append((r['round'], g, s[0], s[1])); gstate[g] = s
        rounds.append({'r': r['round'], 'sg': r['submittedGems'], 'c': [(c['x'], c['y'], c['health'], c['gems'], c['gold'], int(c['alive'])) for c in r['champions']]})
    champs = [(c['team'], c['typeName'], c['maxHealth']) for c in first['champions']]
    win = summ['outcomeName'] == 'teamA'
    sel = [{'match': f'{tag}_{mp}', 'team': tname, 'side': 'a', 'map': mp, 'opp': 'b', 'res': 'win' if win else 'loss', 'score': summ['submittedGems'][0], 'oscore': summ['submittedGems'][1], 'rounds': summ['finalRound']}]
    json.dump({'match': sel[0]['match'], 'sel': sel, 'groups': groups, 'gev': gev, 'champs': champs, 'rounds': rounds,
               'final': {'round': summ['finalRound'], 'outcome': summ['outcomeName'], 'gems': summ['submittedGems'], 'stats': []}}, open(f'{od}/{mp}.json', 'w'))
