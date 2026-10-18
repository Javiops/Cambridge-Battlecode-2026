"""REPORT.md: the leaderboard, the win matrix, and how each version plays.

Carson's agents read a report like this before proposing a change (cb-bc ABLATION_PROMPT.md):
first find *why* the best bot loses a matchup from the stats, then design one change.
"""
from __future__ import annotations

import json
import time
from collections import Counter, defaultdict
from statistics import mean

from . import core, rating


def _side_records(games: list[dict]):
    """Yield (version, opponent, side, score, own team stats, opp team stats, game) for both sides."""
    for g in games:
        s = core.score_a(g)
        if s is None:
            continue
        ta, tb = g["teams"]["teamA"], g["teams"]["teamB"]
        yield g["name_a"], g["name_b"], "A", s, ta, tb, g
        yield g["name_b"], g["name_a"], "B", 1.0 - s, tb, ta, g


def round_reaching(snap_rounds: list[int], snap_gems: list[int], target: int = 1000):
    for r, gm in zip(snap_rounds, snap_gems):
        if gm >= target:
            return r
    return None


def build(games: list[dict], title: str, cfg: dict, history: list[dict] | None = None) -> tuple[str, dict]:
    panel_version, champion = cfg["league"]["panel_version"], cfg["league"]["champion"]
    ok = [g for g in games if "error" not in g]
    errors = [g for g in games if "error" in g]
    by_map = defaultdict(list)
    for g in ok:
        if g["name_a"] != g["name_b"]:
            by_map[g["map"]].append((g["name_a"], g["name_b"], core.score_a(g)))
    ratings = rating.bootstrap(by_map) if by_map else {}

    per = defaultdict(list)
    matrix = defaultdict(list)
    seat = defaultdict(lambda: {"A": [], "B": []})
    mirror = defaultdict(list)
    for v, opp, side, s, me, them, g in _side_records(ok):
        if v == opp:
            if side == "A":
                mirror[v].append(s)
            continue
        per[v].append((s, me, them, g))
        matrix[(v, opp)].append(s)
        seat[v][side].append(s)

    names = sorted(per, key=lambda v: -ratings.get(v, (0, 0, 0))[0])
    lines = [f"# {title}", "",
             f"Generated {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · panel v{panel_version} · "
             f"champion `{champion}` · {len(ok)} games on {len({g['map'] for g in ok})} maps"
             + (f" · **{len(errors)} games did not finish**" if errors else ""), ""]

    lines += ["## Leaderboard", "",
              "Rating on the Elo scale (mean 1500), fitted on all games at once; the range is a 90% bootstrap over maps.", "",
              "| # | version | rating | 90% range | games | score | changelog |", "|---|---|---|---|---|---|---|"]
    meta = {}
    for i, v in enumerate(names, 1):
        try:
            meta[v] = core.version(v).meta
        except SystemExit:
            meta[v] = {}
        r, lo, hi = ratings.get(v, (float("nan"),) * 3)
        sc = mean(x[0] for x in per[v])
        lines.append(f"| {i} | `{v}` | {r:.0f} | {lo:.0f}–{hi:.0f} | {len(per[v])} | {100 * sc:.0f}% | {meta[v].get('changelog', '')} |")

    pair = cfg["league"].get("noise_pair", [])
    if len(pair) == 2 and all(p in ratings for p in pair):
        x, y = pair
        gap = abs(ratings[x][0] - ratings[y][0])
        h2h = matrix.get((x, y), [])
        lines += ["", f"**Noise band:** `{x}` and `{y}` have the same strength by construction. Here they differ by "
                  f"**{gap:.0f} points**" + (f" and score {100 * mean(h2h):.0f}% head to head over {len(h2h)} games" if h2h else "")
                  + ". A gap between two versions smaller than this is not a result."]

    lines += ["", "## Win matrix", "", "Score of the row against the column, both sides, all maps.", "",
              "| row \\ col | " + " | ".join(f"`{c}`" for c in names) + " |",
              "|---|" + "---|" * len(names)]
    for v in names:
        cells = []
        for c in names:
            xs = matrix.get((v, c))
            cells.append("·" if v == c else (f"{100 * mean(xs):.0f}% ({len(xs)})" if xs else ""))
        lines.append(f"| `{v}` | " + " | ".join(cells) + " |")

    lines += ["", "## How each version plays", "",
              "Averages over that version's games in this report. Gems are banked gems; r1000 is the median "
              "snapshot round where it reached 1000 gems (games where it did).", "",
              "| version | gems r500 | r1000 | final gems | reached 1000 | deaths | kills | gold | faults | fuel lost | camps cleared | distinct camps | wards |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for v in names:
        rs = per[v]
        def at(rec, rnd):
            me, g = rec[1], rec[3]
            idx = [i for i, r in enumerate(g["snap_rounds"]) if r <= rnd]
            return me["snap_gems"][idx[-1]] if idx else 0
        reach = [round_reaching(x[3]["snap_rounds"], x[1]["snap_gems"]) for x in rs]
        hit = sorted(r for r in reach if r)
        lines.append("| `{}` | {:.0f} | {} | {:.0f} | {:.0f}% | {:.1f} | {:.1f} | {:.0f} | {} | {:.1f} | {:.1f} | {:.1f} | {:.1f} |".format(
            v, mean(at(x, 500) for x in rs), hit[len(hit) // 2] if hit else "–", mean(x[1]["gems"] for x in rs),
            100 * len(hit) / len(rs), mean(x[1]["deaths"] for x in rs), mean(x[1]["kills"] for x in rs),
            mean(x[1]["gold"] for x in rs), sum(x[1]["faults"] for x in rs), mean(x[1]["fuel_exhausted"] for x in rs),
            mean(x[1]["camp_clears"] for x in rs), mean(x[1]["distinct_camps"] for x in rs), mean(x[1]["wards"] for x in rs)))

    lines += ["", "## Seat split and symmetry", "",
              "Carson: a bot that wins from one side and loses from the other has an edge from the start position, not a strategy.", "",
              "| version | score as side A | score as side B | gap |", "|---|---|---|---|"]
    for v in names:
        a, b = seat[v]["A"], seat[v]["B"]
        if a and b:
            lines.append(f"| `{v}` | {100 * mean(a):.0f}% | {100 * mean(b):.0f}% | {100 * (mean(a) - mean(b)):+.0f} |")
    if mirror:
        lines += ["", "Mirror games (a version against itself): side A wins this share. Far from 50% means the maps or "
                  "the bot favour one side.", ""]
        for v, xs in sorted(mirror.items()):
            lines.append(f"- `{v}`: side A {100 * mean(xs):.0f}% of {len(xs)}")

    lines += ["", "## Strategy coverage", "",
              "What each version actually does. If one draft or one item takes almost every game, the strategy has collapsed "
              "(Carson's kaggriculture bot bought the same land in every game and he saw it too late).", "",
              "| version | distinct drafts | top drafts | top items |", "|---|---|---|---|"]
    for v in names:
        drafts = Counter(", ".join(x[1]["draft"]) for x in per[v])
        items = Counter()
        for x in per[v]:
            items.update(x[1]["items"])
        top = "; ".join(f"{d} ({100 * n / len(per[v]):.0f}%)" for d, n in drafts.most_common(2))
        lines.append(f"| `{v}` | {len(drafts)} | {top} | " + ", ".join(f"{k} ×{n}" for k, n in items.most_common(3)) + " |")

    if True:
        runs = [h for h in (history or []) if h.get("panel_version") == panel_version][-8:]
        if ratings:
            lines += ["", "## Best rating per league run", "",
                      f"Carson's stopping rule: when the best rating gains less than {cfg['league'].get('plateau_points', 20)} "
                      "points for two runs in a row, the current idea has plateaued; change direction.", "",
                      "| run | best version | rating | gain |", "|---|---|---|---|"]
            prev = None
            gains = []
            for h in runs + [{"time": time.time(), "ratings": {v: ratings[v][0] for v in names if v in ratings}}]:
                if not h["ratings"]:
                    continue
                best = max(h["ratings"], key=h["ratings"].get)
                r = h["ratings"][best]
                gain = "" if prev is None else f"{r - prev:+.0f}"
                if prev is not None:
                    gains.append(r - prev)
                lines.append(f"| {time.strftime('%m-%d %H:%M', time.gmtime(h['time']))} | `{best}` | {r:.0f} | {gain} |")
                prev = r
            pp = cfg["league"].get("plateau_points", 20)
            if len(gains) >= 2 and all(g < pp for g in gains[-2:]):
                lines += ["", f"**Plateau:** the last two runs gained less than {pp} points each."]

    lines += ["", "## Lineage", "", "Each version and the version it was copied from, with its changelog line.", "", "```"]
    kids = defaultdict(list)
    for v in names:
        kids[meta[v].get("parent", "")].append(v)
    def render(v, depth):
        lines.append("  " * depth + f"{v}  ({meta[v].get('changelog', '')[:90]})")
        for k in sorted(kids.get(v, [])):
            if k != v:
                render(k, depth + 1)
    for root in sorted(v for v in names if meta[v].get("parent") not in names or meta[v].get("parent") == v):
        render(root, 0)
    lines.append("```")

    if errors:
        lines += ["", "## Games that did not finish", ""]
        for g in errors[:20]:
            lines.append(f"- `{g['name_a']}` vs `{g['name_b']}` on {g['map']}: {g['error'].splitlines()[-1] if g['error'] else '?'}")

    summary = {"time": time.time(), "panel_version": panel_version, "champion": champion,
               "ratings": {v: ratings[v][0] for v in names if v in ratings}}
    curves = {}
    for v in names:  # mean banked gems at each snapshot round, for the dashboard
        acc = defaultdict(list)
        for x in per[v]:
            pts = list(zip(x[3]["snap_rounds"], x[1]["snap_gems"]))
            for r in range(100, 2001, 100):  # banked gems never go away: hold the last value after the game ends
                acc[r].append(max([gm for rr, gm in pts if rr <= r], default=0))
        curves[v] = [(r, mean(acc[r])) for r in sorted(acc)]
    summary["_curves"] = curves
    return "\n".join(lines) + "\n", summary
