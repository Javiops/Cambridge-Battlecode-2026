"""Extract hit-reaction, retreat, recall, help and death rows for all 150 games (both teams)."""
import sys, json, collections
sys.path.insert(0, '/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/ws2/scripts_reactions')
from common import *

def band(h): return '>70' if h > 70 else ('40-70' if h >= 40 else '<40')

def process(rec):
    G = Game(rec); side = G.side
    base = dict(match=rec['match'], map=rec['map'], opp=rec['opp'], orank=rec['orank'], tier=tier(rec['orank']), res=rec['res'], nch=len(rec['draft']))
    hits, retreats, recalls, helps, deaths = [], [], [], [], []
    order = G.order; last = order[-1]
    for i in G.types:
        t = G.team(i); us = (t == side); ty = G.ty(i)
        # ---- hit episodes (champion damage) ----
        hitrounds = [r for r in order if G.champ_dmg(r, i)]
        episodes = []
        for r in hitrounds:
            if episodes and r - episodes[-1][-1] <= 5: episodes[-1].append(r)
            else: episodes.append([r])
        ep_of = {}
        for en, ep in enumerate(episodes):
            for r in ep: ep_of[r] = en
        for en, ep in enumerate(episodes):
            r0 = ep[0]; pr = r0 - 1
            if pr not in G.rounds: continue
            hp0 = G.hpp(pr, i)
            dfoe0, fidx = G.nearest_foe(pr, i)
            died_r = next((d for d in G.death_round[i] if r0 <= d <= ep[-1] + 6), None)
            # first retreat step in the episode window: 'away' class and distance to nearest foe grows by >=2 over the next 3 rounds
            ret_r = None
            for r in range(r0, ep[-1] + 4):
                if r not in G.rounds or not G.alive(r, i): break
                c = G.classify(r, i)
                if c in ('away', 'fight+away'):
                    d_now = G.nearest_foe(r, i)[0]; d_prev = G.nearest_foe(r - 1, i)[0]
                    r3 = min(r + 3, last)
                    d3 = G.nearest_foe(r3, i)[0] if G.alive(r3, i) else 99
                    if d3 - d_prev >= 2 or c == 'away' and d3 - d_prev >= 1:
                        ret_r = r; break
            allies8 = [a for a in G.allies(pr, i) if cheb(G.pos(pr, i), (a['x'], a['y'])) <= 8]
            # group retreat? allies within 6 at retreat start move away from the same foe over ret..ret+2
            grp = None
            if ret_r is not None and ret_r - 1 in G.rounds:
                al6 = [a for a in G.allies(ret_r - 1, i) if cheb(G.pos(ret_r - 1, i), (a['x'], a['y'])) <= 6]
                if not al6: grp = 'no_ally_within_6'
                else:
                    nf = G.nearest_foe(ret_r - 1, i)[1]
                    also = 0; stay = 0
                    for a in al6:
                        r2 = min(ret_r + 2, last)
                        if nf is not None and G.alive(r2, a['i']) and G.alive(r2, nf):
                            d_a0 = cheb((a['x'], a['y']), G.pos(ret_r - 1, nf)); d_a1 = cheb(G.pos(r2, a['i']), G.pos(r2, nf))
                            if d_a1 - d_a0 >= 2: also += 1
                            else: stay += 1
                        else: stay += 1
                    grp = 'allies_also_retreat' if also == len(al6) else ('some_allies_retreat' if also else 'allies_stay')
            hits.append(dict(base, us=us, ty=ty, cls=cls(ty), i=i, r=r0, n=len(ep), hp0=round(hp0), band=band(hp0), dfoe0=dfoe0, allies8=len(allies8),
                             ret_delay=(ret_r - r0) if ret_r is not None else None, grp=grp, died=died_r is not None,
                             seq=[G.classify(r, i) for r in range(r0, r0 + 4)], nfoe_hitting=len(set(s for r in ep for (s, v, k) in G.champ_dmg(r, i)))))
            # per hit round classification (every hit round, not only first)
            for r in ep:
                h = G.hpp(r - 1, i) if r - 1 in G.rounds else hp0
                hits[-1].setdefault('rows', []).append(dict(r=r, band=band(h), seq=[G.classify(rr, i) for rr in range(r, r + 4)]))
            # ---- retreat quality ----
            if ret_r is not None and fidx is not None:
                nf_d, nf = G.nearest_foe(ret_r - 1, i)
                p0 = G.pos(ret_r - 1, i)
                follow = 0; chase_len = 0
                for k in range(0, 12):
                    r = ret_r + k
                    if r + 1 not in G.rounds or not G.alive(r, i) or nf is None or not G.alive(r, nf): break
                    # the foe moved and its distance to the champion's current position decreased vs standing still
                    f0 = G.pos(r, nf); f1 = G.pos(r + 1, nf); p = G.pos(r + 1, i) if G.alive(r + 1, i) else G.pos(r, i)
                    if f1 != f0 and cheb(f1, p) < cheb(f0, p):
                        follow += 1; chase_len = k + 1
                r5 = min(ret_r + 5, last)
                alive5 = G.alive(r5, i)
                d5 = G.nearest_foe(r5, i)[0] if alive5 else None
                p5 = G.pos(r5, i) if alive5 else None
                ds0 = G.dspawn(i, p0); ds5 = G.dspawn(i, p5) if alive5 else None
                da0 = G.nearest_ally_d(ret_r - 1, i); da5 = G.nearest_ally_d(r5, i) if alive5 else None
                # outcome within 15 rounds
                out = None; out_r = None
                for r in range(ret_r, ret_r + 16):
                    if r > last: break
                    if not G.alive(r, i): out = 'death'; out_r = r; break
                    if r in G.recall_arrive[i]: out = 'recall'; out_r = r; break
                if out is None:
                    rr = min(ret_r + 15, last)
                    hit_late = any(G.champ_dmg(r, i) for r in range(ret_r + 8, rr + 1))
                    d15 = G.nearest_foe(rr, i)[0]
                    out = 'escape' if (d15 >= 8 and not hit_late) else ('still_fighting' if hit_late else 'escape_near')
                    out_r = rr
                recall_after = next((s for s in G.recall_start[i] if ret_r <= s <= ret_r + 15), None)
                retreats.append(dict(base, us=us, ty=ty, cls=cls(ty), i=i, r=ret_r, ep_r=r0, hp=round(G.hpp(ret_r - 1, i)), band=band(G.hpp(ret_r - 1, i)), dfoe=nf_d, foe_ty=G.ty(nf), foe_cls=cls(G.ty(nf)),
                                     follow=follow, chase_len=chase_len, d5=d5, dd5=(d5 - nf_d) if d5 is not None else None, ds0=ds0, dds5=(ds5 - ds0) if ds5 is not None else None,
                                     da0=da0, dda5=(da5 - da0) if (da5 is not None and da0 < 99 and da5 < 99) else None, out=out, out_delay=out_r - ret_r, recall_delay=(recall_after - ret_r) if recall_after is not None else None,
                                     allies8=len(allies8), nfoe8=sum(1 for f in G.foes(ret_r - 1, i) if cheb(p0, (f['x'], f['y'])) <= 8), zone=G.zone(i, p0)))
            # ---- help ----
            for a in allies8:
                ai = a['i']; d0 = cheb(G.pos(pr, i), (a['x'], a['y']))
                came_r = None; fought_r = None; farmed = 0; moved_away = 0
                for k in range(0, 6):
                    r = r0 + k
                    if r > last or not G.alive(r, ai) or not G.alive(r, i): break
                    d = cheb(G.pos(r, i), G.pos(r, ai))
                    if came_r is None and d <= d0 - 2: came_r = r
                    if fought_r is None and G.act[r][ai] & {'atk', 'spell'}: fought_r = r
                    if G.act[r][ai] & {'atkcamp', 'spellcamp'}: farmed += 1
                    if G.classify(r, ai) == 'away': moved_away += 1
                if fought_r is not None: res = 'fought'
                elif came_r is not None: res = 'came'
                elif farmed >= 2: res = 'kept_farming'
                elif moved_away >= 2: res = 'moved_away'
                else: res = 'other'
                helps.append(dict(base, us=us, ty=ty, ally_ty=G.ty(ai), ally_cls=cls(G.ty(ai)), i=i, r=r0, d0=d0, res=res, t_help=min([x for x in (came_r, fought_r) if x is not None], default=None),
                                  ally_hp=round(G.hpp(pr, ai)), victim_hp=round(hp0), ally_was_farming=bool(G.act[pr][ai] & {'atkcamp', 'spellcamp'}), ally_recalling=G.recall_active(pr, ai) is not None,
                                  victim_died=died_r is not None))
        # ---- recalls ----
        starts = G.recall_start[i]; rows_rc = []
        for s in starts:
            pr = s - 1
            if pr not in G.rounds: continue
            p = G.pos(pr, i); c = G.rounds[pr][i]
            dfoe, nf = G.nearest_foe(pr, i)
            out = 'game_end'; end = None; src = None
            for r in range(s, s + 6):
                if r > last: break
                if r in G.recall_arrive[i] and r > s: out = 'arrived'; end = r; break
                dm = G.dmg[r][i]
                if r in G.death_round[i]: out = 'died'; end = r; break
                if dm:
                    src = dm[0][0]; out = 'hit_camp' if src == 'camp' else 'hit_foe'; end = r
                    if src != 'camp': src = G.ty(src)
                    break
                if r > s and r in G.recall_start[i]: out = 'restart'; end = r; break
                if r > s and G.act[r][i] & {'move', 'dash'}: out = 'moved'; end = r; break
                if r > s and G.act[r][i] & {'atk', 'spell', 'atkcamp'}: out = 'attacked'; end = r; break
            hit_recent = any(G.champ_dmg(r, i) for r in range(max(1, s - 3), s))
            rows_rc.append(dict(base, us=us, ty=ty, cls=cls(ty), i=i, r=s, hp=round(G.hpp(pr, i)), band=band(G.hpp(pr, i)), gems=c['gems'], gold=c['gold'], dfoe=dfoe, nfoe8=sum(1 for f in G.foes(pr, i) if cheb(p, (f['x'], f['y'])) <= 8),
                                dspawn=G.dspawn(i, p), hit_recent=hit_recent, out=out, dur=(end - s) if end is not None else None, src=src, zone=G.zone(i, p)))
        # chains: a start whose previous start (same champion) ended in 'restart' continues that attempt (spam while channelling)
        cid = -1
        for k, x in enumerate(rows_rc):
            if k > 0 and rows_rc[k - 1]['out'] == 'restart': x['chain'] = cid
            else: cid += 1; x['chain'] = cid
        by_chain = collections.defaultdict(list)
        for x in rows_rc: by_chain[x['chain']].append(x)
        attempts = []
        for ch, xs in sorted(by_chain.items()):
            a = dict(xs[0]); a['out'] = xs[-1]['out']; a['src'] = xs[-1]['src']; a['chain_len'] = len(xs); a['end'] = xs[-1]['r'] + (xs[-1]['dur'] or 0)
            attempts.append(a)
        for k, a in enumerate(attempts):
            prev = attempts[k - 1] if k > 0 else None
            a['retry'] = bool(prev) and prev['out'] in ('hit_foe', 'hit_camp', 'moved', 'attacked') and a['r'] - prev['end'] <= 10
            a['retry_gap'] = (a['r'] - prev['end']) if a['retry'] else None
            # what happened in the 10 rounds after an interruption
            if a['out'] in ('hit_foe', 'hit_camp', 'moved', 'attacked'):
                e = a['end']; nxt = 'none'
                for r in range(e, e + 11):
                    if r > last: break
                    if r in G.death_round[i]: nxt = 'died'; break
                    if r > e and r in G.recall_start[i]: nxt = 'retry'; break
                    if G.act[r][i] & {'atk', 'spell'}: nxt = 'fought'; break
                    if G.act[r][i] & {'move', 'dash'} and nxt == 'none': nxt = 'walked'
                a['after'] = nxt
            else: a['after'] = None
            del a['chain']
        recalls += attempts
        # ---- deaths ----
        for d in G.death_round[i]:
            pr = d - 1
            if pr not in G.rounds: continue
            p = G.pos(pr, i); c = G.rounds[pr][i]
            # final episode: champion hits leading to death (gap <= 5), else camp hits
            ep = next((e for e in episodes if e[0] <= d <= e[-1] + 1), None)
            if ep is None:
                # camp-only death: find camp damage rounds
                cr = [r for r in range(max(1, d - 30), d + 1) if G.dmg[r][i]]
                ep = [cr[0]] if cr else [d]
            r0 = ep[0]
            hp_first = round(G.hpp(r0 - 1, i)) if r0 - 1 in G.rounds else 100
            # activity in 5 rounds before first hit
            acts = collections.Counter()
            for r in range(max(1, r0 - 5), r0):
                if r in G.rounds and G.alive(r, i): acts[G.classify(r, i)] += 1
            def summarize(cnt):
                if not cnt: return 'unknown'
                m = {'camp': 'farming', 'tribute': 'tributing', 'recall': 'recalling', 'away': 'fleeing', 'closer': 'approaching', 'lateral': 'walking', 'nothing': 'idle', 'arrived': 'walking'}
                sc = collections.Counter()
                for k, v in cnt.items():
                    if k.startswith('fight'): sc['fighting'] += v
                    else: sc[m.get(k, k)] += v
                return sc.most_common(1)[0][0]
            before = summarize(acts)
            acts5 = collections.Counter()
            for r in range(max(1, d - 5), d):
                if r in G.rounds and G.alive(r, i): acts5[G.classify(r, i)] += 1
            last5 = summarize(acts5)
            dmg_src = collections.Counter(); dmg_kind = collections.Counter(); foes_dealing = set()
            for r in range(r0, d + 1):
                for (s, v, k) in G.dmg[r][i]:
                    dmg_kind[k] += v
                    if s != 'camp': foes_dealing.add(s); dmg_src[G.ty(s)] += v
                    else: dmg_src['camp'] += v
            tot = sum(dmg_kind.values()) or 1
            killer = G.kill.get((d, i)); killer_ty = 'camp' if killer == 'camp' else (G.ty(killer) if isinstance(killer, int) else str(killer))
            pair = (d, i) in G.pair_death
            allies6 = sum(1 for a in G.allies(pr, i) if cheb(p, (a['x'], a['y'])) <= 6)
            allies_alive = len(G.allies(pr, i))
            rec_active = G.recall_active(pr, i) is not None or (G.recall_active(d, i) is not None) or any(s <= d <= s + 4 for s in G.recall_start[i])
            rec_tries = sum(1 for s in G.recall_start[i] if r0 - 2 <= s <= d)
            fled = sum(1 for r in range(r0, d + 1) if r in G.rounds and G.alive(r, i) and G.classify(r, i) == 'away')
            fought = sum(1 for r in range(r0, d + 1) if r in G.rounds and G.alive(r, i) and G.classify(r, i).startswith('fight'))
            dfoe0 = G.nearest_foe(r0 - 1, i)[0] if r0 - 1 in G.rounds else 99
            nfoe8_0 = sum(1 for f in G.foes(r0 - 1, i) if cheb(G.pos(r0 - 1, i), (f['x'], f['y'])) <= 8) if r0 - 1 in G.rounds else 0
            allies8_0 = sum(1 for a in G.allies(r0 - 1, i) if cheb(G.pos(r0 - 1, i), (a['x'], a['y'])) <= 8) if r0 - 1 in G.rounds else 0
            deaths.append(dict(base, us=us, ty=ty, cls=cls(ty), i=i, r=d, pair=pair, kkind=G.killkind.get((d, i), 'other'), r0=r0, ep_len=d - r0 + 1, zone=G.zone(i, p), dspawn=G.dspawn(i, p), daltar=G.daltar(p), despawn=G.despawn(i, p),
                               before=before, last5=last5, hp_first=hp_first, nfoes=len(foes_dealing), spell_share=round(100 * dmg_kind['spell'] / tot), camp_share=round(100 * dmg_kind['camp'] / tot),
                               allies6=allies6, allies_alive=allies_alive, gems=c['gems'], recall_active=rec_active, recall_tries=rec_tries, killer=killer_ty, fled=fled, fought=fought,
                               dfoe0=dfoe0, nfoe8_0=nfoe8_0, allies8_0=allies8_0, dmg_src=dict(dmg_src), hp_traj=[round(G.hpp(r, i)) for r in range(max(0, d - 8), d) if r in G.rounds]))
    return hits, retreats, recalls, helps, deaths

if __name__ == '__main__':
    sel = load_sel()
    out = dict(hits=[], retreats=[], recalls=[], helps=[], deaths=[])
    for n, rec in enumerate(sel):
        if not os.path.exists(W + '/steps/%s.c.jsonl' % rec['match']): print('missing', rec['match']); continue
        h, rt, rc, hl, dt = process(rec)
        out['hits'] += h; out['retreats'] += rt; out['recalls'] += rc; out['helps'] += hl; out['deaths'] += dt
        if n % 20 == 0: print(n, len(out['hits']), len(out['deaths']), flush=True)
    json.dump(out, open(W + '/scripts_reactions/rows.json', 'w'))
    print({k: len(v) for k, v in out.items()})
