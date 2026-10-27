r"""check_dec.py STATS.json DUMP.jsonl : compara un volcado de replaydump con el json de estadísticas del motor (misma partida).
Per ronda: oro y gemas de cada campeón frente a championTimelines; posiciones dentro del mapa y saltos entre rondas.
Final: kills/deaths/daño/oro/gemas/objetos de la línea summary."""
import json, sys
st, dump = sys.argv[1:3]
j = json.load(open(st))
def series(runs):
    o = []
    for r in runs: o += [float(r['value'])] * r['duration']
    return o
tl = {}
for x in j['championTimelines']:
    o = x['owner']; tl[(o['team'], o['name'], x['metric'])] = series(x['runs'])
names = {'HeartOfRuin': 'Heart of Ruin', 'VesperVale': 'Vesper Vale'}
L = [json.loads(l) for l in open(dump)]
summ = L[-1]; L = L[:-1]
W, Hh = j['match']['width'], j['match']['height']
ok = bad = 0; maxstep = 0; prev = {}; oob = 0; camps_ok = 0
for l in L:
    r = l['round']
    for c in l.get('champions', []):
        t = 'teamA' if c['team'] == 0 else 'teamB'; n = names.get(c['typeName'], c['typeName'])
        for k in ('gold', 'gems'):
            s = tl.get((t, n, k))
            if s and 1 <= r <= len(s):
                if round(s[r - 1]) == c[k]: ok += 1
                else: bad += 1
        if c['x'] >= 0:
            if not (0 <= c['x'] < W and 0 <= c['y'] < Hh): oob += 1
            key = (t, n)
            if key in prev and prev[key][2] == r - 1 and prev[key][0] >= 0:
                maxstep = max(maxstep, max(abs(c['x'] - prev[key][0]), abs(c['y'] - prev[key][1])))
        prev[(t, n)] = (c['x'], c['y'], r)
    for cp in l.get('camps', []):
        camps_ok += (cp['x'] < 0) or (0 <= cp['x'] < W and 0 <= cp['y'] < Hh and cp['health'] <= cp['maxHealth'] + 1e-6)
ncamps = sum(len(l.get('camps', [])) for l in L)
print(f'oro/gemas por ronda: coinciden {ok}, difieren {bad}; posiciones fuera del mapa {oob}; mayor salto entre rondas {maxstep}; '
      f'campamentos coherentes {camps_ok}/{ncamps}')
dif = 0
for c in summ['statistics']['champions']:
    t = 'teamA' if c['team'] == 0 else 'teamB'; n = names.get(c['typeName'], c['typeName'])
    for k in ('monsterDamageDone', 'championDamageDone', 'championDamageTaken', 'earnedGold', 'collectedGems', 'kills', 'deaths'):
        if round(c[k]) != round(tl[(t, n, k)][-1]): dif += 1; print('DIF', t, n, k, c[k], tl[(t, n, k)][-1])
print('estadísticas finales distintas:', dif, '; ganador', summ['outcomeName'], 'motor', j['match']['outcome'])
