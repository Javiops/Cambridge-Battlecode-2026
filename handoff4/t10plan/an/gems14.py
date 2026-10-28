"""gems14.py TAG BOT: submitted gems at r300 / r600 / end, deaths to r600 and total, captures <= r600 for the bot side (local rep/TAG, one replaydump --camps pass per game)."""
import sys, os, json, glob, subprocess, statistics as st
T, BOT = sys.argv[1], sys.argv[2]
RD = '/home/user/ws/pcassets/viewer/replaydump.js'
def one(f):
    side = 0 if f.endswith('_a.repl26a') else 1
    p = subprocess.Popen(['node', RD, f, '--camps'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1 << 20)
    g = {}; deaths600 = 0; prev_alive = {}; prevgs = {}; prevct = {}; caps = 0
    for l in p.stdout:
        d = json.loads(l)
        if d.get('summary'):
            s = d['statistics']; g['end'] = s['submittedGems'][side]; g['endo'] = s['submittedGems'][1 - side]
            g['deaths'] = sum(c['deaths'] for c in s['champions'] if c['team'] == side); g['win'] = s['outcome'] == side + 1; g['fr'] = s['round']
            continue
        r = d.get('round')
        if r is None: continue
        if r in (300, 600): g[r] = d['submittedGems'][side]
        if r <= 600:
            for c in d['champions']:
                if c['team'] == side:
                    a = c['alive'] if 'alive' in c else c.get('health', 1) > 0
                    if prev_alive.get(c['index'], True) and not a: deaths600 += 1
                    prev_alive[c['index']] = a
            gs = {}; ct = {}
            for k in d['camps']:
                gs[k['group']] = k['groupStateName']
                if k['captureTeam'] != 2: ct[k['group']] = k['captureTeam']
            for gi, s_ in gs.items():
                if prevgs.get(gi) == 'reward_available' and s_ == 'respawning' and prevct.get(gi, ct.get(gi)) == side: caps += 1
            prevgs, prevct = gs, ct
    p.wait(); g['d600'] = deaths600; g['caps'] = caps
    return g
from concurrent.futures import ThreadPoolExecutor
files = sorted(glob.glob(f'/home/user/ws/rep/{T}/*.repl26a'))
with ThreadPoolExecutor(2) as ex: R = list(ex.map(one, files))
R = [x for x in R if 300 in x]
m = lambda k: sum(x.get(k, 0) for x in R) / len(R)
print(f"{T} ({BOT}): {len(R)} games, wins {sum(1 for x in R if x.get('win'))}; gems r300 {m(300):.0f}, r600 {m(600):.0f}, end {m('end'):.0f} (rival {m('endo'):.0f}); deaths <=r600 {m('d600'):.2f}, total {m('deaths'):.2f}; captures <=r600 {m('caps'):.1f}; final round {m('fr'):.0f}")
