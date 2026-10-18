"""One local/CI check: frozen sources, contracts, engine cases and metered guests."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import baseline

HERE = Path(__file__).resolve().parent
ROOT = baseline.ROOT
ENGINE_SHA = '1919c5a6f2ea039041071166aef38f6f1ede8d5c29b062db8c2e028109e3f96f'
ENGINE_BUILD = 'd7e29ae3546357b011419c764204b7b9e2232bdb1b07868250c6b35d4c18d2a5'


def executable(name):
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f'Missing executable: {name}')
    return str(Path(path).resolve())


def engine_path(explicit):
    if explicit:
        path = Path(explicit).resolve()
        if baseline.sha(path) != ENGINE_SHA:
            raise RuntimeError('Engine differs from the reviewed 0.0.3 pin; review mechanics before changing it')
        return path
    caches = [Path.home()/'.cache/cambc/assets']
    if os.environ.get('LOCALAPPDATA'):
        caches.append(Path(os.environ['LOCALAPPDATA'])/'cambc/assets')
    for cache in caches:
        for path in sorted(cache.glob('*/visualiser/assets/v0_0_3-*.wasm')):
            if baseline.sha(path) == ENGINE_SHA:
                return path
    raise RuntimeError('Pinned engine not found; run cambc init --yes or pass --engine <official engine.wasm>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli', default='cambc')
    parser.add_argument('--engine')
    parser.add_argument('--cxx', default='c++')
    parser.add_argument('--wasi-cxx', help='Use a wasi-sdk clang++ instead of a native C++ compiler')
    args = parser.parse_args()
    output = ROOT/'out/foundation'
    output.mkdir(parents=True, exist_ok=True)
    report = output/'checks.json'
    report.unlink(missing_ok=True)  # Clear the old PASS before validating any input.
    baseline.verify()
    before = baseline.source_identity(HERE/'src')
    tests_before = baseline.source_identity(HERE/'tests')
    runner_before = baseline.sha(Path(__file__))
    manifest_before = baseline.sha(baseline.MANIFEST)
    cli, node = executable(args.cli), executable('node')
    engine = engine_path(args.engine)
    environment = {**os.environ, 'CAMBC_NO_UPDATE_CHECK': '1',
                   'CAMBC_WASMTIME_CACHE': str(output/'wasmtime-cache')}
    commands = []

    def run(name, command):
        result = subprocess.run([str(x) for x in command], cwd=ROOT, env=environment,
                                capture_output=True, text=True, errors='replace', timeout=300)
        log = output/(name+'.log')
        log.write_text(result.stdout+result.stderr, encoding='utf-8')
        commands.append({'name': name, 'command': [str(x) for x in command],
                         'exit_code': result.returncode, 'log_sha256': baseline.sha(log)})
        if result.returncode:
            raise RuntimeError(f'{name} failed: {log}\n{result.stdout[-3000:]}{result.stderr[-3000:]}')
        print(f'PASS {name}', flush=True)
        return result.stdout

    version = run('cli-version',[cli,'--version']).strip()
    if version != 'cambc 2.2.5':
        raise RuntimeError(f'Expected cambc 2.2.5, got {version}; review and repin deliberately')
    run('baseline-tests',[sys.executable,HERE/'tests/baseline_test.py'])
    compiler = executable(args.wasi_cxx or args.cxx)
    flags = ['-std=c++20','-O2','-UNDEBUG']
    if args.wasi_cxx:
        sdk = Path(compiler).parent.parent/'share/wasi-sysroot'
        flags += ['-fwasm-exceptions','-mllvm','-wasm-use-legacy-eh=false','--no-wasm-opt',
                  '-isystem', str(sdk/'include/wasm32-wasip1/eh/c++/v1'),
                  '-L'+str(sdk/'lib/wasm32-wasip1/eh'),'-lunwind']
    for suite in ('actions', 'planner'):
        binary = output/(suite + ('.wasm' if args.wasi_cxx else '-test'))
        run('compile-'+suite,[compiler,*flags,HERE/('tests/'+suite+'.cpp'),'-o',binary])
        if args.wasi_cxx:
            runner = output/(suite+'-run.mjs')
            runner.write_text("import fs from 'node:fs';import{WASI}from'node:wasi';"
                "const w=new WASI({version:'preview1',args:[],env:{},preopens:{}});"
                "const{instance}=await WebAssembly.instantiate(fs.readFileSync(new URL('./"+suite+".wasm',import.meta.url)),"
                "{wasi_snapshot_preview1:w.wasiImport});w.start(instance);",encoding='utf-8')
            run(suite+'-contracts',[node,runner])
        else:
            run(suite+'-contracts',[binary])
    mechanics = json.loads(run('engine-cases',[node,HERE/'tests/engine.mjs',engine]))
    run('build-foundation',[cli,'build','bots/foundation','--release'])
    guest = Path(tempfile.mkdtemp(prefix='guest-',dir=output))
    source = guest/'src'
    # Exact current modules, with only the entrypoint replaced by the guest test.
    # A fresh tree prevents deleted headers/modules surviving from earlier runs.
    shutil.copytree(HERE/'src',source)
    shutil.copyfile(HERE/'tests/guest.cpp',source/'main.cpp')
    run('build-guest',[cli,'build',guest,'--release'])
    games = []
    map_file = ROOT/'maps/lanes.map26a'
    if not map_file.is_file():
        raise RuntimeError('Missing official lanes map; run cambc init --yes')
    for side in (0,1):
        match = output/f'guest-side-{side}'
        if match.exists():
            # Retain previous logs and avoid mistaking them for this run.
            i=1
            while (output/f'guest-side-{side}-{i}').exists(): i+=1
            match=output/f'guest-side-{side}-{i}'
        stats = match/'statistics.json'
        players = [guest,ROOT/'bots/foundation'] if side==0 else [ROOT/'bots/foundation',guest]
        run(f'guest-side-{side}',[cli,'run',*players,'--map',map_file,'--release',
                                 '--statistics',stats,'--json','-o',match])
        data=json.loads(stats.read_text(encoding='utf-8'))
        team = ('teamA','teamB')[side]
        expected={c['id'] for c in data['champions'] if c['team']==team}
        markers={e['owner']['id']:e['entries'] for e in data['events']
                 if e['kind']=='wardPlacement' and e['owner']['team']==team}
        faults=data['diagnostics']['botFaults']
        if not expected or set(markers)!=expected or any(len(entries)!=1 for entries in markers.values()):
            raise RuntimeError(f'Missing guest completion markers: {match}')
        if faults!={'teamA':0,'teamB':0} or not data['diagnostics']['detailedCaptureComplete']:
            raise RuntimeError(f'Bot faults or incomplete diagnostics: {match}')
        bad_events=[e for e in data['events'] if e['kind'] in ('fuelExhausted','resignation','botFault') and e['entries']]
        if bad_events or data['match']['roundsCompleted']!=2000 or data['match']['finalRoundPartial']:
            raise RuntimeError(f'Incomplete or fuel-exhausted guest game: {match}')
        if data['match']['engineVersion']!='0.0.3' or data['match']['engineBuildHash']!=ENGINE_BUILD:
            raise RuntimeError('CLI game used a different engine version/build; review before repinning')
        games.append({'side':side,'statistics_sha256':baseline.sha(stats),
                      'guest_instances':len(expected),'reserve_asserted_in_guest':12000,
                      'engine_build_hash':data['match']['engineBuildHash'],
                      'bot_faults':faults,'fuel_exhausted_events':0})
    baseline.verify()
    if (baseline.source_identity(HERE/'src') != before or
            baseline.source_identity(HERE/'tests') != tests_before or
            baseline.sha(Path(__file__)) != runner_before or
            baseline.sha(baseline.MANIFEST) != manifest_before):
        raise RuntimeError('Foundation sources, tests, runner or baseline changed while checks were running')
    result={'schema':1,'passed':True,'created_utc':datetime.now(timezone.utc).isoformat(),
        'baseline_manifest_sha256':manifest_before,
        'runner_sha256':runner_before,
        'test_sources':tests_before,
        'guest_sources':baseline.source_identity(source),
        'guest_artifact_sha256':baseline.sha(guest/'.cambc/build-release/bot-injected.wasm'),
        'node':{'version':run('node-version',[node,'--version']).strip(),'sha256':baseline.sha(node)},
        'foundation_source':before,'cli':{'version':version,'sha256':baseline.sha(cli)},
        'compiler_sha256':baseline.sha(compiler),'sdk_cpp':baseline.source_identity(ROOT/'sdk/cpp'),
        'build_config_sha256':baseline.sha(ROOT/'cmake/CMakeLists.txt'),
        'project_config_sha256':baseline.sha(ROOT/'cambc.toml'),
        'engine':{'version':'0.0.3','sha256':baseline.sha(engine)},
        'map':{'name':map_file.name,'sha256':baseline.sha(map_file)},
        'artifact_sha256':baseline.sha(HERE/'.cambc/build-release/bot-injected.wasm'),
        'mechanics':mechanics,'guest_games':games,'commands':commands,
        'live_upload_verified':False,'competitive_improvement_tested':False}
    report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'PASS all foundation checks; evidence: {report}')


if __name__ == '__main__': main()
