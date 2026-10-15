import sys, json, collections, statistics as st
# usage: python3 -I trips.py $S  -> stat choice per map, family order (uni), shopping trips, gold economy, examples
S = sys.argv[1]
d = json.load(open(f'{S}/reports/scripts_draft/shop.json'))
def med(v): return round(st.median(v), 1) if v else None
def mean(v): return round(st.mean(v), 1) if v else None

print('## A. Mite: main stat per type per map (focus/strength from shard families)')
for team in ('mite', 'uni'):
    tab = collections.defaultdict(collections.Counter)
    for g in d:
        if g['team'] != team: continue
        for c in g['champs'].values():
            stats = collections.Counter()
            for k, v in c.get('items', {}).items():
                if 'shard' in k: stats[k.split('_')[-1]] += v
            main = max(stats, key=stats.get) if stats else '-'
            tab[(c['ty'], g['map'])][main] += 1
    print(team)
    for (ty, m), cnt in sorted(tab.items()): print(f'   {ty:8s} {m:10s} {dict(cnt)}')

print('\n## A2. Uni family composition by shard count')
byty = collections.defaultdict(list)
for g in d:
    if g['team'] != 'uni': continue
    for c in g['champs'].values():
        it = c.get('items', {}); sh = {k.replace('_shard_of_', ':'): v for k, v in it.items() if 'shard' in k}
        byty[c['ty']].append((sum(sh.values()), tuple(sorted(sh.items(), key=lambda x: -x[1]))))
for ty, l in byty.items():
    print(ty)
    for (n, comp), k in sorted(collections.Counter(l).items()): print('   ', n, k, comp)

print('\n## B. shopping trips')
for team in ('mite', 'uni'):
    games = [g for g in d if g['team'] == team]
    rec_tot = rec_buy = rec_hi = rec_hi_buy = 0; hp_at_rec = []; stay = []
    dead_buy = 0; buys_tot = 0; first_death_buy = 0; deaths_tot = 0
    for g in games:
        for c in g['champs'].values():
            if c['ty'] == 'Tavi': continue
            buyr = sorted(set(b['r'] for b in c['buys']))
            for rc in c['recalls']:
                rec_tot += 1; hpp = rc['hp'] / rc['mhp']; hp_at_rec.append(hpp)
                b = any(0 <= r - rc['r'] <= 2 for r in buyr)
                rec_buy += b
                if hpp >= 0.7: rec_hi += 1; rec_hi_buy += b
            for b in c['buys']:
                buys_tot += 1; dead_buy += b['dead']
            for dr in c['deaths']:
                deaths_tot += 1
                first_death_buy += any(dr <= r <= dr + 60 and any(b['dead'] for b in c['buys'] if b['r'] == r) for r in buyr)
    print(f"{team}: recalls={rec_tot} with purchase within 2 rounds={rec_buy} ({100*rec_buy/max(rec_tot,1):.0f}%); recalls at hp>=70%: {rec_hi}, of which with purchase {rec_hi_buy}; median hp% at recall arrival={med(hp_at_rec)}")
    print(f"   purchases while dead: {dead_buy}/{buys_tot} ({100*dead_buy/max(buys_tot,1):.0f}%); deaths={deaths_tot}, deaths followed by a dead-purchase={first_death_buy} ({100*first_death_buy/max(deaths_tot,1):.0f}%)")
    # gold held when arriving at spawn by recall (do they recall with gold to spend?)
    gold_at_rec = [rc['gold'] for g in games for c in g['champs'].values() for rc in c['recalls']]
    print(f"   gold carried at recall arrival: median={med(gold_at_rec)} mean={mean(gold_at_rec)} share>=30: {100*sum(x>=30 for x in gold_at_rec)/max(len(gold_at_rec),1):.0f}%")
    # gold before first purchase and gold left after last purchase in a trip
    before = [c['buys'][0]['before'] for g in games for c in g['champs'].values() if c['buys']]
    print(f"   gold at first purchase: median={med(before)}, distribution={sorted(collections.Counter(before).items())[:12]}")
    # how long do they hold >=30 gold while alive before buying? approximate with rounds between first reaching 30 gold and first buy -> skip; instead: spawn rounds per game
    sr = [c['spawn_rounds'] for g in games for c in g['champs'].values()]
    print(f"   rounds alive on spawn per champion-game: median={med(sr)} mean={mean(sr)}")

print('\n## C. consumable (slot 2) usage: what happens after a 10-gold purchase')
import re
def load_ev(m):
    ev = collections.defaultdict(list); rounds = {}
    for line in open(f'{S}/ws/steps/{m}.c.jsonl'):
        x = json.loads(line)
        if x['t'] == 'ev': ev[x['r']].append(x)
        elif x['t'] == 'round': rounds[x['r']] = x
    return ev, rounds
kinds = collections.Counter(); jumps = collections.Counter(); shown = 0
for team in ('mite', 'uni'):
    for g in [g for g in d if g['team'] == team][:12]:
        ev, rounds = load_ev(g['match'])
        for i, c in g['champs'].items():
            i = int(i)
            tens = [b['r'] for b in c['buys'] if b['gold'] == 10]
            for r0 in tens:
                # next 80 rounds: actions of this champion with unusual kinds or short pos jumps at ph 14
                for r in range(r0, min(r0 + 120, g['last_round'])):
                    for e in ev.get(r, []):
                        if e['ak'] == 1 and e['a'] == i and e['k'] in (11, 12, 20, 23, 26, 14, 2, 3, 8):
                            kinds[(team, e['k'], tuple(sorted(x for x in e['eff'][0].keys())) if e['eff'] else ())] += 1
                        for x in e['eff']:
                            if x['i'] == i and 'pos' in x and e['ph'] == 14 and x.get('alive') is None:
                                dd = max(abs(x['pos'][2] - x['pos'][0]), abs(x['pos'][3] - x['pos'][1]))
                                if 2 <= dd <= 3: jumps[(team, dd)] += 1
                                if 2 <= dd <= 3 and shown < 6: shown += 1; print('   jump example', team, g['match'][:8], c['ty'], 'buy r', r0, 'jump r', r, x['pos'])
print('   step kinds by this champion after a 10g buy:', kinds.most_common(12))
print('   2-3 tile jumps at turn start after buy:', jumps)

print('\n## D. gold economy per team-game (final_gold from snapshot)')
for team in ('mite', 'uni'):
    games = [g for g in d if g['team'] == team]
    E = [sum(c['earned'] for c in g['champs'].values()) for g in games]
    Sp = [sum(b['gold'] for c in g['champs'].values() for b in c['buys']) for g in games]
    F = [sum(c['final_gold'] for c in g['champs'].values()) for g in games]
    R = [g['rounds'] for g in games]
    print(f"{team}: per game earned median={med(E)} spent={med(Sp)} unspent at end={med(F)} ({100*sum(F)/sum(E):.0f}% of earned); gold/round={sum(E)/sum(R):.2f}; per champion unspent median={med([c['final_gold'] for g in games for c in g['champs'].values()])}")
    for m in 'collision corners elkring expanse interlock lanes monolith packs rows'.split():
        gs = [g for g in games if g['map'] == m]
        e = [sum(c['earned'] for c in g['champs'].values()) for g in gs]; s = [sum(b['gold'] for c in g['champs'].values() for b in c['buys']) for g in gs]
        w = sum(g['res'] == 'win' for g in gs)
        print(f"   {m:10s} {w}-{len(gs)-w} earned/g={mean(e)} spent/g={mean(s)} rounds={mean([g['rounds'] for g in gs])} emblems/g={mean([sum(v for c in g['champs'].values() for k,v in c.get('items',{}).items() if 'emblem' in k) for g in gs])}")

print('\n## E. example purchase sequences')
def show(g):
    print(f"-- {g['team']} {g['match']} map={g['map']} side={g['side']} vs {g['opp']} {g['res']} {g['score']}-{g['oscore']} rounds={g['rounds']}")
    for i, c in g['champs'].items():
        it = {k.replace('_shard_of_', ' sh '): v for k, v in c.get('items', {}).items() if 'shard' in k}
        seq = '; '.join(f"r{b['r']}:-{b['gold']}{'(hp+%d)'%b['maxhp'] if b['maxhp'] else ''}{'[dead]' if b['dead'] else ''}{'[field]' if not b['dead'] and not b['onspawn'] else ''}" for b in c['buys'])
        print(f"   {c['ty']:8s} earned={c['earned']} spent={sum(b['gold'] for b in c['buys'])} left={c['final_gold']} cons={c.get('consumables')} items={it}\n      {seq}")
for m in ('e9c3f66b-32ce-49dc-a9da-7eddbcb69fdc', '265a46b9', 'ced08a2f'):
    for g in d:
        if g['match'].startswith(m): show(g)
