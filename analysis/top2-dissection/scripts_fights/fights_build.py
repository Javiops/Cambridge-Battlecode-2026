"""Build fight records for all 108 selected games -> $S/reports/scripts_fights/fights.json
A fight = cluster of champion-on-champion hits, merged when within 5 rounds and 8 tiles (union-find).
"""
import sys, json, collections
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_fights')
from common import *

def build(g):
    hits = sorted(g.hits, key=lambda h: h['seq'])
    n = len(hits); par = list(range(n))
    def find(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for i in range(n):
        for j in range(i-1, -1, -1):
            if hits[i]['r'] - hits[j]['r'] > 5: break
            if cheb(hits[i]['vpos'], hits[j]['vpos']) <= 8 or cheb(hits[i]['apos'], hits[j]['apos']) <= 8:
                par[find(i)] = find(j)
    groups = collections.defaultdict(list)
    for i in range(n): groups[find(i)].append(hits[i])
    fights = []
    for gid, hs in groups.items():
        hs.sort(key=lambda h: h['seq'])
        r0, r1 = hs[0]['r'], hs[-1]['r']
        first = hs[0]
        pr = prev_round(g, r0)
        s0 = g.rounds[pr]
        loc = first['vpos']
        f = dict(match=g.match, team=g.team, us=g.us, map=g.map, opp=g.rec['opp'], res=g.rec['res'], r0=r0, r1=r1, loc=loc, nhits=len(hs))
        f['first'] = dict(a=first['a'], at=g.types[first['a']][0], aty=g.types[first['a']][1], v=first['v'], vty=g.types[first['v']][1], kind=first['kind'], dist=first['dist'], dmg=first['dmg'])
        ateam = g.types[first['a']][0]
        # participants = alive within 8 of the first hit location at snapshot before r0, plus anyone who dealt/received damage in the fight
        involved = set(h['a'] for h in hs) | set(h['v'] for h in hs)
        side = {}
        for t in (0, 1):
            pres = [c for c in s0.values() if c['team'] == t and c['alive'] and cheb((c['x'], c['y']), loc) <= 8]
            inv = [i for i in involved if g.types[i][0] == t]
            ids = sorted(set(c['i'] for c in pres) | set(inv))
            hp = sum(s0[i]['hp'] for i in ids if s0[i]['alive']); mhp = sum(s0[i]['mhp'] for i in ids if s0[i]['alive'])
            dmg = sum(h['dmg'] for h in hs if g.types[h['a']][0] == t)
            dmg_atk = sum(h['dmg'] for h in hs if g.types[h['a']][0] == t and h['kind'] == 'atk')
            deaths = [(r, i, k) for (r, i, k) in g.deaths if g.types[i][0] == t and r0 <= r <= r1 + 1 and i in ids]
            # position context of the side's champions at s0 (those present)
            dsp = [g.dspawn[t][s0[i]['y']][s0[i]['x']] for i in ids if s0[i]['alive']]
            dal = [g.daltar[s0[i]['y']][s0[i]['x']] for i in ids if s0[i]['alive']]
            gems = sum(s0[i]['gems'] for i in ids if s0[i]['alive'])
            # busy with a camp in the 2 rounds before r0 (hitting a camp or hit by a camp)
            busy = [i for i in ids if any(rr in g.campatk[i] or rr in g.camphit[i] for rr in (pr, r0))]
            # camp awake within 4 tiles of any of our champs at s0
            camp_near = any(cm['alive'] and cm['awake'] and cheb((cm['x'], cm['y']), (s0[i]['x'], s0[i]['y'])) <= 4 for cm in g.camps[pr].values() for i in ids if s0[i]['alive'])
            # all alive champions of the team in the game (for "allies dead" context)
            alive_total = sum(1 for c in s0.values() if c['team'] == t and c['alive'])
            side[t] = dict(ids=ids, types=[g.types[i][1] for i in ids], n=len([i for i in ids if s0[i]['alive']]), n_present=len(pres), hp=hp, mhp=mhp, hpp=round(100*hp/mhp) if mhp else 0,
                           dmg=dmg, dmg_atk=dmg_atk, deaths=[(r, i, g.types[i][1]) for (r, i, k) in deaths], kills=0,
                           dspawn=min(dsp) if dsp else None, daltar=min(dal) if dal else None, gems=gems, busy=busy, camp_near=camp_near, alive_total=alive_total)
        for t in (0, 1): side[t]['kills'] = len(side[1-t]['deaths'])
        # ---- approach: who closed the distance in the 4 rounds before the first hit
        a, v = first['a'], first['v']
        rs = [rr for rr in g.order if r0 - 4 <= rr < r0]
        if rs:
            s_a = g.rounds[rs[0]]
            if s_a[a]['alive'] and s_a[v]['alive']:
                d_start = cheb((s_a[a]['x'], s_a[a]['y']), (s_a[v]['x'], s_a[v]['y']))
                # attacker movement toward victim's final position vs victim movement toward attacker's final position
                a_move = cheb((s_a[a]['x'], s_a[a]['y']), first['apos']); v_move = cheb((s_a[v]['x'], s_a[v]['y']), first['vpos'])
                da = cheb((s_a[a]['x'], s_a[a]['y']), first['vpos']) - cheb(first['apos'], first['vpos'])
                dv = cheb((s_a[v]['x'], s_a[v]['y']), first['apos']) - cheb(first['vpos'], first['apos'])
                f['approach'] = dict(d_start=d_start, a_closed=da, v_closed=dv, a_moved=a_move, v_moved=v_move)
        # ---- per-champion retreat detection within [r0, r1+8]
        win = [rr for rr in g.order if r0 <= rr <= r1 + 8]
        retreats = []
        for t in (0, 1):
            for i in side[t]['ids']:
                prevd = None; prevnear = None; started = False
                for k, rr in enumerate(win):
                    c = g.rounds[rr][i]
                    if not c['alive']: break
                    foes = [e for e in g.rounds[rr].values() if e['team'] != t and e['alive'] and cheb((e['x'], e['y']), (c['x'], c['y'])) <= 10]
                    if not foes: prevd = None; continue
                    d = min(cheb((e['x'], e['y']), (c['x'], c['y'])) for e in foes)
                    moved = 'move' in g.acts[i].get(rr, []) or 'dash' in g.acts[i].get(rr, [])
                    if prevd is not None and d > prevd and moved and not started:
                        # sustained: no damage dealt in next 3 rounds and distance not decreasing by own moves
                        nxt = win[k+1:k+4]
                        if nxt and all(g.dealt[i].get(x, 0) == 0 for x in nxt):
                            pc = g.rounds[win[k-1]][i]
                            hpp = round(100 * pc['hp'] / pc['mhp'])
                            allies = sum(1 for e in g.rounds[rr].values() if e['team'] == t and e['alive'] and e['i'] != i and cheb((e['x'], e['y']), (c['x'], c['y'])) <= 8)
                            enemies = len(foes)
                            # destination over the next 8 rounds
                            after = [x for x in g.order if rr < x <= rr + 12]
                            died = any(not g.rounds[x][i]['alive'] for x in after)
                            recalled = any(rr <= x <= rr + 10 for x in g.recall_start[i])
                            arrived = any(rr <= x <= rr + 16 for x in g.recall_arrive[i])
                            dsp0 = g.dspawn[t][c['y']][c['x']]
                            last = after[-1] if after else rr
                            lc = g.rounds[last][i]
                            dsp1 = g.dspawn[t][lc['y']][lc['x']] if lc['alive'] else None
                            # nearest ally distance change
                            def nearest_ally(x):
                                cc = g.rounds[x][i]
                                al = [cheb((e['x'], e['y']), (cc['x'], cc['y'])) for e in g.rounds[x].values() if e['team'] == t and e['alive'] and e['i'] != i]
                                return min(al) if al else None
                            na0 = nearest_ally(rr); na1 = nearest_ally(min(rr + 4, last)) if lc['alive'] else None
                            into_bush = any(tile(g, g.rounds[x][i]['x'], g.rounds[x][i]['y']) == '"' for x in after[:4]) if after else False
                            taken_prev = sum(g.taken[i].get(x, 0) for x in win[max(0, k-3):k])
                            # recall distance to nearest enemy at recall start
                            rec_d = None
                            for x in g.recall_start[i]:
                                if rr <= x <= rr + 10:
                                    cc = g.rounds[x][i]
                                    fo = [cheb((e['x'], e['y']), (cc['x'], cc['y'])) for e in g.rounds[x].values() if e['team'] != t and e['alive']]
                                    rec_d = min(fo) if fo else 99; break
                            retreats.append(dict(team=t, i=i, ty=g.types[i][1], r=rr, hpp=hpp, hp=pc['hp'], allies=allies, enemies=enemies, d=d, died=died, recalled=recalled, arrived=arrived,
                                                 dsp0=dsp0, dsp1=dsp1, na0=na0, na1=na1, bush=into_bush, taken_prev=taken_prev, rec_d=rec_d,
                                                 allies_dead=side[t]['alive_total'] - sum(1 for e in g.rounds[rr].values() if e['team'] == t and e['alive'])))
                            started = True
                    prevd = d
        f['retreats'] = retreats
        f['sides'] = {str(t): side[t] for t in (0, 1)}
        # chase: after the first retreat of a side, how many tiles did the enemy hitters keep advancing / keep hitting
        fights.append(f)
    fights.sort(key=lambda f: f['r0'])
    return fights

if __name__ == '__main__':
    out = []
    for rec in selected():
        g = load_game(rec)
        fs = build(g)
        out.extend(fs)
        print(rec['team'], rec['map'], rec['match'][:8], 'fights', len(fs), file=sys.stderr)
    json.dump(out, open(S + '/reports/scripts_fights/fights.json', 'w'))
    print(len(out), 'fights')
