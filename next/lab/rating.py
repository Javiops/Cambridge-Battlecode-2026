"""Ratings for a pool of bots from all games played between them.

Carson rates every version together (TrueSkill in cb-bc). Here we use the Bradley-Terry model,
which is what Elo approximates: P(i beats j) = 1 / (1 + 10^((Rj - Ri) / 400)). It is fitted on
the whole batch at once, so the order games were played in does not matter, and it needs only
the standard library. A draw counts as half a win for each side.

Uncertainty comes from a bootstrap: resample the maps with replacement, refit, and take the
spread. Maps are the unit we resample because games on one map are not independent.
"""
from __future__ import annotations

import math
import random
from collections import defaultdict

BASE = 1500.0
SCALE = 400.0 / math.log(10)  # converts natural-log strengths to the Elo scale


def fit(games: list[tuple[str, str, float]], iters: int = 400, prior: float = 1.0) -> dict[str, float]:
    """games: (bot_x, bot_y, score of x in [0,1]). Returns an Elo-scale rating per bot (mean BASE).

    Minorise-maximise updates (Hunter 2004). `prior` adds that many virtual draws against a
    BASE-rated phantom, which keeps ratings finite for a bot that wins or loses every game.
    """
    bots = sorted({b for g in games for b in g[:2]})
    if not bots:
        return {}
    wins = defaultdict(float)
    pairs = defaultdict(float)  # games played between each unordered pair
    for x, y, s in games:
        wins[x] += s
        wins[y] += 1.0 - s
        pairs[(x, y)] += 1
        pairs[(y, x)] += 1
    strength = {b: 1.0 for b in bots}
    for _ in range(iters):
        new = {}
        for i in bots:
            denom = prior / (strength[i] + 1.0)  # virtual games vs the phantom (strength 1)
            for j in bots:
                n = pairs.get((i, j), 0.0)
                if n:
                    denom += n / (strength[i] + strength[j])
            new[i] = (wins[i] + prior * 0.5) / denom
        # normalise so the geometric mean is 1 (mean rating = BASE)
        g = math.exp(sum(math.log(v) for v in new.values()) / len(new))
        strength = {b: v / g for b, v in new.items()}
    return {b: BASE + SCALE * math.log(v) for b, v in strength.items()}


def bootstrap(games_by_map: dict[str, list[tuple[str, str, float]]], samples: int = 200,
              seed: int = 1) -> dict[str, tuple[float, float, float]]:
    """(rating, low, high) per bot: the point fit plus a 90% interval from resampled maps."""
    maps = sorted(games_by_map)
    point = fit([g for m in maps for g in games_by_map[m]])
    rng = random.Random(seed)
    draws = defaultdict(list)
    for _ in range(samples):
        pick = [rng.choice(maps) for _ in maps]
        r = fit([g for m in pick for g in games_by_map[m]], iters=150)
        for b in point:
            if b in r:
                draws[b].append(r[b])
    out = {}
    for b, r in point.items():
        d = sorted(draws[b]) or [r]
        out[b] = (r, d[int(0.05 * (len(d) - 1))], d[int(0.95 * (len(d) - 1))])
    return out


def expected_score(ra: float, rb: float) -> float:
    return 1.0 / (1.0 + 10 ** ((rb - ra) / 400.0))
