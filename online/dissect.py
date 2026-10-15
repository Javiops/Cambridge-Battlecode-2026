#!/usr/bin/env python3
"""One-command dissection (stage 4 of the harness): from the online games of a version to its metric scorecard and a
list of proposals for the brainstorm.

usage (from online/, with data/games.jsonl up to date):
  python3 dissect.py --version "corners fix"                      # the latest 150 unranked games of that label
  python3 dissect.py --version "corners fix" --ref "v36 = study27"  # extra column: the same scorecard of the previous version
  python3 dissect.py --version 2026-10-15T20:00/2026-10-15T22:00 --max 60 --maps corners,rows --jobs 4
  python3 dissect.py --version "corners fix" --idea I012          # record the summary on the board

What it does: picks the games (a label from data/versions.jsonl or a from/to window), downloads the missing replays
to data/replays/, decodes them step by step (tools/replaydump.js + tools/compact.py, ~25 s per game, in parallel and
cached in <out>/steps/) and measures the same things for us and for the rival in the same games: deaths and how we
die, captures per champion-round, dead and idle time, contact before the first hit, openings alone, spells, fuel.
Writes <out>/scorecard.md, scorecard.json and selected.json (the workspace the scripts in
analysis/v35-dissection-2026-10-15/scripts_* read for finer questions: WS=<out>).

The scorecard ends with "Proposals": the biggest gaps against the rival, ready for `tools/idea.py add`.
"""
import argparse, collections, json, os, re, subprocess, sys, time, urllib.request
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
    sys.exit(f'cannot find {name} (the repo tools/, online/tools/ or HARNESS_TOOLS)')


def fetch_replay(g, dest):
    if os.path.exists(dest) or not g.get('replay'):
        return os.path.exists(dest)
    for a in range(3):
        try:
            time.sleep(0.5)
            urllib.request.urlretrieve(BASE + g['replay'], dest + '.tmp'); os.replace(dest + '.tmp', dest)
            return True
        except Exception as e:
            print('  download failed', g['match'][:8], e, file=sys.stderr); time.sleep(5 * (a + 1))
    return False


def decode(zip_path, out_path):
    if os.path.exists(out_path):
        return True
    dump, comp = tool('replaydump.js'), tool('compact.py')
    p1 = subprocess.Popen(['node', dump, zip_path, '--every-step', '--camps'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    p2 = subprocess.run([sys.executable, '-I', comp, '/dev/stdin', out_path + '.tmp'], stdin=p1.stdout, capture_output=True)
    p1.wait()
    if p2.returncode == 0 and os.path.getsize(out_path + '.tmp') > 1000:
        with open(out_path + '.tmp', 'rb') as f:   # complete = it carries the summary line at the end
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
            sys.exit(f'missing map {n}: neither online/mapsj/{n}.json nor maps/{n}.map26a (run `cambc init --yes` in the repo)')
        r = subprocess.run(['node', tool('mapjson.js'), mp], capture_output=True, text=True)
        if r.returncode != 0: sys.exit('mapjson.js failed: ' + r.stderr[-300:])
        open(dst, 'w').write(r.stdout)


# ---------------------------------------------------------------- metrics
def measure(ws, rec):
    """One row per team (us/them) with this game's counters."""
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
            # deaths
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
            # episodes of hits taken: opening and the contact before it
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
    # tributed gems: the last snapshot
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


def scorecard(tot):
    """Per-team metrics from the aggregated counters."""
    F = {}
    for who, c in tot.items():
        g = max(1, c['games']); d = max(1, c['deaths']); e = max(1, c['eps']); ct = max(1, sum(v for k, v in c.items() if k.startswith('ct_') and k != 'ct_len'))
        F[who] = collections.OrderedDict([
            ('games', c['games']), ('win %', 100.0 * c['win'] / g),
            ('deaths / game', c['deaths'] / g),
            ('  in own half %', 100.0 * c['d_own'] / d),
            ('  while fleeing (3 rounds before) %', 100.0 * c['d_flee'] / d),
            ('  with an ally within 6 that did not attack %', 100.0 * c['d_ally_idle'] / d),
            ('  by spell %', 100.0 * c['d_spell'] / d),
            ('  by monster %', 100.0 * c['d_camp'] / d),
            ('champion-rounds dead %', 100.0 * c['dead_r'] / max(1, c['dead_r'] + c['alive_r'])),
            ('champion-rounds idle %', 100.0 * c['idle_r'] / max(1, c['alive_r'])),
            ('champion-rounds in contact (enemy within 8) %', 100.0 * c['contact_r'] / max(1, c['alive_r'])),
            ('captures / 100 alive champion-rounds', 100.0 * c['captures'] / max(1, c['alive_r'])),
            ('tributed gems / 100 rounds', 100.0 * c['gems'] / max(1, c['rounds'])),
            ('crossings into the enemy half / game', c['crossings'] / g),
            ('spells at champions / game', c['spells'] / g),
            ('basic attacks at champions / game', c['atks'] / g),
            ('hit episodes taken / game', c['eps'] / g),
            ('  victim with no ally within 8 %', 100.0 * c['ep_alone'] / e),
            ('  attacker with no ally within 8 %', 100.0 * c['ep_att_alone'] / e),
            ('  contact before the hit (rounds, mean)', c['ct_len'] / e),
            ('  in contact: farming %', 100.0 * c['ct_farm'] / ct),
            ('  in contact: idle %', 100.0 * c['ct_idle'] / ct),
            ('  in contact: moving away %', 100.0 * c['ct_away'] / ct),
            ('  in contact: moving closer %', 100.0 * c['ct_closer'] / ct),
            ('  in contact: channeling (recall/tribute) %', 100.0 * c['ct_channel'] / ct),
            ('fuel-exhausted turns / game', c['fuel'] / g),
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
        ('deaths / game', True, 0.15, 0.3, 'We die {a:.1f} times a game and the rival {b:.1f}: every death gives away the gems and 60 rounds; look at what the deaths are made of in the scorecard (fleeing, alone, spells).'),
        ('  while fleeing (3 rounds before) %', True, 0.2, 5, '{a:.0f}% of our deaths come while fleeing (rival {b:.0f}%): we flee late or one tile a round with the attacker adjacent; try fleeing earlier (danger threshold) or not fleeing and hitting back.'),
        ('  victim with no ally within 8 %', True, 0.15, 5, 'We get hit with no ally within 8 in {a:.0f}% of the episodes (rival {b:.0f}%): we farm apart; try pairs/a ball per camp on fight maps.'),
        ('  with an ally within 6 that did not attack %', True, 0.15, 5, 'In {a:.0f}% of our deaths an ally within 6 never attacked (rival {b:.0f}%): a help rule (when an ally within 6 takes damage, attack its attacker).'),
        ('  in contact: farming %', True, 0.15, 5, 'With an enemy within 8 we keep farming {a:.0f}% of the rounds (rival {b:.0f}%): react to contact before the first hit.'),
        ('  in contact: idle %', True, 0.15, 5, 'With an enemy within 8 we stand still {a:.0f}% of the rounds (rival {b:.0f}%): decide fight or retreat as soon as there is contact.'),
        ('captures / 100 alive champion-rounds', False, 0.08, 0.0, 'We capture {a:.2f} per 100 alive champion-rounds and the rival {b:.2f}: farming speed is also behind (route, camp queue, squad size).'),
        ('champion-rounds idle %', True, 0.2, 2, 'Idle rounds {a:.0f}% vs {b:.0f}%: champions without a target (empty queue, waiting for a respawn); review the camp choice.'),
        ('spells at champions / game', False, 0.3, 2, 'We cast {a:.0f} spells at champions a game and the rival {b:.0f}: the casters do not use their spells in fights (range, cooldown, target).'),
        ('fuel-exhausted turns / game', True, 0.5, 5, 'Fuel-exhausted turns {a:.0f} a game (rival {b:.0f}): there are expensive per-turn loops; profile before adding rules.'),
        ('crossings into the enemy half / game', False, 0.3, 1, 'We cross into their half {a:.1f} times a game and they {b:.1f}: we neither contest nor defend territory (they capture in our half).'),
    ]
    for k, hi, rel, ab, txt in rules:
        d = gap(k, hi, rel, ab)
        if d is not None:
            P.append((abs(d) / max(abs(th[k]), 1e-9), txt.format(a=us[k], b=th[k])))
    P.sort(reverse=True)
    maps = sorted(bymap.items(), key=lambda kv: (kv[1]['win'] / max(1, kv[1]['games'])))
    worst = [f"{m} {100 * v['win'] / max(1, v['games']):.0f}% ({v['games']} games, deaths {v['du'] / max(1, v['games']):.1f} vs {v['dt'] / max(1, v['games']):.1f})"
             for m, v in maps[:3]]
    return [p for _, p in P], worst


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--version', required=True, help='label from data/versions.jsonl (substring) or a from/to window')
    p.add_argument('--ref', default='', help='a second version to compare our scorecard with')
    p.add_argument('--kind', default='unranked'); p.add_argument('--max', type=int, default=150)
    p.add_argument('--maps', default=''); p.add_argument('--jobs', type=int, default=min(4, os.cpu_count() or 2))
    p.add_argument('--out', default='', help='output folder (default data/dissect/<version>-<date>)')
    p.add_argument('--idea', default='')
    A = p.parse_args()
    vs = versions()
    games = [g for g in load_jsonl(os.path.join(DATA, 'games.jsonl')) if g['result'] in ('win', 'loss') and g['kind'] == A.kind]
    if A.maps: games = [g for g in games if g['map'] in A.maps.split(',')]

    def pick(spec):
        sel, name = selector(spec, vs)
        G = sorted((g for g in games if sel(g)), key=lambda g: g['at'], reverse=True)[:A.max]
        if not G: sys.exit(f'no games for {spec}')
        return name, G
    sets = [pick(A.version)] + ([pick(A.ref)] if A.ref else [])
    short = lambda name: name.split(' (')[0][:30]
    slug = re.sub(r'[^a-z0-9]+', '-', sets[0][0].lower())[:30].strip('-')
    out = A.out or os.path.join(DATA, 'dissect', f'{slug}-{time.strftime("%m%d-%H%M", time.gmtime())}')
    steps = os.path.join(out, 'steps'); os.makedirs(steps, exist_ok=True)
    reps = os.path.join(DATA, 'replays'); os.makedirs(reps, exist_ok=True)
    allg = [g for _, G in sets for g in G]
    ensure_mapsj(out, sorted({g['map'] for g in allg}))
    print(f'{len(allg)} games; downloading missing replays to {reps} ...', flush=True)
    todo = [g for g in allg if fetch_replay(g, os.path.join(reps, g['match'] + '.zip'))]
    print(f'decoding {len(todo)} (cache in {steps}, ~25 s per new game, {A.jobs} at a time) ...', flush=True)
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
            except Exception as e:  # one odd game does not sink the scorecard
                print('  not measured', g['match'][:8], g['map'], repr(e)[:80], file=sys.stderr); continue
            rows.append(row)
            for tab, k in ((bymap, g['map']), (bytier, tier(g['opp_rank']))):
                tab[k]['games'] += 1; tab[k]['win'] += row['us']['win']; tab[k]['du'] += row['us']['deaths']; tab[k]['dt'] += row['them']['deaths']
        results.append((name, rows, scorecard(agg(rows)), bymap, bytier))
    # ---- scorecard.md
    L = [f'# Scorecard: {sets[0][0]}', '', f'{len(results[0][1])} {A.kind} games measured (the most recent, max {A.max}), generated {time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())}. '
         'Every metric is measured the same way for us and for the rival in the same games.', '']
    head = '| metric | us | rival |' + (' us before (' + short(results[1][0]) + ') |' if len(results) > 1 else '')
    L += [head, '|---|---|---|' + ('---|' if len(results) > 1 else '')]
    F0 = results[0][2]
    for k in F0['us']:
        fmt = (lambda v: f'{v:.0f}') if k == 'games' else (lambda v: f'{v:.1f}')
        L.append(f'| {k} | {fmt(F0["us"][k])} | {fmt(F0["them"][k])} |' + (f' {fmt(results[1][2]["us"][k])} |' if len(results) > 1 else ''))
    for title, tab in (('By map', results[0][3]), ('By rival tier', results[0][4])):
        L += ['', f'## {title}', '', '| | games | win % | our deaths / game | rival deaths / game |', '|---|---|---|---|---|']
        for k, v in sorted(tab.items(), key=lambda kv: kv[1]['win'] / max(1, kv[1]['games'])):
            n = max(1, v['games']); L.append(f"| {k} | {v['games']} | {100 * v['win'] / n:.0f} | {v['du'] / n:.1f} | {v['dt'] / n:.1f} |")
    props, worst = proposals(F0, results[0][3])
    L += ['', '## Proposals (biggest gaps against the rival, largest first)', '']
    L += [f'{i + 1}. {t}' for i, t in enumerate(props)] or ['- no metric is clearly worse than the rival in these games']
    L += ['', 'Worst maps: ' + '; '.join(worst), '',
          'Next step: `python3 tools/idea.py add "..." --kind fight|farm --source "dissection ' + short(sets[0][0]) + '"` for every proposal worth a test.',
          f'Workspace for finer questions: `WS={out}` with the scripts in analysis/v35-dissection-2026-10-15/scripts_*.']
    txt = '\n'.join(L) + '\n'
    open(os.path.join(out, 'scorecard.md'), 'w').write(txt)
    json.dump({name: {'us': dict(F['us']), 'them': dict(F['them']), 'bymap': bymap, 'bytier': bytier} for name, _, F, bymap, bytier in results},
              open(os.path.join(out, 'scorecard.json'), 'w'), indent=1, ensure_ascii=False)
    print(txt); print('written to', out)
    if A.idea:
        sys.path.insert(0, os.path.join(ROOT, 'tools'))
        import idea
        idea.record(A.idea, note=f'dissection {short(sets[0][0])}: {len(results[0][1])} games, {F0["us"]["win %"]:.0f}%, deaths {F0["us"]["deaths / game"]:.1f} vs {F0["them"]["deaths / game"]:.1f}; scorecard in {out}/scorecard.md')


if __name__ == '__main__':
    main()
