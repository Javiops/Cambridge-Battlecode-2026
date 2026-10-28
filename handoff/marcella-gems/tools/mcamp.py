#!/usr/bin/env python3
"""mcamp.py t10|LOCALRES : Marcella vs camps, per phase (r30-150, r150-400): per game, rounds alive, rounds in contact
(<=1 of a live camp monster), rounds she dealt monster damage, damage per damaging round, spike rounds (>=1.7x her
median hit), monster damage taken, camp deaths. Sources: summary timelines (per-round cumulative) + replay positions."""
import sys, json, os, glob, collections, statistics
sys.path.insert(0, "/mnt/project-files/analysis/farm-route-1021/capkind"); from capkind_light import dump, cheb
from concurrent.futures import ProcessPoolExecutor
def series(runs, n):
    out = []; 
    for x in runs:
        out += [float(x['value'])] * x['duration']
    out += [out[-1] if out else 0.0] * max(0, n - len(out))
    return out
def one(a):
    summ, rep, team = a
    try: s = json.load(open(summ)); rows = dump(rep)
    except Exception: return None
    if not rows: return None
    tn = 'teamA' if team == 0 else 'teamB'
    tl = {t['metric']: t for t in s['championTimelines'] if t['owner']['team'] == tn and t['owner']['name'] == 'Marcella'}
    if 'monsterDamageDone' not in tl: return None
    N = 420
    dd = series(tl['monsterDamageDone']['runs'], N); dt = series(tl['monsterDamageTaken']['runs'], N)
    cd = series(tl.get('championDamageDone', {'runs': []})['runs'], N)
    res = collections.defaultdict(collections.Counter); hits = []
    for r in rows:
        rd = r['round']
        if rd < 30: continue
        if rd >= 400: break
        ph = 'r30-150' if rd < 150 else 'r150-400'
        me = [c for c in r['champions'] if c['team'] == team and c['typeName'] == 'Marcella']
        if not me: continue
        me = me[0]; R = res[ph]
        if not me['alive']: R['dead'] += 1; continue
        R['alive'] += 1
        mons = [(m['x'], m['y']) for m in r['camps'] if m['alive'] and m['x'] >= 0]
        dm = min((cheb((me['x'], me['y']), m) for m in mons), default=99)
        foes = [(c['x'], c['y']) for c in r['champions'] if c['alive'] and c['team'] != team]
        df = min((cheb((me['x'], me['y']), f) for f in foes), default=99)
        d = dd[rd] - dd[rd - 1] if rd < N else 0; t = dt[rd] - dt[rd - 1] if rd < N else 0
        c = cd[rd] - cd[rd - 1] if rd < N else 0
        R['contact'] += dm <= 1; R['near24'] += 2 <= dm <= 4
        R['foe4'] += df <= 4
        R['contact_foe4'] += dm <= 1 and df <= 4
        if d > 0:
            R['dmgr'] += 1; R['dmg'] += d; R['dmg_at%d' % min(dm, 5)] += d
            R['dmgr_at%d' % min(dm, 5)] += 1
            hits.append((ph, d))
        if dm <= 1 and d == 0: R['contact_idle'] += 1
        if dm <= 1 and d == 0 and c > 0: R['contact_hitchamp'] += 1
        R['taken'] += t
        R['hp_frac_contact'] += (me['health'] / me['maxHealth']) if dm <= 1 else 0
    for ph in res:
        hs = sorted(h for p, h in hits if p == ph)
        if hs:
            med = statistics.median(hs); res[ph]['spike'] = sum(1 for h in hs if h >= 1.7 * med); res[ph]['spike_dmg'] = sum(h for h in hs if h >= 1.7 * med)
            res[ph]['med_x100'] = int(med * 100)
    return {ph: dict(c) for ph, c in res.items()}
def jobs(which):
    if which == 't10':
        L = json.load(open('/mnt/project-files/online/data/t10_vs_band_1024/index.json'))['games']
        R = '/mnt/project-files/online/data/replays/'
        return [(g['summary'], R + g['match'] + '.zip', 0 if g['side'] == 'a' else 1) for g in L
                if not g.get('far') and g.get('summary') and '6' in g['draft'] and os.path.exists(R + g['match'] + '.zip')]
    out = []
    for z in glob.glob(which + '/*/*.repl26a'):
        side = 0 if os.path.basename(z).startswith('A_') else 1
        out.append((z[:-8] + '.json', z, side))
    return out
if __name__ == '__main__':
    J = jobs(sys.argv[1]); T = collections.defaultdict(collections.Counter); n = 0; meds = collections.defaultdict(list)
    with ProcessPoolExecutor(4) as ex:
        for res in ex.map(one, J):
            if not res: continue
            n += 1
            for ph, c in res.items():
                for k, v in c.items():
                    if k == 'med_x100': meds[ph].append(v / 100)
                    else: T[ph][k] += v
    print(sys.argv[1], 'games', n)
    for ph in ['r30-150', 'r150-400']:
        c = T[ph]; g = max(n, 1)
        print(f" {ph}: alive {c['alive']/g:5.1f} dead {c['dead']/g:5.1f} contact {c['contact']/g:5.1f} (idle {c['contact_idle']/g:4.1f}, hitting champ {c['contact_hitchamp']/g:4.1f}, foe<=4 {c['contact_foe4']/g:4.1f}) near2-4 {c['near24']/g:5.1f} foe<=4 {c['foe4']/g:5.1f}")
        print(f"   dmg {c['dmg']/g:6.0f}/game in {c['dmgr']/g:5.1f} rounds = {c['dmg']/max(1,c['dmgr']):5.1f}/round; median hit {statistics.median(meds[ph]) if meds[ph] else 0:5.1f}; spikes {c['spike']/g:4.1f}/game ({c['spike_dmg']/max(1,c['dmg']):.0%} of dmg)"
              f"; dmg rounds by dist " + ' '.join(f"{k}:{c['dmgr_at%d'%k]/g:.1f}" for k in range(6)) + f"; taken {c['taken']/g:5.0f}; hp in contact {c['hp_frac_contact']/max(1,c['contact']):.2f}")
