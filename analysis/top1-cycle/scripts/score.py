import json, collections, sys
DEC = json.load(open('decisions.json'))
def model(name, K=200, gw=0.0, dep=True, side=0.0):
    def f(c):
        t = c['tr'] + c['wait'] + c['hp']/K + 5 + (c['dep'] if dep else 0)
        return ((c['gems'] + gw*c['gold']) / t) - side*max(0, c['side'])*0.01
    return f
MODELS = {
 'nearest': lambda c: -(c['tr'] + c['wait']),
 'nearest_nowait': lambda c: -c['tr'],
 'rate': model('rate'),
 'rate_nodep': model('r', dep=False),
 'rate_gold': model('g', gw=0.15),
 'rate_K400': model('k', K=400),
 'rate_K100': model('k', K=100),
 'rate_side': model('s', side=1.0),
 'own_nearest': lambda c: -(c['tr'] + c['wait']) - 1000*(c['side'] > 0),
}
# repeat model: same transition (prev chosen -> next) seen earlier for the same champion in same game
acc = collections.defaultdict(collections.Counter)
last = {}
for D in DEC:
    key = (D['map'], D['team'])
    for mn, f in MODELS.items():
        best = max(D['cands'], key=f)['g']; acc[key][mn] += best == D['chosen']
    acc[key]['n'] += 1
    acc[key]['rand'] += 1/len(D['cands'])
    acc[key]['ncand'] += len(D['cands'])
names = list(MODELS) 
print(f"{'map':10}{'team':5}{'n':>5}{'cand':>5}{'rand':>6}" + ''.join(f"{n[:11]:>12}" for n in names))
tot = collections.Counter()
for key in sorted(acc):
    A = acc[key]; n = A['n']
    print(f"{key[0]:10}{key[1]:5}{n:5}{A['ncand']/n:5.1f}{A['rand']/n:6.2f}" + ''.join(f"{A[m]/n:12.2f}" for m in names))
    for m in names + ['n', 'rand']: tot[(key[1], m)] += A[m]
for tm in ('mite', 'uni'):
    n = tot[(tm, 'n')]; print(f"{'ALL':10}{tm:5}{n:5}{'':5}{tot[(tm,'rand')]/n:6.2f}" + ''.join(f"{tot[(tm,m)]/n:12.2f}" for m in names))
