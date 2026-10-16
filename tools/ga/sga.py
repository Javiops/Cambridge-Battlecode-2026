#!/usr/bin/env python3
"""Structure evolution of the micro, levels 1-3 (structure.py, gp.py, neat.py, ga_struct.h, struct.patch).

  level 1  rules on/off, rule order and the existing fight switches as genes (weights optional)
  level 2  genetic programming of the two key conditions: back off (GP0) and engage (GP1)
  level 3  NEAT network choosing the action while enemies are in sight (or deferring to the rules)

usage (repo root, after `cambc init --yes`):
  python3 tools/ga/sga.py prepare                                   # one instrumented build (~15 s)
  python3 tools/ga/sga.py check --level 2                           # seed = control? (identical games, unlimited fuel)
  python3 tools/ga/sga.py run --level 1 --gens 30                   # resumes from out/sga/L1/state.json
  python3 tools/ga/sga.py run --level 2 --base out/sga/L1/best.json # programs on top of a level-1 genome
  python3 tools/ga/sga.py validate --level 1 --top 3                # v100 maps never trained on, sign test vs control
  python3 tools/ga/sga.py export --level 1 --id ID --out bots/NAME  # normal bot folder + NAME.json genome

It reuses ga.py's machinery (map pools, the cached game bench, fitness = margin over the control on the same games,
shrunk mean over generations) and its rule: always compare with the control (the base genome in the same wasm),
never with the base build, because any code change moves ~18% of games through fuel chaos.
"""
import argparse, copy, json, math, os, random, shutil, struct, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import ga, gp, neat, structure as T
import genome as G
from ab import load_stats

GA_GENOMES = '/mnt/project-files/analysis/ga-micro-2026-10-16/genomes'
# v44 (online since 16 Oct 10:46) = the weight GA's genome 65a6d152b6 = /mnt/project-files/bot/mybot_ga65a6.zip,
# unzipped into bots/ga65a6 (untracked). Rivals: v44, the previous online bot, the caster panel's two strongest,
# one earlier weight-GA genome.
OPPS = ','.join(['bots/ga65a6', 'bots/study27-economy', 'bots/spar11', 'bots/spar16'] +
                [os.path.join(GA_GENOMES, w) for w in ('opp_9872f93cac.wasm',)
                 if os.path.exists(os.path.join(GA_GENOMES, w))])
# the two best weight genomes of the weight GA (thread "Algoritmo genético para la micro", v100 validation 09:50)
PRESETS = {
    # v44 online (P_MONO stays on here: the contest fix, which v44 lacks, only changes the contest map)
    'ga65a6': {"P_FLEE_PCT": 29, "P_UNI_FLEE": 44, "P_RECALL_PCT": 54, "P_RECALL_NEAR": 7, "P_BAIL_PCT": 12,
               "P_AVOID_DIST": 4, "P_GA_AVOID_HP": 60, "P_ENGAGE2": 74, "P_GA_FAV": 83, "P_GA_KILL_X": 5, "P_LOWHP": 50,
               "P_GA_SPAWN_HEAL": 87, "P_FRONT_ZONE": 3, "P_FRONT_OUT": 145, "P_KITE_ZONE": 4, "P_KITE_OUT": 2,
               "P_GA_KITE_HP": 128, "P_VOLLEY": 43, "P_CHASE_GEMS": 144, "P_DANGER": 4, "P_DANGER_T": 45,
               "P_DANGER_R": 5},
    '9872f93cac': {"P_FLEE_PCT": 29, "P_RECALL_NEAR": 4, "P_BAIL_PCT": 11, "P_ENGAGE2": 72, "P_GA_FAV": 89,
                   "P_VOLLEY": 52, "P_CHASE_GEMS": 149, "P_DANGER": 4, "P_DANGER_R": 5},
    '78880781f7': {"P_FLEE_PCT": 29, "P_UNI_FLEE": 43, "P_RECALL_PCT": 54, "P_RECALL_NEAR": 6, "P_BAIL_PCT": 7,
                   "P_ENGAGE2": 81, "P_GA_FAV": 73, "P_GA_KILL_X": 7, "P_GA_SPAWN_HEAL": 88, "P_FRONT_OUT": 170,
                   "P_KITE_ZONE": 5, "P_KITE_OUT": 3, "P_GA_KITE_HP": 140, "P_VOLLEY": 42, "P_CHASE_GEMS": 187,
                   "P_DANGER": 4, "P_DANGER_T": 46, "P_DANGER_R": 5},
}


# ------------------------------------------------------------------------------------------------------- bench
class Bench(ga.Bench):
    """ga.Bench with the structure template (full int vector per candidate) and cambc 2.2 statistics."""

    def __init__(self, work, jobs, meta_dir, extra=()):
        self.work, self.jobs, self.extra = work, jobs, list(extra)
        os.makedirs(work, exist_ok=True)
        self.meta = json.load(open(os.path.join(meta_dir, 'meta.json')))
        self.template = open(self.meta['wasm'], 'rb').read()
        self.offset = self.meta['offset']
        if self.meta['length'] != T.LENGTH:
            sys.exit('the instrumented wasm is from another genome layout: run `sga.py prepare` again')
        self.cand_dir = os.path.join(meta_dir, 'cands')
        os.makedirs(self.cand_dir, exist_ok=True)
        self.cache_path = os.path.join(work, 'games.jsonl')
        self.cache = {}
        if os.path.exists(self.cache_path):
            for line in open(self.cache_path):
                try:
                    d = json.loads(line)
                    self.cache[d['key']] = d
                except ValueError:
                    pass
        self.opp_wasm, self.map_md5 = {}, {}

    def cand_wasm(self, ints):
        cid = T.cid_of(ints)
        path = os.path.join(self.cand_dir, cid + '.wasm')
        if not os.path.exists(path):
            blob = struct.pack('<%di' % len(ints), *ints)
            b = bytearray(self.template)
            b[self.offset:self.offset + len(blob)] = blob
            with open(path + '.tmp', 'wb') as f:
                f.write(b)
            os.replace(path + '.tmp', path)
        return cid, path

    def play(self, job):
        key, a, b, m, side = job
        tmp = tempfile.mkdtemp(prefix='g', dir=os.path.join(self.work, 'tmp'))
        stats = os.path.join(tmp, 's.json')
        r = subprocess.run([ga.CLI, 'run', a, b, '--map', m, '-o', tmp, '--statistics', stats, '--json'] + self.extra,
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
                   'gm': gems[me] - gems[op], 'gems': gems[me], 'dth': dth[me], 'kil': kil[me],
                   'flt': d['botFaults'][me]}
        else:
            res['log'] = (r.stdout + r.stderr)[-300:]
        shutil.rmtree(tmp, ignore_errors=True)
        return res


# ------------------------------------------------------------------------------------------------ representations
def load_base(spec):
    """--base: '' (the base bot), a PRESETS id, a JSON file written by `export` (its scalars), or inline JSON."""
    sc = T.default_scalars()
    if not spec:
        return sc
    if spec in PRESETS:
        sc.update(PRESETS[spec])
    elif os.path.exists(spec):
        sc.update(json.load(open(spec))['scalars'])
    else:
        sc.update(json.loads(spec))
    return sc


class Level1:
    """Switches, rule on/off and rule order (random keys); optionally the weights too. Genotype = dict of genes."""
    level = 1

    def __init__(self, A):
        self.base = load_base(A.base)
        self.genes = list(T.L1_GENES) + (list(G.NAMES) if A.evolve_weights else [])
        self.sigma = A.sigma
        self.init = [p for p in A.init.split(',') if p]

    def control(self):
        return {k: self.base[k] for k in self.genes}

    def ints(self, geno):
        sc = dict(self.base)
        sc.update(geno)
        return T.to_ints(sc, {})

    def mutate(self, geno, rng, rate=None):
        g = dict(geno)
        p = rate if rate is not None else 2.0 / len(self.genes)
        for k in self.genes:
            if rng.random() >= p:
                continue
            d, lo, hi, kind = T.spec(k)
            if kind == 'bool':
                g[k] = 1 - g[k] if hi == 1 else rng.randint(lo, hi)
            elif kind == 'order':
                g[k] = int(min(hi, max(lo, round(g[k] + rng.gauss(0, 18)))))
            else:
                g[k] = int(min(hi, max(lo, round(g[k] + rng.gauss(0, self.sigma * (hi - lo) + 0.5)))))
        return g

    def cross(self, a, b, rng):
        return {k: (a if rng.random() < 0.5 else b)[k] for k in self.genes}

    def initial(self, n, rng):
        c = self.control()
        out = []
        for path in self.init:  # structure of earlier winners (export JSONs) on top of this base
            sc = json.load(open(path))['scalars']
            out.append({k: sc[k] if k in T.L1_GENES else c[k] for k in self.genes})
        return out + [self.mutate(c, rng, 3.0 / len(self.genes)) for _ in range(n - len(out))]

    def describe(self, geno):
        sc = dict(self.base)
        sc.update(geno)
        d = T.describe_scalars(sc)
        b = T.describe_scalars(self.base)
        return {k: v for k, v in d.items() if b.get(k) != v}

    def next_pop(self, st, ranked, n, rng):
        return default_next_pop(self, st, ranked, n, rng)


class Level2:
    """Two programs (GP0 back off, GP1 engage) on top of a fixed level-1 genome. Genotype = {'gp0', 'gp1', 'on'}."""
    level = 2

    def __init__(self, A):
        self.base = load_base(A.base)
        self.which = [int(c) for c in A.programs.split(',')]

    def control(self):
        return {'gp0': gp.SEED_GP0, 'gp1': gp.SEED_GP1, 'on': [0, 0]}

    def ints(self, geno):
        sc = dict(self.base)
        sc['P_GP0_ON'], sc['P_GP1_ON'] = geno['on']
        blocks = {'GA_GP0': gp.compile_tree(geno['gp0']), 'GA_GP1': gp.compile_tree(geno['gp1'])}
        return T.to_ints(sc, blocks)

    def seed(self):
        return {'gp0': gp.SEED_GP0, 'gp1': gp.SEED_GP1, 'on': [1 if 0 in self.which else 0, 1 if 1 in self.which else 0]}

    def mutate(self, geno, rng):
        g = copy.deepcopy(geno)
        k = rng.choice(self.which)
        key = 'gp%d' % k
        for _ in range(1 + (rng.random() < 0.3)):
            g[key] = gp.mutate(g[key], rng)
        return g

    def cross(self, a, b, rng):
        g = copy.deepcopy(a)
        k = rng.choice(self.which)
        key = 'gp%d' % k
        g[key] = gp.crossover(a[key], b[key], rng)
        return g

    def initial(self, n, rng):
        s = self.seed()
        return [s] + [self.mutate(s, rng) for _ in range(n - 1)]

    def describe(self, geno):
        return {'gp%d' % k: gp.text(geno['gp%d' % k]) for k in self.which
                if geno['gp%d' % k] != (gp.SEED_GP0, gp.SEED_GP1)[k]} or {'seed': 'base conditions'}

    def next_pop(self, st, ranked, n, rng):
        return default_next_pop(self, st, ranked, n, rng)


class Level3:
    """NEAT on top of a fixed level-1 genome. Genotype = neat genome dict. Speciated reproduction."""
    level = 3

    def __init__(self, A):
        self.base = load_base(A.base)
        self.inn = neat.Innov()

    def control(self):
        return {'off': True, **neat.seed()}

    def ints(self, geno):
        sc = dict(self.base)
        sc['P_NN_ON'] = 0 if geno.get('off') else 1
        return T.to_ints(sc, {'GA_NN': neat.compile_net(geno)})

    def mutate(self, geno, rng):
        return neat.mutate(geno, rng, self.inn)

    def initial(self, n, rng):
        out = [neat.seed()]
        while len(out) < n:  # the seed plus one threshold rule into a non-default action each
            g = neat.seed()
            neat.add_rule(g, rng, self.inn)
            out.append(g)
        return out

    def describe(self, geno):
        return {'net': neat.describe(geno)}

    def next_pop(self, st, ranked, n, rng):
        """NEAT: species by distance, offspring per species by its mean shrunk score, best of each species kept."""
        inds = st['inds']
        genos = {i: inds[i]['geno'] for i in ranked}
        reps = st.setdefault('species_reps', {})
        thr = st.setdefault('species_thr', 1.5)
        species, reps = neat.speciate(ranked[:2 * n], genos, reps, thr)
        st['species_reps'] = reps
        st['species_thr'] = max(0.3, thr * (0.9 if len(species) < 3 else 1.1 if len(species) > 5 else 1.0))
        score = {i: ga.shrunk(inds[i]) for i in ranked}
        means = {s: sum(score[i] for i in m) / len(m) for s, m in species.items()}
        lo = min(means.values())
        weight = {s: means[s] - lo + 0.02 for s in species}
        tot = sum(weight.values())
        new = []
        for s, m in sorted(species.items(), key=lambda kv: -means[kv[0]]):
            m = sorted(m, key=lambda i: -score[i])
            if m[0] not in new:
                new.append(m[0])
        quota = {s: max(1, int(round((n - 1) * weight[s] / tot))) for s in species}
        for s, m in species.items():
            m = sorted(m, key=lambda i: -score[i])[:max(2, (len(m) + 1) // 2)]
            for _ in range(quota[s]):
                if len(new) >= n - 1:
                    break
                a = rng.choice(m)
                if len(m) > 1 and rng.random() < 0.6:
                    b = rng.choice(m)
                    fa, fb = (a, b) if score[a] >= score[b] else (b, a)
                    child = neat.crossover(genos[fa], genos[fb], rng)
                else:
                    child = copy.deepcopy(genos[a])
                child = self.mutate(child, rng)
                new.append(add_ind(self, st, child))
        while len(new) < n - 1:
            new.append(add_ind(self, st, self.mutate(genos[rng.choice(ranked[:4])], rng)))
        return new[:n - 1]


REPS = {1: Level1, 2: Level2, 3: Level3}


def add_ind(rep, st, geno, born=None):
    cid = T.cid_of(rep.ints(geno))
    if cid not in st['inds']:
        st['inds'][cid] = {'geno': geno, 'deltas': [], 'born': st['gen'] + 1 if born is None else born}
    return cid


def default_next_pop(rep, st, ranked, n, rng, elite=4):
    inds = st['inds']
    elites = ranked[:elite]
    parents = ranked[:max(elite, n // 2)]

    def tour():
        c = rng.sample(parents, min(3, len(parents)))
        return max(c, key=lambda i: ga.shrunk(inds[i]))
    new = list(elites)
    tries = 0
    while len(new) < n - 1 and tries < 1000:
        tries += 1
        a = inds[tour()]['geno']
        g = rep.cross(a, inds[tour()]['geno'], rng) if rng.random() < 0.6 else copy.deepcopy(a)
        g = rep.mutate(g, rng)
        cid = add_ind(rep, st, g)
        if cid in new or cid == st['base']:
            continue
        new.append(cid)
    return new


# ------------------------------------------------------------------------------------------------------ commands
def work_of(A):
    return os.path.join(A.work, 'L%d' % A.level)


def cmd_prepare(A):
    os.makedirs(A.work, exist_ok=True)
    bot = os.path.join(A.work, 'gabot')
    T.write_src(A.base_bot, bot, T.to_ints(T.default_scalars(), {}))
    ga.build(bot)
    w = ga.wasm_of(bot)
    off = T.find_genome(open(w, 'rb').read())
    tmpl = os.path.join(A.work, 'template.wasm')
    shutil.copy(w, tmpl)
    json.dump({'base': A.base_bot, 'wasm': tmpl, 'offset': off, 'length': T.LENGTH, 'scalars': T.SCALARS},
              open(os.path.join(A.work, 'meta.json'), 'w'), indent=1)
    print(f'instrumented bot built, genome ({T.LENGTH} ints, {len(T.SCALARS)} scalars) at byte {off} of {tmpl}')


def cmd_check(A):
    """The level's seed vs its control, and the control vs the base build: with --fuel 10000000 (default here)
    every game must be identical; with normal fuel a minority differs (fuel chaos)."""
    rep = REPS[A.level](A)
    extra = ['--fuel', str(A.fuel)] if A.fuel else []
    B = Bench(os.path.join(work_of(A), 'check%s' % ('_fuel' if A.fuel else '')), A.jobs, A.work, extra)
    maps = ga.map_pool(['maps/*.map26a'])[:A.n]
    opps = A.opps.split(',')
    ctl = B.cand_wasm(rep.ints(rep.control()))
    seed = rep.seed() if hasattr(rep, 'seed') else (neat.seed() if A.level == 3 else rep.control())
    sd = B.cand_wasm(rep.ints(seed))
    base = B.meta['base']
    if not os.path.exists(ga.wasm_of(base)):
        ga.build(base)
    bw = ga.wasm_of(base)
    bh = ga.md5(bw)
    B.games([ctl, sd, (bh, bw)], opps, maps)
    for name, cid in (('seed', sd[0]), ('base build', bh)):
        same = diff = 0
        for ob in opps:
            oh = B.opp(ob)[0]
            for m in maps:
                for s in (0, 1):
                    x = B.cache[f'{ctl[0]}|{oh}|{B.mkey(m)}|{s}']
                    y = B.cache[f'{cid}|{oh}|{B.mkey(m)}|{s}']
                    if (x['r'], x['round'], x['gm']) == (y['r'], y['round'], y['gm']):
                        same += 1
                    else:
                        diff += 1
        print(f'level {A.level} control {ctl[0]} vs {name} {cid}: {same} identical games, {diff} different'
              f'{" (unlimited fuel)" if A.fuel else ""}')


def cmd_run(A):
    rep = REPS[A.level](A)
    work = work_of(A)
    B = Bench(work, A.jobs, A.work)
    opps = A.opps.split(',')
    pool = ga.map_pool(ga.TRAIN, exclude=ga.SEALED + [ga.VALID])
    statep = os.path.join(work, 'state.json')
    st = json.load(open(statep)) if os.path.exists(statep) else None
    if st is None:
        rng = random.Random(A.seed)
        st = {'level': A.level, 'gen': 0, 'inds': {}, 'pop': [], 'history': [], 'seed': A.seed, 'opps': opps,
              'base_scalars': rep.base, 'pool': len(pool)}
        st['base'] = add_ind(rep, st, rep.control(), born=0)
        for g in rep.initial(A.pop - 1, rng):
            cid = add_ind(rep, st, g, born=0)
            if cid not in st['pop'] and cid != st['base']:
                st['pop'].append(cid)
    if A.level == 3 and 'innov' in st:
        rep.inn = neat.Innov(st['innov'])
    logp = os.path.join(work, 'log.md')
    if not os.path.exists(logp):
        open(logp, 'w').write(f'level {A.level}, opponents: {", ".join(os.path.basename(o) for o in opps)}\n\n'
                              '| gen | maps | games | min | control fit | mean delta | best new (delta) | '
                              'best overall (shrunk, n) | best overall genome |\n|---|---|---|---|---|---|---|---|---|\n')
    for _ in range(A.gens):
        t0 = time.time()
        gen = st['gen']
        rng = random.Random(A.seed * 1000 + gen)
        maps = rng.sample(pool, A.maps)
        bid = st['base']
        ids = [bid] + st['pop']
        cands = [B.cand_wasm(rep.ints(st['inds'][i]['geno'])) for i in ids]
        n0 = len(B.cache)
        B.games(cands, opps, maps)
        played = len(B.cache) - n0
        fits = {i: B.score(i, opps, maps) for i in ids}
        cfit = fits[bid][0]
        for i in st['pop']:
            st['inds'][i]['deltas'].append(fits[i][0] - cfit)
            flt = sum(B.cache.get(f'{i}|{B.opp(o)[0]}|{B.mkey(m)}|{s}', {}).get('flt', 0) for o in opps for m in maps for s in (0, 1))
            if flt:
                st['inds'][i]['faults'] = st['inds'][i].get('faults', 0) + flt
        evald = [i for i, d in st['inds'].items() if d['deltas'] and i != bid and not d.get('faults')]
        ranked = sorted(evald, key=lambda i: ga.shrunk(st['inds'][i]), reverse=True)
        best_new = max(st['pop'], key=lambda i: st['inds'][i]['deltas'][-1])
        top = ranked[0]
        bt = st['inds'][top]
        h = {'gen': gen, 'maps': [os.path.basename(m) for m in maps], 'games': played, 'secs': round(time.time() - t0),
             'control': round(cfit, 4), 'best_new': best_new, 'best_new_delta': round(st['inds'][best_new]['deltas'][-1], 4),
             'top': top, 'top_shrunk': round(ga.shrunk(bt), 4), 'top_n': len(bt['deltas']),
             'mean_delta': round(sum(st['inds'][i]['deltas'][-1] for i in st['pop']) / len(st['pop']), 4),
             'control_per': {os.path.basename(o): round(v['fit'], 3) for o, v in fits[bid][1].items()}}
        st['history'].append(h)
        st['pop'] = rep.next_pop(st, ranked, A.pop, rng)
        st['gen'] = gen + 1
        if A.level == 3:
            st['innov'] = rep.inn.dump()
        json.dump(st, open(statep + '.tmp', 'w'))
        os.replace(statep + '.tmp', statep)
        with open(logp, 'a') as f:
            f.write(f"| {gen} | {len(maps)} | {played} | {h['secs'] / 60:.1f} | {cfit:+.3f} | {h['mean_delta']:+.3f} | "
                    f"{best_new} ({h['best_new_delta']:+.3f}) | {top} ({h['top_shrunk']:+.3f}, {h['top_n']}) | "
                    f"{json.dumps(rep.describe(bt['geno']))} |\n")
        print(f"L{A.level} gen {gen}: {played} games {h['secs']}s control {cfit:+.3f} mean delta {h['mean_delta']:+.3f} "
              f"best new {h['best_new_delta']:+.3f} top {top} {h['top_shrunk']:+.3f} n={h['top_n']}", flush=True)


def cmd_validate(A):
    rep = REPS[A.level](A)
    work = work_of(A)
    st = json.load(open(os.path.join(work, 'state.json')))
    B = Bench(work, A.jobs, A.work)
    opps = A.opps.split(',')
    maps = ga.map_pool([A.maps])
    if A.ids:
        ids = A.ids.split(',')
    else:
        evald = [i for i, d in st['inds'].items() if len(d['deltas']) >= A.min_n and i != st['base'] and not d.get('faults')]
        ids = sorted(evald, key=lambda i: ga.shrunk(st['inds'][i]), reverse=True)[:A.top]
    bid = st['base']
    B.games([B.cand_wasm(rep.ints(st['inds'][i]['geno'])) for i in [bid] + ids], opps, maps)
    out = [f'level {A.level} validation on {len(maps)} maps ({A.maps}), both sides, vs '
           f'{", ".join(os.path.basename(o) for o in opps)}']
    cf, cper = B.score(bid, opps, maps)
    out.append(f"control {bid}: fit {cf:+.3f} " + ' '.join(f"{os.path.basename(o)} {v['won2']}-{v['lost2']}" for o, v in cper.items()))
    for i in ids:
        f, per = B.score(i, opps, maps)
        better = worse = 0
        for ob in opps:
            oh = B.opp(ob)[0]
            for m in maps:
                k = B.mkey(m)
                ga_ = [B.cache.get(f'{i}|{oh}|{k}|{s}') for s in (0, 1)]
                gb_ = [B.cache.get(f'{bid}|{oh}|{k}|{s}') for s in (0, 1)]
                if not all(ga_ + gb_):
                    continue
                a = sum(x['r'] for x in ga_)
                b = sum(x['r'] for x in gb_)
                better += a > b
                worse += a < b
        out.append(f"{i}: fit {f:+.3f} (delta {f - cf:+.3f}) " + ' '.join(
            f"{os.path.basename(o)} {v['won2']}-{v['lost2']} d{v['dth']:.1f}" for o, v in per.items()) +
            f" | pairs better/worse than control {better}-{worse} p={ga.sign_p(better, worse):.3f} | "
            f"{json.dumps(rep.describe(st['inds'][i]['geno']))}")
    txt = '\n'.join(out)
    print(txt)
    open(os.path.join(work, 'validate.txt'), 'a').write(txt + '\n\n')


def cmd_export(A):
    """A normal bot folder holding the genome (same instrumented source, so it plays like the candidate wasm), and
    NAME.json with its scalars and blocks (usable as --base of the next level)."""
    rep = REPS[A.level](A)
    st = json.load(open(os.path.join(work_of(A), 'state.json')))
    if A.level == 3:
        rep.inn = neat.Innov(st.get('innov'))
    geno = st['inds'][A.id]['geno']
    ints = rep.ints(geno)
    T.write_src(json.load(open(os.path.join(A.work, 'meta.json')))['base'], A.out, ints)
    n = len(T.SCALARS)
    sc = dict(zip(T.SCALARS, ints[:n]))
    json.dump({'level': A.level, 'id': A.id, 'scalars': sc, 'genotype': geno, 'describe': rep.describe(geno)},
              open(A.out.rstrip('/') + '.json', 'w'), indent=1)
    print(f'{A.out}: {json.dumps(rep.describe(geno))}')


def cmd_migrate(A):
    """Write genomes for the GA farm (/mnt/project-files/ga-farm/migrants/): full scalars + blocks, fitness history,
    the validation line if any, the base they were measured on and what part of the bot they touch."""
    rep = REPS[A.level](A)
    work = work_of(A)
    st = json.load(open(os.path.join(work, 'state.json')))
    vt = open(os.path.join(work, 'validate.txt')).read() if os.path.exists(os.path.join(work, 'validate.txt')) else ''
    os.makedirs(A.dir, exist_ok=True)
    meta = json.load(open(os.path.join(A.work, 'meta.json')))
    for i in A.ids.split(','):
        d = st['inds'][i]
        ints = rep.ints(d['geno'])
        n = len(T.SCALARS)
        lines = [l for l in vt.split('\n') if l.startswith(i + ':')]
        out = {'id': i, 'source': 'thread "Evolucionar la estructura de la micro", tools/ga/sga.py level %d' % A.level,
               'scope': ['micro structure (rules on/off, rule order, fight switches)', 'GP conditions',
                         'NEAT action net'][A.level - 1],
               'base_bot': meta['base'], 'base_src_md5': ga.md5(meta['wasm']), 'base_scalars_label': A.base or 'default',
               'scalars': dict(zip(T.SCALARS, ints[:n])), 'blocks': ints[n:] if A.level > 1 else [],
               'genotype': d['geno'], 'describe': rep.describe(d['geno']),
               'train': {'deltas_vs_control': [round(x, 4) for x in d['deltas']], 'shrunk': round(ga.shrunk(d), 4)},
               'validation': lines[-1] if lines else '', 'extra': A.note,
               'time': time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())}
        path = os.path.join(A.dir, 'structL%d_%s.json' % (A.level, i))
        json.dump(out, open(path, 'w'), indent=1)
        print(path)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--work', default='out/sga')
    p.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
    sub = p.add_subparsers(dest='cmd', required=True)

    def common(s):
        s.add_argument('--level', type=int, default=1, choices=(1, 2, 3))
        s.add_argument('--base', default='', help='fixed genome under the evolved part: PRESETS id, export JSON or inline JSON')
        s.add_argument('--evolve-weights', action='store_true', help='level 1: also evolve the 22 weight genes')
        s.add_argument('--sigma', type=float, default=0.15)
        s.add_argument('--programs', default='0,1', help='level 2: which programs evolve (0 back off, 1 engage)')
        s.add_argument('--opps', default=OPPS)
        s.add_argument('--init', default='', help='level 1: export JSONs whose structure genes join generation 0')
    s = sub.add_parser('prepare'); s.add_argument('--base-bot', default='bots/study27-economy')
    s = sub.add_parser('check'); common(s)
    s.add_argument('--n', type=int, default=17); s.add_argument('--fuel', type=int, default=10000000)
    s = sub.add_parser('run'); common(s)
    s.add_argument('--gens', type=int, default=10); s.add_argument('--pop', type=int, default=16)
    s.add_argument('--maps', type=int, default=10); s.add_argument('--seed', type=int, default=1)
    s = sub.add_parser('validate'); common(s)
    s.add_argument('--top', type=int, default=3); s.add_argument('--min-n', type=int, default=3)
    s.add_argument('--ids', default=''); s.add_argument('--maps', default=ga.VALID)
    s = sub.add_parser('export'); common(s)
    s.add_argument('--id', required=True); s.add_argument('--out', required=True)
    s = sub.add_parser('migrate'); common(s)
    s.add_argument('--ids', required=True); s.add_argument('--dir', default='/mnt/project-files/ga-farm/migrants')
    s.add_argument('--note', default='')
    A = p.parse_args()
    {'migrate': cmd_migrate, 'prepare': cmd_prepare, 'check': cmd_check, 'run': cmd_run, 'validate': cmd_validate, 'export': cmd_export}[A.cmd](A)


if __name__ == '__main__':
    main()
