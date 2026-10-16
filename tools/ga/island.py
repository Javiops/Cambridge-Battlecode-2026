#!/usr/bin/env python3
"""GA farm: one island of an island-model genetic algorithm over the whole bot (tools/ga/FARM.md).

Every machine (a cloud thread, the PC) runs one island. All islands evolve the same genome, which covers everything
the two earlier tools evolved plus the macro:
  micro      the 22 fight weights (genome.py)
  structure  rule on/off, rule order, the fight switches (structure.py SWITCHES)
  macro      tributes, shop, camp choice and sharing, recall trips, draft, holding (macro.py)
  gp         the two evolved conditions "back off" / "engage" (gp.py)
  neat       the evolved network choosing the action in a fight (neat.py)
`--scope` says which of these an island mutates (comma list, or `all`); the rest is inherited from its start
genome and from migrants. Islands swap their best genomes ("migrants", small JSON files with the full genome) through
a farm folder (the shared folder in the cloud) and/or a git branch (the PC), and use other islands' best as rivals.

Same machinery as ga.py / sga.py: one instrumented wasm, candidates are byte-patched copies (no build), fitness =
margin over the control (the start genome, same wasm) on the same games, shrunk mean over generations.

  python3 tools/ga/island.py run --name cloud-a --scope all --farm /mnt/project-files/ga-farm
  python3 tools/ga/island.py ensure --name cloud-a ...   # same args: start it in the background unless it runs
  python3 tools/ga/island.py stop --name cloud-a
  python3 tools/ga/island.py board --farm /mnt/project-files/ga-farm
  python3 tools/ga/island.py validate --name cloud-a --top 3
  python3 tools/ga/island.py export --name cloud-a --id CID --out bots/NAME

State (checkpoint after every generation, resumed on start): <farm>/islands/<name>/ when the farm is the shared
folder, else out/islands/<name>/ (the PC). It holds state.json, games.jsonl, log.md, template.wasm, meta.json.
"""
import argparse, copy, datetime, glob, hashlib, json, math, os, platform, random, shutil, socket, subprocess, sys
import time, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import ga, gp, neat, sga, structure as T
import genome as G
import macro as M
import pair as PR

FAMILIES = {'micro': list(G.NAMES) + list(PR.NAMES), 'structure': list(T.L1_GENES), 'macro': list(M.NAMES)}
ONLINE = {'online1520': ('ga65a6', {'P_IM_PAIRED': 1})}  # online bot genomes: (sga preset, extra genes)
SHARED = '/mnt/project-files'
TRAIN = ga.TRAIN + ['maps_train/*/*.map26a']
VALID = ['maps_v100/*.map26a', ga.VALID]
# v44 self-play is one rival of many: the caster sparring panel and the ghosts of real top-10 games weigh more
GHOSTS = [('gh_cabbage_corners', 'corners'), ('gh_tip_corners', 'corners'), ('gh_hinana_corners', 'corners'),
          ('gh_cabbage_collision', 'collision'), ('gh_antifreeze_collision', 'collision'), ('gh_cabbage_lanes', 'lanes')]
DEFAULT_OPPS = ','.join(['genome:start', 'bots/spar11', 'bots/spar12', 'bots/spar16'] +
                        ['bots/%s@maps_ghost/%s.map26a:0' % g for g in GHOSTS])
WIN = platform.system() == 'Windows'


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')


def base_hash(bot):
    """Identity of the base bot source (LF-normalised so Windows and Linux checkouts agree)."""
    h = hashlib.md5()
    src = os.path.join(bot, 'src')
    for f in sorted(os.listdir(src)):
        p = os.path.join(src, f)
        if os.path.isfile(p):
            h.update(f.encode() + b'\0' + open(p, 'rb').read().replace(b'\r\n', b'\n'))
    return h.hexdigest()[:12]


# ------------------------------------------------------------------------------------------------------ genotype
# {'sc': {gene: value} (only genes that differ from the base bot), 'gp0': tree|None, 'gp1': tree|None,
#  'nn': neat genome|None, 'nn_from': island whose innovation numbers the net uses}. None = the seed (= base bot).
DEF = T.default_scalars()


def norm(geno):
    g = {'sc': {k: int(v) for k, v in geno.get('sc', {}).items() if k in DEF and int(v) != DEF[k]}}
    for k in ('gp0', 'gp1', 'nn', 'nn_from'):
        if geno.get(k) is not None:
            g[k] = geno[k]
    return g


def scalars(geno):
    sc = dict(DEF)
    sc.update(geno.get('sc', {}))
    return sc


def to_ints(geno):
    blocks = {'GA_GP0': gp.compile_tree(geno.get('gp0') or gp.SEED_GP0),
              'GA_GP1': gp.compile_tree(geno.get('gp1') or gp.SEED_GP1),
              'GA_NN': neat.compile_net(geno.get('nn') or neat.seed())}
    return T.to_ints(scalars(geno), blocks)


def cid_of(geno):
    return T.cid_of(to_ints(geno))


def describe(geno, ref=None):
    """What the genome changes: vs the base bot, or vs `ref` (e.g. the island's start genome)."""
    full = T.describe_scalars(scalars(geno))
    d = full
    if ref is not None:
        r = T.describe_scalars(scalars(ref))
        d = {k: v for k, v in full.items() if r.get(k) != v}
        d.update({k: DEF[k] for k in r if k not in full and k in DEF})  # changes of ref the genome undid
    for k in ('gp0', 'gp1'):
        if geno.get(k) is not None and d.get('P_%s_ON' % k.upper()):
            d[k] = gp.text(geno[k])
    if geno.get('nn') is not None and d.get('P_NN_ON'):
        d['nn'] = neat.describe(geno['nn'])
    return d


def resolve(spec):
    """A genome from: 'default' (the base bot), a sga.PRESETS id ('ga65a6' = v44), an export JSON of sga/island
    (its 'scalars'), a migrant JSON (its 'genome') or inline JSON scalars."""
    if spec in ('', 'default'):
        return norm({})
    if spec in sga.PRESETS:
        return norm({'sc': sga.PRESETS[spec]})
    if spec in ONLINE:  # the online bots' genomes (with ONLINE_ZIP as overlay they build the uploaded zip)
        return norm({'sc': dict(sga.PRESETS[ONLINE[spec][0]], **ONLINE[spec][1])})
    if os.path.exists(spec):
        d = json.load(open(spec))
        if 'genome' in d:
            return norm(d['genome'])
        g = {'sc': d['scalars']}
        geno = d.get('genotype') or {}
        if isinstance(geno, dict) and 'gp0' in geno:
            g.update(gp0=geno['gp0'], gp1=geno['gp1'])
        if isinstance(geno, dict) and 'conns' in geno:
            g['nn'] = {'nodes': geno['nodes'], 'conns': geno['conns']}
        return norm(g)
    return norm({'sc': json.loads(spec)})


def renumber_net(net, inn):
    """A net from another island, re-keyed into this island's innovation numbers (hidden nodes get new ids)."""
    outs = set(neat.OUTS)
    remap = {}
    nodes = {}
    for k, n in net['nodes'].items():
        k = int(k)
        if k in outs:
            nodes[str(k)] = dict(n)
        else:
            remap[k] = inn.next_node
            inn.next_node += 1
            nodes[str(remap[k])] = dict(n)
    conns = {}
    for c in net['conns'].values():
        s, d = remap.get(c[0], c[0]), remap.get(c[1], c[1])
        conns[str(inn.of_conn(s, d))] = [s, d, c[2], c[3]]
    return {'nodes': nodes, 'conns': conns}


class Evolver:
    """Mutation and crossover over the genome families named by --scope."""

    def __init__(self, scope, sigma, inn, name):
        fams = [f.strip() for f in scope.split(',')]
        if 'all' in fams:
            fams = ['micro', 'structure', 'macro', 'gp', 'neat']
        bad = [f for f in fams if f not in FAMILIES and f not in ('gp', 'neat')]
        if bad:
            sys.exit('unknown scope %s (micro, structure, macro, gp, neat, all)' % bad)
        self.genes = [g for f in fams if f in FAMILIES for g in FAMILIES[f]]
        self.gp = 'gp' in fams
        self.nn = 'neat' in fams
        self.sigma, self.inn, self.name = sigma, inn, name
        # how often each kind of mutation is picked: scalars by gene count, programs and net a fixed share
        self.kinds = ([('sc', 0.7 if (self.gp or self.nn) else 1.0)] if self.genes else []) + \
                     ([('gp', 0.15 if self.genes else 0.5)] if self.gp else []) + \
                     ([('nn', 0.15 if self.genes else 0.5)] if self.nn else [])

    def mutate(self, geno, rng):
        g = copy.deepcopy(geno)
        tot = sum(w for _, w in self.kinds)
        r, kind = rng.random() * tot, self.kinds[-1][0]
        for k, w in self.kinds:
            if r < w:
                kind = k
                break
            r -= w
        if kind == 'sc':
            sc = scalars(g)
            p = 2.0 / len(self.genes)
            changed = False
            while not changed:
                for k in self.genes:
                    if rng.random() >= p:
                        continue
                    d, lo, hi, kd = T.spec(k)
                    old = sc[k]
                    if kd == 'bool':
                        sc[k] = 1 - sc[k] if hi == 1 else rng.randint(lo, hi)
                    elif kd == 'order':
                        sc[k] = int(min(hi, max(lo, round(sc[k] + rng.gauss(0, 18)))))
                    else:
                        sc[k] = int(min(hi, max(lo, round(sc[k] + rng.gauss(0, self.sigma * (hi - lo) + 0.5)))))
                    changed |= sc[k] != old
            g['sc'] = sc
        elif kind == 'gp':
            which = rng.choice([0, 1])
            key = 'gp%d' % which
            sc = scalars(g)
            if not sc['P_GP%d_ON' % which]:  # switching a program on starts from the seed (= the fixed condition)
                sc['P_GP%d_ON' % which] = 1
                g[key] = g.get(key) or (gp.SEED_GP0, gp.SEED_GP1)[which]
            g['sc'] = sc
            for _ in range(1 + (rng.random() < 0.3)):
                g[key] = gp.mutate(g.get(key) or (gp.SEED_GP0, gp.SEED_GP1)[which], rng)
        else:
            sc = scalars(g)
            net = g.get('nn')
            if net is None or g.get('nn_from') != self.name:
                net = renumber_net(net, self.inn) if net is not None else neat.seed()
            if not sc['P_NN_ON']:
                sc['P_NN_ON'] = 1
                g['sc'] = sc
                neat.add_rule(net, rng, self.inn)  # a net with no links defers everything: give it one rule
            else:
                net = neat.mutate(net, rng, self.inn)
            g['nn'], g['nn_from'] = net, self.name
        return norm(g)

    def cross(self, a, b, rng):
        """a is the fitter parent."""
        sa, sb = scalars(a), scalars(b)
        g = {'sc': {k: (sa if rng.random() < 0.5 else sb)[k] for k in DEF}}
        for k in ('gp0', 'gp1'):
            ta, tb = a.get(k), b.get(k)
            if ta is not None and tb is not None and rng.random() < 0.5:
                g[k] = gp.crossover(ta, tb, rng)
            else:
                g[k] = ta if ta is not None else tb
        if a.get('nn') is not None:
            if b.get('nn') is not None and a.get('nn_from') == b.get('nn_from'):
                g['nn'] = neat.crossover(a['nn'], b['nn'], rng)
            else:
                g['nn'] = copy.deepcopy(a['nn'])
            g['nn_from'] = a.get('nn_from')
        elif b.get('nn') is not None:
            g['nn'], g['nn_from'] = copy.deepcopy(b['nn']), b.get('nn_from')
        return norm(g)


# ----------------------------------------------------------------------------------------------------- the bench
class Bench(sga.Bench):
    """sga.Bench (cambc 2.2 --json statistics) on the island's template, plus rivals given as genomes."""

    def __init__(self, home, scratch, jobs, meta):
        self.work, self.jobs, self.extra = scratch, jobs, []
        self.meta = meta
        self.template = open(os.path.join(home, 'template.wasm'), 'rb').read()
        self.offset = meta['offset']
        self.cand_dir = os.path.join(scratch, 'cands')
        os.makedirs(os.path.join(scratch, 'tmp'), exist_ok=True)
        os.makedirs(self.cand_dir, exist_ok=True)
        self.cache_path = os.path.join(home, 'games.jsonl')
        self.cache = {}
        if os.path.exists(self.cache_path):
            for line in open(self.cache_path):
                try:
                    d = json.loads(line)
                    self.cache[d['key']] = d
                except ValueError:
                    pass
        self.opp_wasm, self.map_md5 = {}, {}
        self.genomes = {}  # 'genome:...' rival -> genotype (set by the island)

    def cand(self, geno):
        return self.cand_wasm(to_ints(geno))

    def opp(self, spec):
        if spec not in self.opp_wasm and spec.startswith('genome:'):
            self.opp_wasm[spec] = self.cand(self.genomes[spec])
        return ga.Bench.opp(self, spec)


# ------------------------------------------------------------------------------------------------- farm exchange
def farm_dirs(A):
    out = []
    if A.farm:
        out.append(A.farm)
    if A.git_branch:
        out.append(A.git_dir)
    return out


def read_migrants(d, bh=None):
    """Island migrants (migrants/<island>/<cid>.json), plus the flat files other GA threads drop in migrants/
    (micro_<id>.json with a weights 'genome', structL1_<id>.json with 'scalars'): read as island <prefix>."""
    out = []
    for p in glob.glob(os.path.join(d, 'migrants', '*', '*.json')):
        try:
            m = json.load(open(p))
            m['_path'] = p
            out.append(m)
        except (ValueError, OSError):
            pass
    for p in glob.glob(os.path.join(d, 'migrants', '*.json')):
        try:
            x = json.load(open(p))
            sc = x.get('scalars') or x.get('genome')
            if not isinstance(sc, dict) or not all(isinstance(v, int) for v in sc.values()):
                continue
            geno = norm({'sc': sc})
            fit = x.get('fitness') if isinstance(x.get('fitness'), dict) else {}
            out.append({'island': os.path.basename(p).split('_')[0], 'cid': cid_of(geno), 'base': bh,
                        'genome': geno, 'fitness': {'shrunk': fit.get('shrunk', 0.0)},
                        'time': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(os.path.getmtime(p))),
                        '_path': p})
        except (ValueError, OSError, KeyError):
            pass
    return out


def write_json(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + '.tmp'
    with open(tmp, 'w', newline='\n') as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, p)


def run_git(args, cwd=None, check=False):
    r = subprocess.run(['git'] + args, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError('git %s: %s' % (' '.join(args), r.stderr.strip()))
    return r


def git_setup(A):
    d, br = A.git_dir, A.git_branch
    if os.path.isdir(os.path.join(d, '.git')):
        return
    url = A.git_remote or run_git(['remote', 'get-url', 'origin'], check=True).stdout.strip()
    os.makedirs(d, exist_ok=True)
    run_git(['init', '-q'], cwd=d, check=True)
    run_git(['remote', 'add', 'origin', url], cwd=d, check=True)
    run_git(['config', 'user.name', 'ga-farm island'], cwd=d)
    run_git(['config', 'user.email', 'ga-farm@localhost'], cwd=d)
    run_git(['config', 'core.autocrlf', 'false'], cwd=d)
    if run_git(['fetch', '-q', 'origin', br], cwd=d).returncode == 0:
        run_git(['checkout', '-q', '-B', br, 'origin/' + br], cwd=d, check=True)
    else:
        run_git(['checkout', '-q', '--orphan', br], cwd=d, check=True)
        open(os.path.join(d, 'README.md'), 'w').write(
            '# GA farm exchange\n\nMigrants (best genomes) and island status of the island-model GA '
            '(tools/ga/island.py, tools/ga/FARM.md on main). Written by the islands; do not edit by hand.\n')


def git_pull(A):
    d, br = A.git_dir, A.git_branch
    if run_git(['fetch', '-q', 'origin', br], cwd=d).returncode == 0:
        run_git(['reset', '-q', '--hard', 'origin/' + br], cwd=d)
        return True
    return False


def git_push(A, write, msg):
    """Our files on top of the latest branch: fetch, reset, write, commit, push; retried on a race."""
    d, br = A.git_dir, A.git_branch
    for attempt in range(6):
        git_pull(A)
        write(d)
        run_git(['add', '-A'], cwd=d)
        if run_git(['diff', '--cached', '--quiet'], cwd=d).returncode == 0:
            return True
        run_git(['commit', '-q', '-m', msg], cwd=d, check=True)
        r = run_git(['push', '-q', 'origin', 'HEAD:' + br], cwd=d)
        if r.returncode == 0:
            return True
        time.sleep(2 ** attempt)
    print('git push failed: %s' % r.stderr.strip()[-300:], file=sys.stderr)
    return False


def board(farm):
    rows = []
    for p in sorted(glob.glob(os.path.join(farm, 'islands', '*', 'status.json'))):
        try:
            rows.append(json.load(open(p)))
        except (ValueError, OSError):
            pass
    out = ['# GA farm board', '',
           f'Regenerated {now()} by the islands (tools/ga/island.py). Fitness = margin over the island\'s own control '
           '(its start genome) on the same games, shrunk mean over generations (n = generations evaluated).', '',
           '| island | host | scope | start | jobs | gen | games | games/s | best (shrunk, n) | best changes vs start | out/in | updated |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for s in sorted(rows, key=lambda r: r['name']):
        b = s.get('best') or {}
        ch = json.dumps(b.get('describe', {}))
        ch = ch if len(ch) <= 160 else ch[:157] + '...'
        out.append(f"| {s['name']} | {s.get('host', '')} | {s.get('scope', '')} | {s.get('start', '')} | {s.get('jobs', '')} "
                   f"| {s.get('gen', 0)} | {s.get('games', 0)} | {s.get('gps', 0):.1f} "
                   f"| {b.get('cid', '-')} ({b.get('shrunk', 0):+.3f}, {b.get('n', 0)}) | {ch} "
                   f"| {s.get('exported', 0)}/{s.get('imported', 0)} | {s.get('updated', '')} |")
    out += ['', 'Code: branch `%s`. Migrants: `migrants/<island>/<cid>.json` (full genome + fitness); '
            'state: `islands/<island>/`.' % (rows[0].get('code', '?') if rows else '?'), '']
    notes = os.path.join(farm, 'NOTES.md')  # farm-wide notes (champion cadence, code changes), kept by the farm thread
    if os.path.exists(notes):
        out += [open(notes).read().strip(), '']
    with open(os.path.join(farm, 'BOARD.md'), 'w', newline='\n') as f:
        f.write('\n'.join(out))


def mirror(src, dst, transport):
    """Bridge: copy the files of islands that publish through `transport` from src to dst."""
    for p in glob.glob(os.path.join(src, 'islands', '*', 'status.json')):
        try:
            s = json.load(open(p))
        except (ValueError, OSError):
            continue
        if s.get('transport') != transport:
            continue
        name = s['name']
        q = os.path.join(dst, 'islands', name, 'status.json')
        os.makedirs(os.path.dirname(q), exist_ok=True)
        shutil.copy(p, q)
        for m in glob.glob(os.path.join(src, 'migrants', name, '*.json')):
            q = os.path.join(dst, 'migrants', name, os.path.basename(m))
            if not os.path.exists(q) or open(q, 'rb').read() != open(m, 'rb').read():
                os.makedirs(os.path.dirname(q), exist_ok=True)
                shutil.copy(m, q)


def legacy_pc(A, farm, bh):
    """The PC island that runs the old weights GA (tools/ga/pc_island.py on branch pc-island) publishes
    islands/pc/best.json there. Read it (fetch only) and turn its best genomes into migrants of island 'pc'."""
    br = A.legacy_branch
    if run_git(['fetch', '-q', 'origin', br]).returncode:
        return
    r = run_git(['show', 'origin/%s:islands/pc/best.json' % br])
    if r.returncode:
        return
    try:
        d = json.loads(r.stdout)
    except ValueError:
        return
    name = 'pc'
    best = d.get('best') or []
    for b in best:
        geno = norm({'sc': b['genome']})
        m = {'island': name, 'cid': cid_of(geno), 'base': bh, 'genome': geno, 'describe': describe(geno),
             'fitness': {'shrunk': b.get('shrunk', 0), 'n': b.get('n', 0)}, 'gen': d.get('gen'), 'scope': 'micro',
             'start': d.get('center', ''), 'time': d.get('updated', ''), 'transport': 'legacy'}
        p = os.path.join(farm, 'migrants', name, m['cid'] + '.json')
        if not os.path.exists(p) or json.load(open(p)).get('fitness') != m['fitness']:
            write_json(p, m)
    top = best[0] if best else None
    start = resolve(d.get('center') or 'default')
    write_json(os.path.join(farm, 'islands', name, 'status.json'), {
        'name': name, 'host': 'PC (weights GA, branch %s)' % br, 'scope': 'micro', 'start': d.get('center', ''),
        'jobs': '', 'gen': d.get('gen', 0), 'games': '', 'gps': 0, 'base': bh,
        'best': {'cid': cid_of(norm({'sc': top['genome']})), 'shrunk': top.get('shrunk', 0), 'n': top.get('n', 0),
                 'describe': describe(norm({'sc': top['genome']}), start)} if top else None,
        'exported': len(best), 'imported': 0, 'updated': d.get('updated', ''), 'code': br, 'transport': 'legacy'})


# --------------------------------------------------------------------------------------------------- the island
def home_of(A):
    if A.home:
        return A.home
    if A.farm and os.path.abspath(A.farm).startswith(SHARED):
        return os.path.join(A.farm, 'islands', A.name)
    return os.path.join('out', 'islands', A.name)


def prepare(A, home, scratch):
    """Build the instrumented template once per island (kept in home, so a restart reuses it)."""
    mp = os.path.join(home, 'meta.json')
    if os.path.exists(mp) and os.path.exists(os.path.join(home, 'template.wasm')):
        meta = json.load(open(mp))
        if meta.get('header') == T.HEADER and meta.get('scalars') == T.SCALARS:
            return meta
        print('genome layout changed: rebuilding the template (genotypes are kept, only cached games are lost)')
    bot = os.path.join(scratch, 'gabot_%d' % os.getpid())  # per process: two runs never edit the same copy
    T.write_src(A.base_bot, bot, T.to_ints(DEF, {}))
    ga.build(bot)
    w = ga.wasm_of(bot)
    off = T.find_genome(open(w, 'rb').read())
    os.makedirs(home, exist_ok=True)
    shutil.copy(w, os.path.join(home, 'template.wasm.tmp'))
    os.replace(os.path.join(home, 'template.wasm.tmp'), os.path.join(home, 'template.wasm'))
    meta = {'base_bot': A.base_bot, 'base_hash': base_hash(A.base_bot), 'offset': off, 'header': T.HEADER,
            'scalars': T.SCALARS, 'built': now(), 'host': socket.gethostname()}
    write_json(mp, meta)
    shutil.rmtree(os.path.join(scratch, 'cands'), ignore_errors=True)
    shutil.rmtree(bot, ignore_errors=True)
    print(f'template built: genome {T.LENGTH} ints ({len(T.SCALARS)} scalars) at byte {off}')
    return meta


def code_version():
    r = run_git(['rev-parse', '--abbrev-ref', 'HEAD'], cwd=HERE)
    c = run_git(['rev-parse', '--short', 'HEAD'], cwd=HERE)
    return '%s@%s' % (r.stdout.strip(), c.stdout.strip())


def pid_alive(pid):
    if WIN:
        r = subprocess.run(['tasklist', '/FI', 'PID eq %d' % pid, '/NH'], capture_output=True, text=True,
                           errors='replace')  # tasklist prints in the OEM code page
        return str(pid) in (r.stdout or '')
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def boot_id():
    """Changes when the machine (or a cloud container) restarts: a pid from an earlier boot means nothing."""
    try:
        return open('/proc/sys/kernel/random/boot_id').read().strip()
    except OSError:
        return ''


def running(home):
    p = os.path.join(home, 'pid.json')
    if not os.path.exists(p):
        return None
    try:
        d = json.load(open(p))
    except ValueError:
        return None
    if d.get('host') != socket.gethostname() or not pid_alive(d['pid']):
        return None
    if 'boot' not in d:  # pid.json of an island started before the boot check: alive if that pid runs island.py
        try:
            cmd = open('/proc/%d/cmdline' % d['pid'], 'rb').read().split(b'\0')
            return d if any(c.endswith(b'island.py') for c in cmd) and b'run' in cmd else None
        except OSError:
            return d if WIN else None
    return d if d['boot'] == boot_id() else None


def lower_priority():
    """Below-normal priority for this process and the games it starts (they inherit it)."""
    try:
        if WIN:
            import ctypes
            k = ctypes.windll.kernel32
            k.SetPriorityClass(k.GetCurrentProcess(), 0x00004000)  # BELOW_NORMAL_PRIORITY_CLASS
        else:
            os.nice(10)
    except Exception as e:  # noqa: BLE001  (never fatal)
        print('could not lower priority:', e)


def cmd_run(A):
    home, scratch = home_of(A), os.path.join(A.scratch, A.name)
    if A.low:
        lower_priority()
    os.makedirs(home, exist_ok=True)
    os.makedirs(scratch, exist_ok=True)
    other = running(home)
    if other and other['pid'] != os.getpid():
        sys.exit(f'island {A.name} already runs (pid {other["pid"]} since {other["started"]})')
    write_json(os.path.join(home, 'pid.json'), {'pid': os.getpid(), 'host': socket.gethostname(), 'boot': boot_id(),
                                                'started': now(),
                                                'args': sys.argv[1:]})
    if A.git_branch:
        git_setup(A)
        git_pull(A)
    meta = prepare(A, home, scratch)
    bh = meta['base_hash']
    statep = os.path.join(home, 'state.json')
    st = json.load(open(statep)) if os.path.exists(statep) else None
    seed = A.seed if A.seed is not None else zlib.crc32(A.name.encode()) % 100000
    inn = neat.Innov((st or {}).get('innov'))
    ev = Evolver(A.scope, A.sigma, inn, A.name)
    start = resolve(A.start)
    if st is None:
        rng = random.Random(seed)
        st = {'name': A.name, 'gen': 0, 'inds': {}, 'pop': [], 'history': [], 'seed': seed, 'start': A.start,
              'scope': A.scope, 'base_hash': bh, 'imported': [], 'exported': {}, 'games': 0}
        st['base'] = add(st, start, born=0, origin='start')
        tries = 0
        while len(st['pop']) < A.pop - 1 and tries < 1000:
            tries += 1
            cid = add(st, ev.mutate(start, rng), born=0, origin=A.name)
            if cid not in st['pop'] and cid != st['base']:
                st['pop'].append(cid)
    else:  # ids are hashes of the patched ints: re-key if the genome layout changed since the last run
        st = rekey(st)
    if st['inds'][st['base']]['geno'] != start:
        sys.exit(f'--start {A.start} differs from the control this island started with ({st["start"]}): '
                 'use a new --name')
    st['scope'] = A.scope
    B = Bench(home, scratch, A.jobs, meta)
    if A.fuel:  # e.g. 10000000: no fuel chaos, identical decisions give identical games (the macro GA's choice)
        B.extra = ['--fuel', str(A.fuel)]
    B.genomes = {'genome:start': start, 'genome:default': norm({})}
    for o in A.opps.split(','):
        if o.startswith('genome:') and o not in B.genomes:
            B.genomes[o] = resolve(o[len('genome:'):])
    pool = ga.map_pool(TRAIN, exclude=ga.SEALED + VALID)
    if len(pool) < A.maps:
        sys.exit(f'only {len(pool)} training maps found (run `cambc init --yes` for maps/)')
    logp = os.path.join(home, 'log.md')
    if not os.path.exists(logp):
        open(logp, 'w', newline='\n').write(
            f'island {A.name}, scope {A.scope}, start {A.start}, base {A.base_bot} ({bh})\n\n'
            '| gen | maps | games | min | rivals | control fit | mean delta | best new (delta) | best (shrunk, n) | '
            'best changes | in |\n|---|---|---|---|---|---|---|---|---|---|---|\n')
    print(f'island {A.name}: {len(pool)} training maps, scope {A.scope}, start {A.start}, home {home}', flush=True)
    for _ in range(A.gens):
        t0 = time.time()
        gen = st['gen']
        rng = random.Random(seed * 1000 + gen)
        # imports: other islands' best on the same base, not seen before
        imported = []
        if A.git_branch:
            git_pull(A)
            if A.farm:
                mirror(A.git_dir, A.farm, 'git')
        if A.legacy_branch and A.farm:
            legacy_pc(A, A.farm, bh)
        if A.imports:
            cands = []
            for d in farm_dirs(A):
                for m in read_migrants(d, bh):
                    tag = '%s/%s' % (m.get('island'), m.get('cid'))
                    if m.get('island') == A.name or m.get('base') != bh or tag in st['imported']:
                        continue
                    cands.append(m)
            seen = set()
            for m in sorted(cands, key=lambda m: -m.get('fitness', {}).get('shrunk', 0)):
                tag = '%s/%s' % (m.get('island'), m.get('cid'))
                if tag in seen or len(imported) >= A.imports:
                    continue
                seen.add(tag)
                st['imported'].append(tag)
                if cid_of(norm(m['genome'])) in st['inds']:  # we have it already (our own, or an echo)
                    continue
                cid = add(st, norm(m['genome']), born=gen, origin=m.get('island'))
                if cid != st['base'] and cid not in st['pop']:
                    imported.append(cid)
        if imported:
            st['pop'] = st['pop'][:max(0, A.pop - 1 - len(imported))] + imported
        # rivals: the fixed list plus the hall of fame (best migrant of the most recently active other islands)
        opps = [o for o in A.opps.split(',') if o and '@' not in o]
        pins = pinned(A.opps)
        hof = []
        if A.hof:
            best = {}
            for d in farm_dirs(A):
                for m in read_migrants(d, bh):
                    if m.get('island') == A.name or m.get('base') != bh:
                        continue
                    k = m.get('island')
                    if k not in best or m.get('fitness', {}).get('shrunk', 0) > best[k].get('fitness', {}).get('shrunk', 0):
                        best[k] = m
            for m in sorted(best.values(), key=lambda m: m.get('time', ''), reverse=True)[:A.hof]:
                key = 'genome:hof:%s/%s' % (m['island'], m['cid'])
                B.genomes[key] = norm(m['genome'])
                hof.append(key)
        # our own past champions stay rivals, so the population does not cycle against one opponent
        cur = ranked_ids(st)[:1]
        for c in [c for c in st.get('champions', []) if c not in cur][-A.own_hof:] if A.own_hof else []:
            key = 'genome:own:%s' % c
            B.genomes[key] = st['inds'][c]['geno']
            hof.append(key)
        opps += hof
        maps = rng.sample(pool, A.maps)
        bid = st['base']
        ids = [bid] + st['pop']
        wasm = {i: B.cand(st['inds'][i]['geno']) for i in ids}
        n0 = len(B.cache)
        # racing: everyone plays the first part of the maps; the worst part of the population stops there
        cut = max(1, int(math.ceil(len(maps) * A.race))) if A.race < 1 else len(maps)
        pin_games(B, [wasm[i] for i in ids], pins)

        def fit(i, ms):  # random-map rivals by weight (v44 up, sparring bots down) and the ghost games
            return wfit(B, i, opps, ms, pins, A)
        B.games([wasm[i] for i in ids], opps, maps[:cut])
        played_maps = {i: maps for i in ids}
        if cut < len(maps):
            c1 = fit(bid, maps[:cut])
            d1 = {i: fit(i, maps[:cut]) - c1 for i in st['pop']}
            elite = set(ranked_ids(st)[:A.elite])
            keep = set(sorted(st['pop'], key=lambda i: -d1[i])[:int(math.ceil(len(st['pop']) * A.keep))]) | elite
            B.games([wasm[i] for i in [bid] + [i for i in st['pop'] if i in keep]], opps, maps[cut:])
            for i in st['pop']:
                if i not in keep:
                    played_maps[i] = maps[:cut]
        played = len(B.cache) - n0
        st['games'] = st.get('games', 0) + played
        cfit_all = fit(bid, maps)
        cfit_cut = fit(bid, maps[:cut])
        deltas = {}
        for i in st['pop']:
            ms = played_maps[i]
            deltas[i] = fit(i, ms) - (cfit_all if ms is maps else cfit_cut)
            st['inds'][i]['deltas'].append(round(deltas[i], 5))
            flt = sum(B.cache.get(f'{i}|{B.opp(o)[0]}|{B.mkey(m)}|{s}', {}).get('flt', 0)
                      for o in opps for m in ms for s in (0, 1))
            if flt:
                st['inds'][i]['faults'] = st['inds'][i].get('faults', 0) + flt
        ranked = ranked_ids(st)
        if ranked and len(st['inds'][ranked[0]]['deltas']) >= 3 and ga.shrunk(st['inds'][ranked[0]]) > 0 and \
                ranked[0] not in st.setdefault('champions', []):
            st['champions'].append(ranked[0])
        best_new = max(st['pop'], key=lambda i: deltas[i])
        top = ranked[0] if ranked else best_new
        bt = st['inds'][top]
        secs = time.time() - t0
        h = {'gen': gen, 'maps': [os.path.basename(m) for m in maps], 'games': played, 'secs': round(secs),
             'rivals': [os.path.basename(o) for o in opps] + ['%s@%s' % (os.path.basename(r), os.path.basename(m)) for r, m, _ in pins],
             'control': round(cfit_all, 4),
             'mean_delta': round(sum(deltas.values()) / len(deltas), 4), 'best_new': best_new,
             'best_new_delta': round(deltas[best_new], 4), 'top': top, 'top_shrunk': round(ga.shrunk(bt), 4),
             'top_n': len(bt['deltas']), 'imported': imported, 'raced': sum(1 for i in st['pop'] if played_maps[i] is not maps)}
        st['history'].append(h)
        st['pop'] = next_pop(st, ranked, A, ev, rng)
        st['gen'] = gen + 1
        st['innov'] = inn.dump()
        write_json(statep, st)
        with open(logp, 'a', newline='\n') as f:
            f.write(f"| {gen} | {len(maps)} | {played} | {secs / 60:.1f} | {len(opps)} | {cfit_all:+.3f} | "
                    f"{h['mean_delta']:+.3f} | {best_new} ({h['best_new_delta']:+.3f}) | {top} ({h['top_shrunk']:+.3f}, "
                    f"{h['top_n']}) | {json.dumps(describe(bt['geno'], start))} | {len(imported)} |\n")
        print(f"{A.name} gen {gen}: {played} games {secs:.0f}s ({played / max(1, secs):.1f}/s) control {cfit_all:+.3f} "
              f"mean {h['mean_delta']:+.3f} best new {h['best_new_delta']:+.3f} top {top} {h['top_shrunk']:+.3f} "
              f"n={h['top_n']} in {len(imported)} raced {h['raced']}", flush=True)
        publish(A, st, home, bh, played / max(1.0, secs), ranked, start)


def pinned(spec):
    """Rivals tied to one map and side: 'bots/gh_x@maps_ghost/corners.map26a:0' (we play side 0 = team A).
    Ghost bots replay a top team's recorded route, so they only make sense on the map and side they were made on."""
    out = []
    for o in spec.split(','):
        if '@' not in o:
            continue
        rival, rest = o.split('@', 1)
        m, _, side = rest.rpartition(':') if rest.rsplit(':', 1)[-1] in ('0', '1') else (rest, '', '0')
        if os.path.exists(m) and (rival.startswith('genome:') or os.path.exists(rival)):
            out.append((rival, m, int(side)))
    return out


def pin_games(B, cands, pins):
    from concurrent.futures import ThreadPoolExecutor
    jobs = []
    for cid, cw in cands:
        for rival, m, side in pins:
            oh, ow = B.opp(rival)
            k = f'{cid}|{oh}|{B.mkey(m)}|{side}'
            if k not in B.cache:
                jobs.append((k,) + ((cw, ow) if side == 0 else (ow, cw)) + (m, side))
    jobs = list({j[0]: j for j in jobs}.values())
    if jobs:
        with ThreadPoolExecutor(B.jobs) as ex, open(B.cache_path, 'a') as log:
            for res in ex.map(B.play, jobs):
                if res['ok']:
                    B.cache[res['key']] = res
                    log.write(json.dumps(res) + '\n')


def pin_fit(B, cid, pins):
    if not pins:
        return 0.0
    tot = 0.0
    for rival, m, side in pins:
        x = B.cache.get(f'{cid}|{B.opp(rival)[0]}|{B.mkey(m)}|{side}')
        if x:
            tot += x['r'] + 0.1 * x['gm'] / 1000.0
    return tot / len(pins)


def rival_weight(o, A):
    """Weight of one random-map rival in the fitness. v44 (genome:start) weighs most: the macro GA thread (16 Oct)
    crowned a genome that only beat the caster sparring bots and lost the sealed gate vs v44 6-19."""
    if o == 'genome:start':
        return A.w_base
    if os.path.basename(o.rstrip('/\\')).startswith('spar'):
        return A.w_spar
    return 1.0


def wfit(B, h, opps, maps, pins, A):
    """Weighted fitness: random-map rivals by rival_weight, the pinned ghost games together weigh --w-ghosts."""
    w = {o: rival_weight(o, A) for o in opps}
    f = B.score(h, opps, maps, w)[0]
    wo = sum(w.values())
    wg = A.w_ghosts if pins else 0.0
    return (f * wo + pin_fit(B, h, pins) * wg) / max(1e-9, wo + wg)


def rekey(st):
    m = {i: cid_of(d['geno']) for i, d in st['inds'].items()}
    if all(i == j for i, j in m.items()):
        return st
    st['inds'] = {m[i]: d for i, d in st['inds'].items()}
    st['base'] = m[st['base']]
    st['pop'] = [m[i] for i in st['pop']]
    st['exported'] = {m.get(i, i): g for i, g in st['exported'].items()}
    st['champions'] = [m[c] for c in st.get('champions', []) if c in m]
    print('genome layout changed: %d genomes re-keyed' % len(m))
    return st


def add(st, geno, born, origin):
    geno = norm(geno)
    cid = cid_of(geno)
    if cid not in st['inds']:
        st['inds'][cid] = {'geno': geno, 'deltas': [], 'born': born, 'origin': origin}
    return cid


def ranked_ids(st):
    ev = [i for i, d in st['inds'].items() if d['deltas'] and i != st['base'] and not d.get('faults')]
    return sorted(ev, key=lambda i: ga.shrunk(st['inds'][i]), reverse=True)


def next_pop(st, ranked, A, ev, rng):
    inds = st['inds']
    elites = ranked[:A.elite]
    parents = ranked[:max(A.elite, A.pop // 2)] or [st['base']]

    def tour():
        c = rng.sample(parents, min(3, len(parents)))
        return max(c, key=lambda i: ga.shrunk(inds[i]))
    new = list(elites)
    tries = 0
    while len(new) < A.pop - 1 and tries < 1000:
        tries += 1
        a, b = tour(), tour()
        if ga.shrunk(inds[b]) > ga.shrunk(inds[a]):
            a, b = b, a
        g = ev.cross(inds[a]['geno'], inds[b]['geno'], rng) if rng.random() < 0.6 else copy.deepcopy(inds[a]['geno'])
        g = ev.mutate(g, rng)
        cid = add(st, g, born=st['gen'] + 1, origin=A.name)
        if cid in new or cid == st['base']:
            continue
        new.append(cid)
    return new


def publish(A, st, home, bh, gps, ranked, start):
    """Export the top genomes as migrants, write the status, regenerate the board, sync git."""
    top = [i for i in ranked if len(st['inds'][i]['deltas']) >= A.min_n and ga.shrunk(st['inds'][i]) > 0][:A.export_top]
    mig = {}
    for i in top:
        d = st['inds'][i]
        mig[i] = {'island': A.name, 'cid': i, 'base': bh, 'genome': d['geno'], 'describe': describe(d['geno']),
                  'vs_start': describe(d['geno'], start),
                  'fitness': {'shrunk': round(ga.shrunk(d), 4), 'n': len(d['deltas']), 'deltas': d['deltas'][-8:]},
                  'gen': st['gen'], 'scope': A.scope, 'start': A.start, 'time': now(),
                  'transport': 'git' if A.git_branch and not A.farm else 'shared'}
        st['exported'][i] = st['gen']
    write_json(os.path.join(home, 'state.json'), st)
    bt = st['inds'][ranked[0]] if ranked else None
    status = {'name': A.name, 'host': socket.gethostname(), 'scope': A.scope, 'start': A.start, 'jobs': A.jobs,
              'gen': st['gen'], 'games': st.get('games', 0), 'gps': round(gps, 2), 'base': bh,
              'best': {'cid': ranked[0], 'shrunk': round(ga.shrunk(bt), 4), 'n': len(bt['deltas']),
                       'describe': describe(bt['geno'], start)} if bt else None,
              'exported': len(st['exported']), 'imported': len(st['imported']), 'updated': now(),
              'code': code_version(), 'home': os.path.abspath(home),
              'transport': 'git' if A.git_branch and not A.farm else 'shared'}

    def write(d):
        write_json(os.path.join(d, 'islands', A.name, 'status.json'), status)
        for i, m in mig.items():
            write_json(os.path.join(d, 'migrants', A.name, i + '.json'), m)
        if A.farm and d != A.farm:  # bridge: the shared folder's islands go to git too
            mirror(A.farm, d, 'shared')
        board(d)
    if A.farm:
        write(A.farm)
    if A.git_branch and not A.git_readonly:
        git_push(A, write, f'island {A.name} gen {st["gen"]}')


# ----------------------------------------------------------------------------------------------------- commands
def cmd_ensure(A):
    """Start `run` with the same arguments in the background unless this island already runs on this host."""
    home = home_of(A)
    r = running(home)
    if r:
        print(f'island {A.name} runs (pid {r["pid"]} since {r["started"]})')
        return
    os.makedirs(home, exist_ok=True)
    args = [sys.executable, os.path.abspath(__file__)] + ['run' if a == 'ensure' else a for a in sys.argv[1:]]
    log = open(os.path.join(home, 'run.log'), 'a')
    # CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP: one hidden console that every child (cambc, git) inherits
    kw = {'creationflags': 0x08000000 | 0x00000200} if WIN else {'start_new_session': True}
    p = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, **kw)
    print(f'island {A.name} started (pid {p.pid}), log {os.path.join(home, "run.log")}')


def cmd_stop(A):
    r = running(home_of(A))
    if not r:
        print('not running')
        return
    if WIN:
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(r['pid'])])
    else:
        os.killpg(os.getpgid(r['pid']), 15) if os.getpgid(r['pid']) == r['pid'] else os.kill(r['pid'], 15)
    print(f'stopped pid {r["pid"]}')


def cmd_board(A):
    for d in farm_dirs(A):
        board(d)
        print(open(os.path.join(d, 'BOARD.md')).read())


def cmd_validate(A):
    home = home_of(A)
    st = json.load(open(os.path.join(home, 'state.json')))
    meta = json.load(open(os.path.join(home, 'meta.json')))
    B = Bench(home, os.path.join(A.scratch, A.name), A.jobs, meta)
    B.genomes = {'genome:start': st['inds'][st['base']]['geno'], 'genome:default': norm({})}
    opps = [o for o in A.opps.split(',') if '@' not in o]
    for o in opps:
        if o.startswith('genome:') and o not in B.genomes:
            B.genomes[o] = resolve(o[len('genome:'):])
    maps = ga.map_pool(A.maps.split(',') if A.maps else VALID)
    ids = A.ids.split(',') if A.ids else [i for i in ranked_ids(st) if len(st['inds'][i]['deltas']) >= A.min_n][:A.top]
    bid = st['base']
    B.games([B.cand(st['inds'][i]['geno']) for i in [bid] + ids], opps, maps)
    out = [f'island {A.name} validation {now()} on {len(maps)} maps, both sides, vs {", ".join(opps)}']
    cf, cper = B.score(bid, opps, maps)
    out.append(f"control {bid}: fit {cf:+.3f} " + ' '.join(f"{os.path.basename(o)} {v['won2']}-{v['lost2']}" for o, v in cper.items()))
    for i in ids:
        f, per = B.score(i, opps, maps)
        better = worse = 0
        for ob in opps:
            oh = B.opp(ob)[0]
            for m in maps:
                k = B.mkey(m)
                a = sum(B.cache[f'{i}|{oh}|{k}|{s}']['r'] for s in (0, 1))
                b = sum(B.cache[f'{bid}|{oh}|{k}|{s}']['r'] for s in (0, 1))
                better += a > b
                worse += a < b
        out.append(f"{i}: fit {f:+.3f} (delta {f - cf:+.3f}) " + ' '.join(
            f"{os.path.basename(o)} {v['won2']}-{v['lost2']}" for o, v in per.items()) +
            f" | pairs better/worse than control {better}-{worse} p={ga.sign_p(better, worse):.3f} | "
            f"{json.dumps(describe(st['inds'][i]['geno']))}")
    txt = '\n'.join(out)
    print(txt)
    open(os.path.join(home, 'validate.txt'), 'a').write(txt + '\n\n')


def cmd_export(A):
    """A normal bot folder playing exactly like the candidate (same instrumented source with the genome baked into
    the array) and <out>.json with the genome (usable as --start or as a rival genome:<out>.json)."""
    if A.migrant:
        geno = norm(json.load(open(A.migrant))['genome'])
    else:
        st = json.load(open(os.path.join(home_of(A), 'state.json')))
        geno = st['inds'][A.id]['geno']
    T.write_src(A.base_bot, A.out, to_ints(geno))
    write_json(A.out.rstrip('/\\') + '.json', {'genome': geno, 'scalars': scalars(geno), 'describe': describe(geno),
                                               'base': base_hash(A.base_bot)})
    print(f'{A.out}: {json.dumps(describe(geno))}')


# ------------------------------------------------------------------------------------------------- champion
FUELGUARD_REF = 'origin/claude/fuel-skipped-turns-004urj'  # PR #23: study27-economy + P_FUELGUARD (+ P_MONO)
# The online bot since 16 Oct 15:20 = mybot_online1252_jackgo_imp.zip = this zip (v44 + contest fix + fuel guard +
# jackpot + stampede rule) built with genome 'online1520' (ga65a6 + im_p as genes): 36/36 identical games, unlimited fuel
ONLINE_ZIP = '/mnt/project-files/bot/mybot_online1252_jackgo.zip'


def overlay_src(A, scratch):
    """The base bot of --overlay-ref (a git ref holding bots/study27-economy with extra fixes, e.g. the fuel guard),
    extracted into scratch. None when no overlay."""
    if A.overlay_ref.endswith('.zip'):  # a bot zip (e.g. the online bot): its src/
        import zipfile
        out = os.path.join(scratch, 'overlay')
        shutil.rmtree(out, ignore_errors=True)
        os.makedirs(os.path.join(out, 'src'))
        with zipfile.ZipFile(A.overlay_ref) as zf:
            for n in zf.namelist():
                if n.startswith('src/') and not n.endswith('/'):
                    open(os.path.join(out, 'src', os.path.basename(n)), 'wb').write(zf.read(n).replace(b'\r\n', b'\n'))
        return out
    if not A.overlay_ref:
        return None
    ref = A.overlay_ref
    run_git(['fetch', '-q', 'origin', ref.split('origin/', 1)[-1]])
    out = os.path.join(scratch, 'overlay')
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(os.path.join(out, 'src'))
    names = run_git(['ls-tree', '--name-only', ref + ':' + A.base_bot.replace('\\', '/') + '/src'], check=True).stdout.split()
    for n in names:
        blob = subprocess.run(['git', 'show', '%s:%s/src/%s' % (ref, A.base_bot.replace('\\', '/'), n)],
                              capture_output=True, check=True).stdout
        open(os.path.join(out, 'src', n), 'wb').write(blob.replace(b'\r\n', b'\n'))
    return out


def write_bot(A, ints, out, overlay, scratch):
    """A normal bot folder with the genome: the instrumented source of the base, carried onto the overlay base by a
    3-way merge (overlay + (instrumented - base)); conflicts that only touch the overlay's fuel-profile markers
    take the instrumented side."""
    T.write_src(A.base_bot, out, ints)
    if not overlay:
        return
    lit = os.path.join(scratch, 'lit')
    olit = os.path.join(scratch, 'olit')
    for src, dst in ((A.base_bot, lit), (overlay, olit)):
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(os.path.join(src, 'src'), os.path.join(dst, 'src'))
        for fname in os.listdir(os.path.join(dst, 'src')):
            q = os.path.join(dst, 'src', fname)
            b = open(q, 'rb').read()
            open(q, 'wb').write(b.replace(b'\r\n', b'\n'))
        for fname, o, n in G.LITERALS:
            q = os.path.join(dst, 'src', fname)
            t = open(q, newline='').read()
            open(q, 'w', newline='\n').write(t.replace(o, n))
        q = os.path.join(dst, 'src', 'params.h')  # genome genes are defined by the genome section only
        if os.path.exists(q):
            pl = open(q, newline='').read().split('\n')
            open(q, 'w', newline='\n').write('\n'.join(l for l in pl if not (l.strip().startswith('#define ') and
                                                                            l.split()[1] in T.SCALARS)))
    for fname in os.listdir(os.path.join(out, 'src')):
        mine = os.path.join(out, 'src', fname)
        base = os.path.join(lit, 'src', fname)
        theirs = os.path.join(olit, 'src', fname)
        if not os.path.exists(base) or not os.path.exists(theirs):
            continue  # ga_struct.h: ours only
        merged = os.path.join(scratch, 'merged_' + fname)
        shutil.copy(theirs, merged)
        r = subprocess.run(['git', 'merge-file', '-p', merged, base, mine], capture_output=True)
        text = r.stdout
        if r.returncode:
            # resolve each conflict: keep the instrumented side, plus the overlay side's lines that are not FP markers
            lines, outl, side = text.decode().split('\n'), [], None
            for l in lines:
                if l.startswith('<<<<<<< '):
                    side, ov, mine_l = 'ov', [], []
                elif l.startswith('=======') and side == 'ov':
                    side = 'mine'
                elif l.startswith('>>>>>>> ') and side == 'mine':
                    if fname == 'params.h':  # params: both sides (the overlay's switches, then our genome)
                        outl[len(outl) - len(mine_l):len(outl) - len(mine_l)] = ov
                    side = None
                elif side == 'ov':
                    ov.append(l)
                else:
                    if side == 'mine':
                        mine_l.append(l)
                    outl.append(l)
            text = '\n'.join(outl).encode()
            if fname != 'params.h' and extra_lost(lines):
                print('warning: %s: overlay lines inside merge conflicts were dropped: %s' % (fname, extra_lost(lines)))
        open(mine, 'wb').write(text)


def extra_lost(lines):
    """Overlay-side lines inside conflicts that are neither FP markers nor present on our side."""
    out, side, ov, mine = [], None, [], []
    for l in lines:
        if l.startswith('<<<<<<< '):
            side, ov, mine = 'ov', [], []
        elif l.startswith('=======') and side == 'ov':
            side = 'mine'
        elif l.startswith('>>>>>>> ') and side == 'mine':
            ms = {x.strip() for x in mine}
            out += [x.strip() for x in ov if x.strip() and not x.strip().startswith('FP(') and x.strip() not in ms]
            side = None
        elif side == 'ov':
            ov.append(l)
        elif side == 'mine':
            mine.append(l)
    return out


def cmd_champion(A):
    """Final local tournament: every island's best genomes, built as the bot we would upload (overlay = fuel guard),
    against the full rival pool on the sealed maps, each judged against the control built the same way."""
    farm = A.farm
    scratch = os.path.join(A.scratch, 'champion')
    os.makedirs(scratch, exist_ok=True)
    bh = base_hash(A.base_bot)
    cands = {}
    for m in read_migrants(farm, bh):
        if m.get('base') != bh:
            continue
        key = cid_of(norm(m['genome']))
        f = m.get('fitness', {}).get('shrunk', 0)
        isl = m.get('island')
        if m.get('fitness', {}).get('n', 0) < A.min_n:  # a leader of one or two generations is mostly selection luck
            continue
        if key not in cands or f > cands[key]['fit']:
            cands[key] = {'geno': norm(m['genome']), 'fit': f, 'island': isl}
    by_isl = {}
    for k, c in cands.items():
        by_isl.setdefault(c['island'], []).append((c['fit'], k))
    finalists = []
    for isl, lst in by_isl.items():
        finalists += [k for f, k in sorted(lst, reverse=True)[:A.per_island] if f > 0]
    start = resolve(A.start)
    ctl = cid_of(start)
    finalists = [k for k in finalists if k != ctl]
    if A.ids:
        finalists = A.ids.split(',')
    print(f'{len(finalists)} finalists from {len(by_isl)} islands, control {A.start} ({ctl})', flush=True)
    overlay = overlay_src(A, scratch)
    genos = dict({k: cands[k]['geno'] for k in finalists if k in cands}, **{ctl: start})
    if A.graft:  # each finalist also with the graft (e.g. the online bot's im_p on genomes evolved without it)
        for k in list(finalists):
            g2 = norm({**genos[k], 'sc': dict(scalars(genos[k]), **json.loads(A.graft))})
            k2 = cid_of(g2)
            if k2 not in genos:
                genos[k2] = g2
                finalists.append(k2)
                cands[k2] = {'island': cands.get(k, {}).get('island', '') + '+graft', 'geno': g2, 'fit': 0}
    bots = {}
    for k in [ctl] + finalists:
        out = os.path.join(scratch, 'bot_' + k)
        if not os.path.exists(ga.wasm_of(out)):
            write_bot(A, to_ints(genos[k]), out, overlay, scratch)
            ga.build(out)
        bots[k] = ga.md5(ga.wasm_of(out)), ga.wasm_of(out)
    home = os.path.join(farm, 'champion')
    os.makedirs(home, exist_ok=True)
    meta = {'offset': 0}
    B = Bench.__new__(Bench)
    B.work, B.jobs, B.extra, B.meta = scratch, A.jobs, [], meta
    B.cache_path = os.path.join(home, 'games.jsonl')
    B.cache = {}
    if os.path.exists(B.cache_path):
        for line in open(B.cache_path):
            try:
                d = json.loads(line)
                B.cache[d['key']] = d
            except ValueError:
                pass
    B.opp_wasm, B.map_md5, B.genomes = {}, {}, {}
    os.makedirs(os.path.join(scratch, 'tmp'), exist_ok=True)
    opps = [o for o in A.opps.split(',') if o and '@' not in o]
    prev = os.path.join(home, 'champion.json')
    if os.path.exists(prev):  # the last champion stays a rival
        opps.append('genome:' + prev)
    for o in opps:  # genome rivals (v44 = start, past champions) are built like the finalists
        if o.startswith('genome:'):
            g = start if o == 'genome:start' else resolve(o[len('genome:'):])
            out = os.path.join(scratch, 'opp_' + cid_of(g))
            if not os.path.exists(ga.wasm_of(out)):
                write_bot(A, to_ints(g), out, overlay, scratch)
                ga.build(out)
            B.opp_wasm[o] = ga.md5(ga.wasm_of(out)), ga.wasm_of(out)
    pins = pinned(A.opps)
    maps = ga.map_pool(A.maps.split(','))
    if A.max_maps and len(maps) > A.max_maps:  # --map-offset 60: the next maps of the same shuffle (a fresh check)
        maps = random.Random(7).sample(maps, len(maps))[A.map_offset:A.map_offset + A.max_maps]
    cl = [(bots[k][0], bots[k][1]) for k in [ctl] + finalists]
    print(f'{len(cl)} bots x {len(opps)} rivals x {len(maps)} maps x 2 sides + {len(pins)} ghost games', flush=True)
    pin_games(B, cl, pins)
    B.games(cl, opps, maps)

    def fit(h):
        return wfit(B, h, opps, maps, pins, A)
    ch = bots[ctl][0]
    cf, cper = fit(ch), B.score(ch, opps, maps)[1]
    rows = []
    for k in finalists:
        h = bots[k][0]
        better = worse = vb = vw = 0
        for ob in opps:
            oh = B.opp(ob)[0]
            for m in maps:
                mk = B.mkey(m)
                a = sum(B.cache.get(f'{h}|{oh}|{mk}|{s}', {}).get('r', 0) for s in (0, 1))
                b = sum(B.cache.get(f'{ch}|{oh}|{mk}|{s}', {}).get('r', 0) for s in (0, 1))
                better += a > b
                worse += a < b
                if ob == 'genome:start':  # head to head vs v44: a winner must not be worse here
                    vb += a > b
                    vw += a < b
        per = B.score(h, opps, maps)[1]
        rows.append({'cid': k, 'island': cands.get(k, {}).get('island', ''), 'delta': fit(h) - cf,
                     'better': better, 'worse': worse, 'p': ga.sign_p(better, worse), 'v44': (vb, vw),
                     'per': {os.path.basename(o): '%d-%d' % (v['won2'], v['lost2']) for o, v in per.items()},
                     'ghosts': pin_fit(B, h, pins), 'describe': describe(genos[k], start),
                     'dth': sum(v['dth'] for o, v in per.items() if rival_weight(o, A) == A.w_spar) /
                            max(1, sum(1 for o in per if rival_weight(o, A) == A.w_spar)),
                     'dth44': per.get('genome:start', {}).get('dth', 0.0),
                     'cast': (better - vb, worse - vw)})
    rows.sort(key=lambda r: -r['delta'])
    lines = ['# GA farm champion', '', f'Tournament {now()}: {len(finalists)} finalists (top {A.per_island} of each '
             f'island), built as uploaded (overlay `{A.overlay_ref or "none"}`), vs {", ".join(opps)} on {len(maps)} '
             f'sealed maps both sides, plus {len(pins)} ghost games. Control = {A.start} built the same way: fit '
             f'{cf:+.3f}, ' + ', '.join(f'{os.path.basename(o)} {v["won2"]}-{v["lost2"]}' for o, v in cper.items()) +
             f', ghosts {pin_fit(B, ch, pins):+.2f}.', '',
             f'Fitness weights: start bot x{A.w_base:g}, each sparring bot x{A.w_spar:g}, ghost games together x{A.w_ghosts:g}, '
             'other rivals x1. A champion needs delta > 0 and pairs vs the start bot not worse.', '',
             f'Deaths per game vs the caster sparring bots: control '
             f'{sum(v["dth"] for o, v in cper.items() if rival_weight(o, A) == A.w_spar) / max(1, sum(1 for o in cper if rival_weight(o, A) == A.w_spar)):.2f}, '
             f'vs the start bot {cper.get("genome:start", {}).get("dth", 0.0):.2f}.', '',
             '| rank | genome | island | delta vs control | pairs better-worse (p) | pairs vs the start bot | pairs vs others | deaths vs casters / start bot | maps won-lost both sides per rival | ghosts | changes vs control |',
             '|---|---|---|---|---|---|---|---|---|---|---|']
    for n, r in enumerate(rows, 1):
        lines.append(f"| {n} | {r['cid']} | {r['island']} | {r['delta']:+.3f} | {r['better']}-{r['worse']} ({r['p']:.3f}) | {r['v44'][0]}-{r['v44'][1]} | {r['cast'][0]}-{r['cast'][1]} | {r['dth']:.2f} / {r['dth44']:.2f} | "
                     f"{' '.join(f'{a} {b}' for a, b in r['per'].items())} | {r['ghosts']:+.2f} | {json.dumps(r['describe'])} |")
    ok = [r for r in rows if r['delta'] > 0 and r['v44'][0] >= r['v44'][1]]
    if ok:
        win = ok[0]
        top = win['cid']
        z = os.path.join(A.zip_dir, 'mybot_%s.zip' % top)
        os.makedirs(A.zip_dir, exist_ok=True)
        import zipfile
        with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
            src = os.path.join(scratch, 'bot_' + top, 'src')
            for f in sorted(os.listdir(src)):
                zf.write(os.path.join(src, f), 'src/' + f)
        write_json(os.path.join(home, 'champion.json'), {'cid': top, 'genome': genos[top], 'zip': z, 'row': win,
                                                         'time': now()})
        lines += ['', f'Champion: **{top}** ({win["island"]}), zip `{z}` (not uploaded). '
                  f'{"Significant" if win["p"] < 0.05 else "Not significant"} vs the control (p={win["p"]:.3f}), '
                  f'pairs vs the start bot {win["v44"][0]}-{win["v44"][1]}.']
    else:
        lines += ['', 'No finalist beats the control without losing to the start bot: no zip.']
    txt = '\n'.join(lines) + '\n'
    with open(os.path.join(farm, 'CHAMPION.md'), 'w', newline='\n') as f:
        f.write(txt)
    print(txt)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)

    def common(s):
        s.add_argument('--name', required=True, help='island name, unique across the farm (e.g. cloud-a, pc)')
        s.add_argument('--farm', default='', help='farm folder shared with other islands (cloud: /mnt/project-files/ga-farm)')
        s.add_argument('--git-branch', default='', help='also exchange through this git branch (the PC: ga-farm)')
        s.add_argument('--git-dir', default=os.path.join('out', 'farm-git'), help='local clone of that branch')
        s.add_argument('--git-remote', default='', help='remote URL (default: origin of this checkout)')
        s.add_argument('--git-readonly', action='store_true', help='only read the branch (import), never push')
        s.add_argument('--w-base', type=float, default=3.0, help='fitness weight of v44 (genome:start)')
        s.add_argument('--w-spar', type=float, default=0.5, help='fitness weight of each sparring bot (we beat them 2:1)')
        s.add_argument('--w-ghosts', type=float, default=1.0, help='fitness weight of all ghost games together')
        s.add_argument('--low', type=int, default=1, help='1 = run at low priority (the machine stays usable)')
        s.add_argument('--legacy-branch', default='', help='bridge: read the old PC weights GA from this branch '
                                                           '(pc-island, islands/pc/best.json) into the farm')
        s.add_argument('--home', default='', help='checkpoint folder (default: <farm>/islands/<name> in the shared '
                                                  'folder, else out/islands/<name>)')
        s.add_argument('--scratch', default=os.path.join('out', 'islands-scratch'), help='local candidate wasm files')
        s.add_argument('--base-bot', default='bots/study27-economy')
        s.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
        s.add_argument('--opps', default=DEFAULT_OPPS, help='rivals: bot folders, .wasm files or genome:<spec> '
                       '(start, default, a sga preset id like ga65a6, or a migrant/export JSON)')
    for name in ('run', 'ensure'):
        s = sub.add_parser(name)
        common(s)
        s.add_argument('--scope', default='all', help='comma list of micro, structure, macro, gp, neat; or all')
        s.add_argument('--start', default='ga65a6', help='start genome = control (default ga65a6 = v44 online)')
        s.add_argument('--gens', type=int, default=100000)
        s.add_argument('--pop', type=int, default=16)
        s.add_argument('--maps', type=int, default=8, help='maps per generation, each played both sides vs every rival')
        s.add_argument('--race', type=float, default=0.5, help='share of the maps every candidate plays (1 = no racing)')
        s.add_argument('--keep', type=float, default=0.5, help='share of the population that plays the rest')
        s.add_argument('--elite', type=int, default=4)
        s.add_argument('--sigma', type=float, default=0.12)
        s.add_argument('--seed', type=int, default=None)
        s.add_argument('--imports', type=int, default=2, help='migrants taken in per generation')
        s.add_argument('--export-top', type=int, default=3)
        s.add_argument('--min-n', type=int, default=3, help='generations evaluated before a genome may migrate')
        s.add_argument('--fuel', type=int, default=0, help='cambc --fuel for training games (0 = the real budget)')
        s.add_argument('--own-hof', type=int, default=2, help='our own past champions kept as rivals')
        s.add_argument('--hof', type=int, default=2, help='rivals taken from other islands\' best (hall of fame)')
    s = sub.add_parser('stop'); common(s)
    s = sub.add_parser('board'); common(s)
    s = sub.add_parser('validate'); common(s)
    s.add_argument('--top', type=int, default=3); s.add_argument('--min-n', type=int, default=3)
    s.add_argument('--ids', default=''); s.add_argument('--maps', default='', help='map globs (default v100)')
    s = sub.add_parser('champion'); common(s)
    s.add_argument('--start', default='online1520', help='the control (the online bot: online1520, or v44: ga65a6)')
    s.add_argument('--graft', default='', help='JSON scalars also tried on top of every finalist, e.g. {"P_IM_PAIRED": 1}')
    s.add_argument('--per-island', type=int, default=2)
    s.add_argument('--ids', default='', help='finalists by cid instead of the islands\' best')
    s.add_argument('--maps', default='maps_hold60/*.map26a,maps_dev200/*.map26a', help='sealed map globs')
    s.add_argument('--min-n', type=int, default=4, help='finalists: generations evaluated on their island (>= 32 maps)')
    s.add_argument('--map-offset', type=int, default=0, help='skip this many maps of the shuffled sealed set')
    s.add_argument('--max-maps', type=int, default=120)
    s.add_argument('--overlay-ref', default=ONLINE_ZIP if os.path.exists(ONLINE_ZIP) else FUELGUARD_REF, help='git ref whose base bot the zip is built on ('' = none)')
    s.add_argument('--zip-dir', default=os.path.join(SHARED, 'bot') if os.path.isdir(SHARED) else os.path.join('out', 'bot'))
    s = sub.add_parser('export'); common(s)
    s.add_argument('--id', default=''); s.add_argument('--migrant', default=''); s.add_argument('--out', required=True)
    A = p.parse_args()
    {'run': cmd_run, 'ensure': cmd_ensure, 'stop': cmd_stop, 'board': cmd_board, 'validate': cmd_validate,
     'export': cmd_export, 'champion': cmd_champion}[A.cmd](A)


if __name__ == '__main__':
    main()
