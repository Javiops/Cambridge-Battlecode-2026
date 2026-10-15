import sys, json, collections
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_opening')
from openlib import *

def summarize(g, team, upto=60):
    M = g.map; an = g.analyse(team, upto); mine = an['mine']; enemy = an['enemy']
    sd = M.dist[team]
    rec = dict(match=g.match, map=M.name, team=g.teams[team], side='ab'[team], opp=g.teams.get(1-team, BYMATCH[g.match][0]['opp']),
               draft=[g.types[i][1] for i in mine])
    # first camp per champion
    fc = {}
    for i in mine:
        hr = sorted(an['act'][i].items())
        first = None
        for r, A in hr:
            cs = [a for a in A if a.startswith('C')]
            if cs: first = (r, int(cs[0][1:])); break
        fc[i] = first
    rec['first_camp_per_champ'] = {g.name(i): fc[i] for i in mine}
    groups_first = [fc[i][1] for i in mine if fc[i]]
    rec['n_distinct_first_groups'] = len(set(groups_first))
    # first camp overall
    if an['camp_first_hit']:
        g0, (r0, i0, p0) = min(an['camp_first_hit'].items(), key=lambda kv: kv[1][0])
        info = g.ginfo[g0]
        hitters = [i for i in mine if fc[i] and fc[i][1] == g0]
        allh = an['camp_hitters'][g0]
        dead = an['camp_death'].get(g0)
        caps = [k for k in an['keys'] if k[1] == 'capture' and k[2]['i'] in mine and k[0] >= (dead or 0) and k[0] <= (dead or 0) + 8]
        # restrict captures to this group's tiles: capture pos within 3 of group tiles (pos is end-of-round)
        caps_g = [k for k in caps if k[2]['pos'] and min(cheb(k[2]['pos'], t) for t in info['tiles']) <= 3]
        # occupancy of the capture tiles between kill and capture; who left and where to
        occ = {}; movers = {}
        if dead:
            capr = caps_g[0][0] if caps_g else dead + 6
            for r in range(dead, capr + 1):
                if r not in g.rounds: break
                occ[r] = [g.name(i) for i in mine if (g.rounds[r]['champs'][i]['x'], g.rounds[r]['champs'][i]['y']) in info['tiles']]
            on_any = set(x for v in occ.values() for x in v)
            for i in allh:
                if g.name(i) not in on_any or g.name(i) not in (occ.get(capr) or []):
                    # next camp hit by this champion after dead
                    nxt = [(r, gg) for r, gg in sorted(an['act'][i].items() and [(r, int(sorted(a for a in A if a.startswith('C'))[0][1:])) for r, A in sorted(an['act'][i].items()) if any(a.startswith('C') for a in A) and r > dead]) if r > dead]
                    movers[g.name(i)] = nxt[0] if nxt else None
        # positions of hitters while hitting: bush? side?
        bush = 0; tot = 0; dirs = collections.Counter(); dist_sp = []; ranges = collections.Counter()
        sp = M.spawn[team]; spc = (sum(p[0] for p in sp)/len(sp), sum(p[1] for p in sp)/len(sp))
        for (r, i, p) in an['camp_hit_positions'][g0]:
            tot += 1
            if M.tile(*p) == '"': bush += 1
            ct = min(info['tiles'], key=lambda t: cheb(t, p))
            v1 = (p[0]-ct[0], p[1]-ct[1]); v2 = (spc[0]-ct[0], spc[1]-ct[1])
            n1 = (v1[0]**2+v1[1]**2)**.5 or 1; n2 = (v2[0]**2+v2[1]**2)**.5 or 1
            cos = (v1[0]*v2[0]+v1[1]*v2[1])/(n1*n2)
            dirs['spawn_side' if cos > 0.3 else ('far_side' if cos < -0.3 else 'flank')] += 1
            ranges[cheb(p, ct)] += 1
            dist_sp.append(sd[p[1]][p[0]])
        rec['first_camp'] = dict(group=g0, types=info['types'], side=M.side_of(team, info['side']), dist=info['dA' if team == 0 else 'dB'],
                                 first_hit=r0, first_hitter=g.name(i0), n_first_choosers=len(hitters), n_hitters=len(allh), hitters=[g.name(i) for i in sorted(allh)],
                                 killed=dead, rounds_to_kill=(dead - r0 + 1) if dead else None,
                                 captured=(caps_g[0][0] if caps_g else None), capturers=[g.name(k[2]['i']) for k in caps_g], cap_gems=[k[2]['gems'] for k in caps_g],
                                 bush_frac=round(bush/tot, 2) if tot else None, side_counts=dict(dirs), range_counts=dict(sorted(ranges.items())),
                                 occupancy=occ, movers=movers)
    else:
        rec['first_camp'] = None
    # all camps hit in opening with first hit round/kill
    camps = []
    for gg, (r, i, p) in sorted(an['camp_first_hit'].items(), key=lambda kv: kv[1][0]):
        if r > upto: continue
        info = g.ginfo[gg]
        camps.append(dict(g=gg, ty='+'.join(t[:4] for t in info['types']), side=M.side_of(team, info['side']), d=info['dA' if team == 0 else 'dB'],
                          hit=r, dead=an['camp_death'].get(gg), n=len(an['camp_hitters'][gg]), who=[g.name(x) for x in sorted(an['camp_hitters'][gg])]))
    rec['camps'] = camps
    # captures
    rec['captures'] = [(k[0], g.name(k[2]['i']), k[2]['gems']) for k in an['keys'] if k[1] == 'capture' and k[0] <= upto]
    # tributes
    ts = [k for k in an['keys'] if k[1] == 'tribute_start' and k[0] <= upto + 10]
    rec['tributes'] = [(k[0], g.name(k[2]['i']), k[2]['bag'], k[2]['altar_side'], k[2]['altar']) for k in ts]
    rec['first_tribute'] = rec['tributes'][0] if rec['tributes'] else None
    # recalls
    rec['recalls'] = [(k[0], g.name(k[2]['i']), k[2]['gems'], k[2]['pos'], 'on_cap_tile' if any(k[2]['pos'] in t for t in g.gtiles.values()) else '') for k in an['keys'] if k[1] == 'recall_start' and k[0] <= upto]
    # buys
    rec['buys_r1'] = [(k[0], g.name(k[2]['i']), k[2]['gold']) for k in an['keys'] if k[1] == 'buy' and k[0] <= 2]
    rec['buys'] = [(k[0], g.name(k[2]['i']), k[2]['gold']) for k in an['keys'] if k[1] == 'buy' and k[0] <= upto]
    # enemy contact
    con = [k for k in an['keys'] if k[1] in ('hit_enemy', 'hit_by_enemy')]
    if con:
        r0 = con[0][0]
        # fight window: contiguous hits with gaps <= 5
        rend = r0
        for k in con:
            if k[0] - rend <= 5: rend = k[0]
            else: break
        my_d = [k for k in an['keys'] if k[1] == 'death' and r0 <= k[0] <= rend + 2]
        # enemy deaths from snapshots
        en_d = []
        prev = None
        for r in g.order:
            if r > rend + 2: break
            if prev is not None and r >= r0:
                for j in enemy:
                    if g.rounds[prev]['champs'][j]['alive'] and not g.rounds[r]['champs'][j]['alive']: en_d.append((r, g.name(j)))
            prev = r
        first_pos = con[0][2].get('pos') or g.pos(con[0][2]['i'], con[0][0])
        rec['first_contact'] = dict(r=r0, end=rend, who=g.name(con[0][2]['i']), kind=con[0][1], pos=first_pos, dcentre=M.near(M.dcentre, first_pos),
                                    my_deaths=[(k[0], g.name(k[2]['i'])) for k in my_d], enemy_deaths=en_d,
                                    my_gems_at_contact=sum(g.rounds[r0]['champs'][i]['gems'] for i in mine))
    else: rec['first_contact'] = None
    # centre arrival: first round any champ within BFS 4 of centre
    ca = None
    for r in g.order:
        if r > upto + 40: break
        for i in mine:
            c = g.rounds[r]['champs'][i]
            if c['alive'] and M.dcentre[c['y']][c['x']] <= 4: ca = (r, g.name(i)); break
        if ca: break
    rec['centre_arrival'] = ca
    # first enemy sighting (enemy within cheb 8 of my champ) - vision approx
    es = None
    for r in g.order:
        if r > upto: break
        for i in mine:
            c = g.rounds[r]['champs'][i]
            if not c['alive']: continue
            for j in enemy:
                e = g.rounds[r]['champs'][j]
                if e['alive'] and cheb((c['x'], c['y']), (e['x'], e['y'])) <= 8: es = (r, g.name(i), g.name(j)); break
            if es: break
        if es: break
    rec['first_enemy_in_8'] = es
    # deaths up to 60
    rec['deaths60'] = [(k[0], g.name(k[2]['i'])) for k in an['keys'] if k[1] == 'death' and k[0] <= upto]
    rec['gems_r60'] = dict(carried=sum(g.rounds[min(upto, g.order[-1])]['champs'][i]['gems'] for i in mine), sub=g.rounds[min(upto, g.order[-1])]['sub'][team])
    # togetherness: max pairwise distance of alive champs at r5, r10, r20
    tog = {}
    for r in (3, 5, 10, 15, 20, 30):
        if r in g.rounds:
            ps = [(g.rounds[r]['champs'][i]['x'], g.rounds[r]['champs'][i]['y']) for i in mine if g.rounds[r]['champs'][i]['alive']]
            tog[r] = max(cheb(a, b) for a in ps for b in ps)
    rec['spread'] = tog
    return rec

if __name__ == '__main__':
    out = []
    for rec in SEL:
        g = Game(rec['match']); team = 0 if rec['side'] == 'a' else 1
        out.append(summarize(g, team))
    json.dump(out, open(S + '/reports/scripts_opening/summaries.json', 'w'), indent=0, default=str)
    print(len(out))
