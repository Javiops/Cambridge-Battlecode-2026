"""The promotion gate: may a candidate replace the champion?

After Carson's kaggriculture finalist gates: freeze the candidate, then play it on maps it was
never tuned on. It must score at least 50% against the current best and at least 90% against
the weak bot, with no crashes. The seat split is always reported next to the verdict.
"""
from __future__ import annotations

from statistics import mean

from . import core


def _scores(games: list[dict], cand: str):
    out = []
    for g in games:
        s = core.score_a(g)
        if s is None:
            out.append((g, None, None))
        elif g["name_a"] == cand:
            out.append((g, s, g["teams"]["teamA"]))
        else:
            out.append((g, 1.0 - s, g["teams"]["teamB"]))
    return out


def run(cand: str, cfg: dict, jobs: int) -> tuple[bool, list[str]]:
    gate = cfg["gate"]
    champ, weak = cfg["league"]["champion"], gate["weak"]
    maps = cfg["maps"]["confirm"]
    lines = [f"# Gate: `{cand}`", "", f"Confirm maps ({len(maps)}): {', '.join(maps)}. Both sides.", ""]
    checks = []
    all_recs = []
    for opp, need in ((champ, gate["vs_champion"]), (weak, gate["vs_weak"])):
        if opp == cand:
            continue
        games = core.play([(cand, opp)], maps, jobs, progress=lambda *_: None)
        recs = _scores(games, cand)
        all_recs += recs
        done = [r for r in recs if r[1] is not None]
        sc = mean(r[1] for r in done) if done else 0.0
        a = [r[1] for r in done if r[0]["name_a"] == cand]
        b = [r[1] for r in done if r[0]["name_b"] == cand]
        checks.append((f"score vs `{opp}` ≥ {need:.0%}", sc >= need and len(done) == len(recs),
                       f"{sc:.0%} over {len(done)} games (side A {mean(a):.0%}, side B {mean(b):.0%})"
                       + (f", {len(recs) - len(done)} unfinished" if len(done) < len(recs) else "")))
        lines += [f"## vs `{opp}`", "", "| map | as A | as B |", "|---|---|---|"]
        for m in maps:
            cell = lambda side: next((("win" if r[1] == 1 else "loss" if r[1] == 0 else "draw") if r[1] is not None else "CRASH"
                                      for r in recs if r[0]["map"] == m and r[0][f"name_{side}"] == cand), "")
            lines.append(f"| {m} | {cell('a')} | {cell('b')} |")
        lines.append("")
    faults = sum(r[2]["faults"] for r in all_recs if r[2])
    fuel = mean(r[2]["fuel_exhausted"] for r in all_recs if r[2]) if any(r[2] for r in all_recs) else 0
    checks.append((f"bot faults ≤ {gate['max_faults']}", faults <= gate["max_faults"], str(faults)))
    checks.append((f"fuel-lost turns per game ≤ {gate['max_fuel_exhausted_per_game']}",
                   fuel <= gate["max_fuel_exhausted_per_game"], f"{fuel:.2f}"))
    passed = all(c[1] for c in checks)
    head = [f"**Verdict: {'PASS' if passed else 'FAIL'}**", "", "| check | result | value |", "|---|---|---|"]
    head += [f"| {c[0]} | {'pass' if c[1] else 'FAIL'} | {c[2]} |" for c in checks]
    return passed, lines[:4] + head + [""] + lines[4:]
