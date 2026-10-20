import numpy as np
import pytest
import zipfile

from lab import cloning, policy, stage3


def sample(dtype=np.float32):
    rng = np.random.default_rng(42)
    x = rng.normal(size=(3, policy.G)).astype(dtype)
    c = rng.normal(size=(3, policy.K, policy.C)).astype(dtype)
    c[:, :, :4] = 0
    for k in range(policy.K):
        c[:, k, k % 4] = 1
    mask = np.ones((3, policy.K), bool); mask[:, 7:] = False
    return dict(features=x, candidates=c, mask=mask, label=np.array([0, 2, 5]))


def test_analytic_gradient_matches_finite_differences():
    w = np.array(policy.weights(), np.float64)
    data = sample(np.float64)
    weights = np.array([.5, 1., 2., 3.])
    _, grad = cloning.loss_gradient(w, data, weights)
    for j in (0, 4, 71, 191, 192, 235, 287, 289, 299, 303, 304):
        delta = np.zeros_like(w); delta[j] = 1e-6
        plus = cloning.loss_gradient(w+delta, data, weights)[0]
        minus = cloning.loss_gradient(w-delta, data, weights)[0]
        assert grad[j] == pytest.approx((plus-minus)/2e-6, abs=2e-8)


def test_padding_has_no_loss_or_gradient_effect():
    w = np.array(policy.weights(), np.float32)
    data = sample(); altered = {k: v.copy() for k, v in data.items()}
    altered['candidates'][:, 7:] *= 100
    a, ga = cloning.loss_gradient(w, data, np.ones(4, np.float32))
    b, gb = cloning.loss_gradient(w, altered, np.ones(4, np.float32))
    assert a == b
    np.testing.assert_array_equal(ga, gb)
    assert (cloning.predict(w, altered) < 7).all()


def test_exact_batch_forward_matches_scalar_deployment_reference():
    data = sample(); w = np.array(policy.weights(), np.float32)
    scores = cloning.forward(w, data['features'], data['candidates'], exact=True)[0]
    for i in range(3):
        encoded = {k: data[k][i].tolist() for k in ('features', 'candidates', 'mask')}
        expected, pick = policy.infer(encoded, w.tolist())
        np.testing.assert_array_equal(scores[i], expected)
        assert cloning.predict(w, {k: v[i:i+1] for k, v in data.items()})[0] == pick


def test_export_preserves_float32_layout_and_rejects_bad_weights(tmp_path):
    w = np.array(policy.weights(), np.float32)
    result = cloning.write_export(tmp_path, w)
    np.testing.assert_array_equal(np.fromfile(tmp_path/'weights.f32', dtype='<f4'), w)
    assert result['parameters'] == 305 and result['bytes'] == 1220
    assert float(w[0]).hex()+'f' in (tmp_path/'weights.h').read_text()
    w[0] = np.nan
    with pytest.raises(ValueError, match='Invalid'):
        cloning.write_export(tmp_path, w)


def test_reject_masked_teacher_and_nonfinite_observation():
    data = sample(); data['label'][0] = 9
    with pytest.raises(ValueError, match='masked'):
        cloning.check(data)
    data = sample(); data['features'][0, 0] = np.inf
    with pytest.raises(ValueError, match='Nonfinite'):
        cloning.check(data)


def test_release_judge_rejects_missing_or_failed_games():
    expected = {('model', 'control', 'screen')}
    good = dict(name_a='model', name_b='control', map='screen', outcome='teamA',
                teams={t: dict(faults=0, fuel_exhausted=0) for t in ('teamA', 'teamB')})
    stage3.check_games([good], expected)
    with pytest.raises(ValueError, match='incomplete'):
        stage3.check_games([], expected)
    with pytest.raises(ValueError, match='duplicated'):
        stage3.check_games([good, good], expected)
    with pytest.raises(ValueError, match='Incomplete'):
        stage3.check_games([{**good, 'outcome':None}], expected)
    good['teams']['teamA']['fuel_exhausted'] = 1
    with pytest.raises(ValueError, match='fuel'):
        stage3.check_games([good], expected)


def test_training_config_changes_cannot_relabel_an_existing_model():
    cfg = dict(model='bc', seed=1, epochs=5, batch_size=32, evaluate_every=1,
               learning_rate=.01, weight_decay=.001, max_class_weight=6., development_maps=['map'])
    stage3.require_training_config({'config':cfg}, cfg)
    with pytest.raises(ValueError, match='settings changed'):
        stage3.require_training_config({'config':cfg}, {**cfg, 'seed':2})


def test_loader_excludes_outcomes_seats_and_future_metadata(tmp_path, monkeypatch):
    data = sample()
    path = tmp_path/'bc.npz'
    np.savez(path, **data, win=np.ones(3), team=np.ones(3), future_secret=np.ones(3))
    monkeypatch.setattr(cloning.dataset, 'shards', lambda _: iter([({'episode_id':'e', 'map':'m'}, path)]))
    loaded, maps, _ = cloning.load('train')
    assert set(loaded) == {'features', 'candidates', 'mask', 'label'}
    assert maps.tolist() == ['m']*3


def test_bundle_verification_preserves_existing_identical_source_zip(tmp_path):
    old, fresh = tmp_path/'old.zip', tmp_path/'fresh.zip'
    for path in (old, fresh):
        with zipfile.ZipFile(path, 'w') as z:
            z.writestr('src/main.cpp', 'int main() {}')
    original = old.read_bytes()
    stage3.preserve_bundle(old, fresh)
    assert old.read_bytes() == original
    with zipfile.ZipFile(fresh, 'w') as z:
        z.writestr('src/main.cpp', 'different code')
    with pytest.raises(ValueError, match='bundle sources differ'):
        stage3.preserve_bundle(old, fresh)
    assert old.read_bytes() == original
    stage3.preserve_bundle(tmp_path/'new.zip', fresh)
    assert (tmp_path/'new.zip').read_bytes() == fresh.read_bytes()
