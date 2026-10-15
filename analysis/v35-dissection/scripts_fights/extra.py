"""Extras: isolated-victim share vs baseline, per-champion spell usage in fights, outcome per opener champion, numbers-by-hit-first per map."""
import sys, json, collections, statistics as st
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_fights')
from common import *
F = json.load(open(S + '/ws2/scripts_fights/fights.json'))
byg = collections.defaultdict(list)
for f in F: byg[f['match']].append(f)
def pos(c): return (c['x'], c['y'])
def pct(a, b): return '%d%%' % round(100*a/b) if b else '-'
def real(f): return f['sides']['0']['dmg'] + f['sides']['1']['dmg'] >= 1000 or f['sides']['0']['deaths'] or f['sides']['1']['deaths']
ISO = {'us': collections.Counter(), 'them': collections.Counter()}
BASE = {'us': collections.Counter(), 'them': collections.Counter()}
USE = {'us': collections.defaultdict(collections.Counter), 'them': collections.defaultdict(collections.Counter)}
OPN = collections.defaultdict(lambda: [0, 0, 0])
for rec in selected():
    g = load_game(rec); usi = g.us
    # baseline: enemy champion-rounds within 8 of a champion of the other team -> isolated (no ally within 4)?  computed for both teams as "victim side"
    for rr in g.order[::3]:
        s = g.rounds[rr]
        for e in s.values():
            if not e['alive']: continue
            t = e['team']; victim_side = 'us' if t == usi else 'them'
            if not any(c['team'] != t and c['alive'] and cheb(pos(c), pos(e)) <= 8 for c in s.values()): continue
            BASE[victim_side]['n'] += 1
            BASE[victim_side]['alone'] += not any(c['team'] == t and c['alive'] and c['i'] != e['i'] and cheb(pos(c), pos(e)) <= 4 for c in s.values())
            BASE[victim_side]['low50'] += e['hp'] < 0.5 * e['mhp']
    for f in byg[g.match]:
        pr = prev_round(g, f['r0']); s = g.rounds[pr]
        v = f['first']['v']; vt = g.types[v][0]; victim_side = 'us' if vt == usi else 'them'
        opener = 'them' if victim_side == 'us' else 'us'
        vc = s[v]
        ISO[opener]['n'] += 1
        ISO[opener]['alone'] += not any(c['team'] == vt and c['alive'] and c['i'] != v and cheb(pos(c), pos(vc)) <= 4 for c in s.values())
        ISO[opener]['low50'] += vc['hp'] < 0.5 * vc['mhp']
        if real(f):
            sd = f['sides'][str(f['first']['at'])]
            o = OPN[(opener, f['first']['aty'])]; o[0] += 1; o[1] += sd['kills']; o[2] += len(sd['deaths'])
        # per champion spell usage: fight rounds with enemy within 4 and no cast in the previous 8 rounds
        win = [rr for rr in g.order if f['r0'] <= rr <= f['r1']]
        for t in (0, 1):
            who = 'us' if t == usi else 'them'
            for i in f['sides'][str(t)]['ids']:
                ty = g.types[i][1]
                for rr in win:
                    sp = g.rounds[prev_round(g, rr)]
                    if not sp[i]['alive'] or not g.rounds[rr][i]['alive']: continue
                    if not any(e['team'] != t and e['alive'] and cheb(pos(e), pos(sp[i])) <= 4 for e in sp.values()): continue
                    if any(rr - 8 <= x < rr for x in g.casts[i]): continue
                    USE[who][ty]['n'] += 1
                    USE[who][ty]['cast'] += rr in g.casts[i]
                    USE[who][ty]['moved'] += (rr not in g.casts[i]) and ('move' in g.acts[i].get(rr, []))
                    USE[who][ty]['atk'] += (rr not in g.casts[i]) and ('atk' in g.acts[i].get(rr, []))
print('# First victim isolated (no ally within 4) and low (<50% hp), vs baseline of the victim team\'s champion-rounds in enemy vision (within 8)')
print('| opener | openers | victim isolated | baseline isolated | victim <50% | baseline <50% |')
print('|---|---|---|---|---|---|')
for who in ('us', 'them'):
    vs = 'them' if who == 'us' else 'us'
    print('| %s | %d | %s | %s | %s | %s |' % (who, ISO[who]['n'], pct(ISO[who]['alone'], ISO[who]['n']), pct(BASE[vs]['alone'], BASE[vs]['n']), pct(ISO[who]['low50'], ISO[who]['n']), pct(BASE[vs]['low50'], BASE[vs]['n'])))
print('\n# Spell usage per champion in fight rounds with an enemy within 4 and no cast in the previous 8 rounds (both slots up)')
print('| champion | us: n | cast | walked | basic-attacked | them: n | cast | walked | basic-attacked |')
print('|---|---|---|---|---|---|---|---|---|')
for ty in sorted(set(USE['us']) | set(USE['them']), key=lambda t: -USE['us'][t]['n']):
    a, b = USE['us'][ty], USE['them'][ty]
    print('| %s | %d | %s | %s | %s | %d | %s | %s | %s |' % (ty, a['n'], pct(a['cast'], a['n']), pct(a['moved'], a['n']), pct(a['atk'], a['n']), b['n'], pct(b['cast'], b['n']), pct(b['moved'], b['n']), pct(b['atk'], b['n'])))
print('\n# Outcome per opener champion (real fights): opener side kills / deaths per fight')
print('| opener side | champion | n | kills | deaths |')
print('|---|---|---|---|---|')
for (who, ty), (n, k, d) in sorted(OPN.items(), key=lambda x: (x[0][0], -x[1][0])):
    print('| %s | %s | %d | %.2f | %.2f |' % (who, ty, n, k/n, d/n))
