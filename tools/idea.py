#!/usr/bin/env python3
"""Tracker de ideas y experimentos del harness (harness/ideas/I###.json, un fichero por idea; tablero harness/IDEAS.md).

uso:
  python3 tools/idea.py add "Dos campeones por campamento como Mite" --kind fight --source "disección study28" --owner Javi
  python3 tools/idea.py set I012 --stage desarrollo --bot bots/study29 --branch idea/I012-dos-por-campo --note "..."
  python3 tools/idea.py set I012 --stage online --version "v38 = study29" --note "activada 21:30 UTC"
  python3 tools/idea.py set I012 --stage rechazada --note "online 14 vs 18 en 58 parejas: ruido"
  python3 tools/idea.py list [--stage online] [--kind fight]
  python3 tools/idea.py show I012
  python3 tools/idea.py board          # reescribe harness/IDEAS.md (el tablero) y lo imprime

Etapas, en orden: idea -> desarrollo -> test-local -> local-ok -> online -> aceptada | rechazada | pausada.
gate.py (--idea I012) y online/lfl.py (--idea I012) apuntan su resultado solos. Un fichero por idea para que dos ramas
no choquen en git; el tablero IDEAS.md se regenera con `board` (si choca en un merge, regenéralo).
"""
import argparse, glob, json, os, sys, time

STAGES = ['idea', 'desarrollo', 'test-local', 'local-ok', 'online', 'aceptada', 'rechazada', 'pausada']
KINDS = ['farm', 'fight', 'macro', 'bug', 'infra']
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.environ.get('HARNESS_IDEAS', os.path.join(ROOT, 'harness', 'ideas'))


def now():
    return time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())


def path(iid):
    return os.path.join(DIR, iid + '.json')


def load_all():
    out = []
    for f in sorted(glob.glob(os.path.join(DIR, 'I*.json'))):
        try:
            out.append(json.load(open(f)))
        except ValueError:
            print('fichero roto:', f, file=sys.stderr)
    return out


def load(iid):
    p = path(iid)
    if not os.path.exists(p):
        sys.exit(f'no existe la idea {iid} (ver `idea.py list`)')
    return json.load(open(p))


def save(d):
    os.makedirs(DIR, exist_ok=True)
    d['updated'] = now()
    json.dump(d, open(path(d['id']), 'w'), indent=1, ensure_ascii=False)


def new_id():
    ids = [int(os.path.basename(f)[1:4]) for f in glob.glob(os.path.join(DIR, 'I[0-9][0-9][0-9].json'))]
    return 'I%03d' % (max(ids, default=0) + 1)


def record(iid, stage=None, note='', result='', **fields):
    """Apunta un paso en la historia de la idea (lo usan gate.py y lfl.py). Devuelve la idea."""
    d = load(iid)
    if stage:
        if stage not in STAGES:
            sys.exit(f'etapa desconocida {stage}; usa una de {STAGES}')
        d['stage'] = stage
    for k, v in fields.items():
        if v:
            d[k] = v
    d.setdefault('history', []).append({k: v for k, v in dict(at=now(), stage=d['stage'], note=note, result=result).items() if v})
    save(d)
    return d


def board(ideas):
    live = [d for d in ideas if d['stage'] not in ('aceptada', 'rechazada', 'pausada')]
    done = [d for d in ideas if d['stage'] in ('aceptada', 'rechazada', 'pausada')]
    order = {s: i for i, s in enumerate(STAGES)}
    L = ['# Tablero de ideas', '',
         f'Generado por `python3 tools/idea.py board` el {now()}. Pipeline y puertas: [harness/README.md](README.md).', '',
         '## En curso', '', '| id | idea | tipo | etapa | quién | bot / rama / PR | último resultado |', '|---|---|---|---|---|---|---|']
    for d in sorted(live, key=lambda d: (-order[d['stage']], d['id'])):
        L.append(row(d))
    L += ['', '## Cerradas', '', '| id | idea | tipo | etapa | quién | bot / rama / PR | resultado |', '|---|---|---|---|---|---|---|']
    for d in sorted(done, key=lambda d: d['id']):
        L.append(row(d))
    L += ['', '## Por etapa', '']
    for s in STAGES:
        n = [d['id'] for d in ideas if d['stage'] == s]
        L.append(f'- **{s}**: {len(n)}' + (' (' + ', '.join(n) + ')' if n else ''))
    return '\n'.join(L) + '\n'


def row(d):
    where = ' / '.join(x for x in (d.get('bot'), d.get('branch'), ('PR #%s' % d['pr']) if d.get('pr') else '', d.get('version')) if x)
    last = d['history'][-1] if d.get('history') else {}
    res = (last.get('note') or '').replace('|', '/').replace('\n', ' ')
    return f"| {d['id']} | {d['title']} | {d.get('kind', '')} | {d['stage']} | {d.get('owner', '')} | {where} | {res[:140]} |"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('add'); a.add_argument('title')
    a.add_argument('--kind', choices=KINDS, required=True); a.add_argument('--source', default='', help='de dónde sale (disección, estudio top, brainstorm...)')
    a.add_argument('--owner', default=''); a.add_argument('--note', default=''); a.add_argument('--hypothesis', default='', help='qué número esperamos mover y cuánto')
    s = sub.add_parser('set'); s.add_argument('id'); s.add_argument('--stage', choices=STAGES)
    for f in ('bot', 'branch', 'pr', 'version', 'owner', 'note', 'result', 'title', 'hypothesis'):
        s.add_argument('--' + f, default='')
    l = sub.add_parser('list'); l.add_argument('--stage'); l.add_argument('--kind')
    sh = sub.add_parser('show'); sh.add_argument('id')
    sub.add_parser('board')
    A = p.parse_args()
    if A.cmd == 'add':
        d = dict(id=new_id(), title=A.title, kind=A.kind, source=A.source, owner=A.owner, hypothesis=A.hypothesis,
                 stage='idea', created=now(), history=[dict(at=now(), stage='idea', note=A.note)])
        save(d); print(d['id'], d['title'])
    elif A.cmd == 'set':
        d = record(A.id, stage=A.stage or None, note=A.note, result=A.result, bot=A.bot, branch=A.branch, pr=A.pr,
                   version=A.version, owner=A.owner, title=A.title, hypothesis=A.hypothesis)
        print(d['id'], d['stage'], '-', d['title'])
    elif A.cmd == 'list':
        for d in load_all():
            if (A.stage and d['stage'] != A.stage) or (A.kind and d.get('kind') != A.kind):
                continue
            print(f"{d['id']}  {d['stage']:10s} {d.get('kind', ''):5s} {d['title']}")
    elif A.cmd == 'show':
        d = load(A.id)
        for k in ('id', 'title', 'kind', 'stage', 'owner', 'source', 'hypothesis', 'bot', 'branch', 'pr', 'version', 'created', 'updated'):
            if d.get(k): print(f'{k:11s} {d[k]}')
        print('historia:')
        for h in d.get('history', []):
            print(f"  {h['at']}  {h['stage']:10s} {h.get('note', '')}" + (f"  [{h['result']}]" if h.get('result') else ''))
    elif A.cmd == 'board':
        txt = board(load_all())
        os.makedirs(DIR, exist_ok=True)
        open(os.path.join(os.path.dirname(DIR), 'IDEAS.md'), 'w').write(txt); print(txt)
    if A.cmd in ('add', 'set'):
        open(os.path.join(os.path.dirname(DIR), 'IDEAS.md'), 'w').write(board(load_all()))


if __name__ == '__main__':
    main()
