"""Q1b: search lexicographic target-choice rules (ordered criteria) that best reproduce observed targets.  python3 -I q1b_rules.py"""
import sys, os, collections, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import *
SINGLE = {('Cassi', 'dmg'), ('Tavi', 'stundmg'), ('Ren', 'stundmg'), ('Marcella', 'dmg'), ('Stellar', 'single'), ('Prism', 'single')}
KEYS = {
    'hp': lambda c, x: c['hp'],
    'hp%': lambda c, x: c['hp'] / c['mhp'],
    'dist': lambda c, x: c['dist'],
    'ranged': lambda c, x: 0 if c['ranged'] else 1,
    'gems': lambda c, x: -c['gems'],
    'allydmg': lambda c, x: 0 if c['allydmg'] > 0 else 1,
    'sticky': lambda c, x: 0 if c['sticky'] else 1,
    'recent': lambda c, x: -c['recent'],
    'killable': lambda c, x: 0 if c['killable'] else 1,
}
for TEAM in ['mite', 'uni']:
    decisions = []  # (ty, kindname, tgt, [cand dicts])
    prev_target = {}
    for s, g in focus_games(TEAM):
        t = s['t']; m = s['match'][:8]
        team_dmg_round = collections.defaultdict(float); cur_r = None
        hit_by_team = collections.defaultdict(dict)
        for r, a, team, ty, acts in iterate_turns(g):
            if r != cur_r: team_dmg_round = collections.defaultdict(float); cur_r = r
            if team != t: continue
            for rec in acts:
                if rec['kind'] == 'atk': R = atk_range(ty); kn = 'atk'
                elif rec['kind'] == 'cast' and (ty, rec['slot']) in SINGLE: R = 4; kn = 'spell'
                else: continue
                if not rec['victims']: continue
                tgt = rec['victims'][0][0]; mydmg = rec['victims'][0][1]
                ch, _ = rec['before']
                key = (m, a); prevt = prev_target[key][1] if (key in prev_target and r - prev_target[key][0] <= 3) else -1
                prev_target[key] = (r, tgt)
                cands = []
                for i, c in ch.items():
                    if g['types'][i][0] == t or not c[4] or c[2] <= 0 or cheb(rec['apos'], (c[0], c[1])) > R: continue
                    cands.append(dict(i=i, hp=c[2], mhp=c[3], dist=cheb(rec['apos'], (c[0], c[1])), ranged=g['types'][i][1] in RANGED, gems=c[5],
                                      allydmg=team_dmg_round.get(i, 0), sticky=i == prevt, killable=c[2] <= mydmg,
                                      recent=sum(v for rr, v in hit_by_team[i].items() if r - 3 <= rr < r)))
                for v in rec['victims']: team_dmg_round[v[0]] += v[1]; hit_by_team[v[0]][r] = hit_by_team[v[0]].get(r, 0) + v[1]
                if len(cands) >= 2 and tgt in [c['i'] for c in cands]: decisions.append((ty, kn, tgt, cands))
    def score(rule, subset=None):
        hit = n = 0
        for ty, kn, tgt, cands in decisions:
            if subset and not subset(ty, kn): continue
            best = min(cands, key=lambda c: tuple(KEYS[k](c, None) for k in rule))
            bk = tuple(KEYS[k](best, None) for k in rule)
            ties = [c for c in cands if tuple(KEYS[k](c, None) for k in rule) == bk]
            n += 1; hit += (1 / len(ties)) if tgt in [c['i'] for c in ties] else 0
        return hit / n if n else 0, n
    print('=== TEAM', TEAM, 'decisions', len(decisions))
    res = []
    base = ['hp', 'hp%', 'dist', 'ranged', 'allydmg', 'sticky', 'recent', 'gems']
    for L in (1, 2, 3):
        for rule in itertools.permutations(base, L):
            if 'killable' not in rule: rule = ('killable',) + rule
            res.append((score(rule)[0], rule))
    res.sort(reverse=True)
    seen = set()
    for sc, rule in res[:12]: print('  %.3f %s' % (sc, '>'.join(rule)))
    for sub, name in [(lambda ty, kn: ty in MELEE, 'melee'), (lambda ty, kn: ty in RANGED and kn == 'atk', 'ranged basic'), (lambda ty, kn: kn == 'spell', 'spells')]:
        rs = sorted(((score(r, sub)[0], r) for _, r in res[:400]), reverse=True)[:4]
        print('  subset', name, 'n=%d' % score(('hp',), sub)[1], ['%.3f %s' % (a, '>'.join(b)) for a, b in rs])
