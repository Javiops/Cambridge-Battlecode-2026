import json, glob, collections, statistics as S
from events import extract, cheb
def legs_for(d, team):
    ev, idx, sp, A, G = extract(d, team)
    R = d['rounds']; out = {}
    for i in idx:
        legs = []; cur = {'start': 0, 'caps': [], 'tribs': [], 'end': None}
        for e in ev[i]:
            r, k, w, a = e
            if k == 'cap': cur['caps'].append((r, w, a))
            elif k == 'trib': cur['tribs'].append((r, a))
            elif k in ('recall', 'death'):
                if k == 'recall':
                    # skip tiny dashes misread: require the previous position far from spawn
                    prev = R[r-1]['c'][i] if r-1 < len(R) else None
                    if prev and cheb((prev[0], prev[1]), sp) <= 6: continue
                hp = R[r-1]['c'][i][2] / d['champs'][i][2] if r-1 < len(R) else None
                cur['end'] = (r, k, hp, R[r-1]['c'][i][3]); legs.append(cur); cur = {'start': r, 'caps': [], 'tribs': [], 'end': None}
        legs.append(cur)
        out[i] = legs
    return out, G, sp, A
def team_of(d, s): return 0 if s['side'] == 'a' else 1
if __name__ == '__main__':
    rows = collections.defaultdict(lambda: collections.Counter()); lists = collections.defaultdict(lambda: collections.defaultdict(list))
    for f in sorted(glob.glob(__import__('os').environ.get('COMPACT','compact')+'/*.json')):
        d = json.load(open(f))
        for s in d['sel']:
            t = team_of(d, s); key = (s['map'], s['team'])
            L, G, sp, A = legs_for(d, t)
            C = rows[key]; X = lists[key]; C['games'] += 1; C['wins'] += s['res'] == 'win'
            X['rounds'].append(d['final']['round'])
            for i, legs in L.items():
                for lg in legs:
                    if lg['end'] is None: continue
                    C[lg['end'][1]] += 1
                    X['caps_per_leg'].append(len(lg['caps'])); X['len'].append(lg['end'][0] - lg['start'])
                    if lg['end'][1] == 'recall':
                        X['rc_hp'].append(lg['end'][2]); X['rc_gems'].append(lg['end'][3])
                        X['rc_after_cap'].append(1 if lg['caps'] and lg['end'][0] - lg['caps'][-1][0] <= 3 else 0)
                        X['rc_trib_in_leg'].append(1 if lg['tribs'] else 0)
    print(f"{'map':10}{'team':5}{'W-G':>6}{'rnd':>5}{'recall':>7}{'death':>6}{'cap/leg':>8}{'leglen':>7}{'rc_hp':>6}{'rc_gem':>7}{'rc@cap':>7}{'trib/leg':>9}")
    for key in sorted(rows):
        C = rows[key]; X = lists[key]; m = lambda v: S.mean(v) if v else float('nan')
        print(f"{key[0]:10}{key[1]:5}{C['wins']:>3}-{C['games']:<2}{m(X['rounds']):5.0f}{C['recall']/C['games']:7.1f}{C['death']/C['games']:6.1f}{m(X['caps_per_leg']):8.2f}{m(X['len']):7.0f}{m(X['rc_hp']):6.2f}{m(X['rc_gems']):7.0f}{m(X['rc_after_cap']):7.2f}{m(X['rc_trib_in_leg']):9.2f}")
