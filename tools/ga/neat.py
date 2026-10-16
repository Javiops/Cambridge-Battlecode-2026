"""Level 3: NEAT, a network that evolves its own shape (structure.py, ga_struct.h ga_nn_act).

Inputs are the fight features (scaled in the bot), outputs the 7 actions of structure.ACTIONS; the bot takes the
argmax while enemies are in sight. Output 0 "default" hands the turn back to the rule list, so the seed network
(no connections, bias 1 on "default") plays exactly like the base bot and evolution only has to find the
situations where another action is better, instead of rediscovering the whole micro from zero.

Genome (JSON): {'nodes': {id: {'bias': b, 'depth': d}}, 'conns': {innov: [src, dst, weight, enabled]}}.
Inputs are ids 0..NF-1 (depth 0), outputs ids OUT0..OUT0+6 (depth 1), hidden nodes get depths in between, and a
connection always goes to a deeper node, so the net is feed-forward and compiles to the bot's ordered layout.
Innovation numbers are shared by the whole run (Innov, kept in the GA state).
"""
import copy, random

import structure as T

NF = len(T.FEATURES)
OUT0 = 1000
OUTS = [OUT0 + k for k in range(T.NN_OUT)]
MAX_HIDDEN = T.NN_NODES - T.NN_OUT


class Innov:
    def __init__(self, d=None):
        d = d or {}
        self.conn = {tuple(map(int, k.split(','))): v for k, v in d.get('conn', {}).items()}
        self.split = {int(k): v for k, v in d.get('split', {}).items()}
        self.next = d.get('next', 1)
        self.next_node = d.get('next_node', 2000)

    def dump(self):
        return {'conn': {'%d,%d' % k: v for k, v in self.conn.items()}, 'split': {str(k): v for k, v in self.split.items()},
                'next': self.next, 'next_node': self.next_node}

    def of_conn(self, src, dst):
        if (src, dst) not in self.conn:
            self.conn[(src, dst)] = self.next
            self.next += 1
        return self.conn[(src, dst)]

    def of_split(self, innov):
        if innov not in self.split:
            self.split[innov] = self.next_node
            self.next_node += 1
        return self.split[innov]


def seed():
    return {'nodes': {str(o): {'bias': 1.0 if o == OUT0 else 0.0, 'depth': 1.0} for o in OUTS}, 'conns': {}}


def depth_of(g, nid):
    return 0.0 if nid < NF else g['nodes'][str(nid)]['depth']


def compile_net(g):
    """-> the bot's int block (structure.NN_LEN ints)."""
    hidden = sorted((int(k) for k in g['nodes'] if int(k) not in OUTS), key=lambda n: (depth_of(g, n), n))
    order = hidden + OUTS
    index = {n: NF + i for i, n in enumerate(order)}
    index.update({i: i for i in range(NF)})
    bias = [int(round(g['nodes'][str(n)]['bias'] * 1000)) for n in order]
    conns = []
    for innov, (src, dst, w, on) in g['conns'].items():
        if on and src in index and dst in index and index[src] < index[dst]:
            conns.append((index[dst], index[src], int(round(max(-30.0, min(30.0, w)) * 1000))))
    conns.sort()
    conns = conns[:T.NN_CONN]
    block = [len(order), len(conns)] + bias + [0] * (T.NN_NODES - len(bias))
    for dst, src, w in conns:
        block += [src, dst, w]
    return block + [0] * (T.NN_LEN - len(block))


def describe(g):
    on = [c for c in g['conns'].values() if c[3]]
    hidden = [k for k in g['nodes'] if int(k) not in OUTS]
    acts = sorted({T.ACTIONS[c[1] - OUT0] for c in on if c[1] in OUTS})
    return f'{len(hidden)} hidden, {len(on)} links, outputs used: {", ".join(acts) or "none"}'


# ------------------------------------------------------------------------------------------------------ operators
def mutate(g, rng, inn, p_conn=0.35, p_node=0.12):
    g = copy.deepcopy(g)
    for c in g['conns'].values():
        if rng.random() < 0.8:
            c[2] = rng.gauss(0, 1.0) if rng.random() < 0.1 else c[2] + rng.gauss(0, 0.4)
    for n in g['nodes'].values():
        if rng.random() < 0.3:
            n['bias'] += rng.gauss(0, 0.25)
    if rng.random() < p_conn:
        add_rule(g, rng, inn) if rng.random() < 0.3 else add_conn(g, rng, inn)
    if rng.random() < p_node:
        add_node(g, rng, inn)
    if g['conns'] and rng.random() < 0.05:
        c = g['conns'][rng.choice(list(g['conns']))]
        c[3] = not c[3]
    return g


def add_conn(g, rng, inn, w=None):
    srcs = list(range(NF)) + [int(k) for k in g['nodes'] if int(k) not in OUTS]
    dsts = [int(k) for k in g['nodes']]
    for _ in range(20):
        s, d = rng.choice(srcs), rng.choice(dsts)
        if depth_of(g, s) >= depth_of(g, d):
            continue
        k = str(inn.of_conn(s, d))
        if k in g['conns']:
            continue
        g['conns'][k] = [s, d, rng.gauss(0, 1.5) if w is None else w, True]
        return True
    return False


# input scales of ga_struct.h ga_feat_scale (input = feature / scale)
SCALE = [100, 10, 3, 3, 3, 3, 200, 200, 1, 1, 1, 100, 10, 50, 20, 100, 1, 1, 1, 1, 200, 1, 3, 3, 1]
assert len(SCALE) == NF


def add_rule(g, rng, inn, w=4.0):
    """A link that makes one action beat 'default' on one side of a threshold: "if feature > t (or < t): action".
    Plain random links almost never beat the default bias, so a population of them plays the seed's games."""
    act = rng.randrange(1, T.NN_OUT)
    f = rng.randrange(NF)
    name = T.FEATURES[f]
    lo, hi = T.FEATURE_RANGE.get(name, (0, 1))
    t = (0.5 if name in T.BOOL_FEATURES else rng.uniform(lo, hi)) / SCALE[f]
    sign = rng.choice([-1.0, 1.0])
    k = str(inn.of_conn(f, OUT0 + act))
    g['conns'][k] = [f, OUT0 + act, sign * w, True]
    # output act = bias + sign*w*x > 1 (the default's bias) exactly when sign*(x - t) > 0
    g['nodes'][str(OUT0 + act)]['bias'] = 1.0 - sign * w * t
    return True


def add_node(g, rng, inn):
    hidden = [k for k in g['nodes'] if int(k) not in OUTS]
    live = [k for k, c in g['conns'].items() if c[3]]
    if len(hidden) >= MAX_HIDDEN or not live:
        return False
    k = rng.choice(live)
    s, d, w, _ = g['conns'][k]
    nid = inn.of_split(int(k))
    if str(nid) in g['nodes']:
        return False
    g['conns'][k][3] = False
    g['nodes'][str(nid)] = {'bias': 0.0, 'depth': (depth_of(g, s) + depth_of(g, d)) / 2.0}
    g['conns'][str(inn.of_conn(s, nid))] = [s, nid, 1.0, True]
    g['conns'][str(inn.of_conn(nid, d))] = [nid, d, w, True]
    return True


def crossover(fit, other, rng):
    """`fit` is the fitter parent: its disjoint/excess genes are kept, matching genes come from either."""
    child = copy.deepcopy(fit)
    for k, c in child['conns'].items():
        if k in other['conns'] and rng.random() < 0.5:
            child['conns'][k] = list(other['conns'][k])
    for k, n in child['nodes'].items():
        if k in other['nodes'] and rng.random() < 0.5:
            child['nodes'][k] = dict(other['nodes'][k])
    # a connection may point at a node only the other parent has: drop it
    child['conns'] = {k: c for k, c in child['conns'].items()
                      if (c[0] < NF or str(c[0]) in child['nodes']) and str(c[1]) in child['nodes']}
    return child


def distance(a, b, c1=1.0, c3=0.4):
    ka, kb = set(a['conns']), set(b['conns'])
    n = max(1, len(ka), len(kb))
    disjoint = len(ka ^ kb)
    common = ka & kb
    w = sum(abs(a['conns'][k][2] - b['conns'][k][2]) for k in common) / max(1, len(common))
    return c1 * disjoint / n + c3 * w


def speciate(ids, genos, reps, threshold):
    """Assign ids to species by distance to each species' representative. -> {species: [ids]}, new reps."""
    species = {s: [] for s in reps}
    for i in ids:
        for s, r in reps.items():
            if distance(genos[i], r) < threshold:
                species[s].append(i)
                break
        else:
            s = str(max([int(x) for x in reps] + [0]) + 1)
            reps[s] = genos[i]
            species[s] = [i]
    species = {s: m for s, m in species.items() if m}
    return species, {s: genos[m[0]] for s, m in species.items()}
