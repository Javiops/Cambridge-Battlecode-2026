#!/usr/bin/env python3
"""Local gate (stage 2 of the harness): may this candidate go online?

usage (from the repo root, after `cambc init --yes`):
  python3 tools/gate.py bots/CAND bots/BASE --kind farm          # a farming / macro change
  python3 tools/gate.py bots/CAND main --kind fight              # a fight change; the base is the same bot folder as on main
  python3 tools/gate.py bots/CAND bots/BASE --kind farm --idea I017 --extra '/mnt/project-files/arena/maps/fresh300/*.map26a'
  python3 tools/gate.py bots/CAND online --kind farm             # the base is the zip that is online (online/version.py --zip)

Runs in phases, cheapest first, and stops as soon as the result is clear:
  1. safety + site maps   the 17 site maps (maps/, the official pool) x 2 sides: no bot fault (botFaults), no broken
                game, the fuel-exhausted turns (step kind 26) on lanes/corners/collision do not rise more than 30 over
                the base, and the site-map head to head is the HEADLINE of the verdict (user rule 2026-10-16: big wins
                on the official maps come first): FAIL if it loses --site-veto (3) more maps on both sides than it wins.
  2. fresh maps hold60 + dev200 (+ --extra) shuffled in chunks of 40 maps, counting maps won on both sides. Stops early
                when it already looks worse (p<0.05 against) or, for farm, already better (p<0.01).
  3. panel      against spar11/12/16 (the rivals that kill like online teams) on official + gen: the candidate and
                the base play the same games; veto if the games that flip go against with p<0.05, on all maps or on
                the site maps alone (so the site maps weigh more than the generated ones).
  4. counterexamples  the fresh maps lost on both sides, worst first, with the command to reproduce them.

Verdict:
  farm : PASS if fresh maps in favour with p<0.05, safety clean and no panel veto.
  fight: PASS if fresh maps are not against (p>=0.05), safety clean and no panel veto. The real judge of a fight rule
         is online (stage 3): local can only say it breaks nothing.
Incomplete runs never pass (2026-10-16 review): a missing panel bot, a game that did not finish (no stats) in any
phase, or more bot faults for the candidate than the base on fresh maps is a FAIL; --no-panel or an unmeasured fuel
check gives "PARTIAL PASS", recorded as partial in result.json.
Everything played stays in out/ab-cache (shared with ab.py): rerunning the gate, or changing only the candidate, never
replays the base against the panel. Output in out/gate/<cand>_vs_<base>/ (gate.txt, result.json, counterexamples.md);
with --idea the result is also recorded on the board (harness/ideas).
"""
import argparse, glob, hashlib, json, os, random, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ab  # noqa: E402  (reuses build, play, sign_p, the result cache and the wasmtime cache variable)
import online_base  # noqa: E402  (which source is online; `online` as the base)

PANEL = ['bots/spar11', 'bots/spar12', 'bots/spar16']
FUEL_MAPS = ['lanes', 'corners', 'collision']
CHUNK = 40


def maps_of(pattern):
    return sorted(glob.glob(pattern))


def jobs_for(a, b, ha, hb, maps, tag, ver, cache, keep=False):
    out = []
    for m in maps:
        hm = hashlib.sha256((ab.sha(m) + ver).encode()).hexdigest()[:8]
        name = os.path.splitext(os.path.basename(m))[0]
        for side, (x, y, hx, hy) in (('A', (a, b, ha, hb)), ('B', (b, a, hb, ha))):
            out.append(((x, y, m, f'{hx}_{hy}_{hm}', cache, os.path.join('out', 'gate', tag, name + '_' + side), keep),
                        (m, side)))
    return out


def run(jobs, n):
    with ThreadPoolExecutor(n) as ex:
        res = list(ex.map(ab.play, [j for j, _ in jobs]))
    per = {}
    for (_, (m, side)), r in zip(jobs, res):
        per.setdefault(m, {})[side] = r
    return per


def score(r, me):
    """WIN/LOSS/DRAW for team index `me` (0 = played as team A)."""
    if not r.get('ok'):
        return 'FAIL'
    won = r['outcome'] == ('teamA' if me == 0 else 'teamB')
    return 'WIN' if won else 'LOSS' if r['outcome'] in ('teamA', 'teamB') else 'DRAW'


def tally(per):
    """maps won both sides / lost both / split for the first bot of the pair; plus counterexample rows."""
    w = l = sp = 0; rows = []
    for m, d in per.items():
        if len(d) < 2:
            continue
        ra, rb = score(d['A'], 0), score(d['B'], 1)
        if ra == rb == 'WIN': w += 1
        elif ra == rb == 'LOSS':
            l += 1
            gd = (d['A']['gems'][0] - d['A']['gems'][1]) + (d['B']['gems'][1] - d['B']['gems'][0])
            rows.append((gd, m, d))
        else: sp += 1
    return w, l, sp, sorted(rows)


def problems(per, first='cand'):
    """Games that did not finish (no stats: CLI crash or timeout) and bot faults per bot, for one stage.
    In jobs_for the first bot of the pair is team A on side A and team B on side B."""
    broken = [f'{os.path.basename(m)} {s}' for m, d in per.items() for s, r in d.items() if not r.get('ok')]
    missing = [os.path.basename(m) for m, d in per.items() if len(d) < 2]
    fa = fb = 0
    for d in per.values():
        for s, r in d.items():
            if r.get('ok') and r.get('faults'):
                me = 0 if s == 'A' else 1
                fa += r['faults'][me]; fb += r['faults'][1 - me]
    return broken + [m + ' (a side never ran)' for m in missing], fa, fb


def fuel_check(cand, base, ha, hb, ver, jobs):
    """k26 (fuel-exhausted turn ends) of each bot on the big official maps, side A vs the other bot."""
    maps = [f'maps/{n}.map26a' for n in FUEL_MAPS if os.path.exists(f'maps/{n}.map26a')]
    tag = 'fuel_' + ha + '_' + hb
    todo = []
    for who, (x, y) in (('cand', (cand, base)), ('base', (base, cand))):
        for m in maps:
            od = os.path.join('out', 'gate', tag, who + '_' + os.path.basename(m))
            todo.append((who, m, od, x, y))

    def one(t):
        who, m, od, x, y = t
        cf = os.path.join(od, 'k26.json')
        if os.path.exists(cf):
            return who, json.load(open(cf))
        os.makedirs(od, exist_ok=True)
        subprocess.run([ab.CLI, 'run', x, y, '--map', m, '-o', od] + [f for f in ab.RUN_FLAGS if f != '--json'], capture_output=True, env=ab.ENV)
        reps = glob.glob(os.path.join(od, '*.repl26a'))
        if not reps:
            return who, None
        p = subprocess.run(['node', 'tools/replaydump.js', reps[0], '--every-step'], capture_output=True, text=True)
        k, team = 0, {}
        for line in p.stdout.splitlines():
            try: d = json.loads(line)
            except ValueError: continue
            if 'step' not in d: continue
            if not team: team = {c['index']: c['team'] for c in d.get('champions', [])}
            st = d['step']
            if st.get('kind') == 26 and st.get('actorKind') == 1 and team.get(st.get('actorIndex')) == 0:
                k += 1
        for f in reps: os.remove(f)
        json.dump(k, open(cf, 'w'))
        return who, k

    with ThreadPoolExecutor(jobs) as ex:
        res = list(ex.map(one, todo))
    tot = {'cand': 0, 'base': 0}
    for who, k in res:
        if k is None: return None
        tot[who] += k
    return tot


def online_maps_line(per):
    """Per-map result on the site's own maps (maps/ = the pool `cambc init` pulls), named, so a loss there is seen."""
    n = len(per)
    marks = []
    for m, d in sorted(per.items()):
        if len(d) < 2: continue
        ra, rb = score(d['A'], 0), score(d['B'], 1)
        marks.append(os.path.splitext(os.path.basename(m))[0] + {('WIN', 'WIN'): ' +', ('LOSS', 'LOSS'): ' -'}.get((ra, rb), ' ='))
    stale = '' if n >= 17 else f' (only {n} maps in maps/: run `cambc init --yes` to pull the current site pool)'
    return f'site maps ({n}, + won both sides, - lost both, = split): ' + ', '.join(marks) + stale


def export_ref(ref, cand):
    """`gate.py bots/study27-economy main`: the base is the candidate's folder as it is in git ref `ref` (main, origin/main, a sha).
    A bare branch name means the branch on origin (fetched first), so a stale local `main` never becomes the base."""
    def rev(r):
        x = subprocess.run(['git', 'rev-parse', '--verify', '--quiet', r + '^{commit}'], capture_output=True, text=True)
        return x.stdout.strip() if x.returncode == 0 else None
    sha = None
    if '/' not in ref and not rev(ref) or ref in ('main', 'master'):
        subprocess.run(['git', 'fetch', '-q', 'origin', ref], capture_output=True)
        sha = rev('origin/' + ref)
        if sha: ref = 'origin/' + ref
    sha = sha or rev(ref)
    if not sha:
        sys.exit(f'{ref}: neither a bot folder nor a git reference')
    dst = os.path.join('out', 'base', f'{os.path.basename(cand)}@{sha[:10]}')
    if not os.path.isdir(os.path.join(dst, 'src')):
        os.makedirs(dst, exist_ok=True)
        ar = subprocess.run(['git', 'archive', '--format=tar', ref, cand], capture_output=True)
        if ar.returncode != 0:
            sys.exit(f'git archive {ref} {cand} failed: {ar.stderr.decode()[-300:]}')
        subprocess.run(['tar', '-x', '-C', dst, '--strip-components=' + str(cand.count('/') + 1)], input=ar.stdout, check=True)
    print(f'base = {cand} at {ref} ({sha[:10]}) -> {dst}')
    return dst


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('cand'); p.add_argument('base', help='a bot folder, or a git ref (main) meaning the candidate folder at that ref')
    p.add_argument('--kind', choices=['farm', 'fight'], required=True)
    p.add_argument('--idea', default='', help='tracker id (I001...): record the result there')
    p.add_argument('--extra', default='', help='glob of additional fresh maps (e.g. fresh300)')
    p.add_argument('--site-veto', type=int, default=3, help='FAIL when the site maps are lost on both sides this many more times than won')
    p.add_argument('--max-maps', type=int, default=0, help='cap on fresh maps (0 = all)')
    p.add_argument('--no-panel', action='store_true'); p.add_argument('--no-fuel', action='store_true')
    p.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
    A = p.parse_args()
    cand, base = A.cand.rstrip('/\\'), A.base.rstrip('/\\')
    if base == 'online':
        base = online_base.export()
    elif not os.path.isdir(base):
        base = export_ref(base, cand)
    base_online, base_msg = online_base.check(base)
    tag = os.path.basename(cand) + '_vs_' + os.path.basename(base)
    outdir = os.path.join('out', 'gate', tag); os.makedirs(outdir, exist_ok=True)
    cache = os.path.join('out', 'ab-cache'); os.makedirs(cache, exist_ok=True)
    t0 = time.time(); log = []

    def say(s=''):
        print(s, flush=True); log.append(s)

    panel = [b for b in PANEL if os.path.isdir(b)] if not A.no_panel else []
    absent = [b for b in PANEL if not os.path.isdir(b)] if not A.no_panel else []
    if absent:
        # a gate without its panel is not a gate: a candidate must never "pass" because the rivals were not there
        say(f'INCOMPLETE: panel bots missing: {", ".join(absent)} (copy them into bots/ or run with --no-panel, '
            'which is recorded in the verdict). FAIL.')
        return finish(A, {'cand': cand, 'base': base, 'kind': A.kind, 'pass': False, 'why': 'panel missing',
                          'panel_missing': absent}, outdir, log)
    with ThreadPoolExecutor(2 + len(panel)) as ex:
        list(ex.map(ab.build, [cand, base] + panel))
    ver = subprocess.run([ab.CLI, '--version'], capture_output=True, text=True, env=ab.ENV).stdout.strip()
    hc, hb = ab.sha(ab.wasm_of(cand)), ab.sha(ab.wasm_of(base))
    verdict = {'cand': cand, 'base': base, 'kind': A.kind, 'cand_wasm': hc, 'base_wasm': hb,
               'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
               'panel_bots': [os.path.basename(b) for b in panel], 'no_panel': bool(A.no_panel),
               'no_fuel': bool(A.no_fuel)}
    say(f'{cand} (candidate) vs {base} (base), kind {A.kind}   [built in {time.time() - t0:.0f}s]')
    say(('   ' if base_online else '   WARNING: ') + base_msg)
    verdict['base_online'] = base_online
    if hc == hb:
        say('The candidate compiles to the same wasm as the base: it changes nothing. FAIL.')
        return finish(A, verdict | {'pass': False, 'why': 'same wasm'}, outdir, log)

    # 1. safety ---------------------------------------------------------------------------------------------
    t = time.time()
    per = run(jobs_for(cand, base, hc, hb, maps_of(ab.SETS['official']), tag, ver, cache), A.jobs)
    broken, faults, _ = problems(per)
    w, l, sp, _ = tally(per)
    say(f'\n1. safety: official maps {w} won both sides, {l} lost both, {sp} split; '
        f'candidate faults {faults}, broken games {len(broken)}   [{time.time() - t:.0f}s]')
    say(f'   {online_maps_line(per)}')
    verdict['online_maps'] = {os.path.splitext(os.path.basename(m))[0]: [score(d['A'], 0), score(d['B'], 1)]
                              for m, d in sorted(per.items()) if len(d) == 2}
    ok = not broken and faults == 0
    fuel = None
    if ok and not A.no_fuel:
        t = time.time()
        fuel = fuel_check(cand, base, hc, hb, ver, A.jobs)
        if fuel is None:
            say('   fuel: could not measure (node or the visualiser wasm missing?); going on without this check '
                '(recorded as fuel_unchecked in the verdict)')
            verdict['fuel_unchecked'] = True
        else:
            say(f'   fuel-exhausted turns on {"/".join(FUEL_MAPS)} (side A): candidate {fuel["cand"]}, base {fuel["base"]}'
                f'   [{time.time() - t:.0f}s]')
            if fuel['cand'] > fuel['base'] + 30:
                ok = False; say('   the candidate runs out of fuel more than the base: look for per-turn loops')
    verdict['safety'] = {'broken': broken, 'faults': faults, 'fuel': fuel, 'official': [w, l, sp]}
    verdict['site'] = {'maps': len(per), 'won': w, 'lost': l, 'split': sp}
    say(f'   SITE MAPS (headline): {w} won both sides, {l} lost both, {sp} split')
    if not ok:
        say('FAIL on safety.' + (f' Broken: {broken[:5]}' if broken else ''))
        return finish(A, verdict | {'pass': False, 'why': 'safety'}, outdir, log)
    if l - w >= A.site_veto:
        say(f'FAIL on the site maps: {l} lost both sides vs {w} won (veto at {A.site_veto} net); the official maps come first.')
        return finish(A, verdict | {'pass': False, 'why': 'site maps'}, outdir, log)

    # 2. fresh maps with early stopping -----------------------------------------------------------------------
    fresh = maps_of(ab.SETS['hold']) + maps_of(ab.SETS['dev']) + (maps_of(A.extra) if A.extra else [])
    random.Random(20261015).shuffle(fresh)
    if A.max_maps: fresh = fresh[:A.max_maps]
    say(f'\n2. fresh maps: {len(fresh)} maps in chunks of {CHUNK}')
    t = time.time(); per2 = {}; stop = ''
    for i in range(0, len(fresh), CHUNK):
        per2.update(run(jobs_for(cand, base, hc, hb, fresh[i:i + CHUNK], tag, ver, cache), A.jobs))
        w, l, sp, _ = tally(per2); n = w + l; pv = ab.sign_p(w, n)
        say(f'   {len(per2):4d} maps: {w}-{l} decided ({sp} split), p={pv:.3f}   [{time.time() - t:.0f}s]')
        if l > w and pv < 0.05: stop = 'worse'; break
        if A.kind == 'farm' and w > l and n >= 30 and pv < 0.01: stop = 'better'; break
    w, l, sp, ce = tally(per2); pv = ab.sign_p(w, w + l)
    rate = lambda per_, me: sum(50.0 * (d['A']['gems'][me] / d['A']['round'] + d['B']['gems'][1 - me] / d['B']['round'])
                               for d in per_.values() if len(d) == 2 and all(x.get('ok') for x in d.values())) / max(1, len(per_))
    gc, gb = rate(per2, 0), rate(per2, 1)
    say(f'   result: {w}-{l} maps won/lost on both sides, p={pv:.3f}; gems/100 rounds {gc:.1f} vs {gb:.1f}'
        + (f' (early stop: {stop})' if stop else ''))
    broken2, fc2, fb2 = problems(per2)
    verdict['fresh'] = {'maps': len(per2), 'won': w, 'lost': l, 'split': sp, 'p': round(pv, 4),
                        'gems100': [round(gc, 1), round(gb, 1)], 'broken': broken2, 'faults': [fc2, fb2]}
    if broken2 or fc2 > fb2:
        # tally() files a game that did not finish under "split" (neutral): never let that pass silently
        say(f'   fresh maps: {len(broken2)} games did not finish{" (" + ", ".join(broken2[:5]) + ")" if broken2 else ""}; '
            f'bot faults candidate {fc2}, base {fb2}')
        say('FAIL: fresh maps incomplete or the candidate faults more than the base.')
        return finish(A, verdict | {'pass': False, 'why': 'fresh broken/faults'}, outdir, log)
    if A.kind == 'farm':
        fresh_ok = w > l and pv < 0.05
    else:
        fresh_ok = not (l > w and pv < 0.05)

    # 4. counterexamples (always written) --------------------------------------------------------------------
    with open(os.path.join(outdir, 'counterexamples.md'), 'w') as f:
        f.write(f'# Counterexamples: {cand} vs {base}\n\nFresh maps the candidate loses on both sides, worst gem '
                'difference first. Reproduce and watch:\n\n')
        for gd, m, d in ce[:25]:
            name = os.path.splitext(os.path.basename(m))[0]
            f.write(f'- `{name}` gems {gd:+d} (side A {d["A"]["gems"][0]}-{d["A"]["gems"][1]} r{d["A"]["round"]}, '
                    f'side B {d["B"]["gems"][1]}-{d["B"]["gems"][0]} r{d["B"]["round"]})  \n'
                    f'  `cambc run {cand} {base} --map {m} -o out/ce/{name} && cambc view out/ce/{name}/*.repl26a`\n')
    verdict['counterexamples'] = [os.path.basename(m) for _, m, _ in ce[:25]]
    if ce:
        say(f'   {len(ce)} counterexamples in {outdir}/counterexamples.md (worst: {os.path.basename(ce[0][1])})')
    if not fresh_ok:
        say('FAIL on fresh maps.' if A.kind == 'fight' or (l >= w) else
            'FAIL: in favour but undecided; add --extra with more fresh maps or leave it as neutral.')
        return finish(A, verdict | {'pass': False, 'why': 'fresh maps'}, outdir, log)

    # 3. caster panel (veto) ----------------------------------------------------------------------------------
    if panel:
        t = time.time(); maps = maps_of(ab.SETS['official']) + maps_of(ab.SETS['gen'])
        up = down = 0; wc = wb = 0; panel_bad = []; sup = sdown = 0
        site = {m for m in maps if os.path.dirname(os.path.abspath(m)) == os.path.abspath('maps')}
        for sp_bot in panel:
            ab.build(sp_bot); hs = ab.sha(ab.wasm_of(sp_bot))
            pc = run(jobs_for(cand, sp_bot, hc, hs, maps, tag + '_' + os.path.basename(sp_bot) + '_c', ver, cache), A.jobs)
            pb = run(jobs_for(base, sp_bot, hb, hs, maps, tag + '_' + os.path.basename(sp_bot) + '_b', ver, cache), A.jobs)
            for who, pp in (('candidate', pc), ('base', pb)):
                br, f_me, _ = problems(pp)
                if br or (who == 'candidate' and f_me):
                    panel_bad.append(f'{os.path.basename(sp_bot)} {who}: {len(br)} unfinished, {f_me} faults')
            c1 = b1 = 0
            for m in pc:
                for s in ('A', 'B'):
                    me = 0 if s == 'A' else 1
                    xc, xb = score(pc[m][s], me) == 'WIN', score(pb[m][s], me) == 'WIN'
                    c1 += xc; b1 += xb; up += xc and not xb; down += xb and not xc
                    if m in site: sup += xc and not xb; sdown += xb and not xc
            wc += c1; wb += b1
            say(f'   {os.path.basename(sp_bot)}: candidate wins {c1}, base wins {b1} (of {2 * len(pc)})')
        pv3 = ab.sign_p(up, up + down)
        pvs = ab.sign_p(sup, sup + sdown)
        veto = (down > up and pv3 < 0.05) or (sdown > sup and pvs < 0.05)
        say(f'3. panel: SITE MAPS games that flip {sup} for, {sdown} against, p={pvs:.3f}; all maps {up} for, {down} against, '
            f'p={pv3:.3f}{" -> VETO" if veto else ""}   [{time.time() - t:.0f}s]')
        verdict['panel'] = {'cand_wins': wc, 'base_wins': wb, 'flips_up': up, 'flips_down': down, 'p': round(pv3, 4), 'veto': veto,
                            'site_flips': [sup, sdown], 'site_p': round(pvs, 4), 'problems': panel_bad}
        if panel_bad:
            say('FAIL: panel games incomplete or the candidate faults: ' + '; '.join(panel_bad))
            return finish(A, verdict | {'pass': False, 'why': 'panel broken/faults'}, outdir, log)
        if veto:
            say('FAIL: the caster panel beats it more (the only local rival that kills like online teams).')
            return finish(A, verdict | {'pass': False, 'why': 'panel'}, outdir, log)

    if A.no_panel or verdict.get('fuel_unchecked'):
        say('\nNote: run without ' + ' and '.join(x for x, on in (('the caster panel', A.no_panel),
                                                                   ('the fuel check', verdict.get('fuel_unchecked'))) if on)
            + ': a partial gate, not a full pass.')
        verdict['partial'] = True
    if not base_online:
        say('\nNote: the base is not (or not known to be) the online bot, so this result does not clear an upload.')
    st = verdict['site']
    say(f'\nSite maps (headline): {st["won"]}-{st["lost"]} won/lost on both sides ({st["split"]} split) of {st["maps"]}.')
    say(f'{"PARTIAL PASS" if verdict.get("partial") else "PASS"} ({A.kind}). ' + ('Upload it and measure in stage 3 (online/lfl.py).' if A.kind == 'fight' else
                                  'Clear farming gain: upload it and confirm online that it does not get worse (stage 3).'))
    say(f'Total {time.time() - t0:.0f}s')
    return finish(A, verdict | {'pass': True}, outdir, log)


def finish(A, verdict, outdir, log):
    json.dump(verdict, open(os.path.join(outdir, 'result.json'), 'w'), indent=1)
    open(os.path.join(outdir, 'gate.txt'), 'w').write('\n'.join(log) + '\n')
    if A.idea:
        import idea
        fr = verdict.get('fresh') or {}
        note = (f"gate {A.kind}: {('PARTIAL PASS' if verdict.get('partial') else 'PASS') if verdict['pass'] else 'FAIL (' + verdict.get('why', '') + ')'}; "
                + (f"site {verdict['site']['won']}-{verdict['site']['lost']}; " if 'site' in verdict else '')
                + f"fresh {fr.get('won', '?')}-{fr.get('lost', '?')} p={fr.get('p', '?')}"
                + (f"; panel {verdict['panel']['flips_up']}/{verdict['panel']['flips_down']}" if 'panel' in verdict else ''))
        idea.record(A.idea, stage='local-ok' if verdict['pass'] else 'local-test', note=note,
                    result=os.path.join(outdir, 'result.json'))
    sys.exit(0 if verdict['pass'] else 1)


if __name__ == '__main__':
    main()
