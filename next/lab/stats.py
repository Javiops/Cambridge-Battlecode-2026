"""Turn one cambc match summary (`cambc run --statistics X --json`) into a small game record.

The engine's summary already holds everything Carson's stats wrapper collected by hand:
per-champion timelines (gems banked, deaths, gold...) and per-champion events (camp clears,
item buys, wards, fuel exhaustion, faults). We keep both teams, so every game can be
diagnosed from either side.
"""
from __future__ import annotations

from collections import Counter

TEAMS = ("teamA", "teamB")
VERSION = 3  # incomplete captures and unknown outcomes are not completed games
SNAPSHOT_EVERY = 100  # rounds between snapshots, as in Carson's stats wrapper


def timeline_value(runs: list[dict], index: int) -> float:
    """Value of a run-length encoded timeline at sample `index` (sample i ~ round i)."""
    pos = 0
    value = 0.0
    for run in runs:
        value = float(run["value"])
        pos += run["duration"]
        if index < pos:
            return value
    return value  # past the end: the final value holds


def _team_sum(timelines: list[dict], metric: str, team: str, index: int) -> float:
    return sum(timeline_value(t["runs"], index) for t in timelines
               if t["metric"] == metric and t["owner"]["team"] == team)


def validate(stats: dict) -> None:
    """Reject unfinished games and statistics that cannot support the safety gate."""
    if not isinstance(stats, dict):
        raise ValueError("Match statistics must be an object")
    match = stats.get("match")
    if not isinstance(match, dict) or match.get("outcome") not in TEAMS:
        raise ValueError("Match has no completed teamA/teamB outcome")
    diagnostics = stats.get("diagnostics")
    if not isinstance(diagnostics, dict) or diagnostics.get("detailedCaptureComplete") is not True:
        raise ValueError("Detailed statistics capture is incomplete; fuel/fault counts are unreliable")
    faults = diagnostics.get("botFaults")
    if not isinstance(faults, dict) or any(type(faults.get(t)) is not int or faults[t] < 0 for t in TEAMS):
        raise ValueError("Missing or invalid team bot fault counters")


def summarize(stats: dict) -> dict:
    """Compact record of one game: outcome, final numbers, snapshots and strategy coverage per team."""
    validate(stats)
    match = stats["match"]
    # The last round can be partial: the winning submission lands in round roundsStarted.
    rounds = int(match["roundsStarted"])
    timelines = stats["championTimelines"]
    snap_rounds = list(range(SNAPSHOT_EVERY, rounds, SNAPSHOT_EVERY)) + [rounds]

    teams: dict[str, dict] = {}
    for team in TEAMS:
        champs = [c for c in stats["champions"] if c["team"] == team]
        metric = lambda name: sum(float(c["metrics"][name]) for c in champs)  # noqa: E731
        events = Counter()
        camps_cleared = Counter()
        items = Counter()
        for ev in stats["events"]:
            if ev["owner"].get("team") != team:
                continue
            events[ev["kind"]] += len(ev["entries"])
            if ev["kind"] == "campClear":
                for e in ev["entries"]:
                    camps_cleared[str(e["target"].get("id"))] += 1
            if ev["kind"] == "buyItem":
                for e in ev["entries"]:
                    items[e["target"].get("name", "?")] += int(float(e["value"]))
        teams[team] = {
            "gems": int(next(t["submittedGems"] for t in stats["teams"] if t["team"] == team)),
            "kills": int(metric("kills")),
            "deaths": int(metric("deaths")),
            "gold": int(metric("earnedGold")),
            "monster_damage": round(metric("monsterDamageDone")),
            "champion_damage": round(metric("championDamageDone")),
            "faults": stats["diagnostics"]["botFaults"][team],
            "fuel_exhausted": events["fuelExhausted"],
            "camp_clears": events["campClear"],
            "distinct_camps": len(camps_cleared),
            "wards": events["wardPlacement"],
            "draft": [c["name"] for c in sorted(champs, key=lambda c: c["id"])],
            "items": dict(items.most_common(6)),
            # Snapshots: banked gems and deaths so far, every SNAPSHOT_EVERY rounds.
            # Sample i is the state after round i; the final snapshot reads the end of the timeline.
            "snap_gems": [int(_team_sum(timelines, "submittedGems", team, r if r < rounds else 10**9))
                          for r in snap_rounds],
            "snap_deaths": [int(_team_sum(timelines, "deaths", team, r if r < rounds else 10**9))
                            for r in snap_rounds],
        }
    return {
        "outcome": match["outcome"],
        "engine_build_hash": match.get("engineBuildHash"),
        "engine_version": match.get("engineVersion"),
        "map_hash": match.get("mapHash"),
        "seed": match.get("seed"),
        "rounds": rounds,
        "snap_rounds": snap_rounds,
        "teams": teams,
    }
