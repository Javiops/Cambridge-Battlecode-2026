#!/usr/bin/env python3
"""Genetic algorithm over the bot's fight ("micro") parameters. Macro (draft, shop, camps, tributes) stays fixed.

usage (from the repo root, after `cambc init --yes`):
  python3 tools/ga/ga.py prepare --base bots/study27-economy          # instrumented build, once (~15 s)
  python3 tools/ga/ga.py check                                         # default genome vs the base build
  python3 tools/ga/ga.py run --gens 30                                 # evolve (resumes from out/ga/state.json)
  python3 tools/ga/ga.py validate --top 3 --maps 'MAPS_GLOB'           # best genomes vs the base on unseen maps
  python3 tools/ga/ga.py export --id ID --out bots/NAME                # a normal bot folder with the genome baked in

How it is fast: the genome lives in a `volatile int` array inside the wasm, marked by a magic number. The bot is
compiled once; every candidate is the same wasm with those bytes patched, so a candidate costs no build.

Fitness of a candidate in one generation: for every (opponent, map) of that generation it plays both sides;
pair score = (result side A + result side B) / 2 with win +1, loss -1 (so +1 = map won from both sides), plus
0.1 x gem margin / 1000. The generation's maps are drawn fresh each time from the training pool and every
candidate plays the same ones, including the control (the default genome = the base bot). Selection uses the
candidate's margin over the control on the same games, averaged over every generation it was evaluated in and
shrunk toward 0 (sum / (n + 1)), so a lucky single evaluation cannot win.
Opponents: the base bot itself plus the caster sparring panel (spar11/12/16), the one local rival that kills
like online teams (team memory cambc-sparring-v27). Plain self-play cannot judge fight rules (cambc-online-ab).
"""
import argparse, glob, hashlib, json, math, os, random, shutil, struct, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genome as G

CLI = os.environ.get('CAMBC_CLI', 'cambc')
ENV = {**os.environ, 'CAMBC_NO_UPDATE_CHECK': '1'}
ENV.setdefault('CAMBC_WASMTIME_CACHE', os.path.abspath(os.path.join('out', 'wasmtime-cache')))

TRAIN = ['maps/*.map26a', 'maps_gen/*.map26a', '/mnt/project-files/arena/maps/gen2/*.map26a',
         '/mnt/project-files/arena/maps/gen3/*.map26a', '/mnt/project-files/arena/maps/f150/*.map26a']
VALID = '/mnt/project-files/arena/maps/v100/*.map26a'
# Sealed, never used here: maps_hold60, maps_dev200 (tools/gate.py decides on them) and fresh300.
SEALED = ['maps_hold60/*.map26a', 'maps_dev200/*.map26a', '/mnt/project-files/arena/maps/fresh300/*.map26a']
OPPS = 'bots/study27-economy,bots/spar11,bots/spar12,bots/spar16'


def md5(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:12]


def wasm_of(bot):
    return os.path.join(bot, '.cambc', 'build', 'bot-injected.wasm')


def build(bot):
    r = subprocess.run([CLI, 'build', bot], capture_output=True, text=True, env=ENV)
    if r.returncode != 0 or not os.path.exists(wasm_of(bot)):
        print(r.stdout[-3000:], r.stderr[-3000:], file=sys.stderr)
        sys.exit(f'build failed: {bot}')


def map_pool(globs, exclude=()):
    """Maps from the globs, deduplicated by content, minus any map whose content is in `exclude` globs."""
    banned = {md5(m) for g in exclude for m in glob.glob(g)}
    seen, out = set(), []
    for g in globs:
        for m in sorted(glob.glob(g)):
            h = md5(m)
            if h in seen or h in banned:
                continue
            seen.add(h)
            out.append(m)
    return out


# ---------------------------------------------------------------------------------------------- instrumented bot
def write_src(base, dst, genome, runtime):
    """Copy base/src to dst/src with the literal genes replaced; params.h gets the genome as constants
    (runtime=False, a normal bot) or as the patchable volatile array (runtime=True)."""
    src = os.path.join(dst, 'src')
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(os.path.join(base, 'src'), src)
    for fname, old, new in G.LITERALS:
        p = os.path.join(src, fname)
        text = open(p).read()
        if text.count(old) != 1:
            sys.exit(f'{fname}: expected exactly one "{old}", found {text.count(old)}')
        open(p, 'w').write(text.replace(old, new))
    p = os.path.join(src, 'params.h')
    lines = open(p).read().split('\n') if os.path.exists(p) else []
    keep = [l for l in lines if not (l.strip().startswith('#define ') and l.split()[1] in G.GENES)]
    out = keep + ['', '// ---- genetic algorithm genome (tools/ga): fight parameters ----']
    if runtime:
        vals = [G.MAGIC[0], G.MAGIC[1], len(G.NAMES)] + [genome[k] for k in G.NAMES]
        out.append('volatile int ga_g[%d] = {%s};' % (len(vals), ', '.join(str(v) for v in vals)))
        # copied once at start-up into plain constants: the hot code then pays an ordinary load, not a volatile one
        out += ['static const int ga_%s = ga_g[%d];' % (k, i + 3) for i, k in enumerate(G.NAMES)]
        out += ['#define %s ga_%s' % (k, k) for k in G.NAMES]
    else:
        out += ['#define %s %d' % (k, genome[k]) for k in G.NAMES]
    open(p, 'w').write('\n'.join(out) + '\n')


def find_genome(wasm_bytes):
    key = struct.pack('<3i', G.MAGIC[0], G.MAGIC[1], len(G.NAMES))
    i = wasm_bytes.find(key)
    if i < 0 or wasm_bytes.find(key, i + 1) >= 0:
        sys.exit('genome marker not found exactly once in the wasm')
    return i + len(key)


class Bench:
    def __init__(self, work, jobs):
        self.work, self.jobs = work, jobs
        meta = json.load(open(os.path.join(work, 'meta.json')))
        self.meta = meta
        self.template = open(meta['wasm'], 'rb').read()
        self.offset = meta['offset']
        self.cand_dir = os.path.join(work, 'cands')
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
        self.opp_wasm = {}
        self.map_md5 = {}

    def cand_wasm(self, g):
        vals = [g[k] for k in G.NAMES]
        blob = struct.pack('<%di' % len(vals), *vals)
        cid = hashlib.sha1(blob).hexdigest()[:10]
        path = os.path.join(self.cand_dir, cid + '.wasm')
        if not os.path.exists(path):
            b = bytearray(self.template)
            b[self.offset:self.offset + len(blob)] = blob
            with open(path + '.tmp', 'wb') as f:
                f.write(b)
            os.replace(path + '.tmp', path)
        return cid, path

    def opp(self, bot):
        if bot not in self.opp_wasm:
            if not os.path.exists(wasm_of(bot)):
                build(bot)
            w = wasm_of(bot)
            self.opp_wasm[bot] = (md5(w), w)
        return self.opp_wasm[bot]

    def mkey(self, m):
        if m not in self.map_md5:
            self.map_md5[m] = md5(m)
        return self.map_md5[m]

    def play(self, job):
        key, a, b, m, side = job
        tmp = tempfile.mkdtemp(prefix='g', dir=os.path.join(self.work, 'tmp'))
        stats = os.path.join(tmp, 's.json')
        r = subprocess.run([CLI, 'run', a, b, '--map', m, '-o', tmp, '--statistics', stats],
                           capture_output=True, text=True, env=ENV)
        res = {'key': key, 'ok': False}
        if os.path.exists(stats):
            d = json.load(open(stats))
            me, op = side, 1 - side
            won = d['outcome'] == ('teamA' if me == 0 else 'teamB')
            lost = d['outcome'] in ('teamA', 'teamB') and not won
            gems = [t['submittedGems'] for t in d['teams']]
            dth = [sum(c['deaths'] for c in d['champions'] if c['team'] == t) for t in (0, 1)]
            kil = [sum(c['kills'] for c in d['champions'] if c['team'] == t) for t in (0, 1)]
            res = {'key': key, 'ok': True, 'r': 1 if won else (-1 if lost else 0), 'round': d['round'],
                   'gm': gems[me] - gems[op], 'gems': gems[me], 'dth': dth[me], 'kil': kil[me],
                   'flt': (d.get('botFaults') or [0, 0])[me] if isinstance(d.get('botFaults'), list) else 0}
        else:
            res['log'] = (r.stdout + r.stderr)[-300:]
        shutil.rmtree(tmp, ignore_errors=True)
        return res

    def games(self, cands, opps, maps):
        """Play every candidate x opponent x map x side (cached). Returns {key: result}."""
        os.makedirs(os.path.join(self.work, 'tmp'), exist_ok=True)
        jobs, keys = [], []
        for cid, cw in cands:
            for ob in opps:
                oh, ow = self.opp(ob)
                for m in maps:
                    for side in (0, 1):
                        k = f'{cid}|{oh}|{self.mkey(m)}|{side}'
                        keys.append(k)
                        if k in self.cache:
                            continue
                        a, b = (cw, ow) if side == 0 else (ow, cw)
                        jobs.append((k, a, b, m, side))
        jobs = list({j[0]: j for j in jobs}.values())
        if jobs:
            with ThreadPoolExecutor(self.jobs) as ex, open(self.cache_path, 'a') as log:
                for res in ex.map(self.play, jobs):
                    if res['ok']:
                        self.cache[res['key']] = res
                        log.write(json.dumps(res) + '\n')
                        log.flush()
                    else:
                        print('game failed:', res.get('log', ''), file=sys.stderr)
        return self.cache

    def score(self, cid, opps, maps, weights=None):
        """Fitness of one candidate (see the module doc), plus per-opponent detail."""
        per = {}
        for ob in opps:
            oh = self.opp(ob)[0]
            pairs, gm, dth, kil, n = 0.0, 0.0, 0, 0, 0
            both_w = both_l = 0
            for m in maps:
                rs = [self.cache.get(f'{cid}|{oh}|{self.mkey(m)}|{s}') for s in (0, 1)]
                if not all(rs):
                    continue
                pr = (rs[0]['r'] + rs[1]['r']) / 2.0
                pairs += pr
                both_w += pr == 1
                both_l += pr == -1
                for x in rs:
                    gm += x['gm']; dth += x['dth']; kil += x['kil']; n += 1
            np_ = max(1, n // 2)
            per[ob] = {'fit': pairs / np_ + 0.1 * (gm / max(1, n)) / 1000.0, 'won2': both_w, 'lost2': both_l,
                       'pairs': n // 2, 'dth': dth / max(1, n), 'kil': kil / max(1, n)}
        w = weights or {}
        tot = sum(w.get(ob, 1.0) for ob in opps)
        fit = sum(per[ob]['fit'] * w.get(ob, 1.0) for ob in opps) / tot
        return fit, per


# --------------------------------------------------------------------------------------------------- commands
def cmd_prepare(A):
    work = A.work
    os.makedirs(work, exist_ok=True)
    bot = os.path.join(work, 'gabot')
    write_src(A.base, bot, G.default(), runtime=True)
    build(bot)
    w = wasm_of(bot)
    off = find_genome(open(w, 'rb').read())
    tmpl = os.path.join(work, 'template.wasm')
    shutil.copy(w, tmpl)
    json.dump({'base': A.base, 'wasm': tmpl, 'offset': off, 'genes': G.GENES}, open(os.path.join(work, 'meta.json'), 'w'),
              indent=1)
    print(f'instrumented bot built, genome at byte {off} of {tmpl}; {len(G.NAMES)} genes')


def cmd_check(A):
    """Default genome vs the base build. Instrumenting costs a little fuel and this bot is fuel-chaotic, so some games
    differ (111/136 identical on 16 Oct; identical with unlimited fuel). Many more would mean a broken genome."""
    B = Bench(A.work, A.jobs)
    base = B.meta['base']
    if not os.path.exists(wasm_of(base)):
        build(base)
    maps = map_pool(['maps/*.map26a'])[:A.n]
    cid, cw = B.cand_wasm(G.default())
    opps = A.opps.split(',')
    B.games([(cid, cw)], opps, maps)
    bh = md5(wasm_of(base))
    B.cache_path = os.path.join(A.work, 'games_basecheck.jsonl')
    B.games([(bh, wasm_of(base))], opps, maps)
    same = diff = 0
    for ob in opps:
        oh = B.opp(ob)[0]
        for m in maps:
            for s in (0, 1):
                x = B.cache[f'{cid}|{oh}|{B.mkey(m)}|{s}']
                y = B.cache[f'{bh}|{oh}|{B.mkey(m)}|{s}']
                if (x['r'], x['round'], x['gm']) == (y['r'], y['round'], y['gm']):
                    same += 1
                else:
                    diff += 1
                    print('differs:', os.path.basename(ob), os.path.basename(m), s, x['r'], x['round'], y['r'], y['round'])
    print(f'default genome vs base: {same} identical games, {diff} different')


def load_state(work):
    p = os.path.join(work, 'state.json')
    return json.load(open(p)) if os.path.exists(p) else None


def save_state(work, st):
    p = os.path.join(work, 'state.json')
    json.dump(st, open(p + '.tmp', 'w'))
    os.replace(p + '.tmp', p)


def shrunk(ind):
    d = ind['deltas']
    return sum(d) / (len(d) + 1.0)


def mutate(x, rng, p, sigma):
    return [min(1.0, max(0.0, u + rng.gauss(0, sigma))) if rng.random() < p else u for u in x]


def crossover(a, b, rng, alpha=0.3):
    out = []
    for u, v in zip(a, b):
        lo, hi = min(u, v), max(u, v)
        span = hi - lo
        out.append(min(1.0, max(0.0, rng.uniform(lo - alpha * span, hi + alpha * span))))
    return out


def cmd_run(A):
    B = Bench(A.work, A.jobs)
    opps = A.opps.split(',')
    weights = dict(zip(opps, [float(w) for w in A.weights.split(',')])) if A.weights else None
    pool = map_pool(TRAIN, exclude=SEALED + [VALID])
    rng = random.Random(A.seed)
    st = load_state(A.work)
    base_x = G.to_unit(G.default())
    if st is None:
        inds = {}
        pop = []
        bid = B.cand_wasm(G.default())[0]
        inds[bid] = {'g': G.default(), 'x': base_x, 'deltas': [], 'born': 0}
        while len(pop) < A.pop - 1:
            x = mutate(base_x, rng, 0.4, 0.15)
            cid = B.cand_wasm(G.from_unit(x))[0]
            if cid in inds:
                continue
            inds[cid] = {'g': G.from_unit(x), 'x': x, 'deltas': [], 'born': 0}
            pop.append(cid)
        st = {'gen': 0, 'base': bid, 'inds': inds, 'pop': pop, 'history': [], 'seed': A.seed, 'opps': opps,
              'pool': len(pool)}
        save_state(A.work, st)
    rng = random.Random(A.seed * 1000 + st['gen'])
    logp = os.path.join(A.work, 'log.md')
    if not os.path.exists(logp):
        open(logp, 'w').write('| gen | maps | games | min | control fit | best new (delta) | best overall (shrunk, n) | '
                              'genes changed in best |\n|---|---|---|---|---|---|---|---|\n')
    for _ in range(A.gens):
        t0 = time.time()
        gen = st['gen']
        maps = rng.sample(pool, A.maps)
        bid = st['base']
        ids = [bid] + st['pop']
        cands = [B.cand_wasm(st['inds'][i]['g']) for i in ids]
        n0 = len(B.cache)
        B.games(cands, opps, maps)
        played = len(B.cache) - n0
        fits = {i: B.score(i, opps, maps, weights) for i in ids}
        cfit = fits[bid][0]
        for i in st['pop']:
            st['inds'][i]['deltas'].append(fits[i][0] - cfit)
        # the next population: elites by shrunk mean, children by tournament + crossover + mutation
        evald = [i for i, d in st['inds'].items() if d['deltas'] and i != bid]
        ranked = sorted(evald, key=lambda i: shrunk(st['inds'][i]), reverse=True)
        elites = ranked[:A.elite]
        parents = ranked[:max(A.elite, A.pop // 2)]

        def tour():
            c = rng.sample(parents, min(3, len(parents)))
            return max(c, key=lambda i: shrunk(st['inds'][i]))
        new = list(elites)
        tries = 0
        while len(new) < A.pop - 1 and tries < 1000:
            tries += 1
            pa = st['inds'][tour()]['x']
            x = crossover(pa, st['inds'][tour()]['x'], rng) if rng.random() < 0.7 else list(pa)
            x = mutate(x, rng, 3.0 / len(x), A.sigma)
            g = G.from_unit(x)
            cid = B.cand_wasm(g)[0]
            if cid in new or cid == bid:
                continue
            if cid not in st['inds']:
                st['inds'][cid] = {'g': g, 'x': x, 'deltas': [], 'born': gen + 1}
            new.append(cid)
        best_new = max(st['pop'], key=lambda i: st['inds'][i]['deltas'][-1])
        top = ranked[0]
        bt = st['inds'][top]
        per_c = {os.path.basename(o): round(v['fit'], 3) for o, v in fits[bid][1].items()}
        per_t = {os.path.basename(o): round(v['fit'], 3) for o, v in fits[top][1].items()} if top in fits else {}
        h = {'gen': gen, 'maps': [os.path.basename(m) for m in maps], 'games': played, 'secs': round(time.time() - t0),
             'control': round(cfit, 4), 'control_per': per_c,
             'best_new': best_new, 'best_new_delta': round(st['inds'][best_new]['deltas'][-1], 4),
             'top': top, 'top_shrunk': round(shrunk(bt), 4), 'top_n': len(bt['deltas']), 'top_per': per_t,
             'mean_delta': round(sum(st['inds'][i]['deltas'][-1] for i in st['pop']) / len(st['pop']), 4)}
        st['history'].append(h)
        st['pop'] = new
        st['gen'] = gen + 1
        save_state(A.work, st)
        with open(logp, 'a') as f:
            f.write(f"| {gen} | {len(maps)} | {played} | {h['secs'] / 60:.1f} | {cfit:+.3f} | "
                    f"{best_new} ({h['best_new_delta']:+.3f}) | {top} ({h['top_shrunk']:+.3f}, {h['top_n']}) | "
                    f"{json.dumps(G.diff(bt['g']))} |\n")
        print(f"gen {gen}: {played} games {h['secs']}s control {cfit:+.3f} mean delta {h['mean_delta']:+.3f} "
              f"best new {h['best_new_delta']:+.3f} top {top} {h['top_shrunk']:+.3f} n={h['top_n']}", flush=True)


def sign_p(w, l):
    n = w + l
    if n == 0:
        return 1.0
    k = max(w, l)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n)


def cmd_validate(A):
    """Top genomes (or --ids) vs the control on maps never used in training: maps won both sides per opponent."""
    B = Bench(A.work, A.jobs)
    st = load_state(A.work)
    opps = A.opps.split(',')
    maps = map_pool([A.maps])
    if A.ids:
        ids = A.ids.split(',')
    else:
        evald = [i for i, d in st['inds'].items() if len(d['deltas']) >= A.min_n and i != st['base']]
        ids = sorted(evald, key=lambda i: shrunk(st['inds'][i]), reverse=True)[:A.top]
    allids = [st['base']] + ids
    B.games([B.cand_wasm(st['inds'][i]['g']) for i in allids], opps, maps)
    out = [f'validation on {len(maps)} maps ({A.maps}), both sides, vs {", ".join(os.path.basename(o) for o in opps)}']
    cf, cper = B.score(st['base'], opps, maps)
    out.append(f"control {st['base']}: fit {cf:+.3f} " + ' '.join(
        f"{os.path.basename(o)} {v['won2']}-{v['lost2']}" for o, v in cper.items()))
    res = {}
    for i in ids:
        f, per = B.score(i, opps, maps)
        # head to head on the same games: pairs where the candidate's pair score beats the control's
        better = worse = 0
        for ob in opps:
            oh = B.opp(ob)[0]
            for m in maps:
                k = B.mkey(m)
                a = sum(B.cache[f'{i}|{oh}|{k}|{s}']['r'] for s in (0, 1))
                b = sum(B.cache[f"{st['base']}|{oh}|{k}|{s}"]['r'] for s in (0, 1))
                better += a > b
                worse += a < b
        res[i] = {'fit': f, 'delta': f - cf, 'better': better, 'worse': worse, 'p': sign_p(better, worse)}
        out.append(f"{i}: fit {f:+.3f} (delta {f - cf:+.3f}) " + ' '.join(
            f"{os.path.basename(o)} {v['won2']}-{v['lost2']} d{v['dth']:.1f}" for o, v in per.items()) +
            f" | pairs better/worse than control {better}-{worse} p={res[i]['p']:.3f} | "
            f"{json.dumps(G.diff(st['inds'][i]['g']))}")
    txt = '\n'.join(out)
    print(txt)
    open(os.path.join(A.work, 'validate.txt'), 'a').write(txt + '\n\n')


def cmd_export(A):
    st = load_state(A.work)
    g = st['inds'][A.id]['g'] if A.id else G.default()
    base = json.load(open(os.path.join(A.work, 'meta.json')))['base']
    write_src(base, A.out, g, runtime=False)
    print(f'{A.out}: base {base} with genome {A.id}: {json.dumps(G.diff(g))}')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--work', default='out/ga')
    p.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('prepare'); s.add_argument('--base', default='bots/study27-economy')
    s = sub.add_parser('check'); s.add_argument('--n', type=int, default=17); s.add_argument('--opps', default=OPPS)
    s = sub.add_parser('run')
    s.add_argument('--gens', type=int, default=10); s.add_argument('--pop', type=int, default=20)
    s.add_argument('--maps', type=int, default=16, help='maps per generation (each played both sides vs every opp)')
    s.add_argument('--elite', type=int, default=4); s.add_argument('--sigma', type=float, default=0.12)
    s.add_argument('--opps', default=OPPS); s.add_argument('--weights', default='')
    s.add_argument('--seed', type=int, default=1)
    s = sub.add_parser('validate')
    s.add_argument('--top', type=int, default=3); s.add_argument('--min-n', type=int, default=3)
    s.add_argument('--ids', default=''); s.add_argument('--maps', default=VALID); s.add_argument('--opps', default=OPPS)
    s = sub.add_parser('export'); s.add_argument('--id', default=''); s.add_argument('--out', required=True)
    A = p.parse_args()
    {'prepare': cmd_prepare, 'check': cmd_check, 'run': cmd_run, 'validate': cmd_validate, 'export': cmd_export}[A.cmd](A)


if __name__ == '__main__':
    main()
