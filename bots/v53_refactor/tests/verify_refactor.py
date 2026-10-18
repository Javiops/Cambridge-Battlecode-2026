#!/usr/bin/env python3
"""Expand only mechanically extracted .inc sections and verify original v53 byte-for-byte.

Unlike a C++ build, this tests the exact textual extraction and remains SDK-independent.
"""
from pathlib import Path
import hashlib, json, sys

root = Path(__file__).resolve().parents[1]
src = root / 'src'
manifest = json.loads((root / 'tests/refactor_manifest.json').read_text())
step2 = json.loads((root / 'tests/step2_manifest.json').read_text())

# Main was split in step 1, then its run loop and turn policy helpers in step 2.
main = (src / 'main.cpp').read_bytes()
for marker, fragment in [
    (b'#include "run_loop.inc"\n', b'run_loop.inc'),
    (b'#include "turn_helpers.inc"\n#include "turn_policy.inc"\n#include "turn_labels.inc"\n', b'turn_policy.inc'),
]:
    if main.count(marker) != 1:
        sys.exit(f'FAIL: missing or duplicated nested section for {fragment.decode()}')
    if fragment == b'turn_policy.inc':
        replacement = b'#include "turn_policy.inc"\n'
    else:
        replacement = (src / fragment.decode()).read_bytes()
        # The include occupied a single line; the original section ends with two newlines.
        # The placeholder itself also supplies a blank line after it.
        assert replacement.endswith(b'\n\n')
        replacement = replacement[:-1]
    main = main.replace(marker, replacement, 1)
if hashlib.sha256(main).hexdigest() != step2['previous_main_sha256']:
    sys.exit('FAIL: step 2 does not reconstruct step 1 main.cpp byte-for-byte')
if main != (root / 'tests/reference/step1_main.cpp').read_bytes():
    sys.exit('FAIL: step 2 main != stored step 1 main')
if b''.join((src / f).read_bytes() for f in ('turn_helpers.inc','turn_policy.inc','turn_labels.inc')) != (root / 'tests/reference/step1_turn_policy.inc').read_bytes():
    sys.exit('FAIL: step 2 policy fragments != stored step 1 turn policy')
print('PASS: step 2 reconstructs step 1 source byte-for-byte')

main = main.replace(
    b'// Policy implementation sections are included in their original declaration order.\n'
    b'// See ARCHITECTURE.md. Do not reorder: these are not independent translation units.\n', b'', 1
)
for frag in manifest['fragments']:
    filename = frag['file']
    marker = f'#include "{filename}"\n'.encode()
    if main.count(marker) != 1:
        sys.exit(f'FAIL: missing/duplicate original section {filename}')
    replacement = (src / filename).read_bytes()
    if filename == 'turn_policy.inc':
        replacement = (root / 'tests/reference/step1_turn_policy.inc').read_bytes()
    main = main.replace(marker,replacement,1)
ref = (root / 'tests/reference/v53_main.cpp').read_bytes()
if main != ref or hashlib.sha256(main).hexdigest() != manifest['original_main_sha256']:
    sys.exit('FAIL: reconstructed main != original v53')
print('PASS: original v53 main reconstructed byte-for-byte:', manifest['original_main_sha256'])

for name, expected in manifest['unchanged_headers_sha256'].items():
    if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
        sys.exit('FAIL: modified legacy header ' + name)
print('PASS: all original headers unchanged, including params.h')
