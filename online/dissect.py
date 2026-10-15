#!/usr/bin/env python3
"""Disección en una orden (etapa 4 del harness): de las partidas online de una versión a su ficha de métricas
y a una lista de propuestas para el brainstorm.

uso (desde online/, con data/games.jsonl al día):
  python3 dissect.py --version "corners fix"                      # últimas 150 partidas unranked de esa etiqueta
  python3 dissect.py --version "corners fix" --ref "v36 = study27"  # columna extra: la misma ficha de la versión anterior
  python3 dissect.py --version 2026-10-15T20:00/2026-10-15T22:00 --max 60 --maps corners,rows --jobs 4
  python3 dissect.py --version "corners fix" --idea I012          # apunta el resumen en el tracker

Qué hace: elige las partidas (etiqueta de data/versions.jsonl o ventana desde/hasta), baja las repeticiones que falten a
data/replays/, las decodifica paso a paso (tools/replaydump.js + tools/compact.py, ~25 s por partida, en paralelo y
con caché en <out>/steps/) y mide lo mismo para nosotros y para el rival en las mismas partidas: muertes y cómo
morimos, capturas por ronda-campeón, tiempo muerto e inactivo, contacto antes del primer golpe, aperturas en solitario,
hechizos, combustible. Escribe <out>/ficha.md, ficha.json y selected.json (el workspace que usan los scripts de
analysis/v35-dissection-2026-10-15/scripts_* para preguntas más finas: WS=<out>).

La ficha termina con "Propuestas": los huecos más grandes respecto al rival, listos para `tools/idea.py add`.
"""
import argparse, collections, json, os, re, statistics, subprocess, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.environ.get('CAMBC_ONLINE_DATA', os.path.join(HERE, 'data'))
sys.path.insert(0, HERE)
from lfl import versions, selector, load_jsonl  # noqa: E402
from dissect_lib import Workspace, Game, cheb, tier  # noqa: E402
BASE = 'https://2026a.battlecode.co.uk'


def tool(name):
    for d in (os.environ.get('HARNESS_TOOLS', ''), os.path.join(HERE, 'tools'), os.path.join(ROOT, 'tools')):
        if d and os.path.exists(os.path.join(d, name)):
            return os.path.join(d, name)
    sys.exit(f'no encuentro {name} (tools/ del repo, online/tools/ o HARNESS_TOOLS)')


def fetch_replay(g, dest):
    if os.path.exists(dest) or not g.get('replay'):
        return os.path.exists(dest)
    for a in range(3):
        try:
            time.sleep(0.5)
            urllib.request.urlretrieve(BASE + g['replay'], dest + '.tmp'); os.replace(dest + '.tmp', dest)
            return True
        except Exception as e:
            print('  descarga fallida', g['match'][:8], e, file=sys.stderr); time.sleep(5 * (a + 1))
    return False


def decode(zip_path, out_path):
    if os.path.exists(out_path):
        return True
    dump, comp = tool('replaydump.js'), tool('compact.py')
    p1 = subprocess.Popen(['node', dump, zip_path, '--every-step', '--camps'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    p2 = subprocess.run([sys.executable, '-I', comp, '/dev/stdin', out_path + '.tmp'], stdin=p1.stdout, capture_output=True)
    p1.wait()
    if p2.returncode == 0 and os.path.getsize(out_path + '.tmp') > 1000:
        with open(out_path + '.tmp', 'rb') as f:   # completa = lleva la línea de resumen del final
            f.seek(max(0, os.path.getsize(out_path + '.tmp') - 65536)); tail = f.read()
        if b'"t": "summary"' in tail:
            os.replace(out_path + '.tmp', out_path); return True
    try: os.remove(out_path + '.tmp')
    except OSError: pass
    return False


def ensure_mapsj(ws_root, names):
    os.makedirs(os.path.join(ws_root, 'mapsj'), exist_ok=True)
    for n in names:
        dst = os.path.join(ws_root, 'mapsj', n + '.json')
        if os.path.exists(dst):
            continue
        src = os.path.join(HERE, 'mapsj', n + '.json')
        if os.path.exists(src):
            open(dst, 'w').write(open(src).read()); continue
        mp = os.path.join(ROOT, 'maps', n + '.map26a')
        if not os.path.exists(mp):
            sys.exit(f'falta el mapa {n}: ni online/mapsj/{n}.json ni maps/{n}.map26a (haz `cambc init --yes` en el repo)')
        r = subprocess.run(['node', tool('mapjson.js'), mp], capture_output=True, text=True)
        if r.returncode != 0: sys.exit('mapjson.js falló: ' + r.stderr[-300:])
        open(dst, 'w').write(r.stdout)


# ---------------------------------------------------------------- métricas
def measure(ws, rec):
    """Una fila por equipo (us/them) con los contadores de esta partida."""
    G = Game(ws, rec); order = G.order; last = order[-1]
    out = {}
    for who, t in (('us', G.side), ('them', 1 - G.side)):
        champs = [i for i in G.types if G.team(i) == t]
        c = collections.Counter(); c['games'] = 1; c['rounds'] = last
        c['win'] = int((rec['result'] == 'win') == (who == 'us'))
        alive_r = 0; dead_r = 0; idle = 0; contact_r = 0; crossings = 0
        for i in champs:
            prev_zone = None
            for r in order:
                if not G.alive(r, i):
                    dead_r += 1; prev_zone = None; continue
                alive_r += 1
                cl = G.classify(r, i)
                if cl == 'nothing': idle += 1
                z = G.zone(i, G.pos(r, i))
                if z == 'enemy' and prev_zone not in (None, 'enemy'): crossings += 1
                prev_zone = z
                if G.nearest_foe(r, i)[0] <= 8: contact_r += 1
                a = G.act[r][i]
                c['spells'] += 'spell' in a; c['atks'] += 'atk' in a
            # muertes
            for r in G.death_round[i]:
                pr = r - 1
                if pr not in G.rounds: continue
                c['deaths'] += 1
                p = G.pos(pr, i)
                c['d_own'] += G.zone(i, p) == 'own'
                c['d_flee'] += any(G.classify(rr, i) in ('away', 'fight+away') for rr in range(r - 3, r) if rr in G.rounds)
                al6 = [x for x in G.allies(pr, i) if cheb(p, (x['x'], x['y'])) <= 6]
                if al6:
                    c['d_ally6'] += 1
                    c['d_ally_idle'] += all(not (G.act[rr][x['i']] & {'atk', 'spell'}) for x in al6 for rr in range(r - 3, r + 1))
                kk = G.killkind.get((r, i), 'other')
                c['d_' + kk] += 1
            # episodios de golpes recibidos: apertura y contacto previo
            hits = [r for r in order if G.champ_dmg(r, i)]
            eps = []
            for r in hits:
                if eps and r - eps[-1][-1] <= 5: eps[-1].append(r)
                else: eps.append([r])
            for ep in eps:
                r0 = ep[0]; pr = r0 - 1
                if pr not in G.rounds or not G.alive(pr, i): continue
                c['eps'] += 1
                c['ep_alone'] += G.nearest_ally_d(pr, i) > 8
                src = G.champ_dmg(r0, i)[0][0]
                if src in G.types and G.alive(pr, src):
                    c['ep_att_alone'] += G.nearest_ally_d(pr, src) > 8
                n = 0; rr = pr
                while rr in G.rounds and G.alive(rr, i) and G.nearest_foe(rr, i)[0] <= 8 and n < 60:
                    n += 1; cl = G.classify(rr, i)
                    key = 'ct_' + ('farm' if cl == 'camp' else 'idle' if cl == 'nothing' else 'away' if cl == 'away' else 'closer' if cl == 'closer'
                                   else 'channel' if cl in ('recall', 'tribute') else 'other')
                    c[key] += 1; rr -= 1
                c['ct_len'] += n
        c['alive_r'] = alive_r; c['dead_r'] = dead_r; c['idle_r'] = idle; c['contact_r'] = contact_r; c['crossings'] = crossings
        c['captures'] = len({r for r, _ in G.captures[t]})
        c['gems'] = 0
        c['fuel'] = G.fuel[t]
        out[who] = c
    # gemas tributadas: último snapshot
    sub = None
    with open(ws.steps_path(rec['match'])) as f:
        for line in f:
            if line.startswith('{"t": "round"') or line.startswith('{"t":"round"'):
                sub = json.loads(line)['sub']
    if sub:
        out['us']['gems'] = sub[G.side]; out['them']['gems'] = sub[1 - G.side]
    return out


def agg(rows):
    tot = {'us': collections.Counter(), 'them': collections.Counter()}
    for row in rows:
        for who in tot: tot[who].update(row[who])
    return tot


def ficha(tot):
    """Métricas por equipo a partir de los contadores agregados."""
    F = {}
    for who, c in tot.items():
        g = max(1, c['games']); d = max(1, c['deaths']); e = max(1, c['eps']); ct = max(1, sum(v for k, v in c.items() if k.startswith('ct_') and k != 'ct_len'))
        F[who] = collections.OrderedDict([
            ('partidas', c['games']), ('victorias %', 100.0 * c['win'] / g),
            ('muertes / partida', c['deaths'] / g),
            ('  en su propia mitad %', 100.0 * c['d_own'] / d),
            ('  huyendo (3 rondas antes) %', 100.0 * c['d_flee'] / d),
            ('  con aliado a 6 que no atacó %', 100.0 * c['d_ally_idle'] / d),
            ('  por hechizo %', 100.0 * c['d_spell'] / d),
            ('  por monstruo %', 100.0 * c['d_camp'] / d),
            ('rondas-campeón muerto %', 100.0 * c['dead_r'] / max(1, c['dead_r'] + c['alive_r'])),
            ('rondas-campeón inactivo %', 100.0 * c['idle_r'] / max(1, c['alive_r'])),
            ('rondas-campeón en contacto (rival a 8) %', 100.0 * c['contact_r'] / max(1, c['alive_r'])),
            ('capturas / 100 rondas-campeón vivas', 100.0 * c['captures'] / max(1, c['alive_r'])),
            ('gemas tributadas / 100 rondas', 100.0 * c['gems'] / max(1, c['rounds'])),
            ('cruces a la mitad enemiga / partida', c['crossings'] / g),
            ('hechizos a campeones / partida', c['spells'] / g),
            ('ataques básicos a campeones / partida', c['atks'] / g),
            ('golpes recibidos (episodios) / partida', c['eps'] / g),
            ('  víctima sin aliado a 8 %', 100.0 * c['ep_alone'] / e),
            ('  atacante sin aliado a 8 %', 100.0 * c['ep_att_alone'] / e),
            ('  contacto previo (rondas, media)', c['ct_len'] / e),
            ('  en contacto: farmeando %', 100.0 * c['ct_farm'] / ct),
            ('  en contacto: inactivo %', 100.0 * c['ct_idle'] / ct),
            ('  en contacto: alejándose %', 100.0 * c['ct_away'] / ct),
            ('  en contacto: acercándose %', 100.0 * c['ct_closer'] / ct),
            ('  en contacto: canalizando (recall/tributo) %', 100.0 * c['ct_channel'] / ct),
            ('turnos sin combustible / partida', c['fuel'] / g),
        ])
    return F


def proposals(F, bymap):
    us, th = F['us'], F['them']; P = []
    def gap(k, worse_if_higher=True, rel=0.15, abs_=0.0):
        a, b = us[k], th[k]
        if b == 0 and a == 0: return None
        diff = a - b if worse_if_higher else b - a
        if diff > max(abs_, rel * max(abs(b), 1e-9)): return diff
        return None
    rules = [
        ('muertes / partida', True, 0.15, 0.3, 'Morimos {a:.1f} veces por partida y el rival {b:.1f}: cada muerte regala las gemas y 60 rondas; mira de qué muertes se compone la ficha (huyendo, solos, hechizo).'),
        ('  huyendo (3 rondas antes) %', True, 0.2, 5, 'El {a:.0f}% de nuestras muertes llegan huyendo (rival {b:.0f}%): huimos tarde o un paso por ronda con el atacante pegado; probar huir antes (umbral de peligro) o no huir y pegar.'),
        ('  víctima sin aliado a 8 %', True, 0.15, 5, 'Nos pegan sin aliado a 8 el {a:.0f}% de las veces (rival {b:.0f}%): farmeamos separados; probar pares/bola por campamento en mapas de pelea.'),
        ('  con aliado a 6 que no atacó %', True, 0.15, 5, 'En el {a:.0f}% de las muertes había un aliado a 6 que no atacó (rival {b:.0f}%): regla de ayuda (si un aliado recibe daño a 6, atacar a su atacante).'),
        ('  en contacto: farmeando %', True, 0.15, 5, 'Con un rival a 8 seguimos farmeando el {a:.0f}% de las rondas (rival {b:.0f}%): reaccionar al contacto antes del primer golpe.'),
        ('  en contacto: inactivo %', True, 0.15, 5, 'Con un rival a 8 estamos parados el {a:.0f}% de las rondas (rival {b:.0f}%): decidir pelea o retirada en cuanto hay contacto.'),
        ('capturas / 100 rondas-campeón vivas', False, 0.08, 0.0, 'Capturamos {a:.2f} por 100 rondas-campeón vivas y el rival {b:.2f}: la velocidad de farmeo también va por detrás (ruta, cola de campamentos, tamaño del grupo).'),
        ('rondas-campeón inactivo %', True, 0.2, 2, 'Rondas inactivas {a:.0f}% vs {b:.0f}%: campeones sin objetivo (cola vacía, esperando respawn); revisar la elección de campamento.'),
        ('hechizos a campeones / partida', False, 0.3, 2, 'Lanzamos {a:.0f} hechizos a campeones por partida y el rival {b:.0f}: los lanzadores no usan sus hechizos en las peleas (alcance, cooldown, objetivo).'),
        ('turnos sin combustible / partida', True, 0.5, 5, 'Turnos sin combustible {a:.0f} por partida (rival {b:.0f}): hay bucles caros por turno; perfilar antes de añadir reglas.'),
        ('cruces a la mitad enemiga / partida', False, 0.3, 1, 'Cruzamos a su mitad {a:.1f} veces por partida y ellos {b:.1f}: no disputamos ni defendemos territorio (ellos capturan en nuestra mitad).'),
    ]
    for k, hi, rel, ab, txt in rules:
        d = gap(k, hi, rel, ab)
        if d is not None:
            P.append((abs(d) / max(abs(th[k]), 1e-9), txt.format(a=us[k], b=th[k])))
    P.sort(reverse=True)
    maps = sorted(bymap.items(), key=lambda kv: (kv[1]['win'] / max(1, kv[1]['games'])))
    worst = [f"{m} {100 * v['win'] / max(1, v['games']):.0f}% ({v['games']} partidas, muertes {v['du'] / max(1, v['games']):.1f} vs {v['dt'] / max(1, v['games']):.1f})"
             for m, v in maps[:3]]
    return [p for _, p in P], worst


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--version', required=True, help='etiqueta de data/versions.jsonl (subcadena) o ventana desde/hasta')
    p.add_argument('--ref', default='', help='segunda versión para comparar nuestra ficha con la suya')
    p.add_argument('--kind', default='unranked'); p.add_argument('--max', type=int, default=150)
    p.add_argument('--maps', default=''); p.add_argument('--jobs', type=int, default=min(4, os.cpu_count() or 2))
    p.add_argument('--out', default='', help='carpeta de salida (por defecto data/dissect/<versión>-<fecha>)')
    p.add_argument('--idea', default='')
    A = p.parse_args()
    vs = versions()
    games = [g for g in load_jsonl(os.path.join(DATA, 'games.jsonl')) if g['result'] in ('win', 'loss') and g['kind'] == A.kind]
    if A.maps: games = [g for g in games if g['map'] in A.maps.split(',')]

    def pick(spec):
        sel, name = selector(spec, vs)
        G = sorted((g for g in games if sel(g)), key=lambda g: g['at'], reverse=True)[:A.max]
        if not G: sys.exit(f'sin partidas para {spec}')
        return name, G
    sets = [pick(A.version)] + ([pick(A.ref)] if A.ref else [])
    slug = re.sub(r'[^a-z0-9]+', '-', sets[0][0].lower())[:30].strip('-')
    out = A.out or os.path.join(DATA, 'dissect', f'{slug}-{time.strftime("%m%d-%H%M", time.gmtime())}')
    steps = os.path.join(out, 'steps'); os.makedirs(steps, exist_ok=True)
    reps = os.path.join(DATA, 'replays'); os.makedirs(reps, exist_ok=True)
    allg = [g for _, G in sets for g in G]
    ensure_mapsj(out, sorted({g['map'] for g in allg}))
    print(f'{len(allg)} partidas; bajando repeticiones que falten a {reps} ...', flush=True)
    todo = [g for g in allg if fetch_replay(g, os.path.join(reps, g['match'] + '.zip'))]
    print(f'decodificando {len(todo)} (caché en {steps}, ~25 s por partida nueva, {A.jobs} a la vez) ...', flush=True)
    t0 = time.time(); done = 0
    with ThreadPoolExecutor(A.jobs) as ex:
        for g, ok in zip(todo, ex.map(lambda g: decode(os.path.join(reps, g['match'] + '.zip'), os.path.join(steps, g['match'] + '.c.jsonl')), todo)):
            done += 1
            if done % 10 == 0: print(f'  {done}/{len(todo)} [{time.time() - t0:.0f}s]', flush=True)
    ws = Workspace(out)
    json.dump([dict(match=g['match'], team='us', side=g['side'], map=g['map'], opp=g['opp'], orank=g['opp_rank'], res=g['result'],
                    score=g['gems'], oscore=g['opp_gems'], rounds=g['rounds'], created=g['at'], draft=g['draft'], version=sets[0][0])
               for g in sets[0][1]], open(os.path.join(out, 'selected.json'), 'w'), indent=0)
    results = []
    for name, G in sets:
        rows = []; bymap = collections.defaultdict(collections.Counter); bytier = collections.defaultdict(collections.Counter)
        for g in G:
            if not os.path.exists(ws.steps_path(g['match'])): continue
            try:
                row = measure(ws, dict(g, side=g['side']))
            except Exception as e:  # una partida rara no tumba la ficha
                print('  no medida', g['match'][:8], g['map'], repr(e)[:80], file=sys.stderr); continue
            rows.append(row)
            for tab, k in ((bymap, g['map']), (bytier, tier(g['opp_rank']))):
                tab[k]['games'] += 1; tab[k]['win'] += row['us']['win']; tab[k]['du'] += row['us']['deaths']; tab[k]['dt'] += row['them']['deaths']
        results.append((name, rows, ficha(agg(rows)), bymap, bytier))
    # ---- ficha.md
    L = [f'# Ficha: {sets[0][0]}', '', f'{len(results[0][1])} partidas {A.kind} medidas (las más recientes, máx. {A.max}), generada {time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())}. '
         'Cada métrica se mide igual para nosotros y para el rival en las mismas partidas.', '']
    short = lambda name: name.split(' (')[0][:30]
    head = '| métrica | nosotros | rival |' + (' nosotros antes (' + short(results[1][0]) + ') |' if len(results) > 1 else '')
    L += [head, '|---|---|---|' + ('---|' if len(results) > 1 else '')]
    F0 = results[0][2]
    for k in F0['us']:
        fmt = (lambda v: f'{v:.0f}') if k == 'partidas' else (lambda v: f'{v:.1f}')
        L.append(f'| {k} | {fmt(F0["us"][k])} | {fmt(F0["them"][k])} |' + (f' {fmt(results[1][2]["us"][k])} |' if len(results) > 1 else ''))
    for title, tab in (('Por mapa', results[0][3]), ('Por nivel de rival', results[0][4])):
        L += ['', f'## {title}', '', '| | partidas | victorias % | muertes nuestras / partida | muertes del rival / partida |', '|---|---|---|---|---|']
        for k, v in sorted(tab.items(), key=lambda kv: kv[1]['win'] / max(1, kv[1]['games'])):
            n = max(1, v['games']); L.append(f"| {k} | {v['games']} | {100 * v['win'] / n:.0f} | {v['du'] / n:.1f} | {v['dt'] / n:.1f} |")
    props, worst = proposals(F0, results[0][3])
    L += ['', '## Propuestas (huecos más grandes respecto al rival, de mayor a menor)', '']
    L += [f'{i + 1}. {t}' for i, t in enumerate(props)] or ['- ninguna métrica va claramente peor que la del rival en estas partidas']
    L += ['', 'Peores mapas: ' + '; '.join(worst), '',
          'Siguiente paso: `python3 tools/idea.py add "..." --kind fight|farm --source "disección ' + short(sets[0][0]) + '"` por cada propuesta que merezca una prueba.',
          f'Workspace para preguntas más finas: `WS={out}` con los scripts de analysis/v35-dissection-2026-10-15/scripts_*.']
    txt = '\n'.join(L) + '\n'
    open(os.path.join(out, 'ficha.md'), 'w').write(txt)
    json.dump({name: {'us': dict(F['us']), 'them': dict(F['them']), 'bymap': bymap, 'bytier': bytier} for name, _, F, bymap, bytier in results},
              open(os.path.join(out, 'ficha.json'), 'w'), indent=1, ensure_ascii=False)
    print(txt); print('escrito en', out)
    if A.idea:
        sys.path.insert(0, os.path.join(ROOT, 'tools'))
        import idea
        idea.record(A.idea, note=f'disección {short(sets[0][0])}: {len(results[0][1])} partidas, {F0["us"]["victorias %"]:.0f}%, muertes {F0["us"]["muertes / partida"]:.1f} vs {F0["them"]["muertes / partida"]:.1f}; ficha en {out}/ficha.md')


if __name__ == '__main__':
    main()
