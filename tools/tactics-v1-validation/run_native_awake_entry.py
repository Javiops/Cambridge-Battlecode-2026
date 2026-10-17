"""Lawful native prelude, then exact production Bot::turn, on both sides.

The wrapper module differs from the competitive main. It physically wakes a
singleton and moves outside basic range, without editing production World,
stats, inventory, claims, mission, or Bot memory. Boundary mode waits for real
camp damage before handoff. Read-only native reconstruction verifies actual
HP below .75 at the paid-current consumer, plus the same owner's native
clear/capture/bank. This is scoped activation/correctness, not strength proof.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
SDK_SHA = '76664dc7c4ab764243a7530eb97be12d9c20518b7bd2601a962fb0669d1da4a4'
ENGINE_SHA = 'e123b59d9dea198762ab7a04db9b3cb6d06dfa991088e41c24750fc4cb88b947'
ENGINE_BUILD = '02c4624c8c9b8bcaf9d906f407c0b1d932d5b5bce6e8ea7e222e08065dd9cede'
MAP_SHA = '486eb1577ee0dc27aec5e9162e75123cfee96d597d317c3c6f3966bc69dfe967'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_hashes(source):
    return {p.name: sha(p) for p in sorted(source.iterdir()) if p.suffix == '.h' or p.name == 'main.cpp'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('cli', 'project', 'source', 'output', 'node', 'engine'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--mode', choices=('ordinary', 'boundary'), default='boundary')
    p.add_argument('--reuse-bot', type=Path)
    p.add_argument('--reuse-game', type=Path)
    a = p.parse_args()
    cli, project, source, output, node, engine = [getattr(a, n).resolve() for n in ('cli', 'project', 'source', 'output', 'node', 'engine')]
    if bool(a.reuse_bot) != bool(a.reuse_game):
        raise ValueError('Reuse requires both --reuse-bot and --reuse-game')
    output.mkdir(parents=True, exist_ok=False)
    sdk = project / 'sdk/cpp/cambc.h'
    map_path = HERE / 'fixtures/native-cycle.map26a'
    fixture = HERE / 'fixtures/native-awake-entry.cpp'
    decoder = HERE / 'native_awake_trace.mjs'
    if sha(sdk) != SDK_SHA or sha(engine) != ENGINE_SHA or sha(map_path) != MAP_SHA:
        raise ValueError('Pinned SDK, replay engine or map differs')
    hashes = source_hashes(source)
    wrapper = fixture.read_text(encoding="utf8").encode("utf8")
    if a.mode == 'boundary':
        needle = b'else if(phase==2){const auto&c=w.groups[gi].camps.front();'
        if wrapper.count(needle) != 1:
            raise ValueError('Native prelude anchor changed')
        wrapper = wrapper.replace(needle, b'else if(phase==2){if(w.self.hp>800){bc::end_turn();continue;}const auto&c=w.groups[gi].camps.front();')
    wrapper_sha = hashlib.sha256(wrapper).hexdigest()
    commands = []

    def invoke(command, label):
        cmd = [str(x) for x in command]
        commands.append(cmd)
        r = subprocess.run(cmd, cwd=project, env={**os.environ, 'CAMBC_NO_UPDATE_CHECK': '1'}, capture_output=True, text=True, errors='replace', timeout=600)
        (output / (label + '.log')).write_text(r.stdout + r.stderr, encoding='utf8')
        if r.returncode:
            raise RuntimeError(r.stdout + r.stderr)

    if a.reuse_bot:
        bot, game = a.reuse_bot.resolve(), a.reuse_game.resolve()
        if (bot / 'src/main.cpp').read_text(encoding='utf8').encode('utf8') != wrapper or sha(bot / 'src/production-main.h') != hashes['main.cpp']:
            raise ValueError('Retained exact main/prelude differs')
        if any(sha(bot / 'src' / n) != h for n, h in hashes.items() if n != 'main.cpp'):
            raise ValueError('Retained production headers differ')
        retained = json.loads((game / 'record.json').read_text())
        module = sha(bot / '.cambc/build-release/bot-injected.wasm')
        if retained['identity']['a'] != module or retained['identity']['b'] != module:
            raise ValueError('Retained local game module differs')
    else:
        bot = output / 'bot'
        (bot / 'src').mkdir(parents=True)
        for name in hashes:
            shutil.copy2(source / name, bot / 'src' / ('production-main.h' if name == 'main.cpp' else name))
        (bot / 'src/main.cpp').write_bytes(wrapper)
        invoke([cli, 'build', bot], 'build-normal')
        invoke([cli, 'build', bot, '--release'], 'build-release')
        game = output / 'game'
        game.mkdir()
        invoke([cli, 'run', bot, bot, '--map', map_path, '--release', '--json', '-o', game, '--statistics', game / 'statistics.json'], 'run')
    module = sha(bot / '.cambc/build-release/bot-injected.wasm')
    wrapper_sha = sha(bot / 'src/main.cpp')
    stats_path = game / 'statistics.json'
    stats = json.loads(stats_path.read_text())
    if stats['match']['engineVersion'] != '0.0.2' or stats['match']['engineBuildHash'] != ENGINE_BUILD or stats['match']['mapHash'] != MAP_SHA:
        raise ValueError('Native engine/map identity differs')
    replay, = game.glob('*.repl26a')
    with zipfile.ZipFile(replay) as z:
        if z.testzip() is not None:
            raise ValueError('Replay CRC failed')
        raw = output / 'native.repl26a'
        raw.write_bytes(z.read('replay.repl26a'))
        stdout = {side: z.read('team-' + side + '.stdout').decode(errors='replace').replace(chr(0), '') for side in ('a', 'b')}
    trace_path = output / 'native-trace.json'
    invoke([node, decoder, '--engine', engine, '--replay', raw, '--output', trace_path], 'decode-native')
    trace = json.loads(trace_path.read_text())
    failures, cases = [], {}

    def events(kind, team, owner):
        return [x for e in stats['events'] if e['kind'] == kind and e.get('owner', {}).get('team') == team and e.get('owner', {}).get('id') == owner for x in e['entries']]

    for side, team in (('a', 'teamA'), ('b', 'teamB')):
        text = stdout[side]
        (output / (side + '.stdout.txt')).write_text(text, encoding='utf8')
        handoff = re.search(r'^AWAKE_MAIN_HANDOFF (\d+) (\d+) at=(-?\d+),(-?\d+) camp=(-?\d+),(-?\d+) campHP=(\d+) campRange=(\d+) hp=(\d+)$', text, re.M)
        bank_marker = re.search(r'^AWAKE_MAIN_BANKED (\d+) (\d+) score=22$', text, re.M)
        if not handoff or not bank_marker:
            failures.append(side + ':prelude-or-completion-marker')
            cases[side] = {'markers': [l for l in text.splitlines() if l.startswith('AWAKE_')]}
            continue
        owner, hand = int(handoff[1]), int(handoff[2])
        target = [int(handoff[5]), int(handoff[6])]
        at = lambda x: x['timestamp']['round']
        clears = [x for x in events('campClear', team, owner) if at(x) > hand and [x['x'], x['y']] == target]
        group = clears[0]['target']['id'] if clears else -1
        captures = [x for x in events('gemCollection', team, owner) if at(x) > hand and x['value'] == '22' and x.get('target', {}).get('id') == group]
        banks = [x for x in events('gemSubmission', team, owner) if at(x) > hand and x['value'] == '22']
        ordered = bool(clears and captures and banks) and hand < at(clears[0]) < at(captures[0]) < at(banks[0])
        stage = re.search(r'^T1 (\d+) ' + str(owner) + r' travel \d+ \d+ 0 solo-early-funded-stage-move$', text, re.M)
        current = re.search(r'^T1 (\d+) ' + str(owner) + r' clear \d+ \d+ 0 solo-paid-awake-current-basic$', text, re.M)
        current_round = int(current[1]) if current else -1
        actual = next((x for x in trace['turns'] if x['round'] == current_round and x['id'] == owner), None)
        move = next((x for x in trace['actions'] if stage and x['round'] == int(stage[1]) and x['owner'] == owner and x['kind'] == 4), None)
        basic = next((x for x in trace['actions'] if x['round'] == current_round and x['owner'] == owner and x['kind'] == 5), None)
        entered = bool(stage and current and move and basic and actual and int(stage[1]) + 1 == current_round and move['to'] == [actual['x'], actual['y']])
        if not entered or not ordered or int(bank_marker[1]) != owner:
            failures.append(side + ':actual-entry-clear-capture-bank-chain')
        below = bool(actual and actual['hp'] < .75 * actual['max_hp'])
        if a.mode == 'boundary' and not below:
            failures.append(side + ':actual-paid-current-not-below-three-quarter-health')
        error = bool(re.search(r'AWAKE_MAIN_FAIL|AWAKE_MAIN_EXCEPTION|TACTICS_ERROR|bot error:|\[err', text)) or any(int(n) > 0 for n in re.findall(r'^T1 \d+ \d+ \S+ \d+ \d+ (-?\d+) ', text, re.M))
        if error or events('death', team, owner) or events('gemLoss', team, owner):
            failures.append(side + ':error-death-or-gem-loss')
        cases[side] = {'owner': owner, 'handoff_round': hand, 'original_actual_camp_position': target, 'stage_move': move, 'actual_paid_current_owner': actual, 'actual_first_basic': basic, 'actual_current_below_three_quarter_hp': below, 'actual_clear': clears[:1], 'actual_capture': captures[:1], 'actual_bank': banks[:1], 'ordered': ordered, 'entry_followed_next_owner_by_current_certificate': entered}
    fuel = sum(len(e['entries']) for e in stats['events'] if e['kind'] == 'fuelExhausted')
    if fuel or any(stats['diagnostics']['botFaults'].values()):
        failures.append('native-fault-or-fuel')
    if source_hashes(source) != hashes:
        failures.append('source-changed-during-run')
    report = {'passed': not failures, 'scope': __doc__, 'mode': a.mode, 'created_utc': datetime.now(timezone.utc).isoformat(), 'source_sha256': hashes, 'sdk_header_sha256': SDK_SHA, 'cli_sha256': sha(cli), 'engine_module_sha256': ENGINE_SHA, 'native_engine': stats['match'], 'module_sha256': module, 'fixture_template_sha256': sha(fixture), 'actual_wrapper_sha256': wrapper_sha, 'decoder_sha256': sha(decoder), 'map_sha256': MAP_SHA, 'statistics_sha256': sha(stats_path), 'replay_sha256': sha(replay), 'native_trace_sha256': sha(trace_path), 'native_faults': stats['diagnostics']['botFaults'], 'fuel_exhausted': fuel, 'cases': cases, 'failures': failures, 'commands': commands, 'reused_existing_local_game': bool(a.reuse_bot), 'existing_game': str(game) if a.reuse_bot else None}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'passed': not failures, 'mode': a.mode, 'fuel': fuel, 'failures': failures, 'cases': {s: {'ordered': c.get('ordered'), 'below_three_quarter': c.get('actual_current_below_three_quarter_hp')} for s, c in cases.items()}}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
