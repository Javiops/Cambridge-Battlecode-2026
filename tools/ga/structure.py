"""Structure genome of the genetic algorithm: what the micro does, not only its thresholds (levels 1-3).

The weight genes of genome.py stay as they are; this module adds, in one patchable array of the bot:
  level 1  switch genes (existing P_* fight switches, on/off or a small int), one on/off gene per micro rule
           (P_R_*) and one order gene per rule (P_O_*: rules run sorted by it; random-key encoding of a permutation);
  level 2  two postfix programs (GP0 = "back off from this group", GP1 = "engage this target") run by the bot's
           interpreter in ga_struct.h over the FEATURES below;
  level 3  one NEAT network (topologically ordered nodes, connection triples) choosing the action while enemies
           are in sight.

The bot side is `ga_struct.h` (interpreter, net, defaults) plus `struct.patch` (play_turn's micro section as a
rule list). With the default genome the bot plays exactly like the base: `sga.py check` measures it with
unlimited fuel, where games must be identical.
"""
import hashlib, os, shutil, struct, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genome as G
import macro as M

HERE = os.path.dirname(os.path.abspath(__file__))

# Switch genes. name: (default = the base bot's value, lo, hi, kind, what it decides). kind 'bool' flips on mutation.
SWITCHES = {
    'P_FRONT':        (1, 0, 1, 'bool', 'front-line rule (hold behind our tank when a fight is on)'),
    'P_KITE':         (1, 0, 1, 'bool', 'kite rule (caster draft: step back while shooting)'),
    'P_WALKHOME':     (0, 0, 1, 'bool', 'walk-home rule (hurt and not safe to recall: walk to spawn)'),
    'P_HITFIRST':     (1, 0, 1, 'bool', 'hit before fleeing when a hit is ready'),
    'P_SAFESTEP':     (1, 0, 1, 'bool', 'back off by the safest step instead of straight home'),
    'P_RETREAT':      (0, 0, 1, 'bool', 'back off: step away from enemies (1) or head for spawn (0), without SAFESTEP'),
    'P_NOCHASE':      (1, 0, 1, 'bool', 'a foe walking away out of reach is no longer a target'),
    'P_FRONT_LOCAL':  (1, 0, 1, 'bool', 'front line only with an ally close and not outnumbered'),
    'P_SHOOT':        (1, 0, 2, 'int',  'shoot back while fleeing: 0 no, 1 basic attack, 2 also spells'),
    'P_GANG':         (0, 0, 4, 'int',  'gang up on a lone hurt foe with this many of us (0 = off)'),
    'P_CALLHELP':     (0, 0, 1, 'bool', 'call allies onto the foe hitting us, answer their calls'),
    'P_TWIN':         (0, 0, 1, 'bool', 'twin guard (stay next to the ally being hit)'),
    'P_ALLYDUTY':     (0, 0, 1, 'bool', 'a foe next to an ally becomes our target'),
    'P_CARRY':        (0, 0, 80, 'int', 'carrying this many gems: avoid unfavourable fights (0 = off)'),
    'P_U34_ENGAGE_FALLBACK': (0, 0, 1, 'bool', 'an engage that does nothing falls through to the next rule'),
}
RULES = ['FLEE', 'NEARRECALL', 'FM', 'KITE', 'FRONT', 'AVOIDLOW', 'AVOID', 'ENGAGE', 'RECALLSHOP', 'WALKHOME']
RULE_DOC = {
    'FLEE': 'below the flee % hp: tribute if on an altar, recall if safe, else run',
    'NEARRECALL': 'caster draft: hurt and 4-6 tiles out of the fight: recall',
    'FM': 'fight-mode model (P_FM, off in the base)',
    'KITE': 'caster draft kite (P_KITE)', 'FRONT': 'front line (P_FRONT)',
    'AVOIDLOW': 'below P_LOWHP with a foe within 6: back off', 'AVOID': 'unfavourable group close: back off',
    'ENGAGE': 'engage the target (killable, channelling, reachable and favourable, helping)',
    'RECALLSHOP': 'recall to heal / shop when safe, capture-recall', 'WALKHOME': 'walk home (P_WALKHOME)'}
for r in ['FLEE', 'NEARRECALL', 'AVOIDLOW', 'AVOID', 'ENGAGE', 'RECALLSHOP']:
    SWITCHES['P_R_' + r] = (1, 0, 1, 'bool', 'rule %s on: %s' % (r, RULE_DOC[r]))
for i, r in enumerate(RULES):
    SWITCHES['P_O_' + r] = (10 * (i + 1), 0, 110, 'order', 'order key of rule %s (lower runs first)' % r)
SWITCHES['P_GP0_ON'] = (0, 0, 1, 'bool', 'rule AVOID uses evolved program GP0 instead of its fixed condition')
SWITCHES['P_GP1_ON'] = (0, 0, 1, 'bool', 'rule ENGAGE uses evolved program GP1 instead of its fixed condition')
SWITCHES['P_NN_ON'] = (0, 0, 1, 'bool', 'the evolved net picks the action while enemies are in sight')

L1_GENES = [k for k in SWITCHES if not k.startswith(('P_GP', 'P_NN'))]

# Fight features, in the order of ga_struct.h GaFeat (level 2 terminals, level 3 inputs).
FEATURES = ['HP', 'NEAR', 'F4', 'F8', 'A4', 'A8', 'RATIO', 'ERATIO', 'FAV', 'KILL', 'REACH', 'THP', 'TDIST', 'GEMS',
            'HOME', 'DANGER', 'SPAWN', 'TCHAN', 'HELP', 'CASTERS', 'ROUND', 'HIT', 'NB', 'EB', 'RANGED']
BOOL_FEATURES = {'FAV', 'KILL', 'REACH', 'SPAWN', 'TCHAN', 'HELP', 'CASTERS', 'HIT', 'RANGED'}
# typical range of each feature (constants drawn near it by the GP)
FEATURE_RANGE = {'HP': (0, 100), 'NEAR': (0, 20), 'F4': (0, 5), 'F8': (0, 5), 'A4': (0, 4), 'A8': (0, 4),
                 'RATIO': (0, 400), 'ERATIO': (0, 400), 'THP': (0, 100), 'TDIST': (0, 20), 'GEMS': (0, 100),
                 'HOME': (0, 40), 'DANGER': (0, 300), 'ROUND': (0, 200), 'NB': (1, 5), 'EB': (0, 5)}

PROG_LEN = 48                       # GA_PROG_LEN
NN_NODES, NN_CONN, NN_OUT = 32, 128, 7
NN_LEN = 2 + NN_NODES + 3 * NN_CONN  # GA_NN_LEN
ACTIONS = ['default', 'engage', 'kite', 'back off', 'flee', 'recall', 'farm']
BLOCKS = [('GA_GP0', PROG_LEN), ('GA_GP1', PROG_LEN), ('GA_NN', NN_LEN)]

SCALARS = list(G.NAMES) + list(SWITCHES) + list(M.NAMES)  # macro genes appended (island.py, 16 Oct)
MAGIC = (0x31534147, 0x5EED5678)  # 'GAS1', then a second word
HEADER = [MAGIC[0], MAGIC[1], len(SCALARS), sum(n for _, n in BLOCKS)]
LENGTH = len(SCALARS) + sum(n for _, n in BLOCKS)


def spec(name):
    if name in G.GENES:
        d, lo, hi, _ = G.GENES[name]
        return d, lo, hi, 'int'
    if name in M.MACRO:
        d, lo, hi, kind, _ = M.MACRO[name]
        return d, lo, hi, kind
    d, lo, hi, kind, _ = SWITCHES[name]
    return d, lo, hi, kind


def default_scalars():
    return {k: spec(k)[0] for k in SCALARS}


def empty_blocks():
    return {name: [0] * n for name, n in BLOCKS}


def to_ints(scalars, blocks):
    """The genome as the int vector patched into the wasm (after the header)."""
    out = [int(scalars[k]) for k in SCALARS]
    for name, n in BLOCKS:
        b = list(blocks.get(name) or [])
        if len(b) > n:
            raise ValueError(f'{name}: {len(b)} ints > {n}')
        out += [int(v) for v in b] + [0] * (n - len(b))
    return out


def cid_of(ints):
    return hashlib.sha1(struct.pack('<%di' % len(ints), *ints)).hexdigest()[:10]


def replace_reindented(text, old, new, fname):
    """text.replace(old, new) for a literal that must occur once; a multi-line literal may sit deeper (the patch
    moved it into a rule), then it is matched whatever its indent and `new` gets the same extra indent."""
    if text.count(old) == 1:
        return text.replace(old, new)
    lines = old.split('\n')
    if len(lines) > 1:
        import re
        ind0 = len(lines[0]) - len(lines[0].lstrip())
        pat = '\n'.join('([ \t]*)' + re.escape(l.lstrip()) if i == 0 else '[ \t]*' + re.escape(l.lstrip())
                         for i, l in enumerate(lines))
        found = list(re.finditer('(?m)^' + pat, text))
        if len(found) == 1:
            extra = len(found[0].group(1)) - ind0
            pad = ' ' * max(0, extra)
            rep = '\n'.join(pad + l if l.strip() else l for l in new.split('\n'))
            return text[:found[0].start()] + rep + text[found[0].end():]
    sys.exit(f'{fname}: expected exactly one "{old[:60]}", found {text.count(old)}')


def write_src(base, dst, ints):
    """base/src -> dst/src: weight literals (genome.LITERALS), the rule-list patch, ga_struct.h and a params.h holding
    the genome as the patchable volatile array `ga_s`."""
    src = os.path.join(dst, 'src')
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(os.path.join(base, 'src'), src)
    for fname in os.listdir(src):  # LF everywhere, so the patch applies whatever git's autocrlf did on Windows
        p = os.path.join(src, fname)
        if os.path.isfile(p):
            b = open(p, 'rb').read()
            if b'\r\n' in b:
                open(p, 'wb').write(b.replace(b'\r\n', b'\n'))
    for fname, old, new in G.LITERALS:
        p = os.path.join(src, fname)
        text = open(p, newline='').read()
        if text.count(old) != 1:
            sys.exit(f'{fname}: expected exactly one "{old}", found {text.count(old)}')
        open(p, 'w', newline='\n').write(text.replace(old, new))
    patch = os.path.join(dst, 'struct.patch')
    open(patch, 'wb').write(open(os.path.join(HERE, 'struct.patch'), 'rb').read().replace(b'\r\n', b'\n'))
    patch = os.path.abspath(patch)
    if shutil.which('patch'):
        r = subprocess.run(['patch', '-s', '-p1', '-d', src, '-i', patch], capture_output=True, text=True)
    else:  # Windows: no `patch`; git apply outside any repository (the ceiling stops it finding ours) works the same
        env = {**os.environ, 'GIT_CEILING_DIRECTORIES': os.path.dirname(os.path.abspath(src))}
        r = subprocess.run(['git', 'apply', '-p1', patch], cwd=src, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        sys.exit('struct.patch does not apply to %s: %s%s' % (base, r.stdout, r.stderr))
    os.remove(patch)
    for fname, old, new in M.LITERALS:  # after the patch: some sit in the code the patch moved into rules
        p = os.path.join(src, fname)
        text = open(p, newline='').read()
        open(p, 'w', newline='\n').write(replace_reindented(text, old, new, fname))
    shutil.copy(os.path.join(HERE, 'ga_struct.h'), src)
    p = os.path.join(src, 'params.h')
    lines = open(p, newline='').read().split('\n') if os.path.exists(p) else []
    keep = [l for l in lines if not (l.strip().startswith('#define ') and l.split()[1] in SCALARS)]
    vals = HEADER + list(ints)
    out = keep + ['', '// ---- genetic algorithm genome (tools/ga/structure.py): weights, structure, programs, net ----',
                  '#define GA_HAVE_GENOME 1',
                  'volatile int ga_s[%d] = {%s};' % (len(vals), ', '.join(str(v) for v in vals))]
    # scalars are copied once at start-up into plain constants; programs and the net are read in place
    out += ['static const int ga_%s = ga_s[%d];' % (k, i + len(HEADER)) for i, k in enumerate(SCALARS)]
    out += ['#define %s ga_%s' % (k, k) for k in SCALARS]
    off = len(HEADER) + len(SCALARS)
    for name, n in BLOCKS:
        out.append('#define %s ((const volatile int*)(ga_s + %d))' % (name, off))
        off += n
    open(p, 'w', newline='\n').write('\n'.join(out) + '\n')


def find_genome(wasm_bytes):
    key = struct.pack('<4i', *HEADER)
    i = wasm_bytes.find(key)
    if i < 0 or wasm_bytes.find(key, i + 1) >= 0:
        sys.exit('structure genome marker not found exactly once in the wasm')
    return i + len(key)


def describe_scalars(sc):
    """Only what differs from the base, rule order spelled out when it changed."""
    base = default_scalars()
    d = {k: sc[k] for k in SCALARS if sc[k] != base[k] and not k.startswith('P_O_')}
    order = sorted(range(len(RULES)), key=lambda i: (sc['P_O_' + RULES[i]], i))
    if order != list(range(len(RULES))):
        d['order'] = '>'.join(RULES[i] for i in order)
    return d
