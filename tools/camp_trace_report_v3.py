#!/usr/bin/env python3
"""Audit V53 camp logs using match statistics and actual champion-turn density.

Run from the repository root:
  python3 path/to/camp_trace_report_v3.py out/ab/diag_varg_trace_vs_exp_varg_camp_v53/official

This program never calls a game runner or changes bot strategy. Engine statistics
are authoritative for match duration / champion deaths; stdout labels are only
observed decision samples, NOT verified captures, kills, or all-game coverage.
"""
from __future__ import annotations
import collections
import json
import pathlib
import statistics
import sys


def num(v):
    try:
        return int(v)
    except (ValueError, TypeError):
        return None


def cand_stats(stats, side):
    champions = stats.get('champions')
    if not isinstance(champions, list):
        return None, None, set()
    selected = []
    for c in champions:
        side_value = c.get('team')
        if side_value in ('teamA' if side == 'A' else 'teamB', 0 if side == 'A' else 1):
            selected.append(c)
    ds = []
    interesting = set()
    for c in selected:
        metrics = c.get('metrics', c)
        if not isinstance(metrics, dict):
            continue
        v = num(metrics.get('deaths'))
        if v is not None:
            ds.append(v)
        interesting.update(k for k in metrics if any(x in k.lower() for x in ('camp','captur','monster','gem','gold')))
    return len(selected) if selected else None, sum(ds) if ds else None, interesting


def read_t(path):
    samples = collections.defaultdict(list)
    farm = collections.Counter()
    mode = collections.Counter()
    n_malformed = 0
    for raw in path.read_text(encoding='utf8', errors='replace').splitlines():
        if not raw.startswith('T '):
            continue
        f = raw.split()
        if len(f) < 18:
            n_malformed += 1
            continue
        try:
            r, who = int(f[1]), int(f[2])
            samples[who].append((r, f[5], f[9], f[10]))
        except ValueError:
            n_malformed += 1
            continue
        mode[f[9]] += 1
        farm[f[10]] += 1
    return samples, farm, mode, n_malformed


def main(root):
    paths = sorted(root.glob('*_A/team-a.stdout')) + sorted(root.glob('*_B/team-b.stdout'))
    if not paths:
        print('No candidate stdout files found. Did you use --keep?', file=sys.stderr)
        return 2
    n_stats = 0
    sum_expected = 0
    sum_observed = 0
    total_trace = 0
    unique_obs = 0
    comparable = []
    stats_deaths = 0
    stats_death_games = 0
    incomplete = []
    gap_count = continuous_count = 0
    all_farm = collections.Counter()
    all_mode = collections.Counter()
    available_metrics = set()
    per_game = []
    for p in paths:
        side = 'A' if p.parent.name.endswith('_A') else 'B'
        logs, farm, mode, malformed = read_t(p)
        all_farm.update(farm)
        all_mode.update(mode)
        n_rows = sum(len(rows) for rows in logs.values())
        total_trace += n_rows
        n_unique = sum(len({r for r, *_ in rows}) for rows in logs.values())
        unique_obs += n_unique
        seen_champs = len(logs)
        local_gap = local_cont = 0
        for who, rows in logs.items():
            rr = sorted(set(r for r, *_ in rows))
            for r0, r1 in zip(rr, rr[1:]):
                local_cont += int(r1 == r0 + 1)
                local_gap += int(r1 > r0 + 1)
        continuous_count += local_cont
        gap_count += local_gap
        sp = p.parent / 'stats.json'
        if not sp.exists():
            incomplete.append((p.parent.name, 'missing stats.json'))
            continue
        try:
            d = json.loads(sp.read_text(encoding='utf8'))
        except (OSError, ValueError):
            incomplete.append((p.parent.name, 'unreadable stats.json'))
            continue
        rounds = num(d.get('match', {}).get('roundsCompleted', d.get('round')))
        n_champs, deaths, metric_keys = cand_stats(d, side)
        available_metrics.update(metric_keys)
        n_champs = n_champs or seen_champs
        if rounds is None or rounds <= 0 or not n_champs:
            incomplete.append((p.parent.name, 'unknown duration/champion count'))
            continue
        n_stats += 1
        n_expected = rounds * n_champs
        sum_expected += n_expected
        sum_observed += n_unique
        density = n_unique / n_expected
        per_game.append((density, p.parent.name, n_unique, n_expected, n_champs, rounds))
        if deaths is not None:
            stats_death_games += 1
            stats_deaths += deaths
        if n_unique > n_expected:
            incomplete.append((p.parent.name, 'more traced rows than expected; inspect logging'))
    print(f'Candidate matches with trace files: {len(paths)}; match statistics read: {n_stats}')
    print(f'Observed T lines: {total_trace:,}, unique champion-round samples: {unique_obs:,}')
    print(f'Average T lines per match: {total_trace / len(paths):.1f}')
    if sum_expected:
        print(f'Expected champion-turns (approx., round count x roster): {sum_expected:,}')
        print(f'**Actual trace density: {sum_observed / sum_expected:.1%} of expected champion-turns**')
        print('  Note: roster alive/dead still has a turn; this is an approximate completeness denominator.')
    if continuous_count + gap_count:
        print(f'Observed adjacent same-champion round pairs: {continuous_count:,} contiguous, {gap_count:,} with gaps')
        print(f'  Gap rate: {gap_count / (continuous_count + gap_count):.1%}')
    if stats_death_games:
        print(f'**Actual candidate champion deaths from engine stats: {stats_deaths} across {stats_death_games} games**')
    else:
        print('Actual deaths: unavailable from match stats, cannot infer zero deaths from T lines.')
    print('Observed decisions (sampled, NOT all champion-turns):')
    for k in ('fight-camp','capture','approach','wait-respawn','rally','bail'):
        print(f'  {k:16s} {all_farm[k]:>6,}')
    print('  dead-mode lines: {:,} (NOT deaths)'.format(all_mode['dead']))
    print('Relevant fields provided by engine champion metrics:')
    print('  '+(', '.join(sorted(available_metrics)) if available_metrics else '(none found)'))
    print('Least complete logged games:')
    for den, name, samples, expected, champs, rounds in sorted(per_game)[:6]:
        print(f'  {name}: {samples}/{expected} ({den:.1%}), roster={champs}, rounds={rounds}')
    if incomplete:
        print(f'Warnings: {len(incomplete)} games have incomplete stats/metadata')
        for name, why in incomplete[:5]:
            print(f'  {name}: {why}')
    print('Conclusion: T labels cannot establish camp completion or absence of bails/deaths when sampled.')
    return 0

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(pathlib.Path(sys.argv[1])))
