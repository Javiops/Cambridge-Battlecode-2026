"""Reproduce all 13 economy source packages from the exact cleaned PR11 baseline.

Python 3.10+ standard library only. Put this script beside baseline-manifest.json,
selection-plan.json, patch_banking.py, patch_camps.py and patch_recall.py. Run:

  python rebuild_candidates.py --baseline PATH_TO_SIX_SOURCE_FILES --out NEW_DIR

The output parent must already exist; NEW_DIR must not exist. This creates source
and provenance manifests only: no compiler, game engine, network or submission.
Rejected research variants are reproduced for review, not endorsed as stronger.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from types import ModuleType

sys.dont_write_bytecode = True
ROOT = Path(__file__).absolute().parent
BASELINE = {
    'de_rules.h': '3e50429c96765f325ea3804c2bbb5c13ce26a4119fc7b8694f58def60531221b',
    'fight.h': '5fb073f23ce41a5f6d07fba3aa55a016582a46ac54c4f8316ee6c96ebe92a7bb',
    'main.cpp': '8ef9c27093272f5c14dbda5d16e7b91852edc63523ea86ac3d50d322514e71f7',
    'opening_replace.h': 'ca6680bae82b74b89fd0bb65573904246df8761d8b22e3ce8cb6bd93207207e7',
    'params.h': 'd99ef2cecff65f7851efb491bb4691d40ddeaaa6a96499e13eddec814fdc1372',
    'utility.h': '5e48af1229195c4b356a617fd7323f49efe2af3a09728f6eda91ed4975c2b580',
}
MODULES = {
    'patch_banking.py': 'a0409c3c9cbbdbd1012609b9b9d79fa61bae3c88be5dccfd655b47f053ae50ce',
    'patch_camps.py': '3413527246b445124d031aa3920bd509aa1091a24f710a3a39686a8b4c835fea',
    'patch_recall.py': '42d5dde8ee6f2a910f5016c018829a0e79f8d1eb18ae3adc4e55e3b9bb047325',
}
PLAN_SHA256 = '8d547b48dca5d482beea10e1358c6b19d6b72f76c161cfb8ae79e5faceb1f130'
BASE_WASM_SHA256 = 'a0077d5324047a799b7947b2b54634e46451cc64eabec1df06bf549c69632e43'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def ordinary(path):
    """Reject POSIX links and Windows junction/reparse redirects at every ancestor."""
    path = Path(os.path.abspath(os.fspath(path)))
    for node in (path, *path.parents):
        try:
            observed = node.lstat()
        except FileNotFoundError:
            continue
        require(not stat.S_ISLNK(observed.st_mode) and
                not (getattr(observed, 'st_file_attributes', 0) & 0x400),
                'Refusing symlink/junction/reparse path: ' + str(node))
    require(path.resolve() == path, 'Path resolves through a redirect: ' + str(path))
    return path


def safe_name(name):
    require(isinstance(name, str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}', name),
            'Unsafe package/feature name: ' + repr(name))
    require(name.upper() not in {'CON', 'PRN', 'AUX', 'NUL',
            *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))},
            'Reserved filesystem name: ' + name)


def pinned_support():
    paths = {name: ordinary(ROOT / name) for name in
             ('baseline-manifest.json', 'selection-plan.json', *MODULES)}
    raw = {name: path.read_bytes() for name, path in paths.items()}
    require(digest(raw['selection-plan.json']) == PLAN_SHA256,
            'selection-plan.json differs from the pre-outcome plan')
    for name, pin in MODULES.items():
        require(digest(raw[name]) == pin, 'Patch module pin mismatch: ' + name)
    baseline = json.loads(raw['baseline-manifest.json'])
    require(baseline['source_sha256'] == BASELINE, 'Baseline manifest differs from exact cleaned PR11 sources')
    require(baseline['expected_injected_wasm_sha256'] == BASE_WASM_SHA256,
            'Baseline manifest expected WASM differs')
    plan = json.loads(raw['selection-plan.json'])
    require(isinstance(plan['packages'], dict) and len(plan['packages']) == 13,
            'Expected exactly thirteen planned packages')
    modules = []
    known = {}
    for name in MODULES:
        module = ModuleType('_economy_rebuild_' + Path(name).stem)
        module.__file__ = str(paths[name])
        exec(compile(raw[name], str(paths[name]), 'exec'), module.__dict__)
        registry = module.FEATURES
        require(isinstance(registry, (dict, tuple, list)) and callable(module.apply_many),
                'Unsupported patch module interface: ' + name)
        for feature in registry:
            safe_name(feature)
            require(feature not in known, 'Ambiguous patch feature: ' + feature)
            known[feature] = name
        modules.append((name, module))
    for name, features in plan['packages'].items():
        safe_name(name)
        require(isinstance(features, list) and features and
                all(isinstance(f, str) for f in features), 'Invalid package features: ' + name)
        require(len(features) == len(set(features)) and set(features) <= set(known),
                'Unknown/duplicate features for ' + name)
    return raw, plan, modules, known


def rebuild(baseline_path, output_path):
    source = ordinary(baseline_path)
    out = ordinary(output_path)
    require(source.is_dir(), '--baseline must be the directory containing six source files')
    require(out.parent.is_dir(), 'Output parent must already exist')
    require(not out.exists(), 'Refusing existing output directory: ' + str(out))
    require(not (out.is_relative_to(source) or source.is_relative_to(out)),
            'Output and baseline trees must be separate')
    require(not (out.is_relative_to(ROOT) and out == ROOT) and not ROOT.is_relative_to(out),
            'Output must not contain the support files')
    support, plan, modules, known = pinned_support()
    names = {p.name for p in source.iterdir()}
    require(names == set(BASELINE), 'Baseline directory must contain exactly the six pinned source files')
    original = {}
    for name, pin in BASELINE.items():
        path = ordinary(source / name)
        require(path.is_file(), 'Non-file baseline source: ' + name)
        original[name] = path.read_bytes()
        require(digest(original[name]) == pin, 'Baseline source hash mismatch: ' + name)
    decoded = {name: raw.decode('utf8') for name, raw in original.items()}
    packages = {}
    # Prepare and validate every transformation in memory before creating output.
    for name, features in plan['packages'].items():
        files = dict(decoded)
        batches = []
        for module_name, module in modules:
            selected = [f for f in module.FEATURES if f in features]
            if not selected:
                continue
            files = module.apply_many(files, selected)
            require(isinstance(files, dict) and files.keys() == original.keys() and
                    all(isinstance(value, str) for value in files.values()),
                    'Transform must preserve the six source files: ' + name)
            batches.append({'module': module_name, 'features': selected})
        payload = {key: original[key] if text == decoded[key] else text.encode('utf8')
                   for key, text in files.items()}
        require(any(payload[key] != original[key] for key in payload), 'Package changed no source: ' + name)
        packages[name] = (payload, {'features': features, 'applied_feature_batches': batches,
            'source_sha256': {key: digest(raw) for key, raw in sorted(payload.items())},
            'patch_modules_sha256': {batch['module']: MODULES[batch['module']] for batch in batches}})
    # Pin all inputs again before any writing; changed imports/inputs cannot be published.
    for name, raw in support.items():
        require(ordinary(ROOT / name).read_bytes() == raw, 'Support file changed during reproduction: ' + name)
    for name, raw in original.items():
        require(ordinary(source / name).read_bytes() == raw, 'Baseline changed during reproduction: ' + name)
    ordinary(out)
    out.mkdir(exist_ok=False)

    def write(relative, raw):
        path = ordinary(out / relative)
        require(path.is_relative_to(out), 'Output child escaped new directory')
        with path.open('xb') as stream:
            stream.write(raw)

    for name, (payload, record) in packages.items():
        ordinary(out / name).mkdir(exist_ok=False)
        ordinary(out / name / 'src').mkdir(exist_ok=False)
        for filename, raw in payload.items():
            write(Path(name) / 'src' / filename, raw)
        write(Path(name) / 'source-manifest.json', (json.dumps(record, indent=2) + '\n').encode('utf8'))
    report = {'created_utc': datetime.now(timezone.utc).isoformat(),
        'purpose': 'Reviewable source reproduction of all planned research packages; no efficacy endorsement.',
        'rebuild_script_sha256': digest(Path(__file__).read_bytes()),
        'baseline_source_sha256': BASELINE,
        'baseline_manifest_sha256': digest(support['baseline-manifest.json']),
        'selection_plan_sha256': PLAN_SHA256, 'patch_modules_sha256': MODULES,
        'canonical_module_order': list(MODULES),
        'packages': {name: record for name, (_, record) in packages.items()},
        'compiled': False, 'games_run': 0,
        'limits': 'Source hashes reproduce tested package inputs. Build with the official SDK/CLI separately; no local executable paths or game results are needed here.'}
    write('reproduction-manifest.json', (json.dumps(report, indent=2) + '\n').encode('utf8'))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--baseline', type=Path, required=True, help='Directory containing exactly six cleaned PR11 source files')
    parser.add_argument('--out', type=Path, required=True, help='New output directory; parent must exist')
    args = parser.parse_args()
    report = rebuild(args.baseline, args.out)
    print('Reproduced %d source packages in %s; no builds or games.' % (len(report['packages']), ordinary(args.out)))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, UnicodeError, TypeError) as error:
        print('REPRODUCTION REFUSED/FAILED: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
