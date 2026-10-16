#!/usr/bin/env python3
"""Generated cousins of the site maps: each site map with its camps moved and retyped, walls thinned or extended,
altars nudged and the team size changed now and then. Training maps that look like the maps we play online without
being them (the qualifying maps are new; tuning on the 17 site maps themselves would overfit them).

usage: python3 tools/ga/cousins.py OUTDIR [--per 12] [--seed 1] [--maps 'maps/*.map26a'] [--identity]
  --identity rebuilds every site map unchanged and checks the result matches it (tests the read/write path).

Reads a map with tools/mapjson.js and writes one with /mnt/project-files/arena/tools/mkmap.js (map-editor wasm).
The editor mirrors what is placed in the source half, so only that half is read and changed.
"""
import argparse, glob, json, os, random, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MAPJSON = os.path.join(os.path.dirname(HERE), 'mapjson.js')
MKMAP = os.environ.get('MKMAP', '/mnt/project-files/arena/tools/mkmap.js')
SYMN = {'H': 'HORIZONTAL', 'V': 'VERTICAL', 'R180': 'ROTATIONAL180'}


def read(path):
    r = subprocess.run(['node', MAPJSON, path], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    return json.loads(r.stdout)


def mirror(m, x, y):
    w, h = m['w'], m['h']
    if m['sym'] == 'H':
        return w - 1 - x, y
    if m['sym'] == 'V':
        return x, h - 1 - y
    return w - 1 - x, h - 1 - y


def layout(m):
    """The source-half layout of a mapjson map (the half holding team A's spawn), in mkmap's format."""
    sa = m['spawnA']
    cx, cy = (sa[0] + sa[2]) / 2, (sa[1] + sa[3]) / 2
    w, h = m['w'], m['h']
    if m['sym'] == 'H':
        inside = (lambda x, y: x <= (w - 1) / 2) if cx < w / 2 else (lambda x, y: x >= (w - 1) / 2)
    else:
        inside = (lambda x, y: y <= (h - 1) / 2) if cy < h / 2 else (lambda x, y: y >= (h - 1) / 2)
    L = {'width': w, 'height': h, 'symmetry': SYMN[m['sym']], 'champs': m['nch'], 'spawnA': sa,
         'walls': [], 'holes': [], 'bushes': [], 'altars': [], 'camps': []}
    key = {'#': 'walls', 'o': 'holes', '"': 'bushes', 'A': 'altars'}
    for y, row in enumerate(m['grid']):
        for x, c in enumerate(row):
            if c in key and inside(x, y):
                L[key[c]].append([x, y])
    # camp groups = 8-connected camps (the engine groups adjacent camps)
    # the editor stores each camp once (anywhere on the map) and mirrors it: keep the stored list as it is
    cs = [(c['type'], c['x'], c['y']) for c in m['camps']]
    left, groups = set(range(len(cs))), []
    while left:
        stack, g = [left.pop()], []
        while stack:
            i = stack.pop()
            g.append(list(cs[i]))
            for j in list(left):
                if abs(cs[j][1] - cs[i][1]) <= 1 and abs(cs[j][2] - cs[i][2]) <= 1:
                    left.discard(j)
                    stack.append(j)
        groups.append(g)
    L['camps'] = [c for g in groups for c in g]
    return L, groups, inside


def write(L, out):
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
        json.dump(L, f)
    try:
        r = subprocess.run(['node', MKMAP, f.name, out], capture_output=True, text=True)
    finally:
        os.unlink(f.name)
    if r.returncode != 0 or not os.path.exists(out):
        raise RuntimeError((r.stderr or r.stdout)[-400:])


def cousin(m, rng):
    L, groups, inside = layout(m)
    w, h = m['w'], m['h']
    sa = L['spawnA']
    spawn = {(x, y) for x in range(sa[0] - 2, sa[2] + 3) for y in range(sa[1] - 2, sa[3] + 3)}
    spawn |= {mirror(m, x, y) for x, y in spawn}

    def both(pts):
        return set(pts) | {mirror(m, x, y) for x, y in pts}

    def occupied():
        occ = set(spawn)
        for k in ('walls', 'holes', 'altars'):
            occ |= both(tuple(p) for p in L[k])
        return occ

    def ok(x, y, occ):
        return 1 <= x < w - 1 and 1 <= y < h - 1 and inside(x, y) and (x, y) not in occ and \
            mirror(m, x, y) != (x, y)

    def near(pts, other):
        return any((x + i, y + j) in other for x, y in pts for i in (-1, 0, 1) for j in (-1, 0, 1))
    # camps: move each group as a block (it and its mirror stay clear of walls, altars, spawns and, by a tile,
    # of every other group, so groups never merge), sometimes retype it
    occ = occupied()
    cur = [list(g) for g in groups]
    for gi, g in enumerate(cur):
        others = both((x, y) for k, gg in enumerate(cur) if k != gi for _, x, y in gg)
        for _ in range(12):
            dx, dy = rng.randint(-3, 3), rng.randint(-3, 3)
            cand = [[t, x + dx, y + dy] for t, x, y in g]
            pts = both((x, y) for _, x, y in cand)
            if all(1 <= x < w - 1 and 1 <= y < h - 1 and (x, y) not in occ for x, y in pts) and \
                    not near(pts, others) and not near({(x, y) for _, x, y in cand},
                                                       {mirror(m, x, y) for _, x, y in cand}):
                cur[gi] = cand
                break
        r = rng.random()
        swap = {}
        if r < 0.15:
            swap = {'WOLF': 'ELK', 'ELK': 'WOLF'}
        elif r < 0.22:
            swap = {'GEM_CLUSTER': 'GOLD_CLUSTER', 'GOLD_CLUSTER': 'GEM_CLUSTER'}
        cur[gi] = [[swap.get(t, t), x, y] for t, x, y in cur[gi]]
    newcamps = [c for g in cur for c in g]
    placed = both((x, y) for _, x, y in newcamps)
    L['camps'] = newcamps
    # walls: thin them (open new paths) or add short segments (close some)
    if L['walls'] and rng.random() < 0.5:
        k = int(len(L['walls']) * rng.uniform(0.05, 0.25))
        for p in rng.sample(L['walls'], k):
            L['walls'].remove(p)
    if rng.random() < 0.4:
        occ = occupied() | placed
        for _ in range(rng.randint(1, 4)):
            x, y = rng.randint(2, w - 3), rng.randint(2, h - 3)
            dx, dy = rng.choice([(1, 0), (0, 1), (1, 1), (1, -1)])
            seg = [(x + i * dx, y + i * dy) for i in range(rng.randint(3, 7))]
            if all(ok(a, b, occ) and not any((a + i, b + j) in placed for i in (-1, 0, 1) for j in (-1, 0, 1))
                   for a, b in seg):
                L['walls'] += [list(p) for p in seg]
                occ |= set(seg)
    # altars: nudge
    if rng.random() < 0.4:
        occ = occupied() | placed
        new = []
        for a in L['altars']:
            occ.discard(tuple(a))
            dx, dy = rng.randint(-2, 2), rng.randint(-2, 2)
            p = (a[0] + dx, a[1] + dy)
            p = p if ok(*p, occ) and p not in placed else tuple(a)
            occ.add(p)
            new.append(list(p))
        L['altars'] = new
    # team size
    if rng.random() < 0.3:
        L['champs'] = max(3, min(5, L['champs'] + rng.choice([-1, 1])))
    L['bushes'] = [b for b in L['bushes'] if tuple(b) not in {tuple(p) for p in L['walls'] + L['altars']}
                   and tuple(b) not in placed]
    return L


def same(a, b):
    return a['grid'] == b['grid'] and a['nch'] == b['nch'] and \
        sorted((c['type'], c['x'], c['y']) for c in a['camps']) == sorted((c['type'], c['x'], c['y']) for c in b['camps'])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('out')
    p.add_argument('--per', type=int, default=12)
    p.add_argument('--seed', type=int, default=1)
    p.add_argument('--maps', default='maps/*.map26a')
    p.add_argument('--identity', action='store_true')
    A = p.parse_args()
    os.makedirs(A.out, exist_ok=True)
    rng = random.Random(A.seed)
    made = fail = 0
    for path in sorted(glob.glob(A.maps)):
        name = os.path.splitext(os.path.basename(path))[0]
        m = read(path)
        if A.identity:
            out = os.path.join(A.out, name + '_id.map26a')
            try:
                write(layout(m)[0], out)
                print(name, 'identical' if same(m, read(out)) else 'DIFFERS')
            except RuntimeError as e:
                print(name, 'FAILED', str(e)[:200])
            continue
        for i in range(A.per):
            out = os.path.join(A.out, f'{name}_c{A.seed}_{i:02d}.map26a')
            for attempt in range(5):
                try:
                    write(cousin(m, rng), out)
                    made += 1
                    break
                except RuntimeError as e:
                    err = str(e)
            else:
                fail += 1
                print(f'{name} {i}: failed: {err[:200]}', file=sys.stderr)
        print(name, 'done', flush=True)
    if not A.identity:
        print(f'{made} cousins written to {A.out}, {fail} failed')


if __name__ == '__main__':
    main()
