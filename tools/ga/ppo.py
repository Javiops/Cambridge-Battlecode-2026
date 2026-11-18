#!/usr/bin/env python3
"""PPO (proximal policy optimisation) for the fight micro, on the DQN tooling (dqn.h mode 4, see DQN.md).

The bot samples its action from softmax(net output) over the valid actions of the micro hook (0 = let the rules
decide, 1 engage, 2 kite, 3 back off, 4 flee, 5 recall, 6 farm). The net starts with a bias on action 0, so the first
policy is "the rules, with some exploration". Each iteration plays fresh games with the current policy (on-policy),
turns the logs into rewarded decisions, and updates the policy with PPO's clipped objective; a critic (value net,
Python only) gives the advantages (GAE). The greedy version of any iteration (argmax) is judged with
`dqn.py --work out/ppo eval --net out/ppo/pol_K.json` like every other candidate.

usage (repo root):
  python3 tools/ga/dqn.py --work out/ppo prepare
  python3 tools/ga/ppo.py run --iters 12 --games 600          # resumes from out/ppo/ppo_state.json
"""
import argparse, glob, json, math, os, random, sys, time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dqn

N_IN, N_H, N_OUT = dqn.N_IN, dqn.N_H, dqn.N_OUT
FS = dqn.FEAT_SCALE

# reward per decision, gem equivalents, until the next decision of the contact (see DQN.md; the hp weight is lower
# than the DQN's 10, which taught it to run away, and the team score margin is added so the real objective shows)
W_HP, W_GOLD, W_TEAM, DEATH = 3.0, 0.1, 0.1, 25.0
GAMMA, LAM = 0.9, 0.9


def episodes(decs, trace):
    """One champion -> list of contacts, each a list of (features, sampled action, valid mask, reward), terminal at the
    end (death or 15 rounds without a decision)."""
    tr = {t[0]: t for t in trace}
    out, cur = [], []
    decs = sorted(decs, key=lambda d: d[0])
    for i, d in enumerate(decs):
        if d[2] < 10:  # not a sampled decision (should not happen in mode 4)
            continue
        r0 = d[0]
        nxt = decs[i + 1] if i + 1 < len(decs) and decs[i + 1][0] - r0 <= dqn.CONTACT_GAP else None
        end = nxt[0] if nxt else r0 + dqn.CONTACT_GAP
        prev = tr.get(r0)
        if prev is None:
            continue
        rew, died = 0.0, False
        for rr in range(r0 + 1, end + 1):
            t = tr.get(rr)
            if t is None:
                continue
            if prev[1] and not t[1]:
                rew -= DEATH + prev[4]
                died = True
            elif t[1] and prev[1]:
                rew += max(0, t[4] - prev[4]) + W_HP * (t[2] - prev[2]) / max(1, t[3]) + W_GOLD * max(0, t[5] - prev[5])
            if t[6] >= 0 and prev[6] >= 0:
                rew += W_TEAM * ((t[6] - prev[6]) - (t[7] - prev[7]))
            prev = t
            if died:
                break
        cur.append((d[4:], d[2] - 10, d[3], rew, GAMMA))
        if died or nxt is None:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def episodes_gems(decs, trace, gamma_round=0.99):
    """--reward gems (the user's objective: gems per turn): one episode per champion for the whole game, reward of a
    decision = change of (our team's submitted gems + this champion's bag) until its next decision, discounted per
    round. A death shows up as the lost bag and as the gems the team does not earn while it is dead; no hp or death
    shaping."""
    tr = {t[0]: t for t in trace}
    decs = [d for d in sorted(decs, key=lambda d: d[0]) if d[2] >= 10 and d[0] in tr and tr[d[0]][6] >= 0]

    def val(t):
        return t[6] + (t[4] if t[1] else 0)
    ep = []
    for i, d in enumerate(decs):
        t0 = tr[d[0]]
        if i + 1 < len(decs):
            t1 = tr[decs[i + 1][0]]
            ep.append((d[4:], d[2] - 10, d[3], float(val(t1) - val(t0)), gamma_round ** (decs[i + 1][0] - d[0])))
        else:
            last = max(tr)  # the trace stops 15 rounds after the last decision
            ep.append((d[4:], d[2] - 10, d[3], float(val(tr[last]) - val(t0)), 0.0))
    return [ep] if ep else []


def mlp_init(rng, hid, nout, zero_out=True):
    return {'w1': rng.normal(0, math.sqrt(2.0 / N_IN), (hid, N_IN)).astype(np.float32), 'b1': np.zeros(hid, np.float32),
            'w2': (np.zeros if zero_out else lambda s: rng.normal(0, 0.1, s))((nout, hid)).astype(np.float32),
            'b2': np.zeros(nout, np.float32)}


def fwd(p, x):
    xs = x / FS
    h = np.maximum(0, xs @ p['w1'].T + p['b1'])
    return h @ p['w2'].T + p['b2'], (xs, h)


def back(p, cache, g):
    xs, h = cache
    gr = {'w2': g.T @ h, 'b2': g.sum(0)}
    gh = (g @ p['w2']) * (h > 0)
    gr['w1'] = gh.T @ xs
    gr['b1'] = gh.sum(0)
    return gr


class Adam:
    def __init__(self, p, lr):
        self.m = {k: np.zeros_like(v) for k, v in p.items()}
        self.v = {k: np.zeros_like(v) for k, v in p.items()}
        self.t, self.lr = 0, lr

    def step(self, p, g):
        self.t += 1
        for k in p:
            gk = np.clip(g[k], -5, 5)
            self.m[k] = 0.9 * self.m[k] + 0.1 * gk
            self.v[k] = 0.999 * self.v[k] + 0.001 * gk ** 2
            p[k] -= self.lr * (self.m[k] / (1 - 0.9 ** self.t)) / (np.sqrt(self.v[k] / (1 - 0.999 ** self.t)) + 1e-8)


def masked_logp(logits, valid):
    m = ((valid[:, None] >> np.arange(N_OUT)[None, :]) & 1).astype(bool)
    z = np.where(m, logits, -1e9)
    z = z - z.max(1, keepdims=True)
    e = np.exp(z) * m
    p = e / e.sum(1, keepdims=True)
    return np.log(p + 1e-12), p


def ppo_update(pol, crit, eps_data, A, rng, log):
    S, Act, V, R, done_idx, GM = [], [], [], [], [], []
    for ep in eps_data:
        for k, (s, a, v, r, g) in enumerate(ep):
            S.append(s); Act.append(a); V.append(v); R.append(r); GM.append(g)
            done_idx.append(k == len(ep) - 1)
    GM = np.array(GM, np.float32)
    S = np.array(S, np.float32); Act = np.array(Act); V = np.array(V); R = np.array(R, np.float32)
    done = np.array(done_idx)
    n = len(Act)
    # critic values and GAE advantages, contact by contact
    vals = fwd(crit, S)[0][:, 0]
    adv = np.zeros(n, np.float32)
    last = 0.0
    for i in range(n - 1, -1, -1):
        nv = 0.0 if done[i] else vals[i + 1]
        delta = R[i] + GM[i] * nv - vals[i]
        last = delta + GM[i] * LAM * (0.0 if done[i] else last)
        adv[i] = last
    ret = adv + vals
    advn = (adv - adv.mean()) / (adv.std() + 1e-8)
    old_logp, _ = masked_logp(fwd(pol, S)[0], V)
    old_lp = old_logp[np.arange(n), Act]
    opt_p, opt_c = Adam(pol, A.lr), Adam(crit, A.lr * 3)
    clipfrac = kl = 0.0
    nb = 0
    for ep in range(A.epochs):
        perm = rng.permutation(n)
        for s in range(0, n, A.batch):
            b = perm[s:s + A.batch]
            logits, cache = fwd(pol, S[b])
            lp, pr = masked_logp(logits, V[b])
            lpa = lp[np.arange(len(b)), Act[b]]
            ratio = np.exp(lpa - old_lp[b])
            ab = advn[b]
            unclipped = ratio * ab
            clipped = np.clip(ratio, 1 - A.clip, 1 + A.clip) * ab
            use = unclipped <= clipped  # gradient flows only where the unclipped term is the minimum
            # d(-min)/d logits = -adv * ratio * (onehot - p) where unclipped is used
            coef = np.where(use, -ab * ratio, 0.0)[:, None]
            onehot = np.zeros_like(pr)
            onehot[np.arange(len(b)), Act[b]] = 1
            g = coef * (onehot - pr)
            # entropy bonus: d(-H)/d logits = p * (log p + H)
            ent = -(pr * lp).sum(1, keepdims=True)
            g += A.ent * pr * (lp + ent)
            g /= len(b)
            opt_p.step(pol, back(pol, cache, g))
            v, cc = fwd(crit, S[b])
            gv = (v[:, 0] - ret[b])[:, None] / len(b)
            opt_c.step(crit, back(crit, cc, gv))
            clipfrac += float((~use).mean())
            kl += float((old_lp[b] - lpa).mean())
            nb += 1
    newlp, newp = masked_logp(fwd(pol, S)[0], V)
    share = np.bincount(Act, minlength=N_OUT) / n
    greedy = np.bincount(np.where(((V[:, None] >> np.arange(N_OUT)) & 1).astype(bool), newp, -1).argmax(1), minlength=N_OUT) / n
    log(f'  {n} decisions in {len(eps_data)} contacts, mean reward {R.mean():.2f}, return {ret.mean():.2f}; '
        f'clip frac {clipfrac / nb:.2f}, kl {kl / nb:.4f}; sampled actions ' +
        ' '.join(f'{dqn.ACTIONS[i]} {100 * share[i]:.0f}%' for i in range(N_OUT)) + '; greedy now ' +
        ' '.join(f'{dqn.ACTIONS[i]} {100 * greedy[i]:.0f}%' for i in range(N_OUT)))
    return {'n': n, 'reward': float(R.mean()), 'share': share.tolist(), 'greedy': greedy.tolist()}


def save_pol(pol, path):
    json.dump({k: v.tolist() for k, v in pol.items()}, open(path, 'w'))


def cmd_run(A):
    work = A.work
    stp = os.path.join(work, 'ppo_state.json')
    rng = np.random.default_rng(A.seed)
    if os.path.exists(stp):
        st = json.load(open(stp))
        pol = {k: np.array(v, np.float32) for k, v in json.load(open(os.path.join(work, 'pol_%d.json' % st['it'])))
               .items()}
        crit = {k: np.array(v, np.float32) for k, v in st['crit'].items()}
    else:
        pol = mlp_init(rng, N_H, N_OUT)
        pol['b2'][0] = A.bias0  # start = the rules most of the time
        crit = mlp_init(rng, 64, 1)
        st = {'it': 0, 'hist': [], 'crit': None}
        save_pol(pol, os.path.join(work, 'pol_0.json'))
    R = dqn.Runner(work, A.jobs)
    maps = dqn.pool_maps('train')
    opps = A.opps.split(',')
    logp = os.path.join(work, 'ppo_log.md')
    log = lambda s: (print(s, flush=True), open(logp, 'a').write(s + '\n'))
    for _ in range(A.iters):
        it = st['it']
        t0 = time.time()
        prng = random.Random(A.seed * 1000 + it)
        ddir = os.path.join(work, 'data', 'it%03d' % it)
        os.makedirs(ddir, exist_ok=True)
        jobs, cands = [], set()
        for k in range(A.games):
            ints = dqn.dq_ints({k2: v for k2, v in pol.items()}, on=4, eps=0, log=1, seed=prng.randrange(1, 2 ** 30))
            cid, cw = R.cand(ints)
            cands.add(cw)
            o, m, side = prng.choice(opps), prng.choice(maps), prng.randrange(2)
            jobs.append((f'{cid}|{R.opp(o)[0]}|{R.mkey(m)}|{side}', cw, R.opp(o)[1], m, side))
        res = R.games(jobs, keep_logs=lambda j: os.path.join(ddir, j[0].replace('|', '_') + '.log'))
        for c in cands:
            if os.path.exists(c):
                os.remove(c)
        ok = [r for r in res if r.get('ok')]
        eps_data = []
        for p in glob.glob(os.path.join(ddir, '*.log')):
            for decs, trace in dqn.parse_log(p):
                eps_data += episodes_gems(decs, trace) if A.reward == 'gems' else episodes(decs, trace)
        log(f'iter {it}: {len(ok)} games in {time.time() - t0:.0f}s, won {sum(r["r"] > 0 for r in ok)} lost '
            f'{sum(r["r"] < 0 for r in ok)}, deaths/game {sum(r["dth"] for r in ok) / max(1, len(ok)):.2f}, '
            f'gems/game {sum(r["gems"] for r in ok) / max(1, len(ok)):.0f}')
        info = ppo_update(pol, crit, eps_data, A, rng, log)
        info.update({'it': it, 'won': sum(r['r'] > 0 for r in ok), 'lost': sum(r['r'] < 0 for r in ok),
                     'deaths': sum(r['dth'] for r in ok), 'games': len(ok)})
        st['hist'].append(info)
        st['it'] = it + 1
        st['crit'] = {k: v.tolist() for k, v in crit.items()}
        save_pol(pol, os.path.join(work, 'pol_%d.json' % (it + 1)))
        json.dump(st, open(stp + '.tmp', 'w'))
        os.replace(stp + '.tmp', stp)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--work', default='out/ppo')
    p.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('run')
    s.add_argument('--iters', type=int, default=10); s.add_argument('--games', type=int, default=600)
    s.add_argument('--epochs', type=int, default=4); s.add_argument('--batch', type=int, default=2048)
    s.add_argument('--lr', type=float, default=3e-4); s.add_argument('--clip', type=float, default=0.2)
    s.add_argument('--ent', type=float, default=0.01); s.add_argument('--bias0', type=float, default=3.0)
    s.add_argument('--opps', default=dqn.OPPS); s.add_argument('--seed', type=int, default=1)
    s.add_argument('--reward', choices=('shaped', 'gems'), default='shaped',
                   help="shaped: per-contact gems/hp/gold/death + team margin; gems: our team's gems per round over the whole game")
    A = p.parse_args()
    {'run': cmd_run}[A.cmd](A)


if __name__ == '__main__':
    main()
