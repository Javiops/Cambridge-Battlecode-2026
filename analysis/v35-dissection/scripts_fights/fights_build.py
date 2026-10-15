"""Build fight records for the 150 games of our bot (v35) -> $S/ws2/scripts_fights/fights.json
A fight = cluster of champion-on-champion hits merged when within 5 rounds and 8 tiles (union-find), as in the top-2 dissection.
Every side-dependent field is computed for both teams (keys '0'/'1'); f['us'] gives our team index.
"""
import sys, json, collections
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_fights')
from common import *
RANGE = {'melee': 1, 'caster': 3, 'ranged': 3}
def rng(ty): return RANGE[cls(ty)]
def pos(c): return (c['x'], c['y'])

def activity(g, i, r0, pr, pr2):
    """what champion i was doing at the moment of the first hit (rounds pr2, pr = the 2 rounds before r0, and r0 before the hit)"""
    # fighting elsewhere: dealt/took champion damage in the previous 5 rounds (a different cluster)
    k = g.ridx[r0]
    prev5 = g.order[max(0, k-5):k]
    if any(g.dealt[i].get(x, 0) or g.taken[i].get(x, 0) for x in prev5): return 'fighting'
    if any(r0 - 5 <= x < r0 for x in g.recall_start[i]) and not any(r0 - 5 <= x <= r0 for x in g.recall_arrive[i]): return 'recalling'
    ts = [x for x in g.tribute_start[i] if r0 - 3 <= x <= r0]
    if ts and not any(ts[-1] <= x < r0 for x in g.tribute_done[i]): return 'tributing'
    if any(x in g.campatk[i] or x in g.camphit[i] for x in (pr, r0)): return 'farming'
    if 'move' in g.acts[i].get(pr, []) or 'dash' in g.acts[i].get(pr, []): return 'walking'
    return 'idle'

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
        k0 = g.ridx[r0]
        pr = g.order[k0-1] if k0 > 0 else r0
        pr2 = g.order[k0-2] if k0 > 1 else pr
        s0 = g.rounds[pr]
        loc = first['vpos']
        f = dict(match=g.match, us=g.us, map=g.map, opp=g.rec['opp'], orank=g.rec['orank'], res=g.rec['res'], r0=r0, r1=r1, loc=loc, nhits=len(hs), rounds_total=g.rec['rounds'])
        a, v = first['a'], first['v']
        ateam = g.types[a][0]
        vc = s0[v]
        f['first'] = dict(a=a, at=ateam, aty=g.types[a][1], v=v, vty=g.types[v][1], kind=first['kind'], dist=first['dist'], dmg=first['dmg'],
                          vhpp=round(100*vc['hp']/vc['mhp']) if vc['alive'] else None, vact=activity(g, v, r0, pr, pr2), aact=activity(g, a, r0, pr, pr2),
                          vgems=vc['gems'], a_hpp=round(100*s0[a]['hp']/s0[a]['mhp']) if s0[a]['alive'] else None)
        involved = set(h['a'] for h in hs) | set(h['v'] for h in hs)
        side = {}
        for t in (0, 1):
            pres = [c for c in s0.values() if c['team'] == t and c['alive'] and cheb(pos(c), loc) <= 8]
            inv = [i for i in involved if g.types[i][0] == t]
            ids = sorted(set(c['i'] for c in pres) | set(inv))
            alive_ids = [i for i in ids if s0[i]['alive']]
            hp = sum(s0[i]['hp'] for i in alive_ids); mhp = sum(s0[i]['mhp'] for i in alive_ids)
            n6 = sum(1 for c in s0.values() if c['team'] == t and c['alive'] and cheb(pos(c), loc) <= 6)
            n8 = len(pres)
            dmg = sum(h['dmg'] for h in hs if g.types[h['a']][0] == t)
            dmg_spell = sum(h['dmg'] for h in hs if g.types[h['a']][0] == t and h['kind'] == 'spell')
            deaths = [(r, i, kk) for (r, i, kk) in g.deaths if g.types[i][0] == t and r0 <= r <= r1 + 1 and i in ids]
            gems_lost = 0
            for (r, i, kk) in deaths:
                pd = g.rounds[prev_round(g, r)][i]
                gems_lost += pd['gems'] if pd['alive'] else 0
            dsp = [g.dspawn[t][s0[i]['y']][s0[i]['x']] for i in alive_ids]
            dal = [g.daltar[s0[i]['y']][s0[i]['x']] for i in alive_ids]
            gems = sum(s0[i]['gems'] for i in alive_ids)
            carriers = sum(1 for i in alive_ids if s0[i]['gems'] > 0)
            busy = [i for i in ids if any(rr in g.campatk[i] or rr in g.camphit[i] for rr in (pr, r0))]
            alive_total = sum(1 for c in s0.values() if c['team'] == t and c['alive'])
            # together / split: all alive team champions within 8 of the fight?
            far = alive_total - n8
            # pairwise max distance among alive team champions
            allc = [pos(c) for c in s0.values() if c['team'] == t and c['alive']]
            maxpair = max((cheb(p, q) for p in allc for q in allc), default=0)
            # per-champion activity
            acts = {i: activity(g, i, r0, pr, pr2) for i in alive_ids}
            side[t] = dict(ids=ids, types=[g.types[i][1] for i in ids], n=len(alive_ids), n6=n6, n8=n8, hp=hp, mhp=mhp, hpp=round(100*hp/mhp) if mhp else 0,
                           dmg=dmg, dmg_spell=dmg_spell, deaths=[(r, i, g.types[i][1]) for (r, i, kk) in deaths], gems_lost=gems_lost, kills=0,
                           dspawn=min(dsp) if dsp else None, daltar=min(dal) if dal else None, gems=gems, carriers=carriers, busy=busy, alive_total=alive_total,
                           far=far, maxpair=maxpair, acts=acts)
        for t in (0, 1): side[t]['kills'] = len(side[1-t]['deaths']); side[t]['gems_won'] = side[1-t]['gems_lost']
        # ---- approach over the 4 rounds before the first hit (attacker vs victim)
        rs = [rr for rr in g.order if r0 - 4 <= rr < r0]
        if rs:
            s_a = g.rounds[rs[0]]
            if s_a[a]['alive'] and s_a[v]['alive']:
                d_start = cheb(pos(s_a[a]), pos(s_a[v]))
                a_move = cheb(pos(s_a[a]), first['apos']); v_move = cheb(pos(s_a[v]), first['vpos'])
                da = cheb(pos(s_a[a]), first['vpos']) - cheb(first['apos'], first['vpos'])
                dv = cheb(pos(s_a[v]), first['apos']) - cheb(first['vpos'], first['apos'])
                # attacker: consecutive rounds before r0 in which it moved and got closer to the victim's live position
                closing = 0
                for kk in range(k0-1, max(-1, k0-8), -1):
                    rr = g.order[kk]; rp = g.order[kk-1] if kk > 0 else rr
                    ca, cp = g.rounds[rr][a], g.rounds[rp][a]
                    cv = g.rounds[rr][v]
                    if not (ca['alive'] and cp['alive'] and cv['alive']): break
                    moved = 'move' in g.acts[a].get(rr, []) or 'dash' in g.acts[a].get(rr, [])
                    if moved and cheb(pos(ca), pos(cv)) < cheb(pos(cp), pos(cv)): closing += 1
                    else: break
                a_farm = sum(1 for rr in rs if rr in g.campatk[a] or rr in g.camphit[a])
                f['approach'] = dict(d_start=d_start, a_closed=da, v_closed=dv, a_moved=a_move, v_moved=v_move, closing=closing, a_farm=a_farm)
        # ---- vision before the hit: how many consecutive rounds before r0 was an enemy of the victim's team within 8 of the victim's team members near the fight
        vt = g.types[v][0]
        vids = side[vt]['ids']
        seen = 0; what = collections.Counter()
        for kk in range(k0-1, max(-1, k0-40), -1):
            rr = g.order[kk]; s = g.rounds[rr]
            ours = [s[i] for i in vids if s[i]['alive']]
            foes = [c for c in s.values() if c['team'] != vt and c['alive']]
            if not ours or not any(cheb(pos(o), pos(e)) <= 8 for o in ours for e in foes): break
            seen += 1
            rp = g.order[kk-1] if kk > 0 else rr
            sp = g.rounds[rp]
            for o in ours:
                i = o['i']
                if not sp[i]['alive']: continue
                if rr in g.campatk[i] or rr in g.camphit[i]: what['farm'] += 1; continue
                moved = 'move' in g.acts[i].get(rr, []) or 'dash' in g.acts[i].get(rr, [])
                if any(rr in g.recall_start[i] for _ in [0]) or any(x < rr for x in g.recall_start[i] if rr - 5 <= x): what['recall'] += 1; continue
                if not moved: what['idle'] += 1; continue
                dn = min(cheb(pos(o), pos(e)) for e in foes); dp = min(cheb(pos(sp[i]), pos(sp[e['i']])) for e in foes if sp[e['i']]['alive']) if any(sp[e['i']]['alive'] for e in foes) else dn
                if dn > dp: what['away'] += 1
                elif dn < dp: what['closer'] += 1
                else: what['side'] += 1
        f['vision'] = dict(rounds=seen, what=dict(what))
        # ---- per-round fight detail: casts, attacks by distance, focus, chasing  (for both sides)
        win = [rr for rr in g.order if r0 <= rr <= r1]
        for t in (0, 1):
            sd = side[t]
            myhits = [h for h in hs if g.types[h['a']][0] == t]
            # focus: rounds where 2+ of our champs hit champions -> same victim?
            byr = collections.defaultdict(list)
            for h in myhits: byr[h['r']].append(h)
            multi = 0; same = 0
            for rr, hh in byr.items():
                attackers = set(h['a'] for h in hh)
                if len(attackers) >= 2:
                    multi += 1
                    if len(set(h['v'] for h in hh)) == 1: same += 1
            sd['focus_multi'] = multi; sd['focus_same'] = same
            # target choice when 2+ enemies within reach (reach = 1 melee / 3 ranged basic / 4 spell; area spells counted via radius: use 5 for spell)
            tc = collections.Counter()
            for h in myhits:
                reach = (4 if h['kind'] == 'spell' else rng(g.types[h['a']][1]))
                cand = [c for c in h['ctx'] if c[1] <= reach]
                if len(cand) < 2: continue
                tc['n'] += 1
                vh = [c for c in cand if c[0] == h['v']]
                if not vh: continue
                mind = min(c[1] for c in cand); minhp = min(c[2] for c in cand)
                tc['nearest'] += vh[0][1] == mind
                tc['lowest'] += vh[0][2] == minhp
                tc['caster'] += cls(g.types[h['v']][1]) == 'caster'
                tc['caster_avail'] += any(cls(g.types[c[0]][1]) == 'caster' for c in cand)
                sv = g.rounds[prev_round(g, h['r'])][h['v']]
                tc['carrier'] += sv['gems'] > 0
                tc['carrier_avail'] += any(g.rounds[prev_round(g, h['r'])][c[0]]['gems'] > 0 for c in cand)
            sd['target'] = dict(tc)
            # attacks that are followed by the target leaving range next round (chasing need)
            out = 0; na = 0; followed = 0
            for h in myhits:
                if h['kind'] != 'atk': continue
                kk = g.ridx[h['r']]
                if kk + 1 >= len(g.order): continue
                rn = g.order[kk+1]
                ca, cv = g.rounds[rn][h['a']], g.rounds[rn][h['v']]
                if not (ca['alive'] and cv['alive']): continue
                na += 1
                if cheb(pos(ca), pos(cv)) > rng(g.types[h['a']][1]):
                    out += 1
                    # did we step toward it in that round?
                    if 'move' in g.acts[h['a']].get(rn, []) or 'dash' in g.acts[h['a']].get(rn, []): followed += 1
            sd['atk_n'] = na; sd['atk_target_left'] = out; sd['atk_followed'] = followed
            # casts in fight window by our participants; cast within 2 rounds of contact
            casts = sum(1 for i in sd['ids'] for rr in g.casts[i] if r0 <= rr <= r1)
            early = any(rr for i in sd['ids'] for rr in g.casts[i] if r0 <= rr <= r0 + 2)
            # opportunity: champion-rounds in the window with an enemy within 4 and no cast in the previous 8 rounds (both slots surely up) -> did it cast?
            opp_n = 0; opp_cast = 0; opp_moved = 0
            for i in sd['ids']:
                for rr in win:
                    c = g.rounds[rr][i]
                    if not c['alive']: continue
                    sp = g.rounds[prev_round(g, rr)]
                    if not sp[i]['alive']: continue
                    foes = [e for e in sp.values() if e['team'] != t and e['alive'] and cheb(pos(e), pos(sp[i])) <= 4]
                    if not foes: continue
                    if any(rr - 8 <= x < rr for x in g.casts[i]): continue
                    opp_n += 1
                    if rr in g.casts[i]: opp_cast += 1
                    elif 'move' in g.acts[i].get(rr, []): opp_moved += 1
            sd['casts'] = casts; sd['cast_early'] = early; sd['opp_n'] = opp_n; sd['opp_cast'] = opp_cast; sd['opp_moved'] = opp_moved
            # ranged champions: distance of basic attacks and spells on champions
            rd = collections.Counter()
            for h in myhits:
                if cls(g.types[h['a']][1]) == 'melee': continue
                rd[(h['kind'], min(h['dist'], 6))] += 1
            sd['ranged_dist'] = {'%s%d' % k: v for k, v in rd.items()}
            # steps spent walking adjacent (dist<=2 to an enemy) by ranged champions during the fight
            adj = 0; rr_n = 0
            for i in sd['ids']:
                if cls(g.types[i][1]) == 'melee': continue
                for rr in win:
                    c = g.rounds[rr][i]
                    if not c['alive']: continue
                    foes = [e for e in g.rounds[rr].values() if e['team'] != t and e['alive']]
                    if not foes: continue
                    d = min(cheb(pos(e), pos(c)) for e in foes)
                    if d <= 8: rr_n += 1; adj += d <= 2
            sd['ranged_rounds'] = rr_n; sd['ranged_adj'] = adj
        # ---- end of fight: separation and how it ended
        k1 = g.ridx[r1]
        sep = None
        for kk in range(k1, min(len(g.order), k1 + 40)):
            rr = g.order[kk]; s = g.rounds[rr]
            A = [s[i] for i in side[0]['ids'] if s[i]['alive']]; B = [s[i] for i in side[1]['ids'] if s[i]['alive']]
            if not A or not B or not any(cheb(pos(p), pos(q)) <= 8 for p in A for q in B): sep = rr; break
        f['sep'] = sep
        f['length'] = r1 - r0 + 1
        f['length_contact'] = (sep - r0) if sep is not None else None
        # last event classification: death at r1 or r1+1?
        lastdeath = any(r1 - 1 <= r <= r1 + 1 for t in (0, 1) for (r, i, ty) in side[t]['deaths'])
        # who stepped away first after the last hit: first side whose alive participant increases its min distance to the other side by moving
        leaver = None; leave_r = None; leave_kind = None
        after = [rr for rr in g.order if r1 <= rr <= (sep if sep is not None else r1 + 40)]
        for idx in range(1, len(after)):
            rr = after[idx]; rp = after[idx-1]
            s, sp = g.rounds[rr], g.rounds[rp]
            found = {}
            for t in (0, 1):
                for i in side[t]['ids']:
                    c, cp = s[i], sp[i]
                    if not (c['alive'] and cp['alive']): continue
                    foes_p = [sp[j] for j in side[1-t]['ids'] if sp[j]['alive']]
                    if not foes_p: continue
                    d0 = min(cheb(pos(cp), pos(e)) for e in foes_p); d1 = min(cheb(pos(c), pos(e)) for e in foes_p)
                    moved = 'move' in g.acts[i].get(rr, []) or 'dash' in g.acts[i].get(rr, [])
                    if moved and d1 > d0 and t not in found:
                        found[t] = 'recall' if any(rr - 1 <= x <= rr + 6 for x in g.recall_start[i]) else 'walk'
            if found:
                leave_r = rr
                if len(found) == 2: leaver = 'both'; leave_kind = found[0] + '/' + found[1]
                else: leaver = list(found)[0]; leave_kind = found[leaver]
                break
        # recall of any participant between r1-1 and sep
        rec_side = [t for t in (0, 1) if any(r1 - 1 <= x <= (sep if sep is not None else r1 + 10) for i in side[t]['ids'] for x in g.recall_start[i])]
        # both sides dead/one side all dead?
        wipe = [t for t in (0, 1) if side[t]['n'] and len(side[t]['deaths']) >= side[t]['n']]
        if wipe: end = 'wipe'
        elif lastdeath: end = 'kill'
        elif leaver is not None and leave_kind == 'recall': end = 'recall'
        elif leaver is not None: end = 'leave'
        else: end = 'other'
        f['end'] = dict(kind=end, leaver=leaver, leave_r=leave_r, leave_kind=leave_kind, recall_sides=rec_side, wipe=wipe)
        # chase: after the first step away by side t (leaver), how many follow-steps by the other side's hitters toward that champion in the next 12 rounds
        f['sides'] = {str(t): side[t] for t in (0, 1)}
        fights.append(f)
    fights.sort(key=lambda f: f['r0'])
    return fights

if __name__ == '__main__':
    out = []
    for rec in selected():
        try:
            g = load_game(rec)
        except FileNotFoundError:
            print('missing', rec['match'][:8], file=sys.stderr); continue
        fs = build(g)
        out.extend(fs)
        print(rec['map'], rec['match'][:8], 'fights', len(fs), file=sys.stderr)
    json.dump(out, open(S + '/ws2/scripts_fights/fights.json', 'w'))
    print(len(out), 'fights')
