"""Loader for the compact replay format ($S/ws/steps/<match>.c.jsonl) producing per-turn action records
with the state *before* each action (live positions / hp of champions and camps).
Reused by the targeting / spell analyses.  Run with: python3 -I <script>
"""
import json, collections, os
S = '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad'
RANGED = {'Cassi', 'VesperVale', 'Prism', 'Stellar', 'Tavi', 'Willow'}
MELEE = {'Issac', 'Ryth', 'Vendetta', 'Marcella', 'Ren', 'Varg'}
CASTERS = {'Cassi', 'Prism', 'Stellar', 'Tavi'}  # ranged damage spell holders
def cheb(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
def atk_range(ty): return 3 if ty in RANGED else 1

def selected():
    sel = json.load(open(S + '/ws/selected.json'))
    return sel

def load_game(match):
    f = '%s/ws/steps/%s.c.jsonl' % (S, match)
    rounds = {}; order = []; events = collections.defaultdict(list); types = {}; camps0 = {}
    final = None
    for line in open(f):
        d = json.loads(line)
        if d['t'] == 'round':
            rounds[d['r']] = {c[0]: dict(i=c[0], team=c[1], ty=c[2], x=c[3], y=c[4], hp=c[5], mhp=c[6], gems=c[7], gold=c[8], alive=c[9]) for c in d['champs']}
            if d['r'] == 0:
                camps0 = {c[0]: dict(i=c[0], ty=c[1], x=c[2], y=c[3], hp=c[4], alive=c[5], awake=c[6], group=c[7]) for c in d['camps']}
            order.append(d['r'])
            for c in d['champs']: types[c[0]] = (c[1], c[2])
        elif d['t'] == 'ev':
            events[d['r']].append(d)
        else: final = d
    return dict(match=match, rounds=rounds, order=order, events=events, types=types, camps0=camps0, final=final)

def classify_cast(ty, victims, kvictims, dashed, second_attack_follows, healed, dmg_vals, gems):
    """returns slot name string for the cast"""
    if ty == 'Cassi': return 'dmg' if (victims or kvictims) else 'stun'
    if ty == 'Issac': return 'dash' if dashed else 'reset'
    if ty == 'Ryth':
        if victims or kvictims: return 'aoestun'
        return 'reset' if second_attack_follows == 2 else 'empty'
    if ty == 'VesperVale': return 'dash' if dashed else 'reset'
    if ty == 'Vendetta': return 'dash' if dashed else 'reset'
    if ty == 'Marcella': return 'dmg' if (victims or kvictims) else 'reset'
    if ty == 'Tavi': return 'stundmg' if (victims or kvictims) else 'reset'
    if ty == 'Willow': return 'heal' if healed else 'reset'
    if ty == 'Ren': return 'dash' if dashed else ('stundmg' if (victims or kvictims) else 'empty')
    if ty == 'Varg': return 'reset' if second_attack_follows == 2 else 'shield'
    if ty in ('Stellar', 'Prism'):
        n = len(victims) + len(kvictims)
        if n == 0: return 'empty'
        if n >= 2: return 'aoe'
        d = max(dmg_vals) if dmg_vals else 0
        if ty == 'Stellar':
            ok0 = d % 20 == 0 and d >= 200
            f1 = d / 1.4
            ok1 = abs(f1 - round(f1)) < 1e-6 and round(f1) % 10 == 0 and round(f1) >= 100
            if ok0 and not ok1: return 'single'
            if ok1 and not ok0: return 'aoe'
            if ok0 and ok1: return 'single?'  # ambiguous, caller may refine
            return 'single~'  # shield-modified or odd value: default single
        else:
            f0 = d / 1.5 - 0.2 * gems; f1 = d / 1.0 - 0.2 * gems
            ok0 = abs(f0 / 10 - round(f0 / 10)) < 0.11 and f0 >= 79
            ok1 = abs(f1 / 10 - round(f1 / 10)) < 0.11 and f1 >= 79
            if ok0 and not ok1: return 'single'
            if ok1 and not ok0: return 'aoe'
            return 'single?'
    return 'unknown'

def iterate_turns(g):
    """Yields (r, actor, team, type, acts) where acts is a list of action dicts in order, each with
    kind in {'mv','atk','cast','other'} plus details and `before` state snapshot (champs dict idx->(x,y,hp,mhp,alive,gems), camps dict)."""
    rounds, order, events, types = g['rounds'], g['order'], g['events'], g['types']
    live = {i: dict(x=c['x'], y=c['y'], hp=c['hp'], mhp=c['mhp'], alive=c['alive'], gems=c['gems']) for i, c in rounds[order[0]].items()}
    camps = {i: dict(c) for i, c in g['camps0'].items()}
    for r in order:
        if r == 0: continue
        # also sync with snapshot of previous round (safer for gems/maxhp)
        pr = order[order.index(r) - 1]
        for i, c in rounds[pr].items():
            live[i].update(x=c['x'], y=c['y'], hp=c['hp'], mhp=c['mhp'], alive=c['alive'], gems=c['gems'])
        cur_actor = None; acts = []
        turns = []
        for e in events[r]:
            if e['ak'] == 1 and e['ph'] == 10:
                a = e['a']
                if a != cur_actor:
                    if cur_actor is not None: turns.append((cur_actor, acts))
                    cur_actor = a; acts = []
                before = ({i: (c['x'], c['y'], c['hp'], c['mhp'], c['alive'], c['gems']) for i, c in live.items()},
                          {i: (c['x'], c['y'], c['hp'], c['alive'], c['awake'], c['ty'], c['group']) for i, c in camps.items()})
                apos = (live[a]['x'], live[a]['y'])
                tt = types[a]
                victims = [x for x in e['eff'] if x['i'] != a and x.get('hp', 0) < 0 and types[x['i']][0] != tt[0]]
                healed = [x for x in e['eff'] if x['i'] != a and x.get('hp', 0) > 0 and types[x['i']][0] == tt[0]]
                kvictims = [x for x in e['keff'] if x.get('hp', 0) < 0]
                dashed = [x for x in e['eff'] if x['i'] == a and 'pos' in x]
                rec = dict(r=r, a=a, team=tt[0], ty=tt[1], k=e['k'], apos=apos, before=before,
                           victims=[(x['i'], -x['hp'], x['hpnow'], x.get('alive', 1)) for x in victims],
                           kvictims=[(x['i'], -x['hp'], x['hpnow'], x.get('alive', 1)) for x in kvictims],
                           healed=[(x['i'], x['hp']) for x in healed],
                           kills=[x['i'] for x in e['eff'] if x.get('alive') == 0 and x['i'] != a],
                           ckills=[x['i'] for x in e['keff'] if x.get('alive') == 0],
                           gold=sum(x.get('gold', 0) for x in e['eff'] if x['i'] == a), gems=sum(x.get('gems', 0) for x in e['eff'] if x['i'] == a))
                if e['k'] == 4:
                    rec['kind'] = 'mv'; rec['to'] = (dashed[0]['pos'][2], dashed[0]['pos'][3]) if dashed else apos
                elif e['k'] == 5: rec['kind'] = 'atk'
                elif e['k'] == 6:
                    rec['kind'] = 'cast'; rec['dashed'] = bool(dashed)
                    if dashed: rec['to'] = (dashed[0]['pos'][2], dashed[0]['pos'][3])
                else: rec['kind'] = 'other'
                acts.append(rec)
            # apply effects to live state
            for x in e['eff']:
                c = live[x['i']]
                if 'pos' in x: c['x'], c['y'] = x['pos'][2], x['pos'][3]
                if 'hpnow' in x: c['hp'] = x['hpnow']
                if 'alive' in x: c['alive'] = x['alive']
                if 'gems' in x: c['gems'] += x['gems']
                if 'maxhp' in x: c['mhp'] += x['maxhp']
            for x in e['keff']:
                c = camps[x['i']]
                if 'hpnow' in x: c['hp'] = x['hpnow']
                if 'alive' in x: c['alive'] = x['alive']
                if 'awake' in x: c['awake'] = x['awake']
                if 'pos' in x: c['x'], c['y'] = x['pos'][2], x['pos'][3]
        if cur_actor is not None: turns.append((cur_actor, acts))
        # post-process casts: classify slot
        for a, acts in turns:
            tt = types[a]
            for j, rec in enumerate(acts):
                if rec['kind'] != 'cast': continue
                after = any(x['kind'] == 'atk' for x in acts[j + 1:]); before_ = any(x['kind'] == 'atk' for x in acts[:j])
                second = 2 if (after and before_) else (1 if after else 0)
                gems = rec['before'][0][a][5]
                rec['slot'] = classify_cast(tt[1], rec['victims'], rec['kvictims'], rec['dashed'], second, rec['healed'],
                                            [v[1] for v in rec['victims']] + [v[1] for v in rec['kvictims']], gems)
                rec['second_attack'] = second
                # refine ambiguous Stellar/Prism single-vs-aoe using cooldown state and the focus estimate
                if tt[1] in ('Stellar', 'Prism') and rec['slot'] in ('single?', 'single~', 'aoe', 'single'):
                    st = g.setdefault('cd', {}).setdefault(a, {'single': -99, 'aoe': -99, 'F': None})
                    if rec['slot'] in ('single?', 'single~'):
                        av0 = r - st['single'] >= 8; av1 = r - st['aoe'] >= 8
                        if av0 and not av1: rec['slot'] = 'single'
                        elif av1 and not av0: rec['slot'] = 'aoe'
                        else:
                            d = max([v[1] for v in rec['victims']] + [v[1] for v in rec['kvictims']])
                            m0, m1 = (2.0, 1.4) if tt[1] == 'Stellar' else (1.5, 1.0)
                            F = st['F'] or (100 if tt[1] == 'Stellar' else 80)
                            lethal = any(v[2] <= 0 for v in rec['victims'] + rec['kvictims'])
                            if lethal: rec['slot'] = 'single' if rec['slot'] == 'single?' else ('single' if d > m1 * F else 'single')
                            else: rec['slot'] = 'single' if abs(d / (m0 * F) - 1) <= abs(d / (m1 * F) - 1) else 'aoe'
                    else:
                        d = max([v[1] for v in rec['victims']] + [v[1] for v in rec['kvictims']])
                        m = (2.0 if rec['slot'] == 'single' else 1.4) if tt[1] == 'Stellar' else (1.5 if rec['slot'] == 'single' else 1.0)
                        if not any(v[2] <= 0 for v in rec['victims'] + rec['kvictims']): st['F'] = max(st['F'] or 0, d / m)
                    st[rec['slot']] = r
            yield r, a, tt[0], tt[1], acts

def focus_games(team=None):
    """yields (record, game) for selected games of team ('mite'/'uni'/None=both). record['t'] = focus team index."""
    for s in selected():
        if team and s['team'] != team: continue
        s = dict(s); s['t'] = 0 if s['side'] == 'a' else 1
        yield s, load_game(s['match'])
