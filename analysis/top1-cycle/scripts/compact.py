import json, sys, os, glob
sel = {r['match']: r for r in json.load(open('selected.json'))}
# a match can be selected for both teams; collect all top teams per match
tops = {}
for r in json.load(open('selected.json')): tops.setdefault(r['match'], []).append(r)
def run(f):
    mid = os.path.basename(f)[:-6]; out = f'compact/{mid}.json'
    if os.path.exists(out): return
    rounds = []; groups = None; gstate = {}; gev = []; summ = None
    for l in open(f):
        r = json.loads(l)
        if r.get('summary'): summ = r; continue
        if groups is None:
            groups = {}
            for c in r['camps']:
                g = groups.setdefault(c['group'], {'tiles': [], 'gems': c.get('rewardGems'), 'gold': c.get('rewardGold'), 'respawn': c.get('respawnDelay'), 'types': []})
                g['tiles'].append((c['spawnX'], c['spawnY'])); g['types'].append(c['typeName'])
        st = {}
        for c in r['camps']:
            st[c['group']] = (c['groupStateName'], c['captureTeam'])
        for g, s in st.items():
            if gstate.get(g) != s: gev.append((r['round'], g, s[0], s[1])); gstate[g] = s
        rounds.append({'r': r['round'], 'sg': r['submittedGems'], 'c': [(c['x'], c['y'], c['health'], c['gems'], c['gold'], int(c['alive'])) for c in r['champions']]})
    champs = [(c['team'], c['typeName'], c['maxHealth']) for c in json.loads(open(f).readline())['champions']]
    json.dump({'match': mid, 'sel': tops[mid], 'groups': groups, 'gev': gev, 'champs': champs, 'rounds': rounds,
               'final': summ and {'round': summ['finalRound'], 'outcome': summ['outcomeName'], 'gems': summ['submittedGems'],
                                 'stats': [{k: c[k] for k in ('team', 'typeName', 'kills', 'deaths', 'collectedGems', 'submittedGems', 'earnedGold', 'spentGold')} for c in summ['statistics']['champions']]}}, open(out, 'w'))
run(sys.argv[1])
