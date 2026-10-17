"""Compile the complete bot and run actual-helper regressions for all 8 switches.

Requires a WASI SDK with exception-enabled libc++ and Python wasmtime.
Writes only to an isolated build directory and an explicitly requested report.
Never edits --src, invokes a game, or accesses the network.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib
import itertools
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent
FLAGS=('P_DP_MEMORY_FIX','P_DP_ANCHOR_FIX','P_DP_CHANNEL_FIX')

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def source_hashes(src: Path) -> dict[str,str]:
    return {p.relative_to(src).as_posix():sha(p.read_bytes()) for p in sorted(src.rglob('*')) if p.is_file()}

def extract_function(source: str, name: str) -> str:
    """Extract the exact definition, ignoring braces in C++ strings/comments."""
    match=re.search(r'^bool\s+'+re.escape(name)+r'\s*\(',source,re.M)
    if not match:
        raise ValueError(f'Missing production function {name}')
    start=match.start(); first=source.index('{',match.end()); depth=0; state='code'; i=first
    while i<len(source):
        c=source[i]; nxt=source[i:i+2]
        if state=='line':
            if c=='\n': state='code'
        elif state=='block':
            if nxt=='*/': state='code'; i+=1
        elif state in ('"',"'"):
            if c=='\\': i+=1
            elif c==state: state='code'
        elif nxt=='//': state='line'; i+=1
        elif nxt=='/*': state='block'; i+=1
        elif c in ('"',"'"): state=c
        elif c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0: return source[start:i+1]
        i+=1
    raise ValueError(f'Unterminated production function {name}')

def override_flags(params: str, values: tuple[int,...]) -> str:
    for flag,value in zip(FLAGS,values):
        expression=r'(?m)^(\s*#\s*define\s+'+flag+r')\s+[^\r\n]+'
        params,n=re.subn(expression,lambda m:f'{m[1]} {value}',params)
        if n!=1: raise ValueError(f'Expected exactly one definition of {flag}; got {n}')
    return params

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--src',type=Path,required=True,help='Bot src directory, or its parent project')
    parser.add_argument('--sdk',type=Path,required=True,help='Official SDK cpp directory, or sdk parent')
    parser.add_argument('--compiler',type=Path,required=True,help='WASI SDK clang++ executable')
    parser.add_argument('--wasi-sdk',type=Path,help='WASI SDK root; defaults to compiler.parent.parent')
    parser.add_argument('--wasmtime-pythonlib',type=Path,help='Optional directory containing Python wasmtime')
    parser.add_argument('--build-dir',type=Path,help='Retain objects/logs/WASM here; otherwise temporary')
    parser.add_argument('--report',type=Path,help='Write concise JSON report; binaries/logs are excluded')
    parser.add_argument('--jobs',type=int,default=1,help='Parallel variant compilations (default1)')
    args=parser.parse_args()
    src=args.src.resolve(); src=src/'src' if (src/'src').is_dir() else src
    sdk=args.sdk.resolve(); sdk=sdk/'cpp' if (sdk/'cpp').is_dir() else sdk
    compiler=args.compiler.resolve(); wasi=(args.wasi_sdk or compiler.parent.parent).resolve()
    if args.jobs<1: parser.error('--jobs must be positive')
    for p in (src/'main.cpp',src/'params.h',src/'draft_plan.h',src/'channel_safety.h',sdk/'cambc.h',compiler):
        if not p.is_file(): parser.error(f'Missing required file: {p}')
    if args.report and args.report.resolve().is_relative_to(src):
        parser.error('--report must be outside --src')
    if args.wasmtime_pythonlib:
        import sys
        sys.path.insert(0,str(args.wasmtime_pythonlib.resolve()))
    try: wasmtime=importlib.import_module('wasmtime')
    except ImportError: parser.error('Install requirements.txt or supply --wasmtime-pythonlib')
    include=wasi/'share/wasi-sysroot/include/wasm32-wasip1/eh/c++/v1'
    lib=wasi/'share/wasi-sysroot/lib/wasm32-wasip1/eh'
    if not include.is_dir() or not lib.is_dir(): parser.error('WASI SDK exception-enabled libc++ layout not found')
    original=source_hashes(src)
    production=(src/'main.cpp').read_text(encoding='utf-8')
    names=('channel_eligible','start_recall','start_submission')
    extracted={name:extract_function(production,name) for name in names}
    fixture_hashes={p.name:sha(p.read_bytes()) for p in sorted((HERE/'fixtures').glob('*.cpp'))}
    fixtures={p.stem:p.read_text(encoding='utf-8') for p in (HERE/'fixtures').glob('*.cpp')}
    fixture='\n'.join(['#include "params.h"',fixtures['memory'],fixtures['channel_mock'],
        *extracted.values(),fixtures['channel_cases'],
        'int main() { memory_regression(); channel_regression(); return 0; }'])
    base=[str(compiler),'--target=wasm32-wasip1','-std=c++20','-fwasm-exceptions',
        '-mllvm','-wasm-use-legacy-eh=false','-msimd128','-mbulk-memory',
        '-isystem',str(include)]
    manager=tempfile.TemporaryDirectory(prefix='mate-bwf-regression-') if not args.build_dir else None
    build=Path(manager.name) if manager else args.build_dir.resolve()
    if build==src or build.is_relative_to(src): parser.error('--build-dir must be outside --src')
    build.mkdir(parents=True,exist_ok=True)
    try:
        def compile_one(values: tuple[int,...]) -> dict:
            label=''.join(str(x) for x in values); folder=build/label
            snapshot=folder/'src'; snapshot.mkdir(parents=True,exist_ok=True)
            for rel in original:
                target=snapshot/rel; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src/rel,target)
            params=snapshot/'params.h'
            params.write_text(override_flags(params.read_text(encoding='utf-8'),values),encoding='utf-8')
            commands=[]
            def compile_command(command:list[str],name:str) -> None:
                process=subprocess.run(command,capture_output=True,text=True,errors='replace',timeout=180)
                (folder/(name+'.log')).write_text(process.stdout+process.stderr,encoding='utf-8')
                if process.returncode:
                    raise RuntimeError(f'{label} {name} failed:\n{process.stdout}{process.stderr}')
                commands.append(command)
            # The entire production TU is compiled, including all enabled callsites.
            full=folder/'production.o'
            compile_command(base+['-O0','-I',str(sdk),'-c',str(snapshot/'main.cpp'),'-o',str(full)],'production')
            test=folder/'regression.cpp'; test.write_text(fixture,encoding='utf-8')
            module=folder/'regression.wasm'
            compile_command(base+['-O1','-I',str(snapshot),'-L',str(lib),str(test),'-lunwind',
                '-Wl,-z,stack-size=4194304','-o',str(module)],'fixture')
            return {'flags':dict(zip(FLAGS,values)),'label':label,'production_object_sha256':sha(full.read_bytes()),
                'fixture_wasm_sha256':sha(module.read_bytes()),'commands':commands,'module':str(module),'folder':str(folder)}
        combos=list(itertools.product((0,1),repeat=3))
        with ThreadPoolExecutor(max_workers=args.jobs) as pool: results=list(pool.map(compile_one,combos))
        config=wasmtime.Config(); config.wasm_exceptions=True; engine=wasmtime.Engine(config)
        for result in results:
            folder=Path(result.pop('folder')); module=Path(result.pop('module'))
            store=wasmtime.Store(engine); config=wasmtime.WasiConfig()
            out=folder/'stdout'; err=folder/'stderr'
            config.stdout_file=str(out); config.stderr_file=str(err); store.set_wasi(config)
            linker=wasmtime.Linker(engine); linker.define_wasi()
            instance=linker.instantiate(store,wasmtime.Module.from_file(engine,str(module)))
            try: instance.exports(store)['_start'](store)
            except Exception as error:
                raise RuntimeError(f'{result["label"]} fixture failed: {error}\n{out.read_text()}\n{err.read_text()}') from error
            text=out.read_text(); errors=err.read_text()
            if 'PASS checks=' not in text or errors: raise RuntimeError(f'{result["label"]} incomplete output: {text}\n{errors}')
            result['stdout']=text; result['status']='pass'
            print(f'PASS {result["label"]}: full SDK compile, memory/anchor/LIGHT channel mechanisms',flush=True)
        # Memory correctness must preserve complete successful geometry/bank outputs.
        by_label={r['label']:r for r in results}
        for anchor,channel in itertools.product((0,1),repeat=2):
            off=by_label[f'0{anchor}{channel}']['stdout'].splitlines()[0]
            on=by_label[f'1{anchor}{channel}']['stdout'].splitlines()[0]
            if off!=on: raise AssertionError(f'Memory flag changed normal geometry/bank output: {off} != {on}')
        if source_hashes(src)!=original: raise RuntimeError('Source changed while tests were running')
        if {p.name:sha(p.read_bytes()) for p in sorted((HERE/'fixtures').glob('*.cpp'))}!=fixture_hashes:
            raise RuntimeError('Fixtures changed while tests were running')
        report={'status':'pass','variants':results,'source_sha256':original,'sdk_header_sha256':sha((sdk/'cambc.h').read_bytes()),
            'extracted_function_sha256':{n:sha(s.encode()) for n,s in extracted.items()},
            'fixture_sha256':fixture_hashes,
            'limits':['SDK compilation is a full translation-unit object compile, not a link or release build.',
                'Mechanisms execute actual production helpers with narrow mocks; no matches or strength claims.',
                'Mock fuel checks do not measure native engine/guest cost; native calibration is separate.']}
        if args.report:
            args.report.parent.mkdir(parents=True,exist_ok=True)
            args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print('PASS all 8 combinations; source unchanged')
    finally:
        if manager: manager.cleanup()

if __name__=='__main__': main()
