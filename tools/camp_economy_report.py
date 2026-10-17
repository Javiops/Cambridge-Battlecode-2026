#!/usr/bin/env python3
"""Compare full-engine V53 camp/economy statistics from paired A/B match files.

Usage (from your repository root):
  python3 path/to/camp_economy_report.py out/ab/diag_varg_trace_vs_exp_varg_camp_v53/official

The supplied root contains *_A/stats.json and *_B/stats.json. In *_A the
candidate is teamA; in *_B the candidate is teamB. Baseline is opposite.
No bot modifications, extra test runs, or per-turn stdout traces needed.

Caveats: match-level monster damage does NOT identify lethal damage source or
which particular camp failed. collectedGems is reported as the engine's own
statistic; we do not treat each increment as a proven completed capture.
"""
import collections
import json
import pathlib
import sys

METRICS = ('deaths', 'kills', 'monsterDamageDone', 'monsterDamageTaken',
           'collectedGems', 'submittedGems', 'earnedGold', 'spentGold')


def number(value):
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def normalize_team(value):
    if value in (0, '0', 'teamA', 'A'):
        return 0
    if value in (1, '1', 'teamB', 'B'):
        return 1
    return None


def read_match(path):
    data = json.loads(path.read_text(encoding='utf-8'))
    match = data.get('match', {})
    rounds = int(number(match.get('roundsCompleted', data.get('round', 0))))
    if rounds <= 0:
        raise ValueError('missing/invalid round count')
    teams = [collections.Counter(), collections.Counter()]
    champs = [[], []]
    winner = match.get('outcome', data.get('outcome', ''))
    for ch in data.get('champions', []):
        tm = normalize_team(ch.get('team'))
        if tm is None:
            continue
        m = ch.get('metrics', ch)
        if not isinstance(m, dict):
            continue
        values = {key: number(m.get(key)) for key in METRICS}
        for k, v in values.items():
            teams[tm][k] += v
        champs[tm].append((str(ch.get('name', ch.get('type', 'unknown'))), values))
    # Game-level submitted gem totals should be authoritative when given. It may
    # include gems submitted by entities without individually enumerated champs.
    for t in data.get('teams', []):
        tm = normalize_team(t.get('team'))
        if tm is not None and 'submittedGems' in t:
            teams[tm]['submittedGems'] = number(t['submittedGems'])
    return rounds, winner, teams, champs


def fmt(v, n=1):
    return f'{v:,.{n}f}'


def safe_div(a, b):
    return a / b if b else 0.0


def describe_side(title, sums, rounds, n_matches):
    print(f'{title}: {n_matches} matches, {rounds:,} total game rounds')
    print(f"  Deaths                     {fmt(sums['deaths'], 0):>10}  ({fmt(100 * safe_div(sums['deaths'], rounds))}/100 rounds)")
    print(f"  Kills                      {fmt(sums['kills'], 0):>10}  ({fmt(100 * safe_div(sums['kills'], rounds))}/100 rounds)")
    print(f"  Monster damage dealt       {fmt(sums['monsterDamageDone'], 0):>10}  ({fmt(100 * safe_div(sums['monsterDamageDone'], rounds))}/100 rounds)")
    print(f"  Monster damage taken       {fmt(sums['monsterDamageTaken'], 0):>10}  ({fmt(100 * safe_div(sums['monsterDamageTaken'], rounds))}/100 rounds)")
    print(f"  Gems collected (engine)    {fmt(sums['collectedGems'], 0):>10}  ({fmt(100 * safe_div(sums['collectedGems'], rounds))}/100 rounds)")
    print(f"  Gems submitted             {fmt(sums['submittedGems'], 0):>10}  ({fmt(100 * safe_div(sums['submittedGems'], rounds))}/100 rounds)")
    print(f"  Gold earned                {fmt(sums['earnedGold'], 0):>10}  ({fmt(100 * safe_div(sums['earnedGold'], rounds))}/100 rounds)")
    print(f"  Monster dmg taken / dealt: {fmt(safe_div(sums['monsterDamageTaken'], sums['monsterDamageDone']), 3)}")
    print(f"  Monster dmg dealt / collected gem: {fmt(safe_div(sums['monsterDamageDone'], sums['collectedGems']))}")
    print()


def main(root):
    files = sorted(root.glob('*_A/stats.json')) + sorted(root.glob('*_B/stats.json'))
    if not files:
        print('No stats.json under *_A and *_B folders. Re-run with --keep, if needed.', file=sys.stderr)
        return 2
    totals = {'candidate': collections.Counter(), 'baseline': collections.Counter()}
    per_champ = {'candidate': collections.defaultdict(collections.Counter),
                 'baseline': collections.defaultdict(collections.Counter)}
    champion_appearances = {'candidate': collections.Counter(), 'baseline': collections.Counter()}
    per_games = []
    team_rounds = 0
    n = 0
    failures = []
    map_pairs = collections.defaultdict(dict)
    for path in files:
        try:
            rounds, outcome, teams, champs = read_match(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            failures.append((path.parent.name, str(exc)))
            continue
        side = path.parent.name[-1]
        candidate_side = 0 if side == 'A' else 1
        opponent_side = 1 - candidate_side
        if not champs[candidate_side]:
            failures.append((path.parent.name, 'no candidate champion records'))
            continue
        n += 1
        team_rounds += rounds
        for label, tm in (('candidate', candidate_side), ('baseline', opponent_side)):
            totals[label].update(teams[tm])
            for champ, metrics in champs[tm]:
                # Canonical champion names may contain spaces; keep raw names.
                per_champ[label][champ].update(metrics)
                champion_appearances[label][champ] += 1
        name = path.parent.name
        mapname = name[:-2]
        candidate_won = normalize_team(outcome) == candidate_side
        baseline_won = normalize_team(outcome) == opponent_side
        map_pairs[mapname][side] = ('W' if candidate_won else 'L' if baseline_won else '?')
        c = teams[candidate_side]
        b = teams[opponent_side]
        row = {'map': name, 'rounds': rounds, 'c': c, 'b': b, 'result': map_pairs[mapname][side],
               'damage_per_gem': safe_div(c['monsterDamageDone'], c['collectedGems']),
               'monsters_and_deaths': c['monsterDamageTaken'] * c['deaths'],
               'collect_per_r': 100*safe_div(c['collectedGems'], rounds)}
        per_games.append(row)
    print(f'FULL ENGINE ECONOMY REPORT — {root}')
    print(f'Games with complete stats: {n} of {len(files)}')
    if failures:
        print('Unreadable/invalid:', '; '.join(f'{name} ({why})' for name,why in failures[:5]))
    print('Note: candidate plays teamA on *_A and teamB on *_B.')
    print('Both teams share the same match durations, so rates below are comparable.\n')
    for label in ('candidate', 'baseline'):
        describe_side(label.upper(), totals[label], team_rounds, n)
    print('DIFFERENCE, CANDIDATE MINUS BASELINE (per 100 match rounds)')
    for key in ('deaths', 'kills', 'monsterDamageDone', 'monsterDamageTaken',
                'collectedGems', 'submittedGems', 'earnedGold'):
        diff = 100 * safe_div(totals['candidate'][key] - totals['baseline'][key], team_rounds)
        print(f'  {key:23s} {diff:+.2f}')
    print()
    print('CANDIDATE CHAMPIONS, grouped by exact name (total stats; multiple matches)')
    print('  Name                       Games   Deaths  Monster dealt/taken   Collected  Submitted  Earned gold')
    for name, ct in sorted(per_champ['candidate'].items(), key=lambda p: -p[1]['monsterDamageTaken']):
        gm = champion_appearances['candidate'][name]
        print(f"  {name[:25]:25s} {gm:5.0f} {ct['deaths']:8.0f}   "
              f"{ct['monsterDamageDone']:7.0f}/{ct['monsterDamageTaken']:<7.0f} "
              f"{ct['collectedGems']:9.0f} {ct['submittedGems']:10.0f} {ct['earnedGold']:11.0f}")
    print()
    both = [(name, p) for name, p in map_pairs.items() if len(p) == 2 and set(p) <= {'W', 'L'}]
    print(f'Paired maps with win/loss results: {len(both)}')
    print(f"  Candidate won both: {sum(all(v == 'W' for v in p.values()) for _,p in both)}; "
          f"lost both: {sum(all(v == 'L' for v in p.values()) for _,p in both)}")
    print()
    print('GAME TRIAGE: candidate low collection relative to monster damage')
    print('  (These are prioritization clues, NOT proof a specific monster killed a champion.)')
    # Heuristic rank: high monster damage and deaths combined with relatively
    # little collection, using per-100-round rates to avoid only ranking long games.
    for r in per_games:
        c = r['c']
        r['triage_score'] = ((100 * safe_div(c['monsterDamageTaken'], r['rounds'])) / 100.0) * \
                            (1.0 + 2.0 * safe_div(c['deaths'], r['rounds'])) / \
                            (1.0 + (100 * safe_div(c['collectedGems'], r['rounds'])) / 50.0)
    for r in sorted(per_games, key=lambda x: x['triage_score'], reverse=True)[:10]:
        c, b = r['c'], r['b']
        print(f"  {r['map']:25s} {r['result']} r={r['rounds']:4d} "
              f"dead={c['deaths']:.0f}/{b['deaths']:.0f} "
              f"monster-taken={c['monsterDamageTaken']:.0f}/{b['monsterDamageTaken']:.0f} "
              f"collected={c['collectedGems']:.0f}/{b['collectedGems']:.0f} "
              f"submitted={c['submittedGems']:.0f}/{b['submittedGems']:.0f}")
    print('\nLIMITATIONS')
    print('  - No per-camp attempts/completions, frontliner positions or causes of death in match statistics.')
    print('  - Collected gems can differ from submitted due to banking, deaths, and other mechanics.')
    print('  - This report compares a logging-enabled candidate against its matched baseline.')
    print('    Logging may affect fuel or decisions, so these are diagnostics, not a performance A/B verdict.')
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(pathlib.Path(sys.argv[1])))
