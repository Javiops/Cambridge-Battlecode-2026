#!/usr/bin/env python3
"""Comparación online emparejada (like-for-like) de dos versiones: etapa 3 del harness.

Online el rival y el mapa cambian cada hora, así que el porcentaje bruto de un batch no dice nada (hoy fue del 25% al
41% sin cambiar el bot). Lo que sí se puede comparar es la MISMA pareja (rival, mapa, lado) jugada con la versión A y
con la versión B: el motor es determinista, así que cada pareja es un experimento controlado.

uso (desde online/, con data/games.jsonl y data/versions.jsonl al día; `python3 collect.py` antes):
  python3 lfl.py --a "corners fix" --b "study27"                 # etiquetas de data/versions.jsonl (subcadena)
  python3 lfl.py --a 2026-10-15T20:00/2026-10-15T22:00 --b 2026-10-15T15:30/2026-10-15T17:00   # ventanas de tiempo
  python3 lfl.py --a "corners fix" --b study27 --maps corners,rows --idea I012   # apunta el resultado en el tracker

Lee: unranked por defecto (--kind ranked|all), ambos lados (la pareja incluye el lado). Si una pareja se repitió,
cuenta la partida más reciente de cada versión. Imprime: récord bruto de cada versión, récord ranked en su ventana,
parejas compartidas y quién las gana, por mapa y por nivel de rival, y el veredicto con el test de signos sobre las
parejas que cambian de resultado.

Regla de parada (harness/README.md): se decide con p<0.05 sobre las parejas que cambian; mientras no, sigue alternando
las dos versiones hora a hora contra los mismos 30 equipos (challenge.py --top 30). Con ~100 parejas se ve un +10%.
"""
import argparse, collections, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('CAMBC_ONLINE_DATA', os.path.join(HERE, 'data'))


def load_jsonl(p):
    return [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []


def sign_p(k, n):
    if n == 0:
        return 1.0
    return min(1.0, sum(math.comb(n, i) for i in range(n + 1) if abs(i - n / 2) >= abs(k - n / 2)) / 2 ** n)


def versions():
    vs = []
    for v in load_jsonl(os.path.join(DATA, 'versions.jsonl')):
        t = v.get('at') or v.get('from')
        if t:
            vs.append((t, v['version']))
    return sorted(vs)


def label_of(t, vs):
    lab = '?'
    for at, v in vs:
        if at <= t:
            lab = v
    return lab


def selector(spec, vs):
    """'desde/hasta' = ventana de tiempo; si no, subcadena de la etiqueta de versión."""
    if '/' in spec:
        a, b = spec.split('/', 1)
        return (lambda g: a <= g['at'] <= (b or '9')), f'{a} .. {b}'
    s = spec.lower()
    labs = sorted({v for _, v in vs if s in v.lower()})
    if not labs:
        sys.exit(f'ninguna versión de data/versions.jsonl contiene "{spec}"; etiquetas: {sorted({v for _, v in vs})}')
    return (lambda g: s in label_of(g['at'], vs).lower()), ' | '.join(labs)


def tier(r):
    r = r or 999
    return 'top 10' if r <= 10 else 'top 11-30' if r <= 30 else 'resto'


def rec(games):
    w = sum(g['result'] == 'win' for g in games); n = len(games)
    return f'{w}-{n - w} ({100 * w / max(1, n):.0f}%)'


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--a', required=True, help='versión candidata (etiqueta o desde/hasta)')
    p.add_argument('--b', required=True, help='versión de referencia')
    p.add_argument('--kind', default='unranked', help='unranked (por defecto), ranked o all')
    p.add_argument('--maps', default='', help='solo estos mapas, separados por comas')
    p.add_argument('--since', default='', help='ignora partidas anteriores a esta hora ISO')
    p.add_argument('--idea', default='', help='apunta el resultado en harness/ideas (tools/idea.py)')
    A = p.parse_args()
    vs = versions()
    games = [g for g in load_jsonl(os.path.join(DATA, 'games.jsonl')) if g['result'] in ('win', 'loss') and g['at'] >= A.since]
    if A.maps:
        games = [g for g in games if g['map'] in A.maps.split(',')]
    selA, nameA = selector(A.a, vs); selB, nameB = selector(A.b, vs)
    kinds = ('unranked', 'ranked') if A.kind == 'all' else (A.kind,)
    GA = [g for g in games if g['kind'] in kinds and selA(g)]
    GB = [g for g in games if g['kind'] in kinds and selB(g)]
    RA = [g for g in games if g['kind'] == 'ranked' and selA(g)]
    RB = [g for g in games if g['kind'] == 'ranked' and selB(g)]
    if not GA or not GB:
        sys.exit(f'sin partidas: A {len(GA)}, B {len(GB)} (¿collect.py? ¿etiqueta? ¿--kind?)')
    print(f'A = {nameA}: {len(GA)} partidas {A.kind}, {rec(GA)}; vs top 10 {rec([g for g in GA if tier(g["opp_rank"]) == "top 10"])}; '
          f'ranked en su ventana {rec(RA)} ({min(g["at"] for g in GA)[11:16]}-{max(g["at"] for g in GA)[11:16]} UTC)')
    print(f'B = {nameB}: {len(GB)} partidas {A.kind}, {rec(GB)}; vs top 10 {rec([g for g in GB if tier(g["opp_rank"]) == "top 10"])}; '
          f'ranked en su ventana {rec(RB)} ({min(g["at"] for g in GB)[11:16]}-{max(g["at"] for g in GB)[11:16]} UTC)')

    def latest(G):
        d = {}
        for g in sorted(G, key=lambda g: g['at']):
            d[(g['opp_id'], g['map'], g['side'])] = g
        return d
    da, db = latest(GA), latest(GB)
    keys = sorted(set(da) & set(db))
    if not keys:
        sys.exit('ninguna pareja (rival, mapa, lado) jugada con las dos versiones: reta a los mismos equipos con las dos')
    both_w = both_l = a_only = b_only = 0
    bymap = collections.defaultdict(lambda: [0, 0, 0]); bytier = collections.defaultdict(lambda: [0, 0, 0])
    flips = []
    for k in keys:
        wa, wb = da[k]['result'] == 'win', db[k]['result'] == 'win'
        for tab, kk in ((bymap, k[1]), (bytier, tier(da[k]['opp_rank']))):
            tab[kk][0] += 1; tab[kk][1] += wa; tab[kk][2] += wb
        if wa and wb: both_w += 1
        elif not wa and not wb: both_l += 1
        elif wa: a_only += 1; flips.append(('A', da[k]))
        else: b_only += 1; flips.append(('B', db[k]))
    n = a_only + b_only; pv = sign_p(a_only, n)
    print(f'\nParejas compartidas (rival, mapa, lado): {len(keys)}. Ganan las dos {both_w}, pierden las dos {both_l}, '
          f'solo A gana {a_only}, solo B gana {b_only}.  A {both_w + a_only} vs B {both_w + b_only}, p={pv:.3f}')
    print(f"\n{'mapa':12s} {'parejas':>7s} {'A gana':>7s} {'B gana':>7s}")
    for m, (c, wa, wb) in sorted(bymap.items(), key=lambda kv: -(kv[1][1] - kv[1][2])):
        print(f'{m:12s} {c:7d} {wa:7d} {wb:7d}')
    print(f"\n{'rival':12s} {'parejas':>7s} {'A gana':>7s} {'B gana':>7s}")
    for m, (c, wa, wb) in bytier.items():
        print(f'{m:12s} {c:7d} {wa:7d} {wb:7d}')
    if flips:
        print('\nParejas que cambian (las 12 más recientes):')
        for who, g in sorted(flips, key=lambda x: x[1]['at'])[-12:]:
            print(f"  gana solo {who}: {g['map']:10s} vs {g['opp']} (#{g['opp_rank']}) lado {g['side']}  gemas {g['gems']}-{g['opp_gems']}")
    if n == 0:
        verdict = 'IGUALES: ninguna pareja cambia de resultado.'
    elif pv < 0.05:
        verdict = f"{'A ES MEJOR' if a_only > b_only else 'A ES PEOR'} que B (p={pv:.3f} sobre {n} parejas que cambian)."
    else:
        q = max(a_only, b_only) / n
        need = math.ceil(((1.96 * 0.5 + 0.84 * math.sqrt(q * (1 - q))) / (q - 0.5)) ** 2) if q > 0.5 else None
        verdict = (f'SIN DECIDIR (p={pv:.3f}): {a_only} vs {b_only} en las parejas que cambian' +
                   (f'; a este ritmo harían falta ~{need} parejas que cambien (hay {n}): sigue alternando A y B.' if need and need < 1000
                    else '; diferencia nula a efectos prácticos: trátalo como empate.'))
    print('\nVeredicto:', verdict)
    if A.idea:
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'tools'))
        import idea
        stage = 'aceptada' if (pv < 0.05 and a_only > b_only) else 'rechazada' if (pv < 0.05 and a_only < b_only) else None
        idea.record(A.idea, stage=stage, note=f'online lfl {nameA} vs {nameB}: parejas {len(keys)}, solo A {a_only} / solo B {b_only}, p={pv:.3f}. {verdict}')
        print(f'apuntado en {A.idea}' + (f' (etapa {stage})' if stage else ''))


if __name__ == '__main__':
    main()
