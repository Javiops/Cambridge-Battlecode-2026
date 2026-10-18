"""Tests for the lab's own numbers. If the judge is wrong, every decision built on it is wrong.

Run from next/:  python3 -m pytest -q tests
"""
import gzip
import json
import random
from pathlib import Path

from lab import rating, stats
from lab.core import score_a

FIX = Path(__file__).parent / "fixtures" / "collision_stats.json.gz"


def load_fixture():
    return json.loads(gzip.open(FIX, "rt").read())


# ------------------------------------------------------------- stats

def test_timeline_value_expands_runs():
    runs = [{"duration": 3, "value": "0"}, {"duration": 2, "value": "5"}, {"duration": 1, "value": "9"}]
    assert [stats.timeline_value(runs, i) for i in range(8)] == [0, 0, 0, 5, 5, 9, 9, 9]


def test_summary_matches_engine_totals():
    # starter vs starter on collision (cambc 2.2.5): A banked 1012, B 550; A: 18 deaths, 14 kills.
    s = stats.summarize(load_fixture())
    a, b = s["teams"]["teamA"], s["teams"]["teamB"]
    assert s["outcome"] == "teamA" and s["rounds"] == 1237
    assert (a["gems"], b["gems"]) == (1012, 550)
    assert (a["deaths"], a["kills"]) == (18, 14)
    # the last snapshot is the final round and agrees with the final totals
    assert s["snap_rounds"][-1] == 1237
    assert a["snap_gems"][-1] == a["gems"] and b["snap_gems"][-1] == b["gems"]
    assert a["snap_deaths"][-1] == a["deaths"]
    # banked gems and deaths never go down
    for t in (a, b):
        assert t["snap_gems"] == sorted(t["snap_gems"]) and t["snap_deaths"] == sorted(t["snap_deaths"])
    assert len(a["draft"]) == 3 and a["camp_clears"] > 0


def test_score_a():
    assert score_a({"outcome": "teamA"}) == 1.0
    assert score_a({"outcome": "teamB"}) == 0.0
    assert score_a({"outcome": "draw"}) == 0.5
    assert score_a({"error": "crash"}) is None


# ------------------------------------------------------------- rating

def simulate(true: dict, per_pair: int, seed: int = 7):
    rng = random.Random(seed)
    games = []
    names = sorted(true)
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            p = rating.expected_score(true[x], true[y])
            games += [(x, y, 1.0 if rng.random() < p else 0.0) for _ in range(per_pair)]
    return games


def test_fit_recovers_known_ratings():
    true = {"a": 1700, "b": 1600, "c": 1500, "d": 1300}
    r = rating.fit(simulate(true, 2000), prior=0.0)
    assert sorted(r, key=r.get, reverse=True) == ["a", "b", "c", "d"]
    mean_true = sum(true.values()) / len(true)
    for k in true:
        assert abs((r[k] - 1500) - (true[k] - mean_true)) < 25


def test_fit_is_symmetric_and_handles_draws():
    r = rating.fit([("x", "y", 0.5)] * 10)
    assert abs(r["x"] - r["y"]) < 1e-6
    r = rating.fit([("x", "y", 1.0)] * 3 + [("y", "x", 0.0)] * 3)  # same result written both ways
    assert r["x"] > r["y"]


def test_fit_stays_finite_with_perfect_separation():
    r = rating.fit([("x", "y", 1.0)] * 20)
    assert 1500 < r["x"] < 2500 and 500 < r["y"] < 1500


def test_bootstrap_interval_contains_point():
    true = {"a": 1600, "b": 1500, "c": 1400}
    games = simulate(true, 60)
    by_map = {f"m{i}": games[i::10] for i in range(10)}
    out = rating.bootstrap(by_map, samples=50)
    for k, (r, lo, hi) in out.items():
        assert lo <= r <= hi
