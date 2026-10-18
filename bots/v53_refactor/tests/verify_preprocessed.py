#!/usr/bin/env python3
"""Compare compiler preprocessing across original, previous and current layouts.

Requires GCC/Clang-style C++ preprocessor; the SDK placeholder is NOT a game SDK.
"""
from pathlib import Path
import hashlib, shutil, subprocess, sys

root = Path(__file__).resolve().parents[1]
compiler = shutil.which('g++') or shutil.which('clang++')
if not compiler:
    sys.exit('No C++ preprocessor: cannot verify preprocessing')
src = root / 'src'
stub = root / 'tests/preprocess_stub'
configs = {
    'normal': [],
    'instrumented': ['-DP_FUELPROF=1', '-DP_DZLOG=1', '-DP_SWEEP_LOG=2',
                     '-DP_FXLOG=1','-DP_MODELOG=1','-DP_DBGT=1','-DP_RANGES=1'],
    'all-instrumentation': ['-DP_FUELPROF=1', '-DP_DZLOG=1', '-DP_SWEEP_LOG=2',
                     '-DP_FXLOG=1','-DP_MODELOG=1','-DP_DBGT=1','-DP_RANGES=1',
                     '-DP_CDPROBE=1','-DP_TRACE=1','-DP_TRACK_LOG=1'],
}
for name, opts in configs.items():
    args = [compiler, '-std=c++20', '-E', '-P', '-I',str(src), '-I',str(stub), *opts]
    before = subprocess.check_output([*args,str(root / 'tests/reference/v53_main.cpp')])
    after = subprocess.check_output([*args,str(src / 'main.cpp')])
    if before != after:
        sys.exit(f'FAIL: {name} preprocessed C++ differs')
    print(f'PASS: {name} preprocessed C++ matches v53 (sha256 {hashlib.sha256(after).hexdigest()[:16]})')
print('NOTE: preprocessing equality is not a runtime build. Local game parity still advised.')
