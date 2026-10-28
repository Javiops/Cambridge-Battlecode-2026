r"""state14.py DECDIR [DECDIR...] [--index index.json] [--r0 30] [--r1 150] [--pertype]
Where do the champion-rounds go (window r30-150, default), rival vs us, from shop13dec.py files.
Each champion-round is put in exactly one bucket (first match wins):
  dead        : not alive
  hit         : at least one damaging step on a camp this round
  fight       : dealt or took champion damage this round (no camp hit)
  flee        : moved, and dealt/took champion damage in the previous 4 rounds (combat move)
  reward      : not moving, within 2 of a camp of a group in reward_available state (carrying / pickup wait)
  recall      : stood still in the <=6 rounds before a teleport (recall channel) or any round within 3 of the team spawn
  still       : same tile as the previous round, none of the above
  walk_camp   : moved and got closer (Chebyshev, nearest tile) to the group of the next camp this champion hits (within 40 rounds)
  walk_home   : moved, no next hit within 40 rounds (or not closer to it), got closer to the team spawn
  walk_other  : moved, none of the above
Also: travel between consecutive group engagements of one champion (rounds from last hit on A to first hit on B, tiles between
the groups), and target choice at the first hit of an engagement: hp / gold of the group taken vs the nearest alive group then.
The side of the bot comes from the index (side a = team 0); without --index the local suffix _a/_b gives it.
"""
import sys, os, json, gzip, collections, statistics as st
TYPES = ['Ryth', 'Vesper', 'Vendetta', 'Cassi', 'Issac', 'Stellar', 'Prism', 'Marcella', 'Willow', 'Ren', 'Varg', 'Tavi', 'HoR']
BUCKETS = ['hit', 'fight', 'flee', 'reward', 'recall', 'still', 'walk_camp', 'walk_home', 'walk_other', 'dead']
args = sys.argv[1:]; dirs = []; index = None; R0, R1 = 30, 150; PERTYPE = False
i = 0
while i < len(args):
    if args[i] == '--index': index = args[i + 1]; i += 2
    elif args[i] == '--r0': R0 = int(args[i + 1]); i += 2
    elif args[i] == '--r1': R1 = int(args[i + 1]); i += 2
    elif args[i] == '--pertype': PERTYPE = True; i += 1
    else: dirs.append(args[i]); i += 1
side = {}
if index:
    for x in json.load(open(index)): side[x['file']] = 0 if x['side'] == 'a' else 1
def cheb(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
B = collections.defaultdict(collections.Counter)        # role -> bucket -> champion-rounds
BT = collections.defaultdict(collections.Counter)       # (role, type) -> bucket
TRAV = collections.defaultdict(list)                    # role -> (rounds, tiles) between engagements
CHOICE = collections.defaultdict(list)                  # role -> (hp_taken, gold_taken, dist_taken, hp_nearest, gold_nearest, dist_nearest, same)
ENG = collections.defaultdict(list)                     # role -> engagement lengths (rounds first hit -> last hit) and hits
STILLRUN = collections.defaultdict(list)                # role -> lengths of still runs
DEATH = collections.defaultdict(list)                   # role -> (round, dead_len, champ_dmg_share, was_hitting, foes_dmg_n, hp_at_r-10, state_before)
ngames = collections.Counter()
for d in dirs:
    bot = os.path.basename(d.rstrip('/'))
    for fn in sorted(os.listdir(d)):
        key = f"{bot}/{fn.replace('.json.gz', '.repl26a')}"
        if index and key not in side: continue
        us = side[key] if index else (1 if fn.endswith('_b.json.gz') else 0)
        D = json.load(gzip.open(os.path.join(d, fn)))
        R = D['rounds']
        if not R: continue
        ngames[bot] += 1
        role = lambda team: 'us' if team == us else 'rival'
        camp = {k[0]: k for k in D['camps']}
        gtiles = collections.defaultdict(list); ghp = collections.Counter(); ggold = {}
        for k in D['camps']: gtiles[k[2]].append((k[3], k[4])); ghp[k[2]] += k[7]; ggold[k[2]] = k[6]
        def gdist(p, g): return min(cheb(p, t) for t in gtiles[g])
        # champion traces
        tr = collections.defaultdict(dict)   # idx -> r -> row
        for rr in R:
            for c in rr['c']: tr[c[0]][rr['r']] = c
        team_of = {c[0]: c[1] for c in R[0]['c']}
        spawn = {}
        for c in R[0]['c']: spawn.setdefault(c[1], (c[3], c[4]))
        byr = {rr['r']: rr for rr in R}
        # hits per champion per round -> group
        hits = collections.defaultdict(dict)   # idx -> r -> set(groups)
        for r, a, k, dmg, kind in D['ck']:
            if k in camp: hits[a].setdefault(r, set()).add(camp[k][2])
        cc = collections.defaultdict(set)      # idx -> rounds with champion damage dealt or taken
        for r, a, t, dmg in D['cc']: cc[a].add(r); cc[t].add(r)
        for idx, rows in tr.items():
            team = team_of[idx]; ro = role(team); typ = TYPES[tr[idx][R[0]['r']][2]]
            sp = spawn[team]
            hr = sorted(hits[idx])
            # teleports: rounds where the position jumps > 3 (alive both)
            tele = set()
            rs = sorted(rows)
            for r in rs:
                if r - 1 in rows and rows[r][9] and rows[r - 1][9] and cheb(rows[r][3:5], rows[r - 1][3:5]) > 3: tele.add(r)
            recall_rounds = set()
            for r in tele:
                for q in range(r - 1, r - 7, -1):
                    if q in rows and q - 1 in rows and rows[q][9] and rows[q][3:5] == rows[q - 1][3:5]: recall_rounds.add(q)
                    else: break
            # engagements: consecutive hits on the same group with gaps <= 8 rounds
            engs = []
            for r in hr:
                for g in hits[idx][r]:
                    if engs and engs[-1][0] == g and r - engs[-1][2] <= 8: engs[-1][2] = r; engs[-1][3] += 1
                    else: engs.append([g, r, r, 1])
            for e0, e1 in zip(engs, engs[1:]):
                if R0 <= e1[1] <= R1 and e0[0] != e1[0]:
                    tiles = min(cheb(a, b) for a in gtiles[e0[0]] for b in gtiles[e1[0]])
                    TRAV[ro].append((e1[1] - e0[2], tiles, e1[0] == e0[0]))
            for e in engs:
                if R0 <= e[1] <= R1:
                    ENG[ro].append((e[2] - e[1] + 1, e[3]))
                    # target choice at first hit: nearest alive group (state alive) at e[1]-10 (approach start) vs taken
                    r0 = max(e[1] - 10, 1)
                    if r0 in rows and rows[r0][9] and 'gs' in byr.get(r0, {}):
                        p = rows[r0][3:5]; gs = byr[r0]['gs']
                        alive = [int(g) for g, s in gs.items() if s == 1 and int(g) in gtiles]
                        if alive and e[0] in gtiles:
                            near = min(alive, key=lambda g: gdist(p, g))
                            CHOICE[ro].append((ghp[e[0]], ggold[e[0]], gdist(p, e[0]), ghp[near], ggold[near], gdist(p, near), near == e[0]))
            # deaths in the window: dead length, champion damage share of the hp lost in the 10 rounds before, state before
            cdm = collections.defaultdict(float); attackers = collections.defaultdict(set)
            for r, a, t, dmg in D['cc']:
                if t == idx: cdm[r] += dmg; attackers[r].add(a)
            for r in rs:
                if R0 <= r <= R1 and r - 1 in rows and rows[r - 1][9] and not rows[r][9]:
                    q = r
                    while q in rows and not rows[q][9]: q += 1
                    hp10 = rows[r - 10][5] if r - 10 in rows and rows[r - 10][9] else rows[r - 1][5]
                    lost = max(hp10, 1.0); cd = sum(cdm[x] for x in range(r - 10, r + 1))
                    foes = set().union(*[attackers[x] for x in range(r - 10, r + 1)])
                    washit = any(x in hits[idx] for x in range(r - 5, r))
                    # context 5 rounds before: allies / foes within 6, dealt champion damage in r-10..r, moved away from foes, own half
                    rq = max(r - 5, R0); ctx = byr.get(rq, {}).get('c', [])
                    pq = rows[rq][3:5] if rq in rows else rows[r - 1][3:5]
                    al = sum(1 for c2 in ctx if c2[1] == team and c2[0] != idx and c2[9] and cheb(c2[3:5], pq) <= 6)
                    fo = sum(1 for c2 in ctx if c2[1] != team and c2[9] and cheb(c2[3:5], pq) <= 6)
                    dealt = sum(dmg for rr2, a2, t2, dmg in D['cc'] if a2 == idx and r - 10 <= rr2 <= r)
                    dspawn = cheb(pq, sp); dfoe = cheb(pq, spawn[1 - team])
                    DEATH[ro].append((r, q - r, min(cd / lost, 1.0), washit, len(foes), hp10, typ, al, fo, dealt, dspawn < dfoe, rows[rq][5] / max(rows[rq][6], 1) if rq in rows else 0))
            # bucket per round
            nxt = {}   # r -> group of the next hit at or after r
            j = 0; hits_list = [(r, next(iter(hits[idx][r]))) for r in hr]
            stillrun = 0
            for r in range(R0, R1 + 1):
                c = rows.get(r)
                if c is None: continue
                while j < len(hits_list) and hits_list[j][0] < r: j += 1
                nh = hits_list[j] if j < len(hits_list) and hits_list[j][0] - r <= 40 else None
                p = c[3:5]; pr = rows.get(r - 1); pp = pr[3:5] if pr else p
                moved = pr is not None and pr[9] and p != pp and r not in tele
                if not c[9]: b = 'dead'
                elif r in hits[idx]: b = 'hit'
                elif r in cc[idx]: b = 'fight'
                elif moved and any(q in cc[idx] for q in range(r - 4, r)): b = 'flee'
                elif not moved and any(gdist(p, int(g)) <= 2 for g, s in byr[r].get('gs', {}).items() if s == 2 and int(g) in gtiles): b = 'reward'
                elif r in recall_rounds or cheb(p, sp) <= 3: b = 'recall'
                elif not moved: b = 'still'
                elif nh and gdist(p, nh[1]) < gdist(pp, nh[1]): b = 'walk_camp'
                elif cheb(p, sp) < cheb(pp, sp): b = 'walk_home'
                else: b = 'walk_other'
                B[ro][b] += 1; BT[(ro, typ)][b] += 1
                if b == 'still': stillrun += 1
                elif stillrun: STILLRUN[ro].append(stillrun); stillrun = 0
            if stillrun: STILLRUN[ro].append(stillrun)
        B['us']['games'] += 1; B['rival']['games'] += 1
def mean(v): return sum(v) / len(v) if v else float('nan')
print(f"games: {dict(ngames)}; window r{R0}-{R1}; champion-rounds per game by bucket (us = the batch's bot, rival = the other side)")
print("| bucket | rival | us | diff (rival-us) |")
print("|---|---|---|---|")
ng = {ro: B[ro]['games'] for ro in ('rival', 'us')}
for b in BUCKETS:
    rv, u = B['rival'][b] / ng['rival'], B['us'][b] / ng['us']
    print(f"| {b} | {rv:.1f} | {u:.1f} | {rv - u:+.1f} |")
tot = {ro: sum(B[ro][b] for b in BUCKETS) / ng[ro] for ro in ng}
print(f"| total | {tot['rival']:.1f} | {tot['us']:.1f} | |")
if PERTYPE:
    print("\n## per champion type (champion-rounds per champion-game)")
    print("| type | role | " + ' | '.join(BUCKETS) + " |")
    print("|---|---|" + '---|' * len(BUCKETS))
    for typ in TYPES:
        for ro in ('rival', 'us'):
            c = BT.get((ro, typ))
            if not c: continue
            n = sum(c.values()) / (R1 - R0 + 1)
            print(f"| {typ} | {ro} (n={n:.0f}) | " + ' | '.join(f"{c[b]/n:.1f}" for b in BUCKETS) + " |")
print("\n## travel between consecutive engagements of one champion (different groups; window by the first hit of the second)")
print("| role | n/game | rounds mean / median | tiles between groups mean / median | rounds per tile |")
print("|---|---|---|---|---|")
for ro in ('rival', 'us'):
    v = TRAV[ro]
    if not v: continue
    print(f"| {ro} | {len(v)/ng[ro]:.2f} | {mean([x[0] for x in v]):.1f} / {st.median([x[0] for x in v]):.0f} | {mean([x[1] for x in v]):.1f} / {st.median([x[1] for x in v]):.0f} | {sum(x[0] for x in v)/max(1,sum(x[1] for x in v)):.2f} |")
    hist = collections.Counter(min(x[0] // 10, 6) for x in v)
    print(f"  rounds 0-9/10-19/20-29/30-39/40-49/50-59/60+: " + ' / '.join(f"{100*hist[k]/len(v):.0f}" for k in range(7)) + '%')
print("\n## engagements (one champion, one group, hits with gaps <= 8): per game, length (first->last hit), hits")
for ro in ('rival', 'us'):
    v = ENG[ro]
    print(f"- {ro}: {len(v)/ng[ro]:.2f} per game, length mean {mean([x[0] for x in v]):.1f} / median {st.median([x[0] for x in v]):.0f}, hits {mean([x[1] for x in v]):.1f}")
print("\n## target choice at the start of an engagement (10 rounds before the first hit): group taken vs nearest alive group")
print("| role | n | took nearest % | hp taken / nearest | gold taken / nearest | tiles to taken / nearest |")
print("|---|---|---|---|---|---|")
for ro in ('rival', 'us'):
    v = CHOICE[ro]
    if not v: continue
    print(f"| {ro} | {len(v)} | {100*sum(x[6] for x in v)/len(v):.0f} | {mean([x[0] for x in v]):.0f} / {mean([x[3] for x in v]):.0f} | {mean([x[1] for x in v]):.0f} / {mean([x[4] for x in v]):.0f} | {mean([x[2] for x in v]):.1f} / {mean([x[5] for x in v]):.1f} |")
print("\n## deaths in the window: per game, dead rounds per death, killed by champions (>=50% of the hp lost in the last 10 rounds is champion damage), was hitting a camp in the 5 rounds before, foes that hit it, hp 10 rounds before")
print("| role | deaths/game | dead rounds/death | champion-killed % | hitting a camp before % | foes hitting (champion-killed) | hp 10 rounds before | by type |")
print("|---|---|---|---|---|---|---|---|")
for ro in ('rival', 'us'):
    v = DEATH[ro]
    if not v: continue
    ck_ = [x for x in v if x[2] >= 0.5]
    bt = collections.Counter(x[6] for x in v)
    print(f"| {ro} | {len(v)/ng[ro]:.2f} | {mean([x[1] for x in v]):.1f} | {100*len(ck_)/len(v):.0f} | {100*sum(1 for x in v if x[3])/len(v):.0f} | {mean([x[4] for x in ck_]) if ck_ else 0:.2f} | {mean([x[5] for x in v]):.0f} | {', '.join(f'{k} {c/ng[ro]:.2f}' for k, c in bt.most_common())} |")
    print(f"  context 5 rounds before (champion-killed): allies<=6 {mean([x[7] for x in ck_]):.2f}, foes<=6 {mean([x[8] for x in ck_]):.2f}, dealt champion dmg last 10r {mean([x[9] for x in ck_]):.0f} (0 dealt: {100*sum(1 for x in ck_ if x[9]==0)/max(1,len(ck_)):.0f}%), own half {100*sum(1 for x in ck_ if x[10])/max(1,len(ck_)):.0f}%, hp frac {mean([x[11] for x in ck_]):.2f}; allies 0/1/2+: " + ' / '.join(f"{100*sum(1 for x in ck_ if min(x[7],2)==k)/max(1,len(ck_)):.0f}" for k in range(3)) + "%; foes 1/2/3+: " + ' / '.join(f"{100*sum(1 for x in ck_ if min(x[8],3)==k)/max(1,len(ck_)):.0f}" for k in range(1,4)) + '%')
    cm = [x for x in v if x[2] < 0.5]
    if cm: print(f"  camp-killed: {len(cm)/ng[ro]:.2f}/game, hp frac 5 rounds before {mean([x[11] for x in cm]):.2f}, allies<=6 {mean([x[7] for x in cm]):.2f}, hitting before {100*sum(1 for x in cm if x[3])/len(cm):.0f}%")
    hist = collections.Counter(min((x[0] - R0) // 30, 3) for x in v)
    print(f"  deaths by 30-round slice from r{R0}: " + ' / '.join(f"{hist[k]/ng[ro]:.2f}" for k in range(4)))
print("\n## still runs (consecutive 'still' rounds): count per game, mean length, share of runs >= 5")
for ro in ('rival', 'us'):
    v = STILLRUN[ro]
    if v: print(f"- {ro}: {len(v)/ng[ro]:.1f} runs/game, mean {mean(v):.1f}, >=5: {100*sum(1 for x in v if x >= 5)/len(v):.0f}%")
