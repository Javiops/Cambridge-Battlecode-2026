#!/usr/bin/env python3
"""Supervised fight value and behaviour cloning for the micro (the "learned fight/flee value" of the RL assessment).

Two sources of labelled contact situations, described with the bot's own fight features (ga_struct.h GaFeat):
  top   decoded every-round replays of the #1/#2 teams (Mite, Univardisty; 101 games,
        analysis/top2-dissection-2026-10-15/data/steps.tgz): every alive champion with an enemy within 8.
  ours  the DQN collection logs of our bot (tools/ga/dqn.py collect: [dq] decision + [dt] trace lines).
Labels: die10 = the champion dies within the next 10 rounds; move = next-round step relative to the nearest enemy
(approach / hold / retreat), for behaviour cloning of the top teams' engage / back-off decisions.

The model is the same 25-H-7 dense net as dqn.h (unused features get zero weights), so it is embedded with the
DQN tooling: mode 2/3 of dqn.h = "back off / flee when p(die within 10) > margin per mille", mode 1 for the cloned
policy (approach -> engage, hold -> rules, retreat -> back off).

usage:
  python3 tools/ga/fightval.py data  --steps out/top2/steps --dqn out/dqn/data     # -> out/fightval/{top,ours}.npz
  python3 tools/ga/fightval.py fit   --src top --label die10 --out out/fightval/die_top.json
  python3 tools/ga/fightval.py fit   --src ours --label die10 --out out/fightval/die_ours.json
  python3 tools/ga/fightval.py fit   --src top --label move --out out/fightval/bc_top.json
  python3 tools/ga/fightval.py compare                                               # same situation, who dies more
"""
import argparse, glob, json, math, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import structure as T

F = {n: i for i, n in enumerate(T.FEATURES)}
N_IN = len(T.FEATURES)
# features both sources can compute the same way (the rest need the bot's own target choice, spell timers or
# team chat, which a replay does not show)
USED = ['HP', 'NEAR', 'F4', 'F8', 'A4', 'A8', 'RATIO', 'FAV', 'REACH', 'THP', 'TDIST', 'GEMS', 'HOME', 'ROUND', 'HIT',
        'NB', 'EB', 'RANGED']
MASK = np.array([n in USED for n in T.FEATURES], np.float32)
FEAT_SCALE = np.array([100, 10, 3, 3, 3, 3, 200, 200, 1, 1, 1, 100, 10, 50, 20, 100, 1, 1, 1, 1, 200, 1, 3, 3, 1], np.float32)
RANGED = {'Cassi', 'VesperVale', 'Vesper Vale', 'Prism', 'Stellar', 'Tavi', 'Willow'}
MOVES = ['approach', 'hold', 'retreat']
HORIZON = 10


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def feats_of(me, mates, foes, home, r, hit):
    """me/mates/foes: (x, y, hp, maxhp, gems, type). Same definitions as struct.patch fight_ctx."""
    f = np.zeros(N_IN, np.float32)
    p = me[:2]
    ds = [cheb(p, o[:2]) for o in foes]
    near = min(ds)
    ti = int(np.argmin(ds))
    tgt = foes[ti]
    ours = me[2] + sum(a[2] for a in mates if cheb(p, a[:2]) <= 6)
    theirs = sum(o[2] for o, d in zip(foes, ds) if d <= 8)
    f[F['HP']] = int(me[2] * 100 / max(1, me[3]))
    f[F['NEAR']] = min(20, near)
    f[F['F4']] = sum(d <= 4 for d in ds)
    f[F['F8']] = sum(d <= 8 for d in ds)
    f[F['A4']] = sum(cheb(p, a[:2]) <= 4 for a in mates)
    f[F['A8']] = sum(cheb(p, a[:2]) <= 8 for a in mates)
    f[F['RATIO']] = min(999, int(ours * 100 / theirs)) if theirs > 0 else 999
    f[F['ERATIO']] = f[F['RATIO']]
    f[F['FAV']] = ours * 100 >= 83 * theirs
    rng = 3 if me[5] in RANGED else 1
    f[F['REACH']] = near <= rng + 1
    f[F['THP']] = int(tgt[2] * 100 / max(1, tgt[3]))
    f[F['TDIST']] = min(20, near)
    f[F['GEMS']] = me[4]
    f[F['HOME']] = cheb(p, home)
    f[F['ROUND']] = r // 10
    f[F['HIT']] = hit
    f[F['NB']] = 1 + sum(cheb(tgt[:2], a[:2]) <= 8 for a in mates)
    f[F['EB']] = sum(cheb(tgt[:2], o[:2]) <= 8 for o in foes)
    f[F['RANGED']] = rng > 1
    return f, ti


def top_dataset(steps_dir, selected):
    """Every round, every alive champion of the recorded top team with an enemy within 8 and away from its spawn."""
    sel = json.load(open(selected))
    teams = {}
    for s in sel:
        teams.setdefault(s['match'], set()).add((0 if s['side'] == 'a' else 1, s['team'], s['map']))
    X, Ydie, Ymove, G, TEAM = [], [], [], [], []
    for gi, path in enumerate(sorted(glob.glob(os.path.join(steps_dir, '*.c.jsonl')))):
        mid = os.path.basename(path).split('.')[0]
        if mid not in teams:
            continue
        rounds = []
        for line in open(path):
            if line.startswith('{"t": "round"') or '"t":"round"' in line[:20] or '"t": "round"' in line[:20]:
                d = json.loads(line)
                rounds.append(d)
        if not rounds:
            continue
        rounds.sort(key=lambda d: d['r'])
        byr = {d['r']: d for d in rounds}
        homes = {}
        for t in (0, 1):
            pts = [(c[3], c[4]) for c in rounds[0]['champs'] if c[1] == t]
            homes[t] = (sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts))
        # death round of each champion after round r: first round where alive goes 1 -> 0
        deaths = {}
        prev = None
        for d in rounds:
            for c in d['champs']:
                if prev is not None and prev.get(c[0], 0) == 1 and c[9] == 0:
                    deaths.setdefault(c[0], []).append(d['r'])
            prev = {c[0]: c[9] for c in d['champs']}
        for side, tname, mapname in teams[mid]:
            for d in rounds:
                r = d['r']
                if r < 1 or r + 1 not in byr:
                    continue
                ch = d['champs']
                last = byr.get(r - 1)
                for c in ch:
                    if c[1] != side or not c[9]:
                        continue
                    me = (c[3], c[4], c[5], c[6], c[7], c[2])
                    if cheb(me[:2], homes[side]) <= 3:
                        continue
                    foes = [(o[3], o[4], o[5], o[6], o[7], o[2]) for o in ch if o[1] != side and o[9]]
                    foes = [o for o in foes if cheb(o[:2], me[:2]) <= 8]
                    if not foes:
                        continue
                    mates = [(o[3], o[4], o[5], o[6], o[7], o[2]) for o in ch if o[1] == side and o[9] and o[0] != c[0]]
                    hit = 0
                    if last:
                        lc = [o for o in last['champs'] if o[0] == c[0]]
                        hit = int(bool(lc) and lc[0][9] and lc[0][5] > c[5] + 1)
                    f, ti = feats_of(me, mates, foes, homes[side], r, hit)
                    die = any(r < dr <= r + HORIZON for dr in deaths.get(c[0], []))
                    nx = [o for o in byr[r + 1]['champs'] if o[0] == c[0]][0]
                    tg = foes[ti]
                    tnext = [o for o in byr[r + 1]['champs'] if o[1] != side and o[3] == tg[0] and o[4] == tg[1]]
                    if not nx[9] or cheb((nx[3], nx[4]), me[:2]) > 2:
                        mv = -1  # died, recalled or dashed: not a walking decision
                    else:
                        d0 = cheb(me[:2], tg[:2])
                        d1 = cheb((nx[3], nx[4]), tg[:2])  # vs the foe's old tile: our own step only
                        mv = 0 if d1 < d0 else (1 if d1 == d0 else 2)
                    X.append(f); Ydie.append(die); Ymove.append(mv); G.append(gi); TEAM.append(tname == 'mite')
    return {'x': np.array(X), 'die': np.array(Ydie, np.float32), 'move': np.array(Ymove), 'g': np.array(G),
            'mite': np.array(TEAM)}


def ours_dataset(dqn_data):
    sys.path.insert(0, HERE)
    import dqn
    X, Y, G, A, GR = [], [], [], [], []
    for gi, p in enumerate(sorted(glob.glob(os.path.join(dqn_data, '*', '*.log')))):
        for decs, trace in dqn.parse_log(p):
            dead = sorted(t[0] for i, t in enumerate(trace) if not t[1] and (i == 0 or trace[i - 1][1]))
            for dd in decs:
                r = dd[0]
                X.append(dd[4:]); A.append(dd[1]); GR.append(dd[2]); G.append(gi)
                Y.append(any(r < x <= r + HORIZON for x in dead))
    return {'x': np.array(X, np.float32), 'die': np.array(Y, np.float32), 'g': np.array(G), 'a': np.array(A),
            'greedy': np.array(GR)}


# ---------------------------------------------------------------------------------------------------- model
def fit_mlp(x, y, nclass, hid=16, epochs=8, lr=3e-3, seed=0, w=None):
    """Softmax (nclass > 1) or logistic (nclass == 1) MLP on masked, scaled features; numpy + Adam."""
    rng = np.random.default_rng(seed)
    xs = (x / FEAT_SCALE) * MASK
    no = max(1, nclass)
    p = {'w1': rng.normal(0, math.sqrt(2 / len(USED)), (hid, N_IN)).astype(np.float32) * MASK,
         'b1': np.zeros(hid, np.float32), 'w2': rng.normal(0, 0.1, (no, hid)).astype(np.float32), 'b2': np.zeros(no, np.float32)}
    m = {k: np.zeros_like(v) for k, v in p.items()}
    v = {k: np.zeros_like(v) for k, v in p.items()}
    t = 0
    n = len(y)
    w = np.ones(n, np.float32) if w is None else w
    for ep in range(epochs):
        perm = rng.permutation(n)
        for s in range(0, n, 512):
            b = perm[s:s + 512]
            h = np.maximum(0, xs[b] @ p['w1'].T + p['b1'])
            o = h @ p['w2'].T + p['b2']
            if nclass == 1:
                pr = 1 / (1 + np.exp(-o[:, 0]))
                g = ((pr - y[b]) * w[b])[:, None] / len(b)
            else:
                e = np.exp(o - o.max(1, keepdims=True))
                pr = e / e.sum(1, keepdims=True)
                g = pr.copy()
                g[np.arange(len(b)), y[b].astype(int)] -= 1
                g = g * w[b][:, None] / len(b)
            gr = {'w2': g.T @ h + 1e-4 * p['w2'], 'b2': g.sum(0)}
            gh = (g @ p['w2']) * (h > 0)
            gr['w1'] = (gh.T @ xs[b]) * MASK + 1e-4 * p['w1']
            gr['b1'] = gh.sum(0)
            t += 1
            for k in p:
                m[k] = 0.9 * m[k] + 0.1 * gr[k]
                v[k] = 0.999 * v[k] + 0.001 * gr[k] ** 2
                p[k] -= lr * (m[k] / (1 - 0.9 ** t)) / (np.sqrt(v[k] / (1 - 0.999 ** t)) + 1e-8)
    return p


def predict(p, x):
    h = np.maximum(0, ((x / FEAT_SCALE) * MASK) @ p['w1'].T + p['b1'])
    return h @ p['w2'].T + p['b2']


def auc(y, s):
    o = np.argsort(s)
    r = np.empty(len(s)); r[o] = np.arange(1, len(s) + 1)
    pos = y > 0.5
    npos, nneg = pos.sum(), (~pos).sum()
    return float((r[pos].sum() - npos * (npos + 1) / 2) / max(1, npos * nneg))


def split(d, seed=0):
    games = np.unique(d['g'])
    rng = np.random.default_rng(seed)
    held = set(rng.choice(games, max(1, len(games) // 5), replace=False))
    te = np.array([g in held for g in d['g']])
    return ~te, te


def to_dq(p, label):
    """The model as a dqn.h net (w1 H x 25, b1, w2 7 x H, b2). die10: output 0 = logit. move: approach -> engage (1),
    hold -> default (0), retreat -> back off (3); the other actions get a large negative bias."""
    hid = p['w1'].shape[0]
    w2 = np.zeros((7, hid), np.float32)
    b2 = np.full(7, -100.0, np.float32)
    if label == 'die10':
        w2[0], b2[0] = p['w2'][0], p['b2'][0]
    else:
        for cls, act in ((0, 1), (1, 0), (2, 3)):
            w2[act], b2[act] = p['w2'][cls], p['b2'][cls]
    return {'w1': p['w1'].tolist(), 'b1': p['b1'].tolist(), 'w2': w2.tolist(), 'b2': b2.tolist()}


# ------------------------------------------------------------------------------------------------- commands
def cmd_data(A):
    os.makedirs(A.work, exist_ok=True)
    if A.steps:
        d = top_dataset(A.steps, A.selected)
        np.savez(os.path.join(A.work, 'top.npz'), **d)
        print(f"top: {len(d['die'])} contact turns, {d['die'].mean() * 100:.1f}% die within {HORIZON}, moves "
              f"{np.bincount(d['move'][d['move'] >= 0], minlength=3).tolist()} ({MOVES}), Mite share {d['mite'].mean():.2f}")
    if A.dqn:
        d = ours_dataset(A.dqn)
        np.savez(os.path.join(A.work, 'ours.npz'), **d)
        print(f"ours: {len(d['die'])} decisions, {d['die'].mean() * 100:.1f}% die within {HORIZON}")


def load(work, src):
    return dict(np.load(os.path.join(work, src + '.npz')))


def cmd_fit(A):
    d = load(A.work, A.src)
    if A.label == 'move':
        keep = d['move'] >= 0
        d = {k: v[keep] for k, v in d.items()}
        y, ncls = d['move'].astype(np.float32), 3
    else:
        y, ncls = d['die'], 1
        if A.src == 'ours' and A.greedy_only:  # states where the rules (not epsilon) chose
            keep = (d['greedy'] == 1) & (d['a'] == 0)
            d = {k: v[keep] for k, v in d.items()}
            y = d['die']
    tr, te = split(d, A.seed)
    p = fit_mlp(d['x'][tr], y[tr], ncls, hid=A.hid, epochs=A.epochs, seed=A.seed)
    o = predict(p, d['x'][te])
    if ncls == 1:
        s = 1 / (1 + np.exp(-o[:, 0]))
        base = y[tr].mean()
        ll = float(-np.mean(y[te] * np.log(s + 1e-9) + (1 - y[te]) * np.log(1 - s + 1e-9)))
        ll0 = float(-np.mean(y[te] * np.log(base) + (1 - y[te]) * np.log(1 - base)))
        msg = f'held-out AUC {auc(y[te], s):.3f}, log-loss {ll:.4f} vs {ll0:.4f} for the base rate {base:.3f}'
        # calibration by decile
        q = np.quantile(s, np.linspace(0, 1, 11))
        cal = [(float(q[i]), float(y[te][(s >= q[i]) & (s <= q[i + 1])].mean())) for i in range(10)]
        msg += '\n  predicted vs real death rate by decile: ' + ' '.join(f'{a:.2f}/{b:.2f}' for a, b in cal)
    else:
        acc = float((o.argmax(1) == y[te]).mean())
        maj = float(np.bincount(y[tr].astype(int)).max() / len(y[tr]))
        msg = f'held-out accuracy {acc:.3f} vs {maj:.3f} for always-the-commonest-move'
    print(f'{A.src} {A.label}: {tr.sum()} train / {te.sum()} held-out rows; {msg}')
    out = to_dq(p, A.label)
    out.update({'label': A.label, 'src': A.src, 'used': USED, 'summary': msg, 'raw': {k: v.tolist() for k, v in p.items()}})
    json.dump(out, open(A.out, 'w'))
    print('->', A.out)


def cmd_compare(A):
    """Same situation, who dies more: the top-team death model scored on our states, and our real death rate."""
    top, ours = load(A.work, 'top'), load(A.work, 'ours')
    pt = fit_mlp(top['x'], top['die'], 1, hid=16, epochs=8)
    keep = (ours['greedy'] == 1) & (ours['a'] == 0)
    s = 1 / (1 + np.exp(-predict(pt, ours['x'][keep])[:, 0]))
    y = ours['die'][keep]
    print(f'our rule-chosen contact turns: {keep.sum()}, real death rate {y.mean():.3f}, '
          f'top-team model expects {s.mean():.3f} for a top team in the same spots; AUC of the top model on ours {auc(y, s):.3f}')
    for name, idx in (('HP', F['HP']), ('RATIO', F['RATIO']), ('F4', F['F4']), ('A4', F['A4']), ('GEMS', F['GEMS'])):
        x = ours['x'][keep][:, idx]
        qs = np.unique(np.quantile(x, [0, .2, .4, .6, .8, 1]))
        row = []
        for a, b in zip(qs[:-1], qs[1:]):
            mk = (x >= a) & (x <= b)
            if mk.sum() > 50:
                row.append(f'{a:.0f}-{b:.0f}: ours {y[mk].mean():.3f} top {s[mk].mean():.3f}')
        print(f'  by {name}: ' + '; '.join(row))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--work', default='out/fightval')
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('data')
    s.add_argument('--steps', default=''); s.add_argument('--dqn', default='')
    s.add_argument('--selected', default='/mnt/project-files/analysis/top2-dissection-2026-10-15/data/selected.json')
    s = sub.add_parser('fit')
    s.add_argument('--src', choices=('top', 'ours'), required=True); s.add_argument('--label', choices=('die10', 'move'), default='die10')
    s.add_argument('--out', required=True); s.add_argument('--hid', type=int, default=16); s.add_argument('--epochs', type=int, default=8)
    s.add_argument('--seed', type=int, default=0); s.add_argument('--greedy-only', action='store_true')
    sub.add_parser('compare')
    A = p.parse_args()
    {'data': cmd_data, 'fit': cmd_fit, 'compare': cmd_compare}[A.cmd](A)


if __name__ == '__main__':
    main()
