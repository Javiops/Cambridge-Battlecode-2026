#!/usr/bin/env python3
"""Puerta local (etapa 2 del harness): ¿puede este candidato subir online?

uso (desde la raíz del repo, después de `cambc init --yes`):
  python3 tools/gate.py bots/CAND bots/BASE --kind farm          # cambio de farmeo / macro
  python3 tools/gate.py bots/CAND bots/BASE --kind fight         # cambio de pelea (local solo puede vetar)
  python3 tools/gate.py bots/CAND bots/BASE --kind farm --idea I017 --extra '/mnt/project-files/arena/maps/fresh300/*.map26a'

Corre por fases, de la más barata a la más cara, y para en cuanto el resultado está claro:
  1. seguridad    9 mapas oficiales x 2 lados: ningún fallo del bot (botFaults), ninguna partida rota, y los turnos
                  sin combustible (paso tipo 26) en lanes/corners/collision no suben más de 30 sobre la base.
  2. mapas nuevos hold60 + dev200 (+ --extra) barajados en tandas de 40 mapas, contando mapas ganados por los dos
                  lados. Para antes si ya se ve peor (p<0.05 en contra) o, en farm, si ya se ve mejor (p<0.01).
  3. panel        contra spar11/12/16 (los rivales que matan como online) en oficiales + gen: el candidato y la base
                  juegan las mismas partidas; veto si las partidas que cambian van en contra con p<0.05.
  4. contraejemplos  los mapas nuevos perdidos por los dos lados, peor primero, con la orden para reproducirlos.

Veredicto:
  farm : PASA si mapas nuevos a favor con p<0.05, seguridad bien y panel sin veto.
  fight: PASA si los mapas nuevos no van en contra (p>=0.05), seguridad bien y panel sin veto. El juicio de verdad
         de una regla de pelea es online (etapa 3): local solo puede decir que no rompe nada.
Todo lo jugado queda en out/ab-cache (lo comparte con ab.py): repetir la puerta o cambiar solo el candidato no
repite las partidas de la base contra el panel. Resultado en out/gate/<cand>_vs_<base>/ (result.json, contraejemplos.md);
con --idea se apunta también en el tracker (harness/ideas.jsonl).
"""
import argparse, glob, hashlib, json, os, random, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ab  # noqa: E402  (reutiliza build, play, sign_p, caché y la variable de caché de wasmtime)

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


def fuel_check(cand, base, ha, hb, ver, jobs):
    """k26 (fuel exhausted turn ends) of each bot on the big official maps, side A vs the other bot."""
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
        subprocess.run([ab.CLI, 'run', x, y, '--map', m, '-o', od], capture_output=True, env=ab.ENV)
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


def export_ref(ref, cand):
    """`gate.py bots/study28 main`: the base is the candidate's folder as it is in git ref `ref` (main, origin/main, a sha).
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
        sys.exit(f'{ref}: ni carpeta de bot ni referencia de git')
    dst = os.path.join('out', 'base', f'{os.path.basename(cand)}@{sha[:10]}')
    if not os.path.isdir(os.path.join(dst, 'src')):
        os.makedirs(dst, exist_ok=True)
        ar = subprocess.run(['git', 'archive', '--format=tar', ref, cand], capture_output=True)
        if ar.returncode != 0:
            sys.exit(f'git archive {ref} {cand} falló: {ar.stderr.decode()[-300:]}')
        subprocess.run(['tar', '-x', '-C', dst, '--strip-components=' + str(cand.count('/') + 1)], input=ar.stdout, check=True)
    print(f'base = {cand} en {ref} ({sha[:10]}) -> {dst}')
    return dst


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('cand'); p.add_argument('base')
    p.add_argument('--kind', choices=['farm', 'fight'], required=True)
    p.add_argument('--idea', default='', help='id del tracker (I001...): apunta el resultado allí')
    p.add_argument('--extra', default='', help='glob de mapas nuevos adicionales (p. ej. fresh300)')
    p.add_argument('--max-maps', type=int, default=0, help='tope de mapas nuevos (0 = todos)')
    p.add_argument('--no-panel', action='store_true'); p.add_argument('--no-fuel', action='store_true')
    p.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
    A = p.parse_args()
    cand, base = A.cand.rstrip('/\\'), A.base.rstrip('/\\')
    if not os.path.isdir(base):
        base = export_ref(base, cand)
    tag = os.path.basename(cand) + '_vs_' + os.path.basename(base)
    outdir = os.path.join('out', 'gate', tag); os.makedirs(outdir, exist_ok=True)
    cache = os.path.join('out', 'ab-cache'); os.makedirs(cache, exist_ok=True)
    t0 = time.time(); log = []

    def say(s=''):
        print(s, flush=True); log.append(s)

    panel = [b for b in PANEL if os.path.isdir(b)] if not A.no_panel else []
    with ThreadPoolExecutor(2 + len(panel)) as ex:
        list(ex.map(ab.build, [cand, base] + panel))
    ver = subprocess.run([ab.CLI, '--version'], capture_output=True, text=True, env=ab.ENV).stdout.strip()
    hc, hb = ab.sha(ab.wasm_of(cand)), ab.sha(ab.wasm_of(base))
    verdict = {'cand': cand, 'base': base, 'kind': A.kind, 'cand_wasm': hc, 'base_wasm': hb,
               'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    say(f'{cand} (candidato) vs {base} (base), tipo {A.kind}   [compilado en {time.time() - t0:.0f}s]')
    if hc == hb:
        say('El candidato compila al mismo wasm que la base: no cambia nada. NO PASA.')
        return finish(A, verdict | {'pass': False, 'why': 'mismo wasm'}, outdir, log)

    # 1. seguridad ------------------------------------------------------------------------------------------
    t = time.time()
    per = run(jobs_for(cand, base, hc, hb, maps_of(ab.SETS['official']), tag, ver, cache), A.jobs)
    broken = [f'{os.path.basename(m)} {s}' for m, d in per.items() for s, r in d.items() if not r.get('ok')]
    faults = sum(r['faults'][0 if s == 'A' else 1] for d in per.values() for s, r in d.items()
                 if r.get('ok') and r.get('faults'))
    w, l, sp, _ = tally(per)
    say(f'\n1. seguridad: oficiales {w} ganados por los dos lados, {l} perdidos, {sp} repartidos; '
        f'fallos del candidato {faults}, partidas rotas {len(broken)}   [{time.time() - t:.0f}s]')
    ok = not broken and faults == 0
    fuel = None
    if ok and not A.no_fuel:
        t = time.time()
        fuel = fuel_check(cand, base, hc, hb, ver, A.jobs)
        if fuel is None:
            say('   combustible: no se pudo medir (¿node o el wasm del visor?); sigue sin esta comprobación')
        else:
            say(f'   turnos sin combustible en {"/".join(FUEL_MAPS)} (lado A): candidato {fuel["cand"]}, base {fuel["base"]}'
                f'   [{time.time() - t:.0f}s]')
            if fuel['cand'] > fuel['base'] + 30:
                ok = False; say('   el candidato se queda sin combustible más que la base: revisa bucles por turno')
    verdict['safety'] = {'broken': broken, 'faults': faults, 'fuel': fuel, 'official': [w, l, sp]}
    if not ok:
        say('NO PASA en seguridad.' + (f' Rotas: {broken[:5]}' if broken else ''))
        return finish(A, verdict | {'pass': False, 'why': 'seguridad'}, outdir, log)

    # 2. mapas nuevos con parada temprana ---------------------------------------------------------------------
    fresh = maps_of(ab.SETS['hold']) + maps_of(ab.SETS['dev']) + (maps_of(A.extra) if A.extra else [])
    random.Random(20261015).shuffle(fresh)
    if A.max_maps: fresh = fresh[:A.max_maps]
    say(f'\n2. mapas nuevos: {len(fresh)} mapas en tandas de {CHUNK}')
    t = time.time(); per2 = {}; stop = ''
    for i in range(0, len(fresh), CHUNK):
        per2.update(run(jobs_for(cand, base, hc, hb, fresh[i:i + CHUNK], tag, ver, cache), A.jobs))
        w, l, sp, _ = tally(per2); n = w + l; pv = ab.sign_p(w, n)
        say(f'   {len(per2):4d} mapas: {w}-{l} decididos ({sp} repartidos), p={pv:.3f}   [{time.time() - t:.0f}s]')
        if l > w and pv < 0.05: stop = 'peor'; break
        if A.kind == 'farm' and w > l and n >= 30 and pv < 0.01: stop = 'mejor'; break
    w, l, sp, ce = tally(per2); pv = ab.sign_p(w, w + l)
    rate = lambda per_, me: sum(50.0 * (d['A']['gems'][me] / d['A']['round'] + d['B']['gems'][1 - me] / d['B']['round'])
                               for d in per_.values() if len(d) == 2 and all(x.get('ok') for x in d.values())) / max(1, len(per_))
    gc, gb = rate(per2, 0), rate(per2, 1)
    say(f'   resultado: {w}-{l} mapas ganados/perdidos por los dos lados, p={pv:.3f}; gemas/100 rondas {gc:.1f} vs {gb:.1f}'
        + (f' (parada temprana: {stop})' if stop else ''))
    verdict['fresh'] = {'maps': len(per2), 'won': w, 'lost': l, 'split': sp, 'p': round(pv, 4),
                        'gems100': [round(gc, 1), round(gb, 1)]}
    if A.kind == 'farm':
        fresh_ok = w > l and pv < 0.05
    else:
        fresh_ok = not (l > w and pv < 0.05)

    # 4. contraejemplos (se escriben siempre) ----------------------------------------------------------------
    with open(os.path.join(outdir, 'contraejemplos.md'), 'w') as f:
        f.write(f'# Contraejemplos: {cand} vs {base}\n\nMapas nuevos que el candidato pierde por los dos lados, '
                'peor diferencia de gemas primero. Reproducir y ver:\n\n')
        for gd, m, d in ce[:25]:
            name = os.path.splitext(os.path.basename(m))[0]
            f.write(f'- `{name}` gemas {gd:+d} (lado A {d["A"]["gems"][0]}-{d["A"]["gems"][1]} r{d["A"]["round"]}, '
                    f'lado B {d["B"]["gems"][1]}-{d["B"]["gems"][0]} r{d["B"]["round"]})  \n'
                    f'  `cambc run {cand} {base} --map {m} -o out/ce/{name} && cambc view out/ce/{name}/*.repl26a`\n')
    verdict['counterexamples'] = [os.path.basename(m) for _, m, _ in ce[:25]]
    if ce:
        say(f'   {len(ce)} contraejemplos en {outdir}/contraejemplos.md (peor: {os.path.basename(ce[0][1])})')
    if not fresh_ok:
        say('NO PASA en mapas nuevos.' if A.kind == 'fight' or (l >= w) else
            'NO PASA: a favor pero sin decidir; añade --extra con más mapas nuevos o déjala como neutra.')
        return finish(A, verdict | {'pass': False, 'why': 'mapas nuevos'}, outdir, log)

    # 3. panel de lanzadores (veto) ---------------------------------------------------------------------------
    if panel:
        t = time.time(); maps = maps_of(ab.SETS['official']) + maps_of(ab.SETS['gen'])
        up = down = 0; wc = wb = 0
        for sp_bot in panel:
            ab.build(sp_bot); hs = ab.sha(ab.wasm_of(sp_bot))
            pc = run(jobs_for(cand, sp_bot, hc, hs, maps, tag + '_' + os.path.basename(sp_bot), ver, cache), A.jobs)
            pb = run(jobs_for(base, sp_bot, hb, hs, maps, tag + '_' + os.path.basename(sp_bot), ver, cache), A.jobs)
            c1 = b1 = 0
            for m in pc:
                for s in ('A', 'B'):
                    me = 0 if s == 'A' else 1
                    xc, xb = score(pc[m][s], me) == 'WIN', score(pb[m][s], me) == 'WIN'
                    c1 += xc; b1 += xb; up += xc and not xb; down += xb and not xc
            wc += c1; wb += b1
            say(f'   {os.path.basename(sp_bot)}: candidato gana {c1}, base gana {b1} (de {2 * len(pc)})')
        pv3 = ab.sign_p(up, up + down)
        veto = down > up and pv3 < 0.05
        say(f'3. panel: partidas que cambian {up} a favor, {down} en contra, p={pv3:.3f}'
            f'{" -> VETO" if veto else ""}   [{time.time() - t:.0f}s]')
        verdict['panel'] = {'cand_wins': wc, 'base_wins': wb, 'flips_up': up, 'flips_down': down, 'p': round(pv3, 4), 'veto': veto}
        if veto:
            say('NO PASA: el panel de lanzadores le gana más (es el único rival local que mata como online).')
            return finish(A, verdict | {'pass': False, 'why': 'panel'}, outdir, log)

    say(f'\nPASA ({A.kind}). ' + ('Sube online y mide en la etapa 3 (online/lfl.py).' if A.kind == 'fight' else
                                  'Mejora de farmeo clara: sube online y confirma que no empeora (etapa 3).'))
    say(f'Total {time.time() - t0:.0f}s')
    return finish(A, verdict | {'pass': True}, outdir, log)


def finish(A, verdict, outdir, log):
    json.dump(verdict, open(os.path.join(outdir, 'result.json'), 'w'), indent=1)
    open(os.path.join(outdir, 'gate.txt'), 'w').write('\n'.join(log) + '\n')
    if A.idea:
        import idea
        fr = verdict.get('fresh') or {}
        note = (f"gate {A.kind}: {'PASA' if verdict['pass'] else 'NO PASA (' + verdict.get('why', '') + ')'}; "
                f"nuevos {fr.get('won', '?')}-{fr.get('lost', '?')} p={fr.get('p', '?')}"
                + (f"; panel {verdict['panel']['flips_up']}/{verdict['panel']['flips_down']}" if 'panel' in verdict else ''))
        idea.record(A.idea, stage='local-ok' if verdict['pass'] else 'test-local', note=note,
                    result=os.path.join(outdir, 'result.json'))
    sys.exit(0 if verdict['pass'] else 1)


if __name__ == '__main__':
    main()
