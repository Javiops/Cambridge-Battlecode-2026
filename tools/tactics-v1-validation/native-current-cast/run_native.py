"""Actual current-cast full-clear admission and paid common-consumer regression.

Both modes use a lawful movement/damage prelude and seed one finite Observe
intent. Caller mode exercises the production early probe, farming, receipt and
gateway. Full-main mode then executes exact Bot::turn, including its ordering.
Neither mode is an autonomous-startup or strength experiment.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import zipfile

SDK_SHA = '76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4'
ENGINE_BUILD = '02c4624c8c9b8bcaf9d906f407c0b1d932d5b5bce6e8ea7e222e08065dd9cede'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('cli', 'project', 'source', 'output', 'map'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--control', action='store_true', help='Expect the old farming admission to decline; use frozen25r1 source.')
    parser.add_argument('--mode', choices=('caller', 'full-main'), default='caller')
    parser.add_argument('--existing', action='store_true', help='Reparse an existing uniquely named output without rerunning a game.')
    args = parser.parse_args()
    if args.control and args.mode == 'full-main':
        raise ValueError('The old-admission negative is a caller-mode control')
    cli, project, source, output, mapfile = (getattr(args, name).resolve() for name in ('cli', 'project', 'source', 'output', 'map'))
    here = Path(__file__).resolve().parent
    bot, game = output / 'bot', output / 'game'
    if sha(project / 'sdk/cpp/cambc.h') != SDK_SHA:
        raise ValueError('Expected reviewed official SDK2.2.2')
    source_hashes = {h.name: sha(h) for h in source.glob('*.h')}
    if not args.existing:
        (bot / 'src').mkdir(parents=True, exist_ok=False)
        for header in source.glob('*.h'):
            shutil.copy2(header, bot / 'src' / header.name)
        prefix = '' if args.control else '#define EXPECT_ADMITTED\n'
        fixture = here / ('full-main.cpp' if args.mode == 'full-main' else 'fixture.cpp')
        (bot / 'src/main.cpp').write_text(prefix + fixture.read_text(encoding='utf8'), encoding='utf8')
        if args.mode == 'full-main':
            shutil.copy2(source / 'main.cpp', bot / 'src/production-main.h')
        shutil.copy2(mapfile, output / 'fixture.map26a')

    def invoke(command, label):
        result = subprocess.run(list(map(str, command)), cwd=project,
                                env={**os.environ, 'CAMBC_NO_UPDATE_CHECK': '1'},
                                capture_output=True, text=True, errors='replace', timeout=600)
        (output / (label + '.log')).write_text(result.stdout + result.stderr, encoding='utf8')
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)

    stats = game / 'statistics.json'
    if not args.existing:
        invoke([cli, 'build', bot], 'normal-build')
        invoke([cli, 'build', bot, '--release'], 'release-build')
        game.mkdir()
        invoke([cli, 'run', bot, bot, '--map', mapfile, '--release', '--json', '-o', game, '--statistics', stats], 'run')
    data = json.loads(stats.read_text())
    replay, = game.glob('*.repl26a')
    with zipfile.ZipFile(replay) as zipped:
        text = '\n'.join(zipped.read('team-' + side + '.stdout').decode(errors='replace').replace('\0', '') for side in ('a', 'b'))
    (output / 'stdout.txt').write_text(text, encoding='utf8')
    markers = [line for line in text.splitlines() if line.startswith('ADMISSION26_')]
    failures = []
    expected = 'ADMISSION26_CONTROL_PASS' if args.control else 'ADMISSION26_PASS'
    if text.count(expected) != 1:
        failures.append('missing-exact-native-result')
    if re.search(r'ADMISSION26_(FAIL|EXCEPTION)|TACTICS_ERROR', text):
        failures.append('native-error-marker')
    fuel = sum(len(event['entries']) for event in data['events'] if event['kind'] == 'fuelExhausted')
    if fuel or any(data['diagnostics']['botFaults'].values()):
        failures.append('native-fault-or-fuel')
    if data['match']['engineVersion'] != '0.0.2' or data['match']['engineBuildHash'] != ENGINE_BUILD:
        failures.append('native-engine-mismatch')
    tested_hashes = {h.name: sha(h) for h in (bot / 'src').glob('*.h') if h.name != 'production-main.h'}
    if tested_hashes != source_hashes:
        failures.append('production-header-affinity')
    if args.mode == 'full-main' and sha(bot / 'src/production-main.h') != sha(source / 'main.cpp'):
        failures.append('production-main-affinity')
    report = {
        'passed': not failures, 'control': args.control, 'mode': args.mode, 'failures': failures,
        'scope': __doc__, 'markers': markers, 'fuel': fuel, 'faults': data['diagnostics']['botFaults'],
        'source_sha256': tested_hashes, 'production_main_sha256': sha(source / 'main.cpp'),
        'production_main_executed': args.mode == 'full-main', 'fixture_sha256': sha(bot / 'src/main.cpp'),
        'module_sha256': sha(bot / '.cambc/build-release/bot-injected.wasm'),
        'sdk_sha256': sha(project / 'sdk/cpp/cambc.h'), 'map_sha256': sha(mapfile),
        'statistics_sha256': sha(stats), 'replay_sha256': sha(replay),
        'engine': data['match'],
    }
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    print(json.dumps({key: report[key] for key in ('passed', 'control', 'markers', 'fuel', 'faults', 'failures')}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
