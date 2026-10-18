"""Turn one cambc match summary (`cambc run --statistics X --json`) into a small game record.

The engine's summary already holds everything Carson's stats wrapper collected by hand:
per-champion timelines (gems banked, deaths, gold...) and per-champion events (camp clears,
item buys, wards, fuel exhaustion, faults). We keep both teams, so every game can be
diagnosed from either side.
"""
from __future__ import annotations

from collections import Counter

TEAMS = ("teamA", "teamB")
VERSION = 2  # bump when the record format or its meaning changes: stored games are then replayed
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


def summarize(stats: dict) -> dict:
    """Compact record of one game: outcome, final numbers, snapshots and strategy coverage per team."""
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
            "faults": int(stats["diagnostics"]["botFaults"].get(team, 0)),
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
        "outcome": match["outcome"],  # "teamA" | "teamB" | anything else = draw
        "rounds": rounds,
        "snap_rounds": snap_rounds,
        "teams": teams,
    }
