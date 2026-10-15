#!/usr/bin/env python3
"""Reproduce source-pinned, paired study28 fix experiments in a repo clone.

Run ``cambc init --yes`` once in the clone before building. This tool never
fetches Git history, submits a bot, or changes tracked source files. Example:

  python tools/study28_fixes/bench.py --candidate fix-danger --features danger \
      --maps "maps/*.map26a" "maps_gen/*.map26a" "maps_dev200/*.map26a"

Use the same arguments with --prepare-only to inspect the generated sources.
For combinations, pass comma-separated features. Development p-values are
descriptive after selection; use a separately frozen, fresh map cohort for
confirmation. File-hash deduplication does not prove topological independence.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from datetime import datetime, timezone
import glob
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
import time
import zipfile

BASE_COMMIT = '43d003323cd16059cda6a54de14ed86e2da3b788'
BASE_PATH = 'bots/study28/src'
BASE_SHA256 = {
    'de_rules.h': '3e50429c96765f325ea3804c2bbb5c13ce26a4119fc7b8694f58def60531221b',
    'fight.h': 'af54a56889b086d06c867b1681cbcab6b2fa4b7de342000dcdf0861ac0d467bf',
    'main.cpp': 'b8b376a48cd6e7d0d01af3df7842945bca9fa2e8ae718dd11653f889394aa8e0',
    'opening_replace.h': 'ca6680bae82b74b89fd0bb65573904246df8761d8b22e3ce8cb6bd93207207e7',
    'params.h': 'c2d84cb2891f46d17442b6295e308b3199034555ed8edaf43803937a08ffa5d5',
    'utility.h': '5e48af1229195c4b356a617fd7323f49efe2af3a09728f6eda91ed4975c2b580',
}
FEATURES = {
    'channel': ('patch_combat.py', 'channel'),
    'dash': ('patch_combat.py', 'dash'),
    'danger': ('patch_economy.py', 'danger'),
    'capture_income': ('patch_economy.py', 'capture_income'),
    'capture_handoff': ('patch_economy.py', 'capture_handoff'),
    'ally_lock': ('patch_utility.py', 'ally_lock'),
    'spawn_path': ('patch_utility.py', 'spawn_path'),
    'channel_resume': ('patch_channel_resume.py', 'channel_resume'),
}
OUTPUT_ROOT = None


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return sha_bytes(Path(path).read_bytes())


def guard(path):
    path = Path(path)
    if OUTPUT_ROOT is not None:
        require(path.resolve().is_relative_to(OUTPUT_ROOT), 'Output child resolves outside the task directory: ' + str(path))
    return path


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    path = guard(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = guard(path.with_name(path.name + f'.{os.getpid()}.{threading.get_ident()}.tmp'))
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def now():
    return datetime.now(timezone.utc).isoformat()


def git(repo, *args):
    proc = subprocess.run(['git', '-C', str(repo), *args], capture_output=True)
    require(proc.returncode == 0, 'Git failed: ' + proc.stderr.decode('utf-8', errors='replace').strip())
    return proc.stdout


def find_repo(requested):
    choices = [Path(requested)] if requested else [Path.cwd(), Path(__file__).resolve().parent]
    for choice in choices:
        proc = subprocess.run(['git', '-C', str(choice), 'rev-parse', '--show-toplevel'], capture_output=True, text=True)
        if proc.returncode == 0:
            return Path(proc.stdout.strip()).resolve()
    raise RuntimeError('Run inside the Git clone, or pass --repo PATH. The pinned baseline commit must exist locally.')


def baseline(repo):
    resolved = git(repo, 'rev-parse', '--verify', BASE_COMMIT + '^{commit}').decode().strip()
    require(resolved == BASE_COMMIT, 'The pinned baseline commit is unavailable.')
    names = git(repo, 'ls-tree', '-r', '--name-only', f'{BASE_COMMIT}:{BASE_PATH}').decode().splitlines()
    require(set(names) == set(BASE_SHA256), 'The pinned baseline source file list differs from the reviewed source.')
    files = {name: git(repo, 'show', f'{BASE_COMMIT}:{BASE_PATH}/{name}') for name in names}
    for name, content in files.items():
        require(sha_bytes(content) == BASE_SHA256[name], 'Baseline SHA256 mismatch: ' + name)
    return files


def prepare(root, name, features, original):
    decoded = {name: content.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n') for name, content in original.items()}
    files = dict(decoded)
    module_pins = {}
    for feature in features:
        module_name, function_name = FEATURES[feature]
        module_path = Path(__file__).resolve().with_name(module_name)
        require(module_path.is_file(), 'Missing neighboring patch module: ' + str(module_path))
        module_pins[module_name] = sha(module_path)
        spec = importlib.util.spec_from_file_location('study28_' + module_path.stem, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        getattr(module, function_name)(files)
    require(set(files) == set(original), 'A patch unexpectedly added or removed a source file.')
    payload = {key: original[key] if value == decoded[key] else value.encode('utf-8') for key, value in files.items()}
    source_pins = {key: sha_bytes(value) for key, value in sorted(payload.items())}
    target = guard(root/'bots'/name/'src')
    if target.exists():
        observed = {p.name: sha(guard(p)) for p in target.iterdir() if p.is_file()}
        require(observed == source_pins and all(p.is_file() for p in target.iterdir()),
                'Existing candidate differs; use a new --candidate name: ' + str(target))
    else:
        target.mkdir(parents=True)
        for filename, content in payload.items():
            guard(target/filename).write_bytes(content)
    metadata = {'name': name, 'base_commit': BASE_COMMIT, 'base_path': BASE_PATH,
                'features': features, 'patch_modules_sha256': module_pins, 'source_sha256': source_pins}
    record = guard(root/'bots'/name/'source-manifest.json')
    if record.exists():
        require(read(record) == metadata, 'Candidate provenance differs; use a new candidate name.')
    else:
        write(record, metadata)
    return target.parent, metadata


def find_cli():
    value = os.environ.get('CAMBC_CLI') or shutil.which('cambc') or shutil.which('cambc.exe')
    require(value, 'cambc was not found. Set CAMBC_CLI to the executable path, or add cambc to PATH.')
    located = shutil.which(value) or value
    path = Path(located).expanduser().resolve()
    require(path.is_file(), 'CAMBC_CLI must name an executable file, not a shell command: ' + str(path))
    return path


@contextmanager
def exclusive(path, timeout=600):
    path = guard(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    while True:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            require(time.monotonic()-start < timeout,
                    'Timed out waiting for ' + str(path) + '. If a process crashed, remove this lock only after checking no run is active.')
            time.sleep(.2)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(json.dumps({'pid': os.getpid(), 'created_utc': now()}))
        yield
    finally:
        guard(path).unlink(missing_ok=True)


def permission_failure(text):
    lower = text.lower()
    return any(token in lower for token in ('access is denied', 'permission denied', 'permissiondenied', 'winerror 5'))


def command(args, repo, env, log_prefix, timeout, retries=3):
    """Retry only explicit Windows/OS access-denied failures, never game faults."""
    attempts = []
    for attempt in range(retries+1):
        try:
            proc = subprocess.run([str(a) for a in args], cwd=repo, env=env,
                                  capture_output=True, text=True, errors='replace', timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            write(log_prefix.with_suffix('.timeout.json'), {'command': list(map(str, args)), 'timeout_seconds': timeout})
            raise RuntimeError(f'Command timed out after {timeout}s: {args[1:]}') from exc
        text = proc.stdout + proc.stderr
        log = guard(log_prefix.with_name(log_prefix.name + f'.attempt-{attempt+1}.log'))
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(text, encoding='utf-8')
        attempts.append({'returncode': proc.returncode, 'log': str(log), 'access_denied_retry': proc.returncode != 0 and permission_failure(text)})
        if proc.returncode == 0:
            return attempts
        if attempt == retries or not permission_failure(text):
            raise RuntimeError('Command failed; see ' + str(log) + '\n' + text[-2500:])
        time.sleep(.25 * (attempt+1))
    raise AssertionError('Unreachable')


def collect_maps(repo, patterns):
    by_hash = {}
    for pattern in patterns:
        expanded = str(Path(pattern).expanduser())
        if not Path(expanded).is_absolute():
            expanded = str(repo/expanded)
        paths = sorted(Path(p).resolve() for p in glob.glob(expanded, recursive=True) if Path(p).is_file())
        require(paths, 'Map glob matched no files: ' + pattern)
        for path in paths:
            require(path.suffix == '.map26a', 'Expected a .map26a file: ' + str(path))
            digest = sha(path)
            if digest not in by_hash:
                by_hash[digest] = {'path': path, 'sha256': digest, 'aliases': []}
            if str(path) not in by_hash[digest]['aliases']:
                by_hash[digest]['aliases'].append(str(path))
    return list(by_hash.values())


def fault_count(value):
    if type(value) is int:
        require(value >= 0, 'Negative botFaults count')
        return value
    require(isinstance(value, list) and len(value) == 2 and all(type(n) is int and n >= 0 for n in value),
            'Unsupported botFaults schema: ' + repr(value))
    return sum(value)


def statistics_fields(data):
    require(data.get('outcome') in ('teamA', 'teamB', 'draw'), 'Invalid completed-game outcome')
    require(type(data.get('round')) is int and 1 <= data['round'] <= 2000, 'Invalid completed-game round')
    require(len(data.get('teams', [])) == 2, 'Expected exactly two teams')
    return {'outcome': data['outcome'], 'rounds': data['round'],
            'gems': [team['submittedGems'] for team in data['teams']],
            'faults': data.get('botFaults'), 'fault_count': fault_count(data.get('botFaults')),
            'engine_version': data.get('engineVersion'), 'statistics_schema': data.get('schemaVersion')}


def cached(root, key, identity):
    path = guard(root/'cache'/(key+'.json'))
    if not path.exists():
        return None
    row = read(path)
    require(row.get('schema_version') == 1 and row.get('key') == key and row.get('identity') == identity,
            'Cache identity mismatch: ' + str(path))
    stats = guard(root/'cache'/(key+'.statistics.json'))
    require(stats.is_file() and sha(stats) == row['statistics_sha256'], 'Cached statistics changed: ' + str(stats))
    fields = statistics_fields(read(stats))
    require(fields == {field: row[field] for field in fields},
            'Cached outcome disagrees with its statistics: ' + str(path))
    retained = row.get('retained_replay')
    if retained:
        replay = guard(root/retained)
        require(replay.is_file() and sha(replay) == row['replay_sha256'], 'Retained replay changed: ' + str(replay))
    return row


def sign_p(wins, losses):
    n = wins + losses
    return min(1.0, 2 * sum(math.comb(n, k) for k in range(min(wins, losses)+1)) / 2**n) if n else 1.0


def main():
    global OUTPUT_ROOT
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--repo', help='Git clone root (default: discover from cwd/script)')
    parser.add_argument('--candidate', default='candidate', help='New immutable output bot name; default: candidate')
    parser.add_argument('--features', required=True, help='Comma-separated: '+', '.join(FEATURES)+'; empty string creates a control')
    parser.add_argument('--maps', nargs='+', action='append', metavar='GLOB', help='One or more quoted .map26a globs; repeatable')
    parser.add_argument('--jobs', type=int, default=1, help='Parallel matches; default1 avoids Windows metadata races')
    parser.add_argument('--prepare-only', action='store_true', help='Create and verify source copies without CLI/build/games')
    parser.add_argument('--timeout', type=int, default=240, help='Per CLI command timeout in seconds; default240')
    args = parser.parse_args()
    require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', args.candidate) is not None, 'Invalid candidate name')
    require(args.candidate != 'original', 'The name original is reserved for the pinned baseline')
    require(1 <= args.jobs <= 32 and args.timeout > 0, 'Require jobs1..32 and a positive timeout')
    features = [f.strip() for f in args.features.split(',') if f.strip()]
    require(len(features) == len(set(features)) and all(f in FEATURES for f in features), 'Unknown or duplicate feature')
    require(not {'channel', 'channel_resume'}.issubset(features), 'channel and channel_resume are mutually exclusive alternatives')
    repo = find_repo(args.repo)
    root = (repo/'out/study28-fixes').resolve()
    require(root.is_relative_to(repo), 'Output directory resolves outside the repo')
    OUTPUT_ROOT = root
    original = baseline(repo)
    with exclusive(root/'locks/prepare.lock'):
        baseline_bot, baseline_meta = prepare(root, 'original', [], original)
        candidate_bot, candidate_meta = prepare(root, args.candidate, features, original)
    print('Prepared:', candidate_bot/'src', flush=True)
    if args.prepare_only:
        print('Source-only preparation complete; no CLI, build or game was started.')
        return 0
    require((repo/'cambc.toml').is_file() and (repo/'sdk/cpp/cambc.h').is_file(),
            'Initialize this clone first with cambc init --yes; the SDK/project files are missing.')
    cli = find_cli()
    wasmtime_cache = guard(root/'wasmtime-cache')
    wasmtime_cache.mkdir(parents=True, exist_ok=True)
    for child in wasmtime_cache.rglob('*'):
        guard(child)
    env = {**os.environ, 'CAMBC_NO_UPDATE_CHECK': '1', 'CAMBC_WASMTIME_CACHE': str(wasmtime_cache)}
    version = subprocess.run([str(cli), '--version'], cwd=repo, env=env, capture_output=True, text=True, check=True).stdout.strip()
    require(version, 'CLI returned an empty version')
    cli_identity = {'version': version, 'executable_sha256': sha(cli)}
    config_sha = sha(repo/'cambc.toml')
    patterns = [p for group in args.maps for p in group] if args.maps else ['maps/*.map26a', 'maps_gen/*.map26a', 'maps_dev200/*.map26a']
    maps = collect_maps(repo, patterns)
    with exclusive(root/'locks/build.lock'):
        builds = {}
        for bot in (baseline_bot, candidate_bot):
            # Do not let an existing child junction redirect CLI build writes.
            guard(bot/'.cambc/build/bot-injected.wasm')
            for child in bot.rglob('*'):
                guard(child)
            builds[bot.name] = command([cli, 'build', str(bot)], repo, env, root/'logs'/('build-'+bot.name), args.timeout)
    wasm = {bot.name: sha(bot/'.cambc/build/bot-injected.wasm') for bot in (baseline_bot, candidate_bot)}
    for bot, meta in ((baseline_bot, baseline_meta), (candidate_bot, candidate_meta)):
        require({p.name: sha(p) for p in (bot/'src').iterdir() if p.is_file()} == meta['source_sha256'], 'Source changed during build')
    physical, slots = {}, []
    for m in maps:
        for side in (0, 1):
            a, b = (candidate_bot, baseline_bot) if side == 0 else (baseline_bot, candidate_bot)
            identity = {'wasm_a_sha256': wasm[a.name], 'wasm_b_sha256': wasm[b.name], 'map_sha256': m['sha256'],
                        'cli': cli_identity, 'project_config_sha256': config_sha, 'settings': 'default-fuel/full-game/cpp'}
            key = sha_bytes(json.dumps(identity, sort_keys=True, separators=(',', ':')).encode())
            physical.setdefault(key, {'key': key, 'identity': identity, 'map': m['path'], 'bot_a': a, 'bot_b': b, 'retain': len(slots)<2})
            slots.append({'map_sha256': m['sha256'], 'map_path': str(m['path']), 'candidate_side': side, 'key': key})
    plan = {'created_utc': now(), 'base_commit': BASE_COMMIT, 'candidate': candidate_meta, 'original': baseline_meta,
            'cli': cli_identity, 'project_config_sha256': config_sha,
            'sdk_header_sha256': sha(repo/'sdk/cpp/cambc.h'), 'wasm_sha256': wasm,
            'maps': [{'path': str(m['path']), 'sha256': m['sha256'], 'aliases': m['aliases']} for m in maps],
            'semantic_map_side_slots': len(slots), 'unique_deterministic_games': len(physical), 'jobs': args.jobs,
            'unit': 'Unique map file with two candidate/original side assignments; both-won versus both-lost sign test.',
            'independence_limit': 'Exact file/input reuse is deduplicated. Correlated or cosmetic-only map variants need an additional geometry audit.',
            'build_attempts': builds, 'slots': slots}
    run_id = now().replace(':', '').replace('+', '_') + '-' + args.candidate
    run_dir = root/'runs'/run_id
    write(run_dir/'plan.json', plan)

    def execute(job):
        key, identity = job['key'], job['identity']
        def unchanged_inputs():
            require(sha(job['map']) == identity['map_sha256'], 'Map changed after planning: ' + str(job['map']))
            require(sha(repo/'cambc.toml') == config_sha, 'Project config changed after planning')
            for team in ('a', 'b'):
                bot = job['bot_'+team]
                require(sha(guard(bot/'.cambc/build/bot-injected.wasm')) == identity['wasm_'+team+'_sha256'],
                        'Compiled bot changed after planning: ' + str(bot))
        with exclusive(root/'locks'/(key+'.lock'), timeout=args.timeout*5+60):
            unchanged_inputs()
            row = cached(root, key, identity)
            if row is not None:
                return row, False
            out = guard(root/'games'/key)
            out.mkdir(parents=True, exist_ok=True)
            require(out.resolve().is_relative_to(root/'games'), 'Unsafe result directory')
            stats = guard(out/'statistics.json')
            attempts = command([cli, 'run', job['bot_a'], job['bot_b'], '--map', job['map'], '-o', out, '--statistics', stats],
                               repo, env, root/'logs'/('game-'+key), args.timeout)
            unchanged_inputs()
            require(stats.is_file(), 'CLI did not write completed-game statistics: ' + str(out))
            fields = statistics_fields(read(stats))
            replays = list(out.glob('*.repl26a'))
            require(len(replays) == 1, 'Expected one replay bundle: ' + str(out))
            replay = guard(replays[0])
            stdout = {}
            with zipfile.ZipFile(replay) as archive:
                require(archive.testzip() is None, 'Replay ZIP CRC failure')
                for team in ('a', 'b'):
                    text = archive.read('team-'+team+'.stdout').decode('utf-8', errors='replace').replace('\0', '')
                    initializations = dict(Counter(re.findall(r'\[init\] (\S+)', text)))
                    stdout[team] = {'sha256': sha_bytes(text.encode()), 'initializations': initializations,
                                    'reinitializations_observed': sum(max(0, n-1) for n in initializations.values()),
                                    'logged_error_messages': dict(Counter(re.findall(r'\[err #\d+\] ([^\r\n]+)', text))),
                                    'low_fuel_status_samples': len(re.findall('mode=low-fuel', text))}
            row = {'schema_version': 1, 'key': key, 'identity': identity, 'created_utc': now(), **fields,
                   'statistics_sha256': sha(stats), 'replay_sha256': sha(replay), 'stdout': stdout,
                   'execution_attempts': attempts}
            reinit = sum(team['reinitializations_observed'] for team in stdout.values())
            if job['retain'] or fields['fault_count'] or reinit:
                retained = guard(root/'retained-replays'/(key+'.repl26a'))
                retained.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(replay, retained)
                row['retained_replay'] = str(retained.relative_to(root))
            guard(root/'cache').mkdir(exist_ok=True)
            shutil.copyfile(stats, guard(root/'cache'/(key+'.statistics.json')))
            write(root/'cache'/(key+'.json'), row)
            # Delete only these known temporary files under the verified task root.
            guard(replay).unlink()
            guard(stats).unlink()
            try:
                out.rmdir()
            except OSError:
                pass
            return row, True

    results, new_keys = {}, set()
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(execute, job): key for key, job in physical.items()}
        for future in as_completed(futures):
            key = futures[future]
            row, fresh = future.result()
            results[key] = row
            if fresh:
                new_keys.add(key)
            if len(results) % 20 == 0 or len(results) == len(physical):
                print(f'{len(results)}/{len(physical)} unique games resolved ({len(new_keys)} newly executed)', flush=True)
    per_map, outcomes = {}, Counter()
    for slot in slots:
        row = results[slot['key']]
        side = slot['candidate_side']
        winner = {'teamA': 0, 'teamB': 1, 'draw': -1}[row['outcome']]
        outcome = 'D' if winner < 0 else 'W' if winner == side else 'L'
        pair = per_map.setdefault(slot['map_sha256'], {})
        require(side not in pair, 'Duplicate map/side slot')
        pair[side] = outcome
        outcomes[outcome] += 1
    require(len(results) == len(physical) and len(per_map) == len(maps) and all(set(pair) == {0, 1} for pair in per_map.values()),
            'Incomplete paired map coverage')
    require(sha(cli) == cli_identity['executable_sha256'], 'CLI executable changed during the run')
    require(sha(repo/'cambc.toml') == config_sha, 'Project config changed during the run')
    for m in maps:
        require(sha(m['path']) == m['sha256'], 'Map changed during the run: ' + str(m['path']))
    for bot, meta in ((baseline_bot, baseline_meta), (candidate_bot, candidate_meta)):
        require({p.name: sha(guard(p)) for p in (bot/'src').iterdir() if p.is_file()} == meta['source_sha256'],
                'Candidate source changed during the run: ' + str(bot))
    both_won = sum(pair[0] == pair[1] == 'W' for pair in per_map.values())
    both_lost = sum(pair[0] == pair[1] == 'L' for pair in per_map.values())
    fault_games = sum(row['fault_count'] > 0 for row in results.values())
    reinit_games = sum(any(team['reinitializations_observed'] for team in row['stdout'].values()) for row in results.values())
    summary = {'candidate': args.candidate, 'features': features, 'unique_maps': len(maps),
               'paired_map_side_slots': len(slots), 'unique_deterministic_games': len(physical),
               'newly_executed_unique_games': len(new_keys), 'cache_hits': len(physical)-len(new_keys),
               'side_wins': outcomes['W'], 'side_losses': outcomes['L'], 'side_draws': outcomes['D'],
               'both_won': both_won, 'both_lost': both_lost, 'split_or_draw': len(maps)-both_won-both_lost,
               'paired_sign_p_two_sided': sign_p(both_won, both_lost),
               'fault_games': fault_games, 'reinitialization_games': reinit_games,
               'clean_completed_evidence': fault_games == 0 and reinit_games == 0,
               'quality_gate_definition': 'Reported botFaults=0 and no observed repeated [init]; not a full roster, native-fuel, or SDK-error audit.',
               'completed_utc': now(), 'plan_sha256': sha(run_dir/'plan.json')}
    write(run_dir/'results.json', {'summary': summary, 'per_map': per_map, 'games': list(results.values()), 'slots': slots})
    print(json.dumps(summary, indent=2))
    print('Evidence:', run_dir/'results.json')
    print('Logged errors and periodic low-fuel samples are not total SDK-exception or FuelExhausted counts.')
    print('A development/selected result alone does not establish general superiority; confirm on a fresh frozen cohort.')
    return 0 if summary['clean_completed_evidence'] else 2


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError, OSError, ValueError) as exc:
        print('ERROR:', exc, file=sys.stderr)
        raise SystemExit(1)
