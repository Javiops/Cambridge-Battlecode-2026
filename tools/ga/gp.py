"""Level 2: genetic programming of the micro's two key conditions (structure.py, ga_struct.h ga_run).

A program is a tree of nested lists: ['VAR', i] (fight feature i), ['CONST', c], or [op, child, ...].
It compiles to the bot's postfix tokens: token = op | (arg << 5). The bot reads a result > 0 as yes.

  GP0 "back off from this group" replaces rule AVOID's condition
  GP1 "engage this target" replaces rule ENGAGE's condition (the bot still needs a target)

The seeds are the base bot's own conditions, so generation 0 starts from the base and every change is measured
against it (sga.py check shows the seeds play the same games as the fixed conditions).
"""
import copy, random

import structure as T

OPS = {'ADD': 3, 'SUB': 4, 'MUL': 5, 'MIN': 6, 'MAX': 7, 'LT': 8, 'AND': 9, 'OR': 10, 'NOT': 11, 'IF': 12, 'GT': 13}
ARITY = {'ADD': 2, 'SUB': 2, 'MUL': 2, 'MIN': 2, 'MAX': 2, 'LT': 2, 'GT': 2, 'AND': 2, 'OR': 2, 'NOT': 1, 'IF': 3}
OP_VAR, OP_CONST = 1, 2
F = {n: i for i, n in enumerate(T.FEATURES)}
MAX_TOKENS = T.PROG_LEN - 1
MAX_DEPTH = 8


def V(name):
    return ['VAR', F[name]]


def C(v):
    return ['CONST', int(v)]


# The base bot's conditions (main.cpp after struct.patch, rules AVOID and ENGAGE, default genome).
SEED_GP0 = ['AND', ['AND', ['NOT', V('FAV')], ['NOT', V('KILL')]],
            ['AND', ['OR', ['LT', V('HP'), C(60)], ['NOT', ['GT', V('NEAR'), C(4)]]], ['NOT', V('SPAWN')]]]
SEED_GP1 = ['OR', ['OR', V('KILL'), V('TCHAN')], ['OR', ['AND', V('REACH'), V('FAV')], V('HELP')]]


def compile_tree(t):
    out = []

    def go(n):
        if n[0] == 'VAR':
            out.append(OP_VAR | (n[1] << 5))
        elif n[0] == 'CONST':
            out.append(OP_CONST | (int(n[1]) << 5))
        else:
            for c in n[1:]:
                go(c)
            out.append(OPS[n[0]])
    go(t)
    return [len(out)] + out


def evaluate(t, feat):
    """Python reference of ga_run (tests and debugging)."""
    op = t[0]
    if op == 'VAR':
        return feat[t[1]]
    if op == 'CONST':
        return t[1]
    a = [evaluate(c, feat) for c in t[1:]]
    if op == 'NOT':
        return 0 if a[0] > 0 else 1
    if op == 'IF':
        return a[1] if a[0] > 0 else a[2]
    x, y = a
    r = {'ADD': x + y, 'SUB': x - y, 'MUL': int(x * y / 100) if x * y >= 0 else -int(-x * y / 100),
         'MIN': min(x, y), 'MAX': max(x, y), 'LT': int(x < y), 'GT': int(x > y),
         'AND': int(x > 0 and y > 0), 'OR': int(x > 0 or y > 0)}[op]
    return max(-1000000, min(1000000, r))


def size(t):
    return 1 if t[0] in ('VAR', 'CONST') else 1 + sum(size(c) for c in t[1:])


def depth(t):
    return 1 if t[0] in ('VAR', 'CONST') else 1 + max(depth(c) for c in t[1:])


def ok(t):
    return size(t) <= MAX_TOKENS and depth(t) <= MAX_DEPTH


def text(t):
    op = t[0]
    if op == 'VAR':
        return T.FEATURES[t[1]]
    if op == 'CONST':
        return str(t[1])
    a = [text(c) for c in t[1:]]
    sym = {'ADD': '+', 'SUB': '-', 'MUL': '*', 'LT': '<', 'GT': '>', 'AND': 'and', 'OR': 'or'}
    if op in sym:
        return '(%s %s %s)' % (a[0], sym[op], a[1])
    if op == 'NOT':
        return 'not ' + a[0]
    if op == 'IF':
        return '(%s if %s else %s)' % (a[1], a[0], a[2])
    return '%s(%s)' % (op.lower(), ', '.join(a))


# --------------------------------------------------------------------------------------------------- random trees
def rand_const(rng, feat=None):
    lo, hi = T.FEATURE_RANGE.get(feat, (0, 100))
    return C(rng.randint(lo, hi))


def rand_numeric_feature(rng):
    return rng.choice([n for n in T.FEATURES if n not in T.BOOL_FEATURES])


def rand_compare(rng):
    """feature < const / feature > const / feature vs feature: the building block of a readable condition."""
    f = rand_numeric_feature(rng)
    if rng.random() < 0.2:
        g = rand_numeric_feature(rng)
        return [rng.choice(['LT', 'GT']), V(f), V(g)]
    return [rng.choice(['LT', 'GT']), V(f), rand_const(rng, f)]


def rand_tree(rng, d):
    if d <= 1 or rng.random() < 0.3:
        r = rng.random()
        if r < 0.4:
            return V(rng.choice(sorted(T.BOOL_FEATURES)))
        if r < 0.9 or d <= 1:
            return rand_compare(rng) if d > 1 else V(rng.choice(T.FEATURES))
        return rand_const(rng)
    op = rng.choices(list(ARITY), weights=[1, 1, 1, 1, 1, 2, 2, 4, 4, 2, 1])[0]
    return [op] + [rand_tree(rng, d - 1) for _ in range(ARITY[op])]


# ------------------------------------------------------------------------------------------------------ operators
def nodes(t, path=()):
    yield path, t
    if t[0] not in ('VAR', 'CONST'):
        for i, c in enumerate(t[1:]):
            yield from nodes(c, path + (i + 1,))


def get(t, path):
    for i in path:
        t = t[i]
    return t


def put(t, path, sub):
    if not path:
        return copy.deepcopy(sub)
    t = copy.deepcopy(t)
    p = t
    for i in path[:-1]:
        p = p[i]
    p[path[-1]] = copy.deepcopy(sub)
    return t


def mutate(t, rng):
    for _ in range(20):
        ps = list(nodes(t))
        path, n = rng.choice(ps)
        r = rng.random()
        if r < 0.35 and any(m[0] == 'CONST' for _, m in ps):  # nudge a threshold
            path, n = rng.choice([(p, m) for p, m in ps if m[0] == 'CONST'])
            parent = get(t, path[:-1]) if path else None
            feat = None
            if parent and parent[0] in ('LT', 'GT') and parent[1][0] == 'VAR':
                feat = T.FEATURES[parent[1][1]]
            lo, hi = T.FEATURE_RANGE.get(feat, (0, 100))
            c = int(round(n[1] + rng.gauss(0, max(1.0, (hi - lo) * 0.12))))
            new = put(t, path, C(c))
        elif r < 0.5 and n[0] in ARITY:  # swap the operator for one of the same arity
            same = [o for o in ARITY if ARITY[o] == ARITY[n[0]] and o != n[0]]
            if not same:
                continue
            new = put(t, path, [rng.choice(same)] + n[1:])
        elif r < 0.6 and n[0] in ARITY:  # hoist: a node becomes one of its children (shrinks)
            new = put(t, path, rng.choice(n[1:]))
        elif r < 0.75:  # wrap: AND / OR with a new comparison, or NOT
            w = rng.random()
            if w < 0.4:
                sub = ['AND', n, rand_compare(rng)]
            elif w < 0.8:
                sub = ['OR', n, rand_compare(rng)]
            else:
                sub = ['NOT', n]
            new = put(t, path, sub)
        else:  # replace a subtree with a fresh one
            new = put(t, path, rand_tree(rng, rng.randint(1, 3)))
        if ok(new) and new != t:
            return new
    return t


def crossover(a, b, rng):
    for _ in range(20):
        pa, _ = rng.choice(list(nodes(a)))
        _, sb = rng.choice(list(nodes(b)))
        new = put(a, pa, sb)
        if ok(new):
            return new
    return copy.deepcopy(a)
