"""Stacking context: per death (camp next to it, camp damage in prev 5 rounds, how many of ours on the same camp group) and
per champion-round exposure by stack size. Data dir from WS, output file from argv[1]."""
import sys, json, collections
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_reactions')
from common import *
MON = {'wolf', 'elk', 'monolith'}
def process(rec):
    G = Game(rec); side = G.side
    base = dict(match=rec['match'], map=rec['map'], opp=rec['opp'], orank=rec['orank'], res=rec['res'])
    r0 = G.order[0]; c0 = G.camps[r0]
    # group key: replay group id, but gem clusters have their own numbering that collides with monster/gold ids
    def gk(k): return ('gem', k['grp']) if k['ty'] == 'gem_cluster' else ('m', k['grp'])
    ghp = collections.Counter(); mono = set()
    for k in c0.values():
        if k['ty'] in ('wolf', 'elk'): ghp[gk(k)] += k['hp']
        if k['ty'] == 'monolith': mono.add(gk(k))
    big = {g: (ghp[g] >= 3000 and g not in mono) for g in set(gk(k) for k in c0.values())}  # bot rule: P_STACK_HP 3000, monoliths excluded
    def oncamp(r, p):
        """group id of a living camp entity within 3 of p (prefer monsters), else None"""
        best = None
        for k in G.camps[r].values():
            if not k['alive']: continue
            d = cheb(p, (k['x'], k['y']))
            if d <= 3 and (best is None or (k['ty'] in MON and best[1] not in MON) or d < best[2]): best = (gk(k), k['ty'], d)
        return best[0] if best else None
    def near_monster(r, p, rad=3):
        out = []
        for k in G.camps[r].values():
            if k['alive'] and k['ty'] in MON and cheb(p, (k['x'], k['y'])) <= rad: out.append(k)
        return out
    expo = collections.Counter(); deaths = []; hits = []
    for r in G.order:
        if r - 1 not in G.rounds: continue
        for t in (0, 1):
            us = (t == side)
            grp_of = {}
            for c in G.rounds[r].values():
                if c['team'] == t and c['alive']: grp_of[c['i']] = oncamp(r, (c['x'], c['y']))
            cnt = collections.Counter(g for g in grp_of.values() if g is not None)
            for i, g in grp_of.items():
                k = cnt[g] if g is not None else 0
                expo[(us, k, big.get(g, False) if g is not None else False)] += 1
                if G.champ_dmg(r, i) and not G.champ_dmg(r - 1, i):  # episode-ish start
                    hits.append(dict(base, us=us, ty=G.ty(i), r=r, stack=k, big=big.get(g, False) if g is not None else False))
    for i in G.types:
        t = G.team(i); us = (t == side)
        for d in G.death_round[i]:
            pr = d - 1
            if pr not in G.rounds or (d, i) in G.pair_death: continue
            p = G.pos(pr, i)
            mons = near_monster(pr, p)
            g = oncamp(pr, p)
            mates = [c for c in G.rounds[pr].values() if c['team'] == t and c['alive'] and c['i'] != i]
            stack = 1 + sum(1 for c in mates if g is not None and oncamp(pr, (c['x'], c['y'])) == g) if g is not None else 0
            # stack 5 rounds before the first hit of final episode is approximated by stack at d-5
            r5 = max(G.order[0] + 1, d - 5)
            p5 = G.pos(r5, i) if G.alive(r5, i) else p
            g5 = oncamp(r5, p5)
            stack5 = (1 + sum(1 for c in G.rounds[r5].values() if c['team'] == t and c['alive'] and c['i'] != i and oncamp(r5, (c['x'], c['y'])) == g5)) if g5 is not None else 0
            campdmg5 = sum(v for rr in range(max(1, d - 5), d + 1) for (s, v, kk) in G.dmg[rr][i] if s == 'camp')
            camphit5 = sum(1 for rr in range(max(1, d - 5), d + 1) if any(s == 'camp' for (s, v, kk) in G.dmg[rr][i]))
            allies6 = sum(1 for c in mates if cheb(p, (c['x'], c['y'])) <= 6)
            foes8 = sum(1 for c in G.rounds[pr].values() if c['team'] != t and c['alive'] and cheb(p, (c['x'], c['y'])) <= 8)
            deaths.append(dict(base, us=us, ty=G.ty(i), i=i, r=d, gems=G.rounds[pr][i]['gems'], killer=G.kill.get((d, i)),
                               mon3=len(mons), mon_awake=sum(1 for k in mons if k['awake']), mon_ty=','.join(sorted(set(k['ty'] for k in mons))),
                               big=big.get(g, False) if g is not None else False, grp=str(g), stack=stack, stack5=stack5, big5=big.get(g5, False) if g5 is not None else False,
                               camphit5=camphit5, campdmg5=campdmg5, allies6=allies6, foes8=foes8))
    return expo, deaths, hits
if __name__ == '__main__':
    sel = load_sel(); expo = collections.Counter(); D = []; H = []
    for n, rec in enumerate(sel):
        if not os.path.exists(W + '/steps/%s.c.jsonl' % rec['match']): print('missing', rec['match']); continue
        e, d, h = process(rec); expo.update(e); D += d; H += h
        if n % 25 == 0: print(n, len(D), flush=True)
    json.dump(dict(expo=[[k[0], k[1], k[2], v] for k, v in expo.items()], deaths=D, hits=H, ngames=len(sel)), open(sys.argv[1], 'w'))
    print('done', len(D), len(H))
