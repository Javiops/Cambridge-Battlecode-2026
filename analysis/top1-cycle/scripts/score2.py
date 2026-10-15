import json, collections, sys
DEC = json.load(open('decisions.json'))
KILL = 12
def rate(c, dep=True, gw=0.0, wscale=1.0):
    return (c['gems'] + gw*c['gold']) / (c['tr'] + wscale*c['wait'] + KILL + 5 + (c['dep'] if dep else 0))
MODELS = {
 'nearest': lambda c: -(c['tr'] + c['wait']),
 'rate': lambda c: rate(c),
 'rate_nodep': lambda c: rate(c, dep=False),
 'rate_gold05': lambda c: rate(c, gw=0.05),
 'rate+mate': lambda c: rate(c) * (1.5 if c['mate'] else 1),
 'near+mate': lambda c: -(c['tr'] + c['wait']) + (8 if c['mate'] else 0),
 'rate-mate': lambda c: rate(c) * (0.3 if c['mate'] else 1),
 'oracle_mate': lambda c: (c['mate'], -(c['tr']+c['wait'])),
}
acc = collections.defaultdict(collections.Counter)
for D in DEC:
    key = (D['map'], D['team'])
    cands = [c for c in D['cands'] if c['hp'] < 20000]
    if not any(c['g'] == D['chosen'] for c in cands): continue
    for mn, f in MODELS.items():
        acc[key][mn] += max(cands, key=f)['g'] == D['chosen']
    acc[key]['n'] += 1; acc[key]['rand'] += 1/len(cands); acc[key]['mate'] += any(c['g']==D['chosen'] and c['mate'] for c in cands)
names = list(MODELS)
print(f"{'map':10}{'team':5}{'n':>5}{'rand':>6}{'chosen=mate':>12}" + ''.join(f"{n[:11]:>12}" for n in names))
tot = collections.Counter()
for key in sorted(acc):
    A = acc[key]; n = A['n']
    print(f"{key[0]:10}{key[1]:5}{n:5}{A['rand']/n:6.2f}{A['mate']/n:12.2f}" + ''.join(f"{A[m]/n:12.2f}" for m in names))
    for m in names + ['n', 'rand', 'mate']: tot[(key[1], m)] += A[m]
for tm in ('mite', 'uni'):
    n = tot[(tm, 'n')]; print(f"{'ALL':10}{tm:5}{n:5}{tot[(tm,'rand')]/n:6.2f}{tot[(tm,'mate')]/n:12.2f}" + ''.join(f"{tot[(tm,m)]/n:12.2f}" for m in names))
