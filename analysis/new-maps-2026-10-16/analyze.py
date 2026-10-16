# Per game and team: draft, items, gold, captures (route), banking, recalls, deaths, map presence. -> data/games.json
import gzip, json, glob, os, collections, statistics as st
ITEMS = [l.strip() for l in open('/mnt/project-files/analysis/data/items.txt')]
pick = {r['match']: r for r in json.load(open('../data/pick.json'))}
def cheb(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
out = []
for f in sorted(glob.glob('../data/compact/*.json.gz')):
    mid = os.path.basename(f)[:-8]; P = pick.get(mid)
    if not P: continue
    d = json.load(gzip.open(f, 'rt')); R = d['R']; CH = d['champs']; S = d['meta']['statistics']
    final = d['meta']['finalRound']; gems = d['meta']['submittedGems']
    sc = {}
    for t in (0, 1):
        ps = [R[0][3][i][:2] for i, c in enumerate(CH) if c[1] == t]
        sc[t] = (sum(p[0] for p in ps) / len(ps), sum(p[1] for p in ps) / len(ps))
    # captures: group state reward_available(team) -> respawning
    last = {}; caps = {0: [], 1: []}; seen = set()
    for g in d['G']:
        r, ci, grp, typ, x, y, state, team, alive, rg, rgold = g
        if state == 'reward_available' and team in (0, 1): last[grp] = (team, r)
        if state == 'respawning' and grp in last and (r, grp) not in seen:
            seen.add((r, grp)); t = last.pop(grp)[0]
            caps[t].append(dict(r=r, grp=grp, gems=rg, gold=rgold, x=x, y=y, typ=typ))
    for t in (0, 1):
        name = P['a'] if t == 0 else P['b']
        me = [i for i, c in enumerate(CH) if c[1] == t]
        own, en = sc[t], sc[1 - t]
        recalls = []; deaths = []; buys = []; enemy_half = 0; tot = 0; contact = None
        for k in range(1, len(R)):
            r = R[k][0]; a = R[k - 1][3]; b = R[k][3]
            for i in me:
                if a[i][6] and b[i][6]:
                    if cheb(b[i][:2], own) <= 3 and cheb(a[i][:2], own) > 6: recalls.append((r, i, round(a[i][2] / a[i][3], 2), a[i][4]))
                    if b[i][5] < a[i][5]: buys.append((r, i, a[i][5] - b[i][5]))
                if a[i][6] and not b[i][6]:
                    p = a[i][:2]; deaths.append((r, i, 'enemy' if cheb(p, en) < cheb(p, own) else 'own', a[i][4]))
                if b[i][6]:
                    tot += 1; enemy_half += cheb(b[i][:2], en) < cheb(b[i][:2], own)
            if contact is None:
                for i in me:
                    for j, c in enumerate(CH):
                        if c[1] != t and b[i][6] and b[j][6] and cheb(b[i][:2], b[j][:2]) <= 5: contact = r; break
                    if contact: break
        sub = [x[1 + t] for x in R]
        def at(rr): return sub[min(rr, len(sub) - 1)]
        banks = [sub[k] - sub[k - 1] for k in range(1, len(sub)) if sub[k] > sub[k - 1]]
        reach = next((R[k][0] for k in range(len(R)) if sub[k] >= 1000), None)
        stc = [c for c in S['champions'] if c['team'] == t]
        items = collections.Counter()
        for c in stc:
            for ii, n in enumerate(c['itemsBought']):
                if n: items[ITEMS[ii]] += n
        cp = caps[t]
        out.append(dict(match=mid, map=P['map'], who=P['who'] if (P['who'] == 'top' or name == 'us') else 'opp', team=name,
            opp=P['b'] if t == 0 else P['a'], side='ab'[t], win=P['win'] == name, final=final, gems=gems[t], ogems=gems[1 - t],
            draft=[CH[i][2] for i in me], kills=sum(c['kills'] for c in stc), deaths=len(deaths),
            deaths_enemy_half=sum(1 for x in deaths if x[2] == 'enemy'), gems_lost=sum(x[3] for x in deaths),
            first_death=deaths[0][0] if deaths else None, contact=contact,
            gold=sum(c['earnedGold'] for c in stc), items=dict(items.most_common()), first_buy=buys[0][0] if buys else None,
            n_buys=len(buys), recalls=len(recalls), recall_hp=st.median([x[2] for x in recalls]) if recalls else None,
            recall_gems=st.median([x[3] for x in recalls]) if recalls else None,
            caps=len(cp), gem_caps=sum(1 for c in cp if c['gems'] > 0), gold_caps=sum(1 for c in cp if c['gems'] == 0),
            first_cap=cp[0]['r'] if cp else None, first_gem_cap=next((c['r'] for c in cp if c['gems'] > 0), None),
            cap_seq=[(c['r'], c['grp'], c['gems'], c['gold'], c['x'], c['y']) for c in cp[:25]],
            cap_groups=collections.Counter(c['grp'] for c in cp).most_common(),
            gold_from_caps=sum(c['gold'] for c in cp), gems_from_caps=sum(c['gems'] for c in cp),
            sub150=at(150), sub300=at(300), sub500=at(500), reach=reach, banks=len(banks),
            bag=st.median(banks) if banks else None, enemy_half=round(enemy_half / max(tot, 1), 3)))
json.dump(out, open('../data/games.json', 'w'))
print(len(out))
