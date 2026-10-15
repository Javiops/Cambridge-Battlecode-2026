"""Per-map stack exposure and carried-bag stats for our team. WS env = data dir."""
import sys, json, collections
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_reactions')
from common import *
from stack import MON
sel = load_sel(); out = collections.defaultdict(collections.Counter); bags = collections.defaultdict(list)
for rec in sel:
    G = Game(rec); side = G.side; c0 = G.camps[G.order[0]]
    def gk(k): return ('gem', k['grp']) if k['ty'] == 'gem_cluster' else ('m', k['grp'])
    ghp = collections.Counter(); mono = set()
    for k in c0.values():
        if k['ty'] in ('wolf', 'elk'): ghp[gk(k)] += k['hp']
        if k['ty'] == 'monolith': mono.add(gk(k))
    big = {g: (ghp[g] >= 3000 and g not in mono) for g in set(gk(k) for k in c0.values())}
    nbig = sum(1 for g, b in big.items() if b)
    out[rec['map']]['games'] += 1; out[rec['map']]['big_groups'] += nbig
    for r in G.order:
        if r - 1 not in G.rounds: continue
        grp_of = {}
        for c in G.rounds[r].values():
            if c['team'] != side or not c['alive']: continue
            best = None
            for k in G.camps[r].values():
                if not k['alive']: continue
                d = cheb((c['x'], c['y']), (k['x'], k['y']))
                if d <= 3 and (best is None or (k['ty'] in MON and best[1] not in MON) or d < best[2]): best = (gk(k), k['ty'], d)
            grp_of[c['i']] = best[0] if best else None
            bags[rec['map']].append(c['gems'])
        cnt = collections.Counter(g for g in grp_of.values() if g is not None)
        for i, g in grp_of.items():
            k = cnt[g] if g is not None else 0
            out[rec['map']]['cr'] += 1
            if k >= 3: out[rec['map']]['cr_stack3+'] += 1
            if k >= 3 and big.get(g): out[rec['map']]['cr_stack3+_big'] += 1
            if k >= 4: out[rec['map']]['cr_stack4+'] += 1
            if g is not None and big.get(g): out[rec['map']]['cr_big'] += 1
    # team gems per game: max bag seen
    mx = 0
    for r in G.order:
        for c in G.rounds[r].values():
            if c['team'] == side: mx = max(mx, c['gems'])
    out[rec['map']]['maxbag_sum'] += mx
print('| map | games | big groups/map | champ-rounds | on a big group | stack 3+ | stack 3+ on big | stack 4+ | mean bag carried | share of champ-rounds carrying >= 60 | max bag per game (mean) |')
print('|---|' * 11)
for m in sorted(out):
    o = out[m]; b = bags[m]
    print('| %s | %d | %d | %d | %s | %s | %s | %s | %.1f | %s | %.0f |' % (m, o['games'], o['big_groups'] // o['games'], o['cr'], '%.1f%%' % (100 * o['cr_big'] / o['cr']), '%.1f%%' % (100 * o['cr_stack3+'] / o['cr']), '%.1f%%' % (100 * o['cr_stack3+_big'] / o['cr']), '%.1f%%' % (100 * o['cr_stack4+'] / o['cr']), sum(b) / len(b), '%.1f%%' % (100 * sum(1 for x in b if x >= 60) / len(b)), o['maxbag_sum'] / o['games']))
