#!/usr/bin/env python3
r"""Deterministic final-stat parity test: original v53 vs v53 refactor step 2.

NO REPLAY OUTPUT is requested. Run from a CAMBC workspace with maps/ and bots/:
    py "$env:USERPROFILE\Downloads\v53_parity_runner_step2_no_replays.py" --sets official --limit 2
    py "$env:USERPROFILE\Downloads\v53_parity_runner_step2_no_replays.py" --sets official,hold

Uses ~/Downloads/mybot_v53.zip and ~/Downloads/battlecode_v53_refactor_step2.zip by default.
Three matches per map: OO, RO, OR. All stats must match exactly.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

SETS = {
    'official': 'maps/*.map26a',
    'gen': 'maps_gen/*.map26a',
    'hold': 'maps_hold60/*.map26a',
    'dev': 'maps_dev200/*.map26a',
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_src_zip(path: Path) -> dict[str, bytes]:
    result = {}
    with zipfile.ZipFile(path) as z:
        for item in z.infolist():
            name = item.filename.replace('\\', '/')
            if item.is_dir() or not name.startswith('src/'):
                continue
            rel = name[4:]
            if not rel or Path(rel).is_absolute() or '..' in Path(rel).parts:
                raise ValueError(f'Unsafe archive entry: {name}')
            result[rel] = z.read(item)
    if 'main.cpp' not in result:
        raise ValueError(f'Missing src/main.cpp in {path}')
    return result


def verify_source(original: dict[str, bytes], new: dict[str, bytes], zip_path: Path):
    """Reconstruct v53, including nested sections, without running game engine."""
    with zipfile.ZipFile(zip_path) as z:
        manifest = json.loads(z.read('tests/refactor_manifest.json'))
        main = z.read('src/main.cpp')
        loop_marker = b'#include "run_loop.inc"\n'
        loop = z.read('src/run_loop.inc')
        if main.count(loop_marker) != 1 or not loop.endswith(b'\n\n'):
            raise ValueError('Unexpected run-loop layout')
        main = main.replace(loop_marker, loop[:-1], 1)
        policy_marker = (b'#include "turn_helpers.inc"\n'
                         b'#include "turn_policy.inc"\n'
                         b'#include "turn_labels.inc"\n')
        if main.count(policy_marker) != 1:
            raise ValueError('Unexpected policy include layout')
        main = main.replace(policy_marker, b'#include "turn_policy.inc"\n', 1)
        main = main.replace(
            b'// Policy implementation sections are included in their original declaration order.\n'
            b'// See ARCHITECTURE.md. Do not reorder: these are not independent translation units.\n', b'', 1)
        for part in manifest['fragments']:
            name = part['file']
            marker = f'#include "{name}"\n'.encode()
            if main.count(marker) != 1:
                raise ValueError(f'Missing or repeated {name} placeholder')
            if name == 'turn_policy.inc':
                block = b''.join(z.read('src/' + f) for f in
                                 ('turn_helpers.inc', 'turn_policy.inc', 'turn_labels.inc'))
            else:
                block = z.read('src/' + name)
            main = main.replace(marker, block, 1)
        if main != original['main.cpp'] or digest(main) != manifest['original_main_sha256']:
            raise ValueError('Refactor does not reconstruct original v53 main.cpp byte-for-byte')
        for name, checksum in manifest['unchanged_headers_sha256'].items():
            short = name.removeprefix('src/')
            if short not in original or digest(original[short]) != checksum or new.get(short) != original[short]:
                raise ValueError(f'Original dependency was changed: {name}')
    print('PASS: reconstructed original v53 source and all legacy headers match exactly')


def prepare_bot(zip_path: Path, destination: Path, members: dict[str, bytes]):
    checksum = digest(b''.join(name.encode()+b'\0'+digest(data).encode()
                               for name, data in sorted(members.items())))
    marker = destination / '.parity_step2_hash'
    if destination.exists():
        if not marker.is_file() or marker.read_text().strip() != checksum:
            raise ValueError(f'{destination} already exists with other contents. Move it first.')
        for name, data in members.items():
            if (destination / 'src' / name).read_bytes() != data:
                raise ValueError(f'Modified parity folder: {destination / "src" / name}')
        return
    (destination / 'src').mkdir(parents=True)
    for name, data in members.items():
        p = destination / 'src' / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    marker.write_text(checksum + '\n')
    print(f'Extracted {zip_path.name} -> {destination}')


def command(args: list[str], env: dict[str, str]):
    r = subprocess.run(args, capture_output=True, text=True, errors='replace', env=env)
    return r


def compile_bot(cli: str, bot: Path, env: dict[str, str]) -> str:
    result = command([cli, 'build', str(bot)], env)
    if result.returncode:
        raise RuntimeError(f'Build failed: {bot}\n{result.stdout[-4000:]}\n{result.stderr[-4000:]}')
    wasm = bot / '.cambc/build/bot-injected.wasm'
    if not wasm.is_file():
        raise RuntimeError(f'Build did not create {wasm}')
    return digest(wasm.read_bytes())


def normalize_number(value):
    if isinstance(value, str):
        try:
            return float(value) if any(c in value for c in '.eE') else int(value)
        except ValueError:
            pass
    return value


def canonical_stats(d: dict) -> dict:
    if 'match' in d:
        teams = sorted(d['teams'], key=lambda t: t['team'])
        faults = d.get('diagnostics', {}).get('botFaults', {})
        champions = [{'team': c.get('team'), 'name': c.get('name'),
                      'metrics': {k: normalize_number(v) for k, v in c.get('metrics', {}).items()}}
                     for c in d.get('champions', [])]
        return {'outcome': d['match'].get('outcome'),
                'round': normalize_number(d['match']['roundsCompleted']),
                'gems': [normalize_number(t['submittedGems']) for t in teams],
                'faults': [normalize_number(faults.get('teamA', 0)), normalize_number(faults.get('teamB', 0))],
                'champions': champions}
    return {'outcome': d.get('outcome'), 'round': normalize_number(d.get('round')),
            'gems': [normalize_number(t['submittedGems']) for t in d.get('teams', [])],
            'faults': [normalize_number(f) for f in d.get('botFaults', [0, 0])],
            'champions': d.get('champions', [])}


def play(cli: str, env: dict[str, str], out: Path, key: str, mapfile: Path,
         team_a: Path, team_b: Path, flags: list[str]):
    directory = out / 'matches' / key
    directory.mkdir(parents=True, exist_ok=True)
    stats_file = directory / 'stats.json'
    stats_file.unlink(missing_ok=True)
    # CRITICAL: no -o option, since that requests replay generation.
    args = [cli, 'run', str(team_a), str(team_b), '--map', str(mapfile),
            '--statistics', str(stats_file), *flags]
    result = command(args, env)
    if result.returncode or not stats_file.is_file():
        return {'error': f'{key}: game returned {result.returncode}. '
                         f'stats exists={stats_file.exists()}\n'
                         f'{result.stdout[-800:]}\n{result.stderr[-1500:]}'}
    try:
        return {'stats': canonical_stats(json.loads(stats_file.read_text('utf-8')))}
    except (ValueError, KeyError, TypeError) as e:
        return {'error': f'{key}: malformed stats: {e}'}


def main():
    home = Path.home() / 'Downloads'
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--original-zip', type=Path, default=home / 'mybot_v53.zip')
    ap.add_argument('--refactored-zip', type=Path, default=home / 'battlecode_v53_refactor_step2.zip')
    ap.add_argument('--sets', default='official')
    ap.add_argument('--limit', type=int, default=0, help='max maps per set (0 = all)')
    ap.add_argument('--jobs', type=int, default=2)
    ap.add_argument('--cli', default=os.environ.get('CAMBC_CLI', 'cambc'))
    ap.add_argument('--out', type=Path, default=Path('out/parity_v53_step2'))
    a = ap.parse_args()
    if a.limit < 0 or a.jobs < 1:
        ap.error('--limit must be >= 0 and --jobs >= 1')
    if not Path('maps').is_dir():
        ap.error('Run from a CAMBC workspace with maps/ and bots/')
    if not a.original_zip.is_file() or not a.refactored_zip.is_file():
        ap.error('ZIP files missing from Downloads; use --original-zip and --refactored-zip')
    try:
        original = read_src_zip(a.original_zip)
        modified = read_src_zip(a.refactored_zip)
        verify_source(original, modified, a.refactored_zip)
        obot = Path('bots/_parity_v53_original_step2')
        rbot = Path('bots/_parity_v53_refactored_step2')
        prepare_bot(a.original_zip, obot, original)
        prepare_bot(a.refactored_zip, rbot, modified)
        env = {**os.environ, 'CAMBC_NO_UPDATE_CHECK': '1'}
        env.setdefault('CAMBC_WASMTIME_CACHE', str(Path('out/wasmtime-cache').resolve()))
        ahash = compile_bot(a.cli, obot, env)
        bhash = compile_bot(a.cli, rbot, env)
        print('Original WASM SHA-256:', ahash)
        print('Refactor WASM SHA-256:', bhash)
        if ahash == bhash:
            print('PASS: compiled WASM hashes identical')
        else:
            print('WASM hashes differ; testing final-stat game parity (may reflect debug metadata).')
        help_run = command([a.cli, 'run', '--help'], env)
        flags = ['--json'] if '--json' in help_run.stdout else []
        maps = []
        for label in a.sets.split(','):
            label = label.strip()
            found = sorted(Path('.').glob(SETS.get(label, label)))
            if not found:
                raise RuntimeError(f'No maps in set {label!r}')
            maps.extend((label, p) for p in (found[:a.limit] if a.limit else found))
        print(f'Running {len(maps)} map(s) x 3 matches. No replays requested.')
        a.out.mkdir(parents=True, exist_ok=True)
        schedule = {}
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
            for label, path in maps:
                prefix = f'{label}_{path.stem}_{digest(path.read_bytes())[:8]}'
                for key, left, right in [('OO', obot, obot), ('RO', rbot, obot), ('OR', obot, rbot)]:
                    future = pool.submit(play, a.cli, env, a.out, prefix+'_'+key, path, left, right, flags)
                    schedule[future] = (prefix, key)
            for future in concurrent.futures.as_completed(schedule):
                results[schedule[future]] = future.result()
        report = {'source_identical': True, 'wasm_identical': ahash == bhash,
                  'original_wasm': ahash, 'refactored_wasm': bhash, 'replays_requested': False,
                  'maps': [], 'mismatches': 0, 'run_errors': 0}
        for label, path in maps:
            prefix = f'{label}_{path.stem}_{digest(path.read_bytes())[:8]}'
            base = results[(prefix,'OO')]
            entry = {'set': label, 'map': str(path), 'comparisons': {}}
            for key in ('RO','OR'):
                alt = results[(prefix, key)]
                same = 'stats' in base and 'stats' in alt and base['stats'] == alt['stats']
                info = {'match': same}
                if not same:
                    if 'error' in base or 'error' in alt:
                        report['run_errors'] += 1
                    else:
                        report['mismatches'] += 1
                    info['original'] = base
                    info['candidate'] = alt
                entry['comparisons'][key] = info
            report['maps'].append(entry)
            print(('PASS' if all(x['match'] for x in entry['comparisons'].values()) else 'DIFFER'),
                  label, path.name, 'A=',entry['comparisons']['RO']['match'],
                  'B=',entry['comparisons']['OR']['match'])
        target = a.out / 'report.json'
        target.write_text(json.dumps(report, indent=2, ensure_ascii=False), 'utf-8')
        if report['mismatches'] or report['run_errors']:
            print(f'FAILED: mismatches={report["mismatches"]} errors={report["run_errors"]}. {target}')
            return 1
        print(f'PASS: all {len(maps)*2} mirrored replacement comparisons matched. {target}')
        print('Note: matching final statistics is not turn-by-turn action equivalence.')
        return 0
    except (RuntimeError, ValueError, OSError, KeyError, zipfile.BadZipFile) as e:
        print('ERROR:',e,file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
