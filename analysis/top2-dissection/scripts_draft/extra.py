import sys, json, collections, statistics as st
S = sys.argv[1]
d = json.load(open(f'{S}/reports/scripts_draft/shop.json'))
def med(v): return round(st.median(v), 1) if v else None
for team in ('mite', 'uni'):
    games = [g for g in d if g['team'] == team]
    hi = [rc for g in games for c in g['champs'].values() if c['ty'] != 'Tavi' for rc in c['recalls'] if rc['hp'] / rc['mhp'] >= 0.7]
    lo = [rc for g in games for c in g['champs'].values() if c['ty'] != 'Tavi' for rc in c['recalls'] if rc['hp'] / rc['mhp'] < 0.7]
    print(team, 'high-hp recalls', len(hi), 'gold median', med([r['gold'] for r in hi]), 'share gold>=90:', round(100 * sum(r['gold'] >= 90 for r in hi) / len(hi)), '% share>=30:', round(100 * sum(r['gold'] >= 30 for r in hi) / len(hi)), '% | low-hp recalls', len(lo), 'gold median', med([r['gold'] for r in lo]), 'share>=90', round(100 * sum(r['gold'] >= 90 for r in lo) / len(lo)))
    # how many shopping turns happen at game start without recall (first buy before any recall and before any death)
    nores = sum(1 for g in games for c in g['champs'].values() if c['buys'] and (not c['recalls'] or c['buys'][0]['r'] < c['recalls'][0]['r']) and (not c['deaths'] or c['buys'][0]['r'] < c['deaths'][0]))
    tot = sum(1 for g in games for c in g['champs'].values() if c['buys'])
    print('   first purchase before any recall/death (walked back or never left):', nores, '/', tot)
    # purchases by shard count per step
    cnt = collections.Counter(b['gold'] // 30 for g in games for c in g['champs'].values() for b in c['buys'] if b['gold'] % 30 == 0)
    print('   shards per buy step:', sorted(cnt.items()))
    # time to first purchase per map
    for m in 'collision corners elkring expanse interlock lanes monolith packs rows'.split():
        fb = [c['buys'][0]['r'] for g in games if g['map'] == m for c in g['champs'].values() if c['buys']]
        print(f'   {m:10s} first-buy round median {med(fb)} ; champion-games with no purchase: {sum(1 for g in games if g["map"]==m for c in g["champs"].values() if not c["buys"])}')
# damage validation: Mite Varg in ced08a2f (buys 5 jungle strength at r62): basic attack damage before/after
m = 'ced08a2f-f879-4815-b317-60247067f35b'
g = [x for x in d if x['match'] == m and x['team'] == 'mite'][0]
vi = [int(i) for i, c in g['champs'].items() if c['ty'] == 'Varg'][0]
dmg = collections.defaultdict(collections.Counter)
for line in open(f'{S}/ws/steps/{m}.c.jsonl'):
    x = json.loads(line)
    if x['t'] == 'ev' and x['k'] == 5 and x['ak'] == 1 and x['a'] == vi:
        for k in x['keff']:
            if k.get('hp', 0) < 0: dmg['before62' if x['r'] < 62 else ('62-192' if x['r'] < 192 else 'after192')][-k['hp']] += 1
print('Mite Varg camp basic-attack damage by period (buys: r62 5 jungle str, r192 5 durability str + 4 bruiser hp):', {k: v.most_common(3) for k, v in dmg.items()})
