"""Regressions for the October 20 runtime migration and promotion judge."""
import gzip
import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from lab import core, gate, probe, runtime, stats


def capture():
    return {"match": {"outcome": "teamA", "roundsStarted": 20, "engineBuildHash": "a" * 64},
            "diagnostics": {"detailedCaptureComplete": True, "botFaults": {"teamA": 0, "teamB": 0}}}


@pytest.mark.parametrize("outcome", [None, "unknown", "draw", "inProgress", ""])
def test_unfinished_capture_is_not_a_result(outcome):
    data = capture()
    data["match"]["outcome"] = outcome
    with pytest.raises(ValueError, match="outcome"):
        stats.validate(data)


@pytest.mark.parametrize("change", [
    {"detailedCaptureComplete": False}, {"botFaults": {}},
    {"botFaults": {"teamA": -1, "teamB": 0}},
])
def test_missing_safety_statistics_fail_closed(change):
    data = capture()
    data["diagnostics"].update(change)
    with pytest.raises(ValueError):
        stats.validate(data)


def test_unknown_score_is_not_draw():
    assert core.score_a({}) is None
    assert core.score_a({"outcome": "inProgress"}) is None


def bot(name="a"):
    return core.Version(name, Path(f"{name}.wasm"), {"wasm_sha256": name})


def test_nonzero_process_rejects_even_valid_stats(tmp_path, monkeypatch):
    def run(*args, **kwargs):
        (tmp_path / "stats.json").write_text(json.dumps(capture()))
        return subprocess.CompletedProcess(args[0], 1, "", "engine failed")
    monkeypatch.setattr(core.subprocess, "run", run)
    result, error = core.run_game(bot(), bot("b"), Path("m.map26a"), str(tmp_path))
    assert result is None and "exit code 1" in error


def test_success_without_new_stats_cannot_reuse_old_watch_file(tmp_path, monkeypatch):
    (tmp_path / "stats.json").write_text(json.dumps(capture()))
    monkeypatch.setattr(core.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a[0], 0, "", ""))
    result, error = core.run_game(bot(), bot("b"), Path("m.map26a"), str(tmp_path))
    assert result is None and error


@pytest.mark.parametrize("data", [[], {"match": None}, {"diagnostics": None}])
def test_malformed_statistics_are_reported_as_failure(tmp_path, monkeypatch, data):
    def run(*args, **kwargs):
        (tmp_path / "stats.json").write_text(json.dumps(data))
        return subprocess.CompletedProcess(args[0], 0, "", "")
    monkeypatch.setattr(core.subprocess, "run", run)
    result, error = core.run_game(bot(), bot("b"), Path("m.map26a"), str(tmp_path))
    assert result is None and "invalid match statistics" in error


def test_actual_engine_hash_must_match_pin(tmp_path, monkeypatch):
    def run(*args, **kwargs):
        (tmp_path / "stats.json").write_text(json.dumps(capture()))
        return subprocess.CompletedProcess(args[0], 0, "", "")
    monkeypatch.setattr(core.subprocess, "run", run)
    result, error = core.run_game(bot(), bot("b"), Path("m.map26a"), str(tmp_path),
                                  profile={"engine_build_hash": "b" * 64})
    assert result is None and "engine build" in error


def test_patch_changes_invalidate_game_cache(tmp_path):
    mp = tmp_path / "m.map26a"
    mp.write_bytes(b"same map")
    assert core.game_key(bot(), bot("b"), mp, "cambc 3.0.1", {"engine": "old"}) != \
           core.game_key(bot(), bot("b"), mp, "cambc 3.0.1", {"engine": "new"})


def test_old_frozen_versions_are_preserved_and_rejected():
    with pytest.raises(SystemExit, match="new name"):
        runtime.require_compatible({"name": "starter-v1"}, {"cli": "cambc 3.0.1"})


def test_runtime_rejects_old_sdk(tmp_path, monkeypatch):
    (tmp_path / "cambc.toml").write_text('sdk_version = "2.2.5"\n')
    monkeypatch.setattr(runtime, "cli_version", lambda *args: "cambc 3.0.1")
    with pytest.raises(SystemExit, match="SDK"):
        runtime.identity(tmp_path, "cambc", {}, {"runtime": {"cli_version": "cambc 3.0.1"}})


def test_sdk_fingerprint_order_is_portable_between_windows_and_linux(tmp_path):
    (tmp_path / "a.h").write_bytes(b"lower")
    (tmp_path / "B.h").write_bytes(b"upper")
    canonical = [["B.h", hashlib.sha256(b"upper").hexdigest()],
                 ["a.h", hashlib.sha256(b"lower").hexdigest()]]
    expected = hashlib.sha256(json.dumps(canonical, separators=(",", ":")).encode()).hexdigest()
    assert runtime.tree_sha(tmp_path) == expected


def cfg():
    return {"maps": {"screen": ["screen"], "confirm": ["sealed"]},
            "league": {"champion": "reference"},
            "gate": {"weak": "reference", "vs_champion": .5, "vs_weak": .9,
                     "max_faults": 0, "max_fuel_exhausted_per_game": 1}}


def pair_games(failed=False):
    teams = {t: {"faults": 0, "fuel_exhausted": 0} for t in stats.TEAMS}
    return [{"map": "sealed", "name_a": a, "name_b": b,
             **({"error": "failed"} if failed else {"outcome": winner, "teams": teams})}
            for a, b, winner in [("candidate", "reference", "teamA"),
                                 ("reference", "candidate", "teamB")]]


def test_gate_all_games_failed_is_fail_not_exception(monkeypatch):
    monkeypatch.setattr(core, "play", lambda *a, **k: pair_games(True))
    passed, lines = gate.run("candidate", cfg(), 1)
    assert not passed and "n/a" in "\n".join(lines)


def test_gate_requires_every_map_in_both_seats(monkeypatch):
    monkeypatch.setattr(core, "play", lambda *a, **k: pair_games()[:1])
    passed, lines = gate.run("candidate", cfg(), 1)
    assert not passed and "incomplete paired schedule" in "\n".join(lines)


@pytest.mark.parametrize("maps", [[], ["sealed", "sealed"], ["screen"]])
def test_gate_rejects_empty_duplicate_or_leaked_holdout(maps, monkeypatch):
    config = cfg()
    config["maps"]["confirm"] = maps
    monkeypatch.setattr(core, "play", lambda *a, **k: pytest.fail("invalid gate must not play"))
    assert gate.run("candidate", config, 1)[0] is False


def test_gate_full_paired_wins_can_pass(monkeypatch):
    monkeypatch.setattr(core, "play", lambda *a, **k: pair_games())
    assert gate.run("candidate", cfg(), 1)[0] is True


def test_gate_cannot_promote_without_opponent(monkeypatch):
    monkeypatch.setattr(core, "play", lambda *a, **k: pytest.fail("self comparison"))
    assert gate.run("reference", cfg(), 1)[0] is False


def test_probe_rejects_empty_log():
    with pytest.raises(ValueError):
        probe.parse("")


def test_current_engine_summary_matches_completed_release_game():
    fixture = Path(__file__).parent / "fixtures" / "week2_collision_stats.json.gz"
    with gzip.open(fixture, "rt", encoding="utf-8") as source:
        data = json.load(source)
    result = stats.summarize(data)
    assert result["outcome"] == "teamB" and result["rounds"] == 2000
    assert result["engine_build_hash"] == "2b36d9c61b2710d06036680d07fc4b7a8319ba35f634e4f1445725e0d99a1e16"
    assert [result["teams"][t]["gems"] for t in stats.TEAMS] == [300, 762]
    assert [result["teams"][t]["faults"] for t in stats.TEAMS] == [0, 0]
    assert result["teams"]["teamA"]["snap_gems"][-1] == 300


def probe_log():
    return (Path(__file__).parent / "fixtures" / "week2_probe.stdout").read_text(encoding="utf-8").replace("\x00", "")


def test_real_probe_covers_patch_designs_and_values():
    facts = probe.parse(probe_log())
    assert facts["constants"]["ward_cooldown"] == 10
    assert facts["constants"]["altar_lock_hits"] == 5
    assert facts["constants"]["kill_gold"] == 100
    assert facts["constants"]["prism_focus_per_gem"] == 1
    assert facts["constants"]["vesper_vale_bonus_gold_percent"] == 33
    assert facts["constants"]["marcella_tribute_gold_per_gem"] == 2
    assert facts["champions"]["tavi"]["strength"] == 45
    assert next(r for r in facts["cc"] if r["champion"] == "tavi")["modifier"] == pytest.approx(1.4)
    assert facts["camps"]["wolf"]["hp"] == 1350
    assert facts["camps"]["golem"] == {"hp": 5000, "strength": 120, "range": 4}
    heart = next(r for r in facts["dash"] if r["champion"] == "heart_of_ruin")
    assert heart == {"champion": "heart_of_ruin", "slot": 1, "range": 2, "radius": 1,
                     "modifier": 1.75, "duration": 1}


@pytest.mark.parametrize("prefix", ["CHAMP heart_of_ruin", "CAMP golem", "DASH heart_of_ruin"])
def test_probe_rejects_missing_new_designs(prefix):
    log = "\n".join(line for line in probe_log().splitlines() if not line.startswith(prefix))
    with pytest.raises(ValueError):
        probe.parse(log)


def test_repeated_opponent_does_not_double_count_faults(monkeypatch):
    config = cfg()
    config["gate"]["max_faults"] = 1
    games = pair_games()
    games[0]["teams"] = {"teamA": {"faults": 1, "fuel_exhausted": 0},
                         "teamB": {"faults": 0, "fuel_exhausted": 0}}
    monkeypatch.setattr(core, "play", lambda *a, **k: games)
    assert gate.run("candidate", config, 1)[0] is True
