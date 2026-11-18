#!/usr/bin/env python3
"""Deep Q-learning for the fight micro: log -> train -> embed -> evaluate (see tools/ga/DQN.md).

The bot side is dqn.h + dqn.patch, on top of the structure GA's rule list (struct.patch, ga_struct.h): where the
level-3 NEAT net acts (enemies in sight, not on spawn) a dense 25-32-7 Q-network picks one of the 7 actions
(0 = let the rules decide). Its weights live in a patchable volatile array (magic 'DQN1'), so every net is the same
wasm with bytes replaced, like the GA's candidates. All-zero weights = action 0 always = the control bot.

usage (repo root, after `cambc init --yes` and building bots/ga65a6, study27-economy, spar11, spar16):
  python3 tools/ga/dqn.py prepare                          # instrumented build (~20 s), base = study27-economy + v44 weights
  python3 tools/ga/dqn.py collect --games 800 --eps 300    # epsilon-greedy games around the rules, logs -> transitions
  python3 tools/ga/dqn.py collect --net out/dqn/net1.json --eps 150 --games 800   # next round: around the trained net
  python3 tools/ga/dqn.py train --out out/dqn/net1.json    # offline double DQN on every transition collected so far
  python3 tools/ga/dqn.py eval --net out/dqn/net1.json     # v100 maps, both sides, vs control (same wasm, net off)
  python3 tools/ga/dqn.py export --net out/dqn/net1.json --out bots/dqn1   # normal bot folder + migrant files

Everything lives under --work (default out/dqn): meta.json, template.wasm, cands/, data/*.npz, games.jsonl.
Judge a net only by `eval` (margin over the control on the same games) and then tools/gate.py, never by the loss.
"""
import argparse, glob, hashlib, io, json, math, os, random, re, shutil, struct, subprocess, sys, tempfile, time, zipfile
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import ga, sga, structure as T
from ab import load_stats

N_IN, N_H, N_OUT = len(T.FEATURES), 32, 7
HDR = 6  # on, eps per mille, log, seed, hidden units, margin x1000
DQ_LEN = HDR + N_H * N_IN + N_H + N_OUT * N_H + N_OUT
SCALE = 4096.0
MAGIC = (0x314E5144, 0x0DD5EED1)  # 'DQN1'
ACTIONS = T.ACTIONS
FEAT_SCALE = np.array([100, 10, 3, 3, 3, 3, 200, 200, 1, 1, 1, 100, 10, 50, 20, 100, 1, 1, 1, 1, 200, 1, 3, 3, 1],
                      dtype=np.float32)  # ga_struct.h ga_feat_scale
assert len(FEAT_SCALE) == N_IN
OPPS = ','.join(['bots/ga65a6', 'bots/study27-economy', 'bots/spar11', 'bots/spar16'])

# Reward, in gem equivalents (see DQN.md "Reward"): gems picked up count +1 each, gems banked are neutral (they move
# from the bag to the score), a death costs the bag plus DEATH_COST, hp is worth HP_VALUE for a full bar, gold
# GOLD_VALUE per coin (kills and assists pay gold).
DEATH_COST = 25.0
HP_VALUE = 10.0
GOLD_VALUE = 0.1
GAMMA = 0.9
CONTACT_GAP = 15  # rounds without a decision that end a contact (dqn.h dq_trace window)


# ------------------------------------------------------------------------------------------------- the genome
def dq_ints(net=None, on=1, eps=0, log=0, seed=0, margin=0):
    """The int vector patched into the wasm. net = dict of numpy arrays w1 (H x IN), b1, w2 (OUT x H), b2."""
    if net is None:
        hid = 0
        body = [0] * (DQ_LEN - HDR)
    else:
        hid = net['w1'].shape[0]
        w1 = np.zeros((N_H, N_IN)); w1[:hid] = net['w1']
        b1 = np.zeros(N_H); b1[:hid] = net['b1']
        w2 = np.zeros((N_OUT, N_H)); w2[:, :hid] = net['w2']
        b2 = np.asarray(net['b2'])
        body = [int(round(v * SCALE)) for v in np.concatenate([w1.ravel(), b1, w2.ravel(), b2])]
        body = [max(-2 ** 31 + 1, min(2 ** 31 - 1, v)) for v in body]
    return [int(on), int(eps), int(log), int(seed), int(hid), int(margin)] + body


def cid_of(ints):
    return hashlib.sha1(struct.pack('<%di' % len(ints), *ints)).hexdigest()[:10]


def load_net(path):
    d = json.load(open(path))
    return {k: np.array(d[k], dtype=np.float32) for k in ('w1', 'b1', 'w2', 'b2')}, d


def write_src(base_bot, dst, scalars, ints):
    """Structure GA source (weights = scalars, structure at the base) + dqn.patch + dqn.h + the DQN genome array."""
    T.write_src(base_bot, dst, T.to_ints(scalars, {}))
    src = os.path.join(dst, 'src')
    r = subprocess.run(['patch', '-s', '-p1', '-d', src, '-i', os.path.join(HERE, 'dqn.patch')], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit('dqn.patch does not apply: %s%s' % (r.stdout, r.stderr))
    shutil.copy(os.path.join(HERE, 'dqn.h'), src)
    vals = [MAGIC[0], MAGIC[1], DQ_LEN, 0] + list(ints)
    with open(os.path.join(src, 'params.h'), 'a') as f:
        f.write('\n// ---- deep Q-network genome (tools/ga/dqn.py): flags + weights ----\n#define DQ_HAVE_GENOME 1\n')
        f.write('volatile int dq_g[%d] = {%s};\n' % (len(vals), ', '.join(str(v) for v in vals)))
        f.write('#define DQ_G ((const volatile int*)(dq_g + 4))\n')


def find_dq(wasm):
    key = struct.pack('<4i', MAGIC[0], MAGIC[1], DQ_LEN, 0)
    i = wasm.find(key)
    if i < 0 or wasm.find(key, i + 1) >= 0:
        sys.exit('DQN genome marker not found exactly once in the wasm')
    return i + len(key)


class Runner:
    """Plays games with patched candidates; caches results by (candidate, opponent, map, side) like the GA bench."""

    def __init__(self, work, jobs, extra=()):
        self.work, self.jobs, self.extra = work, jobs, list(extra)
        self.meta = json.load(open(os.path.join(work, 'meta.json')))
        self.template = open(self.meta['wasm'], 'rb').read()
        self.offset = self.meta['offset']
        self.cand_dir = os.path.join(work, 'cands')
        os.makedirs(self.cand_dir, exist_ok=True)
        os.makedirs(os.path.join(work, 'tmp'), exist_ok=True)
        self.cache_path = os.path.join(work, 'games.jsonl')
        self.cache = {}
        if os.path.exists(self.cache_path):
            for line in open(self.cache_path):
                try:
                    d = json.loads(line)
                    self.cache[d['key']] = d
                except ValueError:
                    pass
        self.opp_cache = {}

    def cand(self, ints):
        cid = cid_of(ints)
        path = os.path.join(self.cand_dir, cid + '.wasm')
        if not os.path.exists(path):
            blob = struct.pack('<%di' % len(ints), *ints)
            b = bytearray(self.template)
            b[self.offset:self.offset + len(blob)] = blob
            open(path + '.tmp', 'wb').write(b)
            os.replace(path + '.tmp', path)
        return cid, path

    def opp(self, o):
        if o not in self.opp_cache:
            w = o if o.endswith('.wasm') else ga.wasm_of(o)
            if not os.path.exists(w):
                ga.build(o)
            self.opp_cache[o] = (ga.md5(w), w)
        return self.opp_cache[o]

    @staticmethod
    def mkey(m):
        return ga.md5(m)

    def play(self, job, keep_log=None):
        """job = (key, cand wasm, opp wasm, map, side). keep_log: path to write our side's [dq]/[dt] lines."""
        key, cw, ow, m, side = job
        a, b = (cw, ow) if side == 0 else (ow, cw)
        tmp = tempfile.mkdtemp(prefix='g', dir=os.path.join(self.work, 'tmp'))
        stats = os.path.join(tmp, 's.json')
        r = subprocess.run([ga.CLI, 'run', a, b, '--map', m, '-o', os.path.join(tmp, 'r'), '--statistics', stats, '--json'] + self.extra,
                           capture_output=True, text=True, env=ga.ENV)
        res = {'key': key, 'ok': False}
        if os.path.exists(stats):
            d = load_stats(stats)
            me, op = side, 1 - side
            won = d['outcome'] == ('teamA' if me == 0 else 'teamB')
            lost = d['outcome'] in ('teamA', 'teamB') and not won
            gems = [t['submittedGems'] for t in d['teams']]
            dth = [sum(c['deaths'] for c in d['champions'] if c['team'] == t) for t in (0, 1)]
            kil = [sum(c['kills'] for c in d['champions'] if c['team'] == t) for t in (0, 1)]
            res = {'key': key, 'ok': True, 'r': 1 if won else (-1 if lost else 0), 'round': d['round'],
                   'gm': gems[me] - gems[op], 'gems': gems[me], 'dth': dth[me], 'kil': kil[me], 'flt': d['botFaults'][me]}
            if keep_log:
                res['log_lines'] = extract_logs(tmp, 'a' if side == 0 else 'b', keep_log)
        else:
            res['log'] = (r.stdout + r.stderr)[-300:]
        shutil.rmtree(tmp, ignore_errors=True)
        return res

    def games(self, jobs, keep_logs=None):
        """jobs = list of (key, cand, opp, map, side); skips cached keys unless keep_logs (collection always plays)."""
        todo = [j for j in jobs if keep_logs or j[0] not in self.cache]
        out = []
        with ThreadPoolExecutor(self.jobs) as ex, open(self.cache_path, 'a') as f:
            futs = [ex.submit(self.play, j, keep_logs(j) if keep_logs else None) for j in todo]
            for k, fu in enumerate(futs):
                res = fu.result()
                out.append(res)
                if res.get('ok') and not keep_logs:
                    self.cache[res['key']] = res
                    f.write(json.dumps(res) + '\n')
                    f.flush()
                if (k + 1) % 100 == 0:
                    print(f'  {k + 1}/{len(todo)} games', flush=True)
        return out


def extract_logs(tmp, team, dst):
    """Our side's [dq]/[dt] lines from the replay bundle cambc wrote under tmp (team-a/b.stdout inside the zip).
    The team's champions share one stdout; every line carries the champion's name. NUL padding is dropped."""
    lines = []
    for root, _, files in os.walk(tmp):
        for fn in files:
            p = os.path.join(root, fn)
            if not zipfile.is_zipfile(p):
                continue
            with zipfile.ZipFile(p) as z:
                for n in z.namelist():
                    if n == 'team-%s.stdout' % team:
                        t = z.read(n).replace(b'\x00', b'').decode('utf-8', 'replace')
                        lines += [l.strip() for l in t.split('\n') if l.strip().startswith(('[dq]', '[dt]'))]
    with open(dst, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    return sum(l.startswith('[dq]') for l in lines)


# ------------------------------------------------------------------------------------------ logs -> transitions
def parse_log(path):
    """[dq] NAME round act greedy valid f0..f24 / [dt] NAME round alive hp mhp gems gold -> per champion
    (decisions, trace)."""
    streams = {}
    for line in open(path):
        f = line.split()
        if len(f) < 3 or f[0] not in ('[dq]', '[dt]'):
            continue
        try:
            v = [int(x) for x in f[2:]]
        except ValueError:
            continue
        st = streams.setdefault(f[1], ([], []))
        if f[0] == '[dq]' and len(v) == 4 + N_IN:
            st[0].append(v)
        elif f[0] == '[dt]' and len(v) in (6, 8):  # 8: + team scores (ours, theirs), since the PPO build
            st[1].append(v if len(v) == 8 else v + [-1, -1])
    return list(streams.values())


def transitions(decs, trace):
    """One champion's decisions [round, act, greedy, valid, f0..f24] and trace [round, alive, hp, mhp, gems, gold]
    -> (s, a, r, s2, done, valid2) rows. The reward of a decision covers the turns until the next decision of the
    same contact: bag gems picked up, hp change, gold earned, and the death penalty if the champion died."""
    tr = {t[0]: t for t in trace}
    rows = []
    decs = sorted(decs, key=lambda d: d[0])
    for i, d in enumerate(decs):
        r0 = d[0]
        nxt = decs[i + 1] if i + 1 < len(decs) and decs[i + 1][0] - r0 <= CONTACT_GAP else None
        end = nxt[0] if nxt else r0 + CONTACT_GAP
        rew, done, prev = 0.0, False, tr.get(r0)
        if prev is None:
            continue
        for rr in range(r0 + 1, end + 1):
            t = tr.get(rr)
            if t is None:
                continue
            if prev[1] and not t[1]:  # died
                rew -= DEATH_COST + prev[4]
                done = True
                break
            if t[1] and prev[1]:
                rew += max(0, t[4] - prev[4])  # gems picked up; banked gems (bag shrinks while alive) are neutral
                rew += HP_VALUE * (t[2] - prev[2]) / max(1, t[3])
                rew += GOLD_VALUE * max(0, t[5] - prev[5])
            prev = t
        if done or nxt is None:
            rows.append((d[4:], d[1], rew, d[4:], 1.0, 127))
        else:
            rows.append((d[4:], d[1], rew, nxt[4:], 0.0, nxt[3]))
    return rows


def build_dataset(log_paths):
    S, A, R, S2, D, V2, G = [], [], [], [], [], [], []
    for gi, p in enumerate(log_paths):
        for decs, trace in parse_log(p):
            for s, a, r, s2, d, v2 in transitions(decs, trace):
                S.append(s); A.append(a); R.append(r); S2.append(s2); D.append(d); V2.append(v2); G.append(gi)
    if not S:
        return None
    return {'s': np.array(S, np.float32), 'a': np.array(A, np.int64), 'r': np.array(R, np.float32),
            's2': np.array(S2, np.float32), 'd': np.array(D, np.float32), 'v2': np.array(V2, np.int64), 'g': np.array(G)}


# ---------------------------------------------------------------------------------------------- the Q network
class MLP:
    """25-H-7 ReLU net in numpy with Adam; the same arithmetic as dqn.h (inputs / ga_feat_scale)."""

    def __init__(self, hid, rng):
        self.p = {'w1': rng.normal(0, math.sqrt(2.0 / N_IN), (hid, N_IN)).astype(np.float32), 'b1': np.zeros(hid, np.float32),
                  'w2': np.zeros((N_OUT, hid), np.float32), 'b2': np.zeros(N_OUT, np.float32)}
        self.m = {k: np.zeros_like(v) for k, v in self.p.items()}
        self.v = {k: np.zeros_like(v) for k, v in self.p.items()}
        self.t = 0

    def copy(self):
        o = MLP.__new__(MLP)
        o.p = {k: v.copy() for k, v in self.p.items()}
        return o

    def forward(self, x):
        x = x / FEAT_SCALE
        h = np.maximum(0, x @ self.p['w1'].T + self.p['b1'])
        return h @ self.p['w2'].T + self.p['b2'], (x, h)

    def step(self, x, a, target, w, lr, l2=1e-4):
        q, (xs, h) = self.forward(x)
        qa = q[np.arange(len(a)), a]
        err = qa - target
        err = np.clip(err, -10, 10)  # Huber
        g = np.zeros_like(q)
        g[np.arange(len(a)), a] = w * err / len(a)
        grads = {'w2': g.T @ h + l2 * self.p['w2'], 'b2': g.sum(0)}
        gh = (g @ self.p['w2']) * (h > 0)
        grads['w1'] = gh.T @ xs + l2 * self.p['w1']
        grads['b1'] = gh.sum(0)
        self.t += 1
        for k in self.p:
            self.m[k] = 0.9 * self.m[k] + 0.1 * grads[k]
            self.v[k] = 0.999 * self.v[k] + 0.001 * grads[k] ** 2
            mh = self.m[k] / (1 - 0.9 ** self.t)
            vh = self.v[k] / (1 - 0.999 ** self.t)
            self.p[k] -= lr * mh / (np.sqrt(vh) + 1e-8)
        return float((w * err ** 2).mean())


def masked_max(q, valid):
    big = np.where((valid[:, None] >> np.arange(N_OUT)[None, :]) & 1, q, -1e9)
    return big


def train_q(data, hid=32, iters=30, steps=400, batch=512, lr=1e-3, gamma=GAMMA, onestep=False, cql=1.0, seed=0, log=print):
    """Offline double DQN (fitted Q iteration with a target net refreshed every `steps` updates).
    onestep=True: SARSA-like evaluation of the logged policy (the rules + epsilon), then act greedily = one-step
    policy improvement, the safest offline variant. cql: weight of a conservative penalty that pushes down the
    Q of actions the data rarely took (CQL-style), so the argmax does not chase unexplored actions."""
    rng = np.random.default_rng(seed)
    n = len(data['a'])
    net = MLP(hid, rng)
    # actions in the data, rarity weights so the rare actions are fitted too
    counts = np.bincount(data['a'], minlength=N_OUT).astype(np.float64)
    w_act = (counts.sum() / np.maximum(counts, 1) / N_OUT) ** 0.5
    w = w_act[data['a']].astype(np.float32)
    w /= w.mean()
    # next action actually logged (for onestep): the action of the next decision row of the same champion
    idx = np.arange(n)
    hist = []
    for it in range(iters):
        tgt_net = net.copy()
        q2, _ = tgt_net.forward(data['s2'])
        if onestep:
            nxt_a = np.minimum(idx + 1, n - 1)
            boot = q2[idx, data['a'][nxt_a]]
        else:
            qo, _ = net.forward(data['s2'])
            a2 = masked_max(qo, data['v2']).argmax(1)
            boot = q2[idx, a2]
        y = data['r'] + gamma * (1 - data['d']) * boot
        loss = 0
        for _ in range(steps):
            b = rng.integers(0, n, batch)
            loss += net.step(data['s'][b], data['a'][b], y[b], w[b], lr)
            if cql > 0:  # conservative term: lower logsumexp(Q) toward Q(data action)
                xb = data['s'][b]
                q, (xs, h) = net.forward(xb)
                mq = q.max(1, keepdims=True)
                p = np.exp(q - mq)
                p /= p.sum(1, keepdims=True)
                g = cql * p
                g[np.arange(len(b)), data['a'][b]] -= cql
                g /= len(b)
                grads = {'w2': g.T @ h, 'b2': g.sum(0)}
                gh = (g @ net.p['w2']) * (h > 0)
                grads['w1'] = gh.T @ xs
                grads['b1'] = gh.sum(0)
                for k in net.p:
                    net.p[k] -= lr * 0.5 * np.sign(grads[k]) * np.minimum(1, np.abs(grads[k]) * 100)
        q, _ = net.forward(data['s'])
        adv = q - q[:, :1]
        hist.append({'iter': it, 'loss': round(loss / steps, 3), 'mean_q0': round(float(q[:, 0].mean()), 2),
                     'greedy_share': [round(float(x), 3) for x in np.bincount(masked_max(q, np.full(n, 127)).argmax(1), minlength=N_OUT) / n]})
        if it % 5 == 4 or it == iters - 1:
            log(f"  iter {it}: loss {hist[-1]['loss']} Q(default) {hist[-1]['mean_q0']} greedy action share {hist[-1]['greedy_share']}")
    return net, hist


# ------------------------------------------------------------------------------------------------------ commands
def cmd_prepare(A):
    os.makedirs(A.work, exist_ok=True)
    bot = os.path.join(A.work, 'dqbot')
    sc = sga.load_base(A.base)
    write_src(A.base_bot, bot, sc, dq_ints(None, on=0))
    ga.build(bot)
    w = ga.wasm_of(bot)
    wb = open(w, 'rb').read()
    off = find_dq(wb)
    tmpl = os.path.join(A.work, 'template.wasm')
    shutil.copy(w, tmpl)
    json.dump({'base_bot': A.base_bot, 'base': A.base, 'scalars': sc, 'wasm': tmpl, 'offset': off, 'length': DQ_LEN},
              open(os.path.join(A.work, 'meta.json'), 'w'), indent=1)
    print(f'instrumented DQN bot built: genome {DQ_LEN} ints at byte {off} of {tmpl} (weights base {A.base})')


def pool_maps(spec):
    if spec == 'train':
        return ga.map_pool(ga.TRAIN, exclude=ga.SEALED + [ga.VALID])
    return ga.map_pool(spec.split(','))


def cmd_collect(A):
    R = Runner(A.work, A.jobs)
    net = load_net(A.net)[0] if A.net else None
    maps = pool_maps(A.maps)
    opps = A.opps.split(',')
    rng = random.Random(A.seed)
    batch = time.strftime('%m%d%H%M%S') + '_%d' % A.seed
    ddir = os.path.join(A.work, 'data', batch)
    os.makedirs(ddir, exist_ok=True)
    jobs = []
    for k in range(A.games):
        seed = rng.randrange(1, 2 ** 30)
        cid, cw = R.cand(dq_ints(net, on=1, eps=A.eps, log=1, seed=seed, margin=A.margin))
        o = rng.choice(opps)
        m = rng.choice(maps)
        side = rng.randrange(2)
        jobs.append((f'{cid}|{R.opp(o)[0]}|{R.mkey(m)}|{side}', cw, R.opp(o)[1], m, side))
    t0 = time.time()
    res = R.games(jobs, keep_logs=lambda j: os.path.join(ddir, j[0].replace('|', '_') + '.log'))
    ok = [r for r in res if r.get('ok')]
    json.dump({'net': A.net, 'eps': A.eps, 'games': len(res), 'ok': len(ok), 'opps': opps, 'maps': A.maps,
               'decisions': sum(r.get('log_lines', 0) for r in ok), 'deaths': sum(r['dth'] for r in ok),
               'wins': sum(r['r'] > 0 for r in ok), 'losses': sum(r['r'] < 0 for r in ok)},
              open(os.path.join(ddir, 'batch.json'), 'w'), indent=1)
    for c in glob.glob(os.path.join(R.cand_dir, '*.wasm')):  # one wasm per game seed: do not keep them
        if time.time() - os.path.getmtime(c) < time.time() - t0 + 5:
            os.remove(c)
    print(f'{len(ok)}/{len(res)} games in {time.time() - t0:.0f}s, {sum(r.get("log_lines", 0) for r in ok)} decisions -> {ddir}')


def load_all(work, batches=None):
    paths = sorted(glob.glob(os.path.join(work, 'data', '*', '*.log')))
    if batches:
        paths = [p for p in paths if os.path.basename(os.path.dirname(p)) in batches.split(',')]
    return build_dataset(paths), paths


def cmd_train(A):
    data, paths = load_all(A.work, A.batches)
    if data is None:
        sys.exit('no transitions: run collect first')
    n = len(data['a'])
    cnt = np.bincount(data['a'], minlength=N_OUT)
    print(f'{n} transitions from {len(paths)} game logs; actions taken: ' +
          ', '.join(f'{ACTIONS[i]} {cnt[i]}' for i in range(N_OUT)) +
          f'; deaths {int((data["r"] < -DEATH_COST + 1).sum())}; mean reward {data["r"].mean():.2f}')
    # hold out 10% of the games to check the fit generalises (a sanity check, not the verdict)
    games = np.unique(data['g'])
    rng = np.random.default_rng(A.seed)
    held = set(rng.choice(games, max(1, len(games) // 10), replace=False))
    tr = np.array([g not in held for g in data['g']])
    sub = {k: v[tr] for k, v in data.items()}
    net, hist = train_q(sub, hid=A.hid, iters=A.iters, steps=A.steps, lr=A.lr, gamma=A.gamma, onestep=A.onestep,
                        cql=A.cql, seed=A.seed)
    te = {k: v[~tr] for k, v in data.items()}
    q, _ = net.forward(te['s'])
    q2, _ = net.forward(te['s2'])
    y = te['r'] + A.gamma * (1 - te['d']) * masked_max(q2, te['v2']).max(1)
    td = float(np.abs(q[np.arange(len(te['a'])), te['a']] - y).mean())
    # how much each action is expected to gain over the rules, where it would be chosen (held-out states)
    adv = q - q[:, :1]
    greedy = masked_max(adv, np.full(len(adv), 127)).argmax(1)
    share = np.bincount(np.where(adv.max(1) > A.margin / 1000.0, greedy, 0), minlength=N_OUT) / len(greedy)
    print(f'held-out TD error {td:.2f}; greedy policy would replace the rules on {100 * (1 - share[0]):.1f}% of contact turns: ' +
          ', '.join(f'{ACTIONS[i]} {100 * share[i]:.1f}%' for i in range(1, N_OUT)))
    out = {k: v.tolist() for k, v in net.p.items()}
    out.update({'n': n, 'games': len(paths), 'args': vars(A), 'held_td': td, 'hist': hist,
                'greedy_share': share.tolist(), 'reward': {'death': DEATH_COST, 'hp': HP_VALUE, 'gold': GOLD_VALUE}})
    json.dump(out, open(A.out, 'w'))
    print('net ->', A.out)


def score_pairs(R, cand, ctl, opps, maps):
    better = worse = 0
    won2 = {cand: 0, ctl: 0}
    lost2 = {cand: 0, ctl: 0}
    per = {}
    for o in opps:
        oh = R.opp(o)[0]
        pb = pw = 0
        for m in maps:
            k = R.mkey(m)
            g = {c: [R.cache.get(f'{c}|{oh}|{k}|{s}') for s in (0, 1)] for c in (cand, ctl)}
            if not all(g[cand] + g[ctl]):
                continue
            sa = sum(x['r'] for x in g[cand])
            sb = sum(x['r'] for x in g[ctl])
            better += sa > sb
            worse += sa < sb
            pb += sa > sb
            pw += sa < sb
            for c in (cand, ctl):
                won2[c] += sum(x['r'] for x in g[c]) == 2
                lost2[c] += sum(x['r'] for x in g[c]) == -2
        per[os.path.basename(o)] = f'{pb}-{pw}'
    return better, worse, won2, lost2, per


def cmd_eval(A):
    R = Runner(A.work, A.jobs, ['--fuel', str(A.fuel)] if A.fuel else [])
    maps = pool_maps(A.maps)
    opps = A.opps.split(',')
    ctl, cw = R.cand(dq_ints(None, on=0))
    lines = []
    for spec in A.net.split(','):
        net = load_net(spec)[0] if spec != 'zero' else None
        cid, nw = R.cand(dq_ints(net, on=A.mode, eps=0, log=0, margin=A.margin))
        jobs = []
        for c, w in ((ctl, cw), (cid, nw)):
            for o in opps:
                for m in maps:
                    for s in (0, 1):
                        jobs.append((f'{c}|{R.opp(o)[0]}|{R.mkey(m)}|{s}', w, R.opp(o)[1], m, s))
        R.games(jobs)
        b, w_, won2, lost2, per = score_pairs(R, cid, ctl, opps, maps)
        res = [R.cache.get(j[0]) for j in jobs]
        dth = {c: sum(x['dth'] for x, j in zip(res, jobs) if x and j[0].startswith(c)) for c in (ctl, cid)}
        gm = {c: sum(x['gems'] for x, j in zip(res, jobs) if x and j[0].startswith(c)) for c in (ctl, cid)}
        line = (f"{spec} (mode {A.mode}, margin {A.margin}) {cid}: map-rival pairs better/worse than control {b}-{w_} p={ga.sign_p(b, w_):.3f}; "
                f"maps won both sides {won2[cid]} vs control {won2[ctl]}, lost both {lost2[cid]} vs {lost2[ctl]}; "
                f"deaths {dth[cid]} vs {dth[ctl]}; gems {gm[cid]} vs {gm[ctl]}; per rival " + ' '.join(f'{k} {v}' for k, v in per.items()))
        print(line)
        lines.append(line)
    with open(os.path.join(A.work, 'eval.txt'), 'a') as f:
        f.write(time.strftime('%Y-%m-%dT%H:%MZ ', time.gmtime()) + f'maps={A.maps} n={len(maps)} opps={A.opps}\n' + '\n'.join(lines) + '\n\n')


def cmd_export(A):
    meta = json.load(open(os.path.join(A.work, 'meta.json')))
    net, d = load_net(A.net)
    ints = dq_ints(net, on=A.mode, eps=0, log=0, margin=A.margin)
    write_src(meta['base_bot'], A.out, meta['scalars'], ints)
    cid = cid_of(ints)
    print(f'{A.out}: DQN {cid} on {meta["base_bot"]} + {meta["base"]} weights')
    if A.migrate:
        R = Runner(A.work, A.jobs)
        _, w = R.cand(ints)
        os.makedirs(A.migrate, exist_ok=True)
        shutil.copy(w, os.path.join(A.migrate, f'dqn_{cid}.wasm'))
        vt = open(os.path.join(A.work, 'eval.txt')).read() if os.path.exists(os.path.join(A.work, 'eval.txt')) else ''
        lines = [l for l in vt.split('\n') if cid in l]
        json.dump({'island': 'dqn (thread "Deep Q-learning", tools/ga/dqn.py)', 'id': cid, 'kind': 'dqn-25-32-7',
                   'scope': 'micro action while enemies are in sight (default rules / engage / kite / back off / flee / recall / farm)',
                   'base_bot': meta['base_bot'], 'base_scalars_label': meta['base'], 'scalars': meta['scalars'],
                   'template_wasm_sha256_16': hashlib.sha256(open(meta['wasm'], 'rb').read()).hexdigest()[:16],
                   'dq_ints': ints, 'mode': A.mode, 'margin': A.margin, 'train': {'transitions': d.get('n'), 'games': d.get('games'),
                   'held_td': d.get('held_td'), 'greedy_share': d.get('greedy_share')},
                   'validation': lines[-1] if lines else '', 'note': A.note,
                   'time': time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())},
                  open(os.path.join(A.migrate, f'dqn_{cid}.json'), 'w'), indent=1)
        print('migrant ->', os.path.join(A.migrate, f'dqn_{cid}.json'))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--work', default='out/dqn')
    p.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('prepare')
    s.add_argument('--base-bot', default='bots/study27-economy')
    s.add_argument('--base', default='ga65a6', help='weights under the net: a sga PRESETS id, export JSON or inline JSON')
    s = sub.add_parser('collect')
    s.add_argument('--games', type=int, default=400); s.add_argument('--eps', type=int, default=300, help='per mille')
    s.add_argument('--net', default=''); s.add_argument('--margin', type=int, default=0)
    s.add_argument('--opps', default=OPPS); s.add_argument('--maps', default='train'); s.add_argument('--seed', type=int, default=1)
    s = sub.add_parser('train')
    s.add_argument('--out', required=True); s.add_argument('--batches', default='')
    s.add_argument('--hid', type=int, default=32); s.add_argument('--iters', type=int, default=30)
    s.add_argument('--steps', type=int, default=300); s.add_argument('--lr', type=float, default=1e-3)
    s.add_argument('--gamma', type=float, default=GAMMA); s.add_argument('--onestep', action='store_true')
    s.add_argument('--cql', type=float, default=1.0); s.add_argument('--margin', type=int, default=0)
    s.add_argument('--seed', type=int, default=0)
    s = sub.add_parser('eval')
    s.add_argument('--net', required=True, help="comma-separated net JSONs ('zero' = net on, all weights 0)")
    s.add_argument('--margin', type=int, default=0); s.add_argument('--opps', default=OPPS)
    s.add_argument('--mode', type=int, default=1, help='1 Q argmax; 2/3 death value (fightval.py): back off / flee if p(die)*1000 > margin')
    s.add_argument('--maps', default=ga.VALID); s.add_argument('--fuel', type=int, default=0)
    s = sub.add_parser('export')
    s.add_argument('--net', required=True); s.add_argument('--out', required=True); s.add_argument('--margin', type=int, default=0)
    s.add_argument('--mode', type=int, default=1)
    s.add_argument('--migrate', default='', help='also write dqn_<id>.json/.wasm into this folder (the GA farm migrants)')
    s.add_argument('--note', default='')
    A = p.parse_args()
    {'prepare': cmd_prepare, 'collect': cmd_collect, 'train': cmd_train, 'eval': cmd_eval, 'export': cmd_export}[A.cmd](A)


if __name__ == '__main__':
    main()
