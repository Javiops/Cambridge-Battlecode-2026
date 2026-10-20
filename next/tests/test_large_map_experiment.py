from collections import deque
import pytest
from lab import mapgen
from tools.large_map_experiment import expanded


@pytest.mark.parametrize('family', range(4))
@pytest.mark.parametrize('size', [(72, 80), (80, 96), (96, 96), (100, 100)])
def test_large_layout_keeps_symmetry_reachable_resources_and_open_spawns(family, size):
    original = mapgen.layout(1000 + family)
    w, h = size
    m = expanded(original, w, h)
    mirror = lambda p: (w - 1 - p[0], h - 1 - p[1])
    terrain = {k: {tuple(p) for p in m[k]} for k in ('walls', 'holes', 'bushes', 'altars')}
    camps = {(x, y): t for t, x, y in m['camps']}
    for cells in terrain.values():
        assert all(mirror(p) in cells for p in cells)
    assert all(camps.get(mirror(p)) == kind for p, kind in camps.items())
    assert len(camps) == len(original['camps'])
    blocked = terrain['walls'] | terrain['holes'] | terrain['altars'] | camps.keys()
    assert all(0 <= x < w and 0 <= y < h for x, y in blocked)
    spawns = {(x, y) for x in range(1, 4) for y in range(1, 4)}
    spawns |= {mirror(p) for p in list(spawns)}
    assert not spawns & blocked
    seen, queue = {(1, 1)}, deque([(1, 1)])
    neighbours = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
    while queue:
        x, y = queue.popleft()
        for dx, dy in neighbours:
            p = (x + dx, y + dy)
            if 0 <= p[0] < w and 0 <= p[1] < h and p not in blocked and p not in seen:
                seen.add(p)
                queue.append(p)
    assert spawns <= seen
    assert all(any((x + dx, y + dy) in seen for dx, dy in neighbours)
               for x, y in camps.keys() | terrain['altars'])


def test_large_layout_rejects_shrink_and_asymmetric_padding():
    m = mapgen.layout(1000)
    for w, h in [(m['width'] - 2, m['height']), (m['width'] + 1, m['height'] + 2)]:
        with pytest.raises(ValueError, match='Padding'):
            expanded(m, w, h)
