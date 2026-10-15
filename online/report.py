"""Win rates from data/games.jsonl. Usage: python3 report.py [--since 2026-10-15T11:00] [--kind unranked]"""
import sys, collections
from common import *
args = sys.argv[1:]; since = args[args.index('--since') + 1] if '--since' in args else ''
kind = args[args.index('--kind') + 1] if '--kind' in args else None
vers = sorted(load_jsonl(DATA + '/versions.jsonl'), key=lambda v: v['at'])
def version_at(t):
    v = [x['version'] for x in vers if x['at'] <= t]
    return v[-1] if v else '?'
games = [g for g in load_jsonl(DATA + '/games.jsonl') if g['at'] >= since and (kind is None or g['kind'] == kind) and g['result'] in ('win', 'loss')]
def table(key, rows, title):
    c = collections.defaultdict(lambda: [0, 0, 0])
    for g in rows: c[key(g)][0 if g['result'] == 'win' else 1] += 1; c[key(g)][2] += (g['gems'] or 0) - (g['opp_gems'] or 0)
    print(f'\n{title}'); 
    for k, (w, l, d) in sorted(c.items(), key=lambda kv: -(kv[1][0] + kv[1][1])): print(f'  {str(k):36s} {w:3d}-{l:<3d} {100*w/max(1,w+l):3.0f}%  gem diff/game {d/max(1,w+l):+5.0f}')
print(f'{len(games)} games since "{since or "start"}": {sum(g["result"]=="win" for g in games)} wins ({100*sum(g["result"]=="win" for g in games)/max(1,len(games)):.0f}%)')
table(lambda g: g['map'], games, 'by map'); table(lambda g: f"{g['opp']} (#{g['opp_rank']})", games, 'by opponent')
table(lambda g: 'top 10' if (g['opp_rank'] or 999) <= 10 else 'top 11-30' if (g['opp_rank'] or 999) <= 30 else 'others', games, 'by opponent tier')
table(lambda g: g['at'][:13] + 'h', games, 'by hour'); table(lambda g: f'v{version_at(g["at"])}', games, 'by active version (data/versions.jsonl)')
