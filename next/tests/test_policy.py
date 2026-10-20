import copy
import math

import pytest

from lab import policy


def sample():
    return {"actor": {"team": 0, "round": 7, "champion": 0}, "width": 30, "height": 30,
            "self": {"x": 2, "y": 2, "health": 1200, "max_health": 1200, "strength": 45,
                     "focus": 100, "gems": 0, "gold": 0, "type": 0, "state": 2073,
                     "move_speed": 1, "attack_range": 1},
            "banks": [0, 0], "vision": [[2, 2]], "moves": [[3, 2], [2, 3]],
            "champions": [], "camps": [], "abilities": []}


def test_encoder_ignores_privileged_fields():
    obs = sample()
    terrain = {"altars": [[14, 14], [15, 15]]}
    expected = policy.encode(obs, terrain)
    obs["hidden_enemy"] = {"health": 1, "gold": 9999}
    obs["critic_state"] = {"all_units": [1, 2, 3]}
    assert policy.encode(obs, terrain) == expected


def test_wait_is_always_available_and_padding_is_masked():
    encoded = policy.encode(sample(), {"altars": [[14, 14]]})
    assert len(encoded["features"]) == 24 and len(encoded["candidates"]) == 16
    assert encoded["mask"] == [True, True, True] + [False] * 13
    assert encoded["candidates"][0][0] == 1
    assert encoded["actions"][:3] == [{"kind":"wait"},{"kind":"move","x":3,"y":2},{"kind":"move","x":2,"y":3}]
    assert encoded["actions"][3:] == [None]*13


def test_dead_actor_cannot_receive_move_or_attack_candidates():
    obs = sample()
    obs["self"]["state"] = 0
    result = policy.encode(obs, {"altars": [[14, 14]]})
    assert sum(result["mask"]) == 1


def test_model_is_finite_deterministic_and_never_selects_padding():
    encoded = policy.encode(sample(), {"altars": [[14, 14]]})
    scores, chosen = policy.infer(encoded)
    assert all(math.isfinite(x) for x in scores)
    assert encoded["mask"][chosen]
    assert (scores, chosen) == policy.infer(encoded)


def test_model_rejects_nonfinite_inputs():
    encoded = policy.encode(sample(), {"altars": [[14, 14]]})
    encoded["features"][0] = float("nan")
    with pytest.raises(ValueError, match="finite"):
        policy.infer(encoded)


def test_attack_reset_candidate_requires_an_already_used_attack():
    obs = sample()
    obs["self"]["state"] |= 2048
    obs["abilities"] = [{"slot":1,"kind":1,"cooldown":0,"targets":8}]
    terrain = {"altars":[[14,14]]}
    assert not any(row[3] for row in policy.encode(obs,terrain)["candidates"])
    obs["self"]["state"] &= ~16
    assert sum(row[3] for row in policy.encode(obs,terrain)["candidates"]) == 1
