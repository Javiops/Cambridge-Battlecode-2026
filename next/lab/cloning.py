"""Stage 3: NumPy behavioural cloning of the certified 305-float candidate actor.

Only features/candidates/mask enter the actor. Win, seat, input index, and replay
metadata never enter training. Validation is loaded only after checkpoint selection
and the final refit. No dependency on the legacy project or a GPU framework.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import sys
import time

import numpy as np

from . import core, dataset, policy

KINDS = ("wait", "move", "attack", "cast")
N = policy.G * policy.H + policy.C * policy.H + 2 * policy.H + 1


def unpack(w):
    g = policy.G * policy.H
    c = g + policy.C * policy.H
    return w[:g].reshape(policy.G, policy.H), w[g:c].reshape(policy.C, policy.H), w[c:c+policy.H], w[c+policy.H:-1], w[-1]


def forward(w, x, c, exact=False):
    wg, wc, b, out, bo = unpack(w)
    if exact:
        # Same operation order as the deployed SIMD, including four output lanes.
        context = np.broadcast_to(b, (len(x), policy.H)).copy()
        for j in range(policy.G):
            context += x[:, j, None] * wg[j]
        z = np.broadcast_to(context[:, None, :], (len(x), policy.K, policy.H)).copy()
        for j in range(policy.C):
            z += c[:, :, j, None] * wc[j]
        h = np.maximum(z, 0)
        lanes = np.zeros((len(x), policy.K, 4), np.float32)
        for j in range(0, policy.H, 4):
            lanes += h[:, :, j:j+4] * out[j:j+4]
        scores = ((lanes[:, :, 0] + lanes[:, :, 1]) + lanes[:, :, 2]) + lanes[:, :, 3] + bo
    else:
        z = (x @ wg + b)[:, None, :] + c @ wc
        h = np.maximum(z, 0)
        scores = h @ out + bo
    return scores, z, h


def labels_kind(data):
    return np.argmax(data['candidates'][np.arange(len(data['label'])), data['label'], :4], axis=1)


def check(data):
    n = len(data['label'])
    if data['features'].shape != (n, policy.G) or data['candidates'].shape != (n, policy.K, policy.C) or data['mask'].shape != (n, policy.K):
        raise ValueError('Invalid actor tensor shape')
    if data['label'].dtype.kind not in 'iu' or np.any(data['label'] < 0) or np.any(data['label'] >= policy.K):
        raise ValueError('Invalid teacher index')
    if not np.isfinite(data['features']).all() or not np.isfinite(data['candidates']).all():
        raise ValueError('Nonfinite actor tensor')
    if not data['mask'][np.arange(n), data['label']].all():
        raise ValueError('Teacher index is masked')
    if data['features'].dtype != np.float32 or data['candidates'].dtype != np.float32 or data['mask'].dtype != bool:
        raise ValueError('Actor tensors must use the certified float32/bool types')


def load(split):
    arrays = {k: [] for k in ('features', 'candidates', 'mask', 'label')}
    maps = []
    episodes = []
    for episode, path in dataset.shards(split):  # Admitted only, with SHA verification.
        with np.load(path, allow_pickle=False) as shard:
            data = {k: shard[k] for k in arrays}
        check(data)
        for k in arrays:
            arrays[k].append(data[k])
        maps.extend([episode['map']] * len(data['label']))
        episodes.append(dict(id=episode['episode_id'], map=episode['map'], rows=len(data['label']), sha256=core.sha(path)))
    if not episodes:
        raise ValueError('No admitted data')
    return {k: np.concatenate(v) for k, v in arrays.items()}, np.asarray(maps), episodes


def subset(data, index):
    return {k: v[index] for k, v in data.items()}


def class_weights(data, maximum):
    count = np.bincount(labels_kind(data), minlength=4)
    weights = np.minimum(np.sqrt(len(data['label']) / (4 * np.maximum(count, 1))), maximum)
    weights /= np.mean(weights[labels_kind(data)])
    return weights.astype(np.float32), count


def loss_gradient(w, data, weights):
    """Masked, action-class-weighted candidate cross entropy and its analytic gradient."""
    x, c, mask, label = (data[k] for k in ('features', 'candidates', 'mask', 'label'))
    scores, z, h = forward(w, x, c)
    scores = np.where(mask, scores, -np.inf)
    shifted = scores - np.max(scores, axis=1, keepdims=True)
    p = np.exp(shifted)
    p /= p.sum(axis=1, keepdims=True)
    row_weights = weights[labels_kind(data)]
    loss = np.sum(row_weights * (-shifted[np.arange(len(x)), label] + np.log(np.exp(shifted).sum(axis=1)))) / row_weights.sum()
    p[np.arange(len(x)), label] -= 1
    p *= (row_weights / row_weights.sum())[:, None]
    _, _, _, out, _ = unpack(w)
    dz = p[:, :, None] * out * (z > 0)
    context_grad = dz.sum(axis=1)
    gradient = np.concatenate(((x.T @ context_grad).ravel(), np.einsum('bkc,bkh->ch', c, dz).ravel(),
                               context_grad.sum(axis=0), np.einsum('bk,bkh->h', p, h), np.zeros(1, w.dtype)))
    return float(loss), gradient


def predict(w, data):
    scores, _, _ = forward(w, data['features'], data['candidates'], exact=True)
    return np.argmax(np.where(data['mask'], scores, -np.inf), axis=1)


def metrics(w, data):
    pred = predict(w, data)
    truth = labels_kind(data)
    predicted = np.argmax(data['candidates'][np.arange(len(pred)), pred, :4], axis=1)
    matrix = np.zeros((4, 4), np.int64)
    np.add.at(matrix, (truth, predicted), 1)
    per_action = {}
    for k, name in enumerate(KINDS):
        support = int(np.sum(truth == k))
        called = int(np.sum(predicted == k))
        per_action[name] = dict(support=support, predicted=called,
            recall=float(matrix[k, k]/support) if support else None,
            precision=float(matrix[k, k]/called) if called else None,
            exact_candidate_accuracy=float(np.mean(pred[truth == k] == data['label'][truth == k])) if support else None)
    return dict(rows=len(pred), exact_candidate_accuracy=float(np.mean(pred == data['label'])),
                action_accuracy=float(np.mean(truth == predicted)),
                macro_action_recall=float(np.mean([p['recall'] for p in per_action.values() if p['recall'] is not None])),
                confusion_truth_rows_predicted_columns=matrix.tolist(), per_action=per_action,
                constant_wait_accuracy=float(np.mean(data['label'] == 0)))


def optimize(data, cfg, epochs, development=None):
    rng = np.random.default_rng(cfg['seed'])
    w = np.asarray(policy.weights(), np.float32)
    weights, counts = class_weights(data, cfg['max_class_weight'])
    m = np.zeros_like(w); v = np.zeros_like(w); step = 0
    history = []; best = (-np.inf, 0)
    for epoch in range(1, epochs+1):
        losses = []
        for indexes in np.array_split(rng.permutation(len(data['label'])), int(np.ceil(len(data['label'])/cfg['batch_size']))):
            loss, grad = loss_gradient(w, subset(data, indexes), weights)
            grad[:-1] += cfg['weight_decay'] * w[:-1]
            step += 1
            m = .9*m + .1*grad; v = .999*v + .001*grad*grad
            w -= cfg['learning_rate'] * (m/(1-.9**step)) / (np.sqrt(v/(1-.999**step)) + 1e-8)
            if not np.isfinite(w).all():
                raise ValueError('Training diverged')
            losses.append(loss)
        if epoch % cfg['evaluate_every'] == 0 or epoch == epochs:
            row = dict(epoch=epoch, mean_batch_weighted_cross_entropy=float(np.mean(losses)))
            if development is not None:
                score = metrics(w, development)
                row['development'] = score
                criterion = (score['exact_candidate_accuracy'] + score['macro_action_recall']) / 2
                if criterion > best[0]:
                    best = (criterion, epoch)
            history.append(row)
            print(json.dumps(dict(epoch=epoch, loss=row['mean_batch_weighted_cross_entropy'],
                                  development_accuracy=row.get('development', {}).get('exact_candidate_accuracy'))), flush=True)
    return w, dict(history=history, selected_epoch=best[1] if development is not None else epochs,
                   class_counts=counts.tolist(), class_weights=weights.tolist(), optimizer_steps=step)


def write_export(folder, w):
    w = np.asarray(w, '<f4')
    if w.shape != (N,) or not np.isfinite(w).all():
        raise ValueError('Invalid float32 model export')
    folder.mkdir(parents=True, exist_ok=True)
    (folder/'weights.f32').write_bytes(w.tobytes())
    # Hexadecimal C++ literals preserve every float32 bit without decimal ambiguity.
    header = '#pragma once\n#include <array>\nnamespace trained {\ninline constexpr std::array<float,305> weights = {\n'
    header += ',\n'.join(', '.join(float(value).hex()+'f' for value in w[i:i+8]) for i in range(0, N, 8))
    header += '\n};\n}\n'
    (folder/'weights.h').write_text(header, encoding='utf-8')
    (folder/'weights.json').write_text(json.dumps(w.tolist())+'\n', encoding='utf-8')
    return dict(parameters=N, dtype='little-endian float32', bytes=w.nbytes,
                weights_sha256=core.sha(folder/'weights.f32'), header_sha256=core.sha(folder/'weights.h'))


def train():
    cfg = core.config()['stage3']
    folder = core.ROOT/'models'/cfg['model']
    if folder.exists():
        raise ValueError('Model version exists; choose a new model name rather than overwrite it')
    # The Stage 2 certificate was checked before Stage 3 source/config edits. Recheck
    # manifest identity and validator identities without accepting a stale engine proof.
    audit = json.loads((core.ROOT/'results/stage2-audit.json').read_text())
    if not audit['passed'] or audit['manifest_sha256'] != core.sha(dataset.root()/'manifest.json'):
        raise ValueError('Dataset certificate changed')
    for source, digest in audit['validator_sources'].items():
        if hashlib.sha256((core.ROOT/source).read_text().encode()).hexdigest() != digest:
            raise ValueError('Dataset validator changed; audit again before training')
    data, maps, episodes = load('train')
    development_mask = np.isin(maps, cfg['development_maps'])
    if not development_mask.any() or development_mask.all() or set(cfg['development_maps']) - set(maps):
        raise ValueError('Development split must contain complete training maps')
    plan = dict(schema=1, config=cfg, dataset_manifest_sha256=audit['manifest_sha256'],
                selection='highest mean of exact candidate accuracy and macro action recall; earliest epoch wins ties',
                training_episodes=episodes, fit_rows=int((~development_mask).sum()), development_rows=int(development_mask.sum()),
                fit_maps=sorted(set(maps[~development_mask])), development_maps=sorted(set(maps[development_mask])),
                validation_access='after epoch selection and full-training refit only',
                actor_inputs=['features', 'candidates', 'mask'], privileged_inputs_used=False,
                runtime=dict(python=platform.python_version(), numpy=np.__version__, platform=sys.platform))
    folder.mkdir(parents=True)
    (folder/'plan.json').write_text(json.dumps(plan, indent=2)+'\n', encoding='utf-8')
    started = time.perf_counter()
    _, selection = optimize(subset(data, ~development_mask), cfg, cfg['epochs'], subset(data, development_mask))
    # Refit at the selected epoch; no validation-dependent model choice.
    w, refit = optimize(data, cfg, selection['selected_epoch'])
    export = write_export(folder, w)
    validation, _, validation_episodes = load('validation')
    train_score = metrics(w, data); score = metrics(w, validation)
    baseline = metrics(np.asarray(policy.weights(), np.float32), validation)
    passed = (score['exact_candidate_accuracy'] > max(score['constant_wait_accuracy'], cfg['minimum_validation_accuracy'])
              and score['macro_action_recall'] >= cfg['minimum_macro_action_recall'])
    result = dict(schema=1, model=cfg['model'], training_complete=True, offline_acceptance_passed=bool(passed),
                  elapsed_seconds=time.perf_counter()-started, plan_sha256=core.sha(folder/'plan.json'),
                  dataset_manifest_sha256=audit['manifest_sha256'], export=export, selection=selection, refit=refit,
                  train=train_score, validation=score, untrained_validation=baseline, validation_episodes=validation_episodes,
                  validation_model_selections=0, confirmation_games=0, promoted=False,
                  limitations=['No supported cast labels in validation; cast generalization unmeasured',
                               'Willow and Heart absent from both dataset partitions',
                               'Only supported local proposals are cloned; no macro planner or full spell policy'])
    (folder/'training.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    (core.ROOT/'results/stage3-training.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return {k: result[k] for k in ('model', 'offline_acceptance_passed', 'elapsed_seconds', 'export', 'train', 'validation')}


if __name__ == '__main__':
    print(json.dumps(train(), indent=2))
