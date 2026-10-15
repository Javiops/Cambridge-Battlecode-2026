import json, collections
from functools import lru_cache
DIRS = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
class Geo:
    def __init__(self, m):
        self.m = m; self.w = m['w']; self.h = m['h']; g = m['grid']
        self.block = [[g[y][x] in '#oA' for x in range(self.w)] for y in range(self.h)]
        self.altars = [(x, y) for y in range(self.h) for x in range(self.w) if g[y][x] == 'A']
        self._cache = {}
    def bfs(self, srcs):
        key = tuple(sorted(srcs))
        if key in self._cache: return self._cache[key]
        INF = 10**6; D = [[INF]*self.w for _ in range(self.h)]; q = collections.deque()
        for x, y in srcs:
            if 0 <= x < self.w and 0 <= y < self.h and D[y][x] == INF: D[y][x] = 0; q.append((x, y))
        while q:
            x, y = q.popleft(); dd = D[y][x] + 1
            for dx, dy in DIRS:
                nx, ny = x+dx, y+dy
                if 0 <= nx < self.w and 0 <= ny < self.h and not self.block[ny][nx] and D[ny][nx] > dd: D[ny][nx] = dd; q.append((nx, ny))
        self._cache[key] = D; return D
    def near(self, tiles, r):
        out = set()
        for x, y in tiles:
            for dx in range(-r, r+1):
                for dy in range(-r, r+1):
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < self.w and 0 <= ny < self.h and not self.block[ny][nx]: out.add((nx, ny))
        return list(out)
    def d_to_group(self, tiles): return self.bfs([tuple(t) for t in tiles])   # stand on the tiles
    def d_to_altar(self, a): return self.bfs(self.near([a], 1))              # within tribute range
