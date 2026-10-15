# Damage dealt to camps per champion and per attacking round, plus damage taken from camps: ours vs Mite.
import json, sys, collections
def stats(f, t):
    own = None; dmg = collections.Counter(); rounds = collections.defaultdict(set); taken = collections.Counter(); names = {}
    for l in open(f):
        d = json.loads(l)
        if d['t'] == 'round' and d['r'] == 0:
            names = {c[0]: c[2] for c in d['champs'] if c[1] == t}
        if d['t'] != 'ev': continue
        if d['ak'] == 1 and d['a'] in names:
            h = -sum(k.get('hp', 0) for k in d.get('keff', []) if k.get('hp', 0) < 0)
            if h: dmg[d['a']] += h; rounds[d['a']].add(d['r'])
        if d['ak'] == 2:
            for x in d.get('eff', []):
                if x['i'] in names and x.get('hp', 0) < 0: taken[x['i']] -= x['hp']
    return {names[i]: (dmg[i], len(rounds[i]), round(dmg[i] / max(1, len(rounds[i]))), taken[i]) for i in names}
a = stats(sys.argv[1], 0 if sys.argv[2] == 'a' else 1); b = stats(sys.argv[3], 0 if sys.argv[4] == 'a' else 1)
print('champ    ours: dmg rounds dmg/round taken   | mite: dmg rounds dmg/round taken')
for n in a: print(f'{n:8s} {a[n]} | {b.get(n)}')
