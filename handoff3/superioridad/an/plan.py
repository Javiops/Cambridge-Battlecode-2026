# plan.py: where the 5 champions are, per map and 50-round window (r1-400).
# Sources: t10 (top10 vs top10, both teams; split winners/losers) and c34 e1foco (us + rival).
import json, gzip, os, sys, collections
W = '/tmp/claude-0/w'
def cheb(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
NW = 8
KEYS = ['fr','nn','a3','big','eh','home','dead','alive','ct','ct_own','ct_foe','ct_up','ct_dn','rc','rc_hp','rt']
def team_stats(D, team, acc):
    R = D['rounds']
    if not R: return
    sp = {}
    for t in (0, 1):
        p = [(c[3], c[4]) for c in R[0]['c'] if c[1] == t]
        sp[t] = (sum(x for x, _ in p)/len(p), sum(y for _, y in p)/len(p))
    last = {}; prev = None
    for rd in R:
        r = rd['r']
        if r < 1 or r > NW*50: prev = rd; continue
        w = (r-1)//50; a = acc[w]
        mine = [c for c in rd['c'] if c[1] == team]
        al = [c for c in rd['c'] if c[9]]
        a['alive'] += sum(1 for c in mine if c[9]); a['dead'] += sum(1 for c in mine if not c[9])
        fld = [c for c in mine if c[9] and cheb((c[3], c[4]), sp[team]) > 3]
        a['home'] += sum(1 for c in mine if c[9] and cheb((c[3], c[4]), sp[team]) <= 3)
        for c in fld:
            nn = min([cheb((c[3], c[4]), (o[3], o[4])) for o in fld if o[0] != c[0]] or [30])
            a['fr'] += 1; a['nn'] += min(nn, 30); a['a3'] += nn <= 3
            a['eh'] += cheb((c[3], c[4]), sp[1-team]) < cheb((c[3], c[4]), sp[team])
        # largest cluster (link <= 4) among field champions, per round
        if fld:
            par = {c[0]: c[0] for c in fld}
            def fd(i):
                while par[i] != i: i = par[i]
                return i
            for x in fld:
                for y in fld:
                    if x[0] < y[0] and cheb((x[3], x[4]), (y[3], y[4])) <= 4: par[fd(x[0])] = fd(y[0])
            a['big'] += max(collections.Counter(fd(c[0]) for c in fld).values()); a['rt'] += 1
        # contacts started by pairs (ours within 4 of theirs, not in contact with each other in the last 10 rounds)
        for x in al:
            if x[1] != team: continue
            for y in al:
                if y[1] == team or cheb((x[3], x[4]), (y[3], y[4])) > 4: continue
                k = (x[0], y[0]); new = r - last.get(k, -99) > 10; last[k] = r
                if not new: continue
                cp = ((x[3]+y[3])/2, (x[4]+y[4])/2)
                n = sum(1 for c in al if c[1] == team and cheb((c[3], c[4]), cp) <= 4)
                m = sum(1 for c in al if c[1] != team and cheb((c[3], c[4]), cp) <= 4)
                a['ct'] += 1; a['ct_own'] += n; a['ct_foe'] += m; a['ct_up'] += n > m; a['ct_dn'] += n < m
        # recalls / teleports home: alive both rounds, jump >= 4 onto own spawn area
        if prev:
            pc = {c[0]: c for c in prev['c']}
            for c in mine:
                p = pc.get(c[0])
                if p and p[9] and c[9] and cheb((c[3], c[4]), (p[3], p[4])) >= 4 and cheb((c[3], c[4]), sp[team]) <= 3:
                    a['rc'] += 1; a['rc_hp'] += p[5]/max(1, p[6])
        prev = rd

def run():
    out = collections.defaultdict(lambda: [collections.Counter() for _ in range(NW)])
    games = collections.Counter()
    t10 = json.load(open(W+'/assets/pcassets/replays_t10/index.json'))
    for e in t10:
        f = W+'/dec4/t10/'+os.path.basename(e['file']).replace('.repl26a', '.json.gz')
        if not os.path.exists(f): continue
        D = json.load(gzip.open(f))
        for t, s in ((0, 'a'), (1, 'b')):
            res = e[s+'_result']; src = 't10win' if res == 'win' else 't10loss'
            for key in (src, 't10'):
                team_stats(D, t, out[(key, e['map'])]); team_stats(D, t, out[(key, '*')]) if False else None
            games[(src, e['map'])] += 1; games[('t10', e['map'])] += 1
    c34 = json.load(open(W+'/assets/pcassets/replays_c34/index.json'))
    for e in c34:
        if e['bot'] != 'e1foco': continue
        f = W+'/dec4/c34e1foco/'+os.path.basename(e['file']).replace('.repl26a', '.json.gz')
        if not os.path.exists(f): continue
        D = json.load(gzip.open(f)); us = 0 if e['side'] == 'a' else 1
        for t, src in ((us, 'e1foco'), (1-us, 'c34riv')):
            team_stats(D, t, out[(src, e['map'])]); games[(src, e['map'])] += 1
    return out, games

def row(a, g):
    fr = max(1, a['fr']); ct = max(1, a['ct']); n = max(1, g)
    return {'nn': a['nn']/fr, 'a3': a['a3']/fr, 'big': a['big']/max(1, a['rt']), 'eh': a['eh']/fr,
            'home': a['home']/50/n, 'dead': a['dead']/50/n, 'ct': a['ct']/n, 'own': a['ct_own']/ct, 'foe': a['ct_foe']/ct,
            'up': a['ct_up']/ct, 'dn': a['ct_dn']/ct, 'rc': a['rc']/n, 'rchp': a['rc_hp']/max(1, a['rc'])}

if __name__ == '__main__':
    out, games = run()
    res = {}
    for (src, mp), wins in out.items():
        res.setdefault(src, {})[mp] = {'games': games[(src, mp)], 'w': [row(wins[w], games[(src, mp)]) for w in range(NW)]}
    # pooled over maps (sum counters)
    for src in list(res):
        pool = [collections.Counter() for _ in range(NW)]; g = 0
        for (s2, mp), wins in out.items():
            if s2 != src: continue
            g += games[(s2, mp)]
            for w in range(NW): pool[w].update(wins[w])
        res[src]['*'] = {'games': g, 'w': [row(pool[w], g) for w in range(NW)]}
    json.dump(res, open(W+'/an/plan.json', 'w'), indent=0)
    for src in ('t10win', 't10loss', 'e1foco', 'c34riv'):
        if src not in res: continue
        p = res[src]['*']; print('==', src, 'team-games', p['games'])
        print(' win   nn  a3   big  enemyhalf home dead  ct/g own foe  up   down recalls rc_hp')
        for w, x in enumerate(p['w']):
            print(' %3d-%3d %4.1f %.2f %.2f %.2f   %.2f %.2f %4.1f %.2f %.2f %.2f %.2f %4.2f %.2f' % (w*50+1, w*50+50, x['nn'], x['a3'], x['big'], x['eh'], x['home'], x['dead'], x['ct'], x['own'], x['foe'], x['up'], x['dn'], x['rc'], x['rchp']))
