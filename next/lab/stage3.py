"""Export, official release execution, and acceptance evidence for Stage 3."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import struct
import tempfile
import zipfile

import numpy as np

from . import cloning, core, dataset, policy, replay, stage1, stats


def folder():
    return core.ROOT/'models'/core.config()['stage3']['model']


def save(name, result):
    (core.ROOT/'results'/name).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return result


def model():
    training = json.loads((folder()/'training.json').read_text())
    if core.sha(folder()/'weights.f32') != training['export']['weights_sha256']:
        raise ValueError('Trained model hash changed')
    w = np.fromfile(folder()/'weights.f32', dtype='<f4')
    if w.shape != (cloning.N,) or not np.isfinite(w).all():
        raise ValueError('Invalid trained model')
    if not np.array_equal(w, np.asarray(json.loads((folder()/'weights.json').read_text()), np.float32)):
        raise ValueError('JSON and binary model exports differ')
    return w


def require_training_config(plan, cfg):
    keys = ('model', 'seed', 'epochs', 'batch_size', 'evaluate_every', 'learning_rate',
            'weight_decay', 'max_class_weight', 'development_maps')
    if any(plan['config'][k] != cfg[k] for k in keys):
        raise ValueError('Training settings changed; use a new model version')


def prepare():
    model()
    # Copies are intentional: a frozen bot bundle must build without sibling folders.
    bot = core.ROOT/'bots/bc-actor/src'
    for name in ('policy.h', 'observe.h'):
        shutil.copyfile(core.ROOT/'bots/contract-probe/src'/name, bot/name)
    shutil.copyfile(folder()/'weights.h', bot/'weights.h')
    control = core.ROOT/'bots/bc-untrained/src'
    control.mkdir(parents=True, exist_ok=True)
    for name in ('main.cpp', 'policy.h', 'observe.h'):
        shutil.copyfile(bot/name, control/name)
    scratch = core.ROOT/'.cambc/stage3-control'
    cloning.write_export(scratch, np.asarray(policy.weights(), np.float32))
    shutil.copyfile(scratch/'weights.h', control/'weights.h')
    cfg = core.config()['stage3']
    for directory, version in (('bc-untrained', cfg['control_version']), ('bc-actor', cfg['trained_version'])):
        if not (core.ARCHIVE/version).exists():
            core.freeze('bots/'+directory, version, parent='contract-probe-v1',
                        note='Stage 3 local actor; fixed controller/draft, '+('trained BC weights' if directory=='bc-actor' else 'untrained reference weights'))
        for source in (core.ROOT/'bots'/directory/'src').iterdir():
            if source.read_bytes() != (core.ARCHIVE/version/'src'/source.name).read_bytes():
                raise ValueError('Frozen model sources differ; choose a new version')
    return dict(prepared=True, trained=cfg['trained_version'], control=cfg['control_version'])


def footers(path):
    result = {}
    with zipfile.ZipFile(path) as z:
        for name in ('team-a.stdout', 'team-b.stdout'):
            data = z.read(name); pos = 0
            while (pos := data.find(b'S3F!', pos)) >= 0:
                r, champion, budget, kernel, used = struct.unpack_from('<5I', data, pos+4)
                if (r, champion) in result:
                    raise ValueError('Duplicate or resumed turn footer')
                result[r, champion] = dict(budget=budget, kernel=kernel, used=used)
                pos += 24
    return result


def check_games(games, expected):
    keys = [(g['name_a'], g['name_b'], g['map']) for g in games]
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise ValueError('Release schedule incomplete or duplicated')
    for game in games:
        if game.get('error') or game.get('outcome') not in ('teamA', 'teamB'):
            raise ValueError('Incomplete release game')
        if any(t['faults'] or t['fuel_exhausted'] for t in game['teams'].values()):
            raise ValueError('Release bot fault or fuel exhaustion')


def preserve_bundle(destination, fresh):
    if destination.exists():
        # CLI bundle refuses overwrites. Compare content and retain the original ZIP,
        # even when a later build assigns different ZIP timestamps or compression.
        def contents(path):
            with zipfile.ZipFile(path) as z:
                names = [n for n in z.namelist() if not n.endswith('/')]
                if len(names) != len(set(names)):
                    raise ValueError('Duplicate source bundle entries')
                return {n: z.read(n) for n in names}
        if contents(destination) != contents(fresh):
            raise ValueError('Existing bundle sources differ from verified release sources')
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(fresh, destination)


def verify():
    cfg = core.config()['stage3']; prepare(); w = model()
    version = core.version(cfg['trained_version']); profile = core.runtime_identity()
    checks = []
    for name in cfg['parity_maps']:
        out = core.ROOT/'.cambc/stage3'/name.replace('/', '_'); out.mkdir(parents=True, exist_ok=True)
        raw, error = core.run_game(version, version, core.map_path(name), str(out), logs=True, profile=profile)
        if raw is None:
            raise ValueError(error)
        summary = stats.summarize(raw)
        if any(t['faults'] or t['fuel_exhausted'] for t in summary['teams'].values()):
            raise ValueError('Model canary fault or fuel exhaustion')
        replay_file = max(out.glob('*.repl26a'), key=lambda p: p.stat().st_mtime)
        traces = stage1.traces(replay_file); fuel = footers(replay_file)
        expected = len(raw['roster']['champions'])*80
        if len(traces) != expected or set(traces) != set(fuel):
            raise ValueError('Model canary trace missing')
        ordered = sorted(traces)
        encoded = {k: np.asarray([traces[key][k] for key in ordered], dtype=bool if k=='mask' else np.float32)
                   for k in ('features', 'candidates', 'mask')}
        scores = cloning.forward(w, encoded['features'], encoded['candidates'], exact=True)[0]
        sdk_scores = np.asarray([traces[key]['scores'] for key in ordered], np.float32)
        if not np.array_equal(scores, sdk_scores):
            raise ValueError('Exported SIMD logits are not bit-identical to float32 reference')
        chosen = np.argmax(np.where(encoded['mask'], scores, -np.inf), axis=1)
        if chosen.tolist() != [traces[key]['pick'] for key in ordered]:
            raise ValueError('Exported model argmax differs')
        # Independent scalar Python reference, rather than just trainer/export code.
        for i in np.linspace(0, len(ordered)-1, 32, dtype=int):
            scalar, pick = policy.infer(traces[ordered[i]], w.tolist())
            if scalar != sdk_scores[i].tolist() or pick != int(chosen[i]):
                raise ValueError('Scalar reference differs from deployed weights')
        blob = dataset.raw_bytes(replay_file)
        actions = replay.decode(blob, core.map_path(name).read_bytes())
        records = dataset.run_replay_engine(blob, name, actions, max_round=80)
        seen = set(); kinds = Counter()
        for row in records:
            if row['type'] != 'decision' or row['decision_index'] != 0:
                continue
            o = row['observation']; key = (o['actor']['round'], o['actor']['champion'])
            trace = traces[key]; e = policy.encode(o, records[0]['terrain'])
            for field in ('features', 'candidates', 'mask'):
                if not stage1.close_float(e[field], trace[field]):
                    raise ValueError('Native replay/model observation mismatch')
            action = e['actions'][trace['pick']]
            actual = dataset.canonical(row['action'])
            if actual != action or trace['actions'][0]['action'] != action or not trace['actions'][0]['result']:
                raise ValueError('Chosen proposal does not match successful SDK/native action')
            seen.add(key); kinds[action['kind']] += 1
        if seen != set(traces):
            raise ValueError('Native replay did not cover all model decisions')
        ordinary = [f for f in fuel.values() if f['budget']==100000]
        kernel_max = max(f['kernel'] for f in ordinary); used_max = max(f['used'] for f in ordinary)
        if kernel_max > core.config()['stage1']['max_kernel_fuel'] or used_max > cfg['max_turn_fuel']:
            raise ValueError('Learned model exceeds the fuel envelope')
        checks.append(dict(map=name, map_sha256=core.sha(core.map_path(name)), observations=len(traces),
                           bit_identical_logit_values=len(traces)*policy.K, scalar_reference_rows=32,
                           successful_first_actions=dict(kinds), kernel_fuel_max=kernel_max, prefooter_fuel_max=used_max,
                           faults=0, fuel_exhausted=0, replay_sha256=core.sha(replay_file)))
        print('Verified trained model on '+name, flush=True)
    return save('stage3-parity.json', dict(passed=True, runtime=profile, weights_sha256=core.sha(folder()/'weights.f32'),
                wasm_sha256=core.sha(version.wasm), maps=checks, observation_action_parity=True,
                bit_identical_logits=True, decisions_per_turn=2, sources=stage1.sources()))


def release():
    cfg = core.config()['stage3']; prepare()
    maps = cfg['release_maps']
    if set(maps)-set(core.config()['maps']['screen']):
        raise ValueError('Stage 3 release diagnostics must use screen maps')
    pairs = [(v, opponent) for v in (cfg['trained_version'], cfg['control_version']) for opponent in cfg['release_opponents']]
    expected = {(x, y, m) for a, b in pairs for x, y in ((a, b), (b, a)) for m in maps}
    games = core.play(pairs, maps, cfg['jobs'])
    check_games(games, expected)
    reports = {}
    for v in (cfg['trained_version'], cfg['control_version']):
        reports[v] = {}
        for opponent in cfg['release_opponents']:
            selected = [g for g in games if {g['name_a'], g['name_b']} == {v, opponent}]
            own = [g['teams']['teamA' if g['name_a']==v else 'teamB'] for g in selected]
            reports[v][opponent] = dict(games=len(selected), wins=sum(g['outcome']==('teamA' if g['name_a']==v else 'teamB') for g in selected),
                mean_banked_gems=float(np.mean([t['gems'] for t in own])),
                mean_gold=float(np.mean([t['gold'] for t in own])),
                mean_camp_clears=float(np.mean([t['camp_clears'] for t in own])),
                faults=sum(t['faults'] for t in own), fuel_exhausted=sum(t['fuel_exhausted'] for t in own))
    bundle = core.ROOT/'results/bundles'/f"{cfg['trained_version']}.zip"
    with tempfile.TemporaryDirectory(dir=core.ROOT/'.cambc') as tmp:
        fresh, same = core.bundle(cfg['trained_version'], Path(tmp)/'verified.zip')
        if not same:
            raise ValueError('Model source bundle did not reproduce frozen release WASM')
        preserve_bundle(bundle, fresh)
    return save('stage3-release.json', dict(passed=True, runtime=core.runtime_identity(), diagnostics=reports, games=games,
                bundle=dict(path=bundle.relative_to(core.ROOT).as_posix(), sha256=core.sha(bundle), rebuild_identical=True),
                confirmation_games=0, promotion_test=False, promoted=False, sources=stage1.sources()))


def analyze():
    """Read-only error analysis of the already frozen model, with no model selection."""
    data, maps, episodes = cloning.load('validation'); w = model()
    per_map = {name: cloning.metrics(w, cloning.subset(data, maps==name)) for name in sorted(set(maps))}
    training = json.loads((folder()/'training.json').read_text())
    if cloning.metrics(w, data) != training['validation']:
        raise ValueError('Frozen model no longer reproduces its reported validation metrics')
    predicted = cloning.predict(w, data)
    predicted_kind = np.argmax(data['candidates'][np.arange(len(predicted)), predicted, :4], axis=1)
    return save('stage3-analysis.json', dict(model=training['model'], weights_sha256=core.sha(folder()/'weights.f32'),
        per_validation_map=per_map, validation_episodes=episodes,
        cast_predictions_without_cast_labels=int(np.sum(predicted_kind==3)),
        exact_accuracy_change_vs_untrained=training['validation']['exact_candidate_accuracy']-training['untrained_validation']['exact_candidate_accuracy'],
        macro_recall_change_vs_untrained=training['validation']['macro_action_recall']-training['untrained_validation']['macro_action_recall'],
        strength_improvement_established=False, model_selections_from_this_analysis=0,
        interpretation='Teacher-lineage shift and supported-proposal limitations; preserve this model and validation result without retuning it'))


def ready():
    dataset.ready()
    training = json.loads((folder()/'training.json').read_text()); model()
    require_training_config(json.loads((folder()/'plan.json').read_text()), core.config()['stage3'])
    provenance = json.loads((folder()/'provenance.json').read_text())
    for source, expected in provenance['sources'].items():
        if hashlib.sha256((core.ROOT/source).read_text(encoding='utf-8').encode()).hexdigest() != expected:
            raise ValueError('Training source provenance changed; preserve the model and use a new version')
    if not training['offline_acceptance_passed']:
        raise ValueError('Offline cloning acceptance failed')
    parity = json.loads((core.ROOT/'results/stage3-parity.json').read_text())
    release_result = json.loads((core.ROOT/'results/stage3-release.json').read_text())
    current = stage1.sources()
    for proof in (parity, release_result):
        if not proof['passed'] or proof['sources'] != current or proof['runtime'] != core.runtime_identity():
            raise ValueError('Stage 3 release proof is stale')
    if core.sha(folder()/'plan.json') != training['plan_sha256'] or training['dataset_manifest_sha256'] != core.sha(dataset.root()/'manifest.json'):
        raise ValueError('Model training inputs changed')
    for file, key in (('weights.f32', 'weights_sha256'), ('weights.h', 'header_sha256')):
        if core.sha(folder()/file) != training['export'][key]:
            raise ValueError('Model export changed')
    version = core.version(core.config()['stage3']['trained_version'])
    if core.sha(version.wasm) != parity['wasm_sha256']:
        raise ValueError('Release model changed')
    if (version.wasm.parent/'src/weights.h').read_bytes() != (folder()/'weights.h').read_bytes():
        raise ValueError('Model header differs from the frozen runtime model')
    return save('stage3-ready.json', dict(passed=True, stage=3, next_stage=4, model=training['model'],
                parameters=cloning.N, weights_sha256=training['export']['weights_sha256'],
                wasm_sha256=parity['wasm_sha256'], validation_accuracy=training['validation']['exact_candidate_accuracy'],
                constant_wait_accuracy=training['validation']['constant_wait_accuracy'],
                untrained_accuracy=training['untrained_validation']['exact_candidate_accuracy'],
                macro_action_recall=training['validation']['macro_action_recall'],
                exact_accuracy_beats_untrained=training['validation']['exact_candidate_accuracy']>training['untrained_validation']['exact_candidate_accuracy'],
                parity_observations=sum(m['observations'] for m in parity['maps']),
                release_games=len(release_result['games']), confirmation_games=0, promoted=False,
                acceptance='training/export/runtime milestone only; not a strength or promotion gate', sources=current))
