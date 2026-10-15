"""Two independent, source-only fixes for the reviewed study28 snapshot.

The caller supplies LF-normalized source text keyed by filename. No files are
read or written here, and each transformation rejects an unexpected source.
"""

LOCK_HELPER = '''// No SDK accessor exposes the altar targeted by another champion's tribute.
// Conservatively protect every possible tribute to this altar, including an
// unseen ally. Overlapping altar ranges may decline an otherwise safe lock.
bool study28_lock_altar_clear(State& s, vec2 altar, const bc::bitboard& visible) {
    const int range = static_cast<int>(bc::constants::submit_gems_range);
    for (int dx = -range; dx <= range; ++dx) {
        for (int dy = -range; dy <= range; ++dy) {
            const vec2 tile = altar + vec2(dx, dy);
            if (!bc::map::is_in_bounds(tile) || s.static_block.is_set(tile)) continue;
            if (!visible.is_set(tile)) return false;
        }
    }
    for (const auto& ally : bc::vision::champions(*s.my)) {
        // A failed live query must not authorize the optional placement.
        const bool clear = attempt([&] {
            return !ally.is_alive() || !ally.is_submitting_gems() ||
                   dist(ally.position(), altar) > range;
        });
        if (!clear) return false;
    }
    return true;
}

'''

LOCK_CACHE = '''        bc::bitboard lock_visibility;
        bool lock_visibility_ready = false;
'''

LOCK_CHECK = '''            if (!fuel_ok(6000)) return false;
            if (!lock_visibility_ready) {
                // The turn may have moved us; s.vis can describe the old tile.
                // This copies current cached vision, not a hypothetical cast.
                bc::vision::visible_tiles_into(lock_visibility);
                lock_visibility_ready = true;
            }
            if (!study28_lock_altar_clear(s, a, lock_visibility)) continue;
'''

SPAWN_ANCHOR = '''            bc::bitboard wall = bc::map::walls() | bc::map::holes() | s.en_spawn;
            bc::distance_field fs, fa;
            bc::bitboard vs, va, ar;
            fs.compute(wall, s.my_spawn & ~wall, vs);
'''

SPAWN_REPLACEMENT = '''            bc::bitboard wall = bc::map::walls() | bc::map::holes() | s.en_spawn;
            bc::distance_field fs, fa;
            bc::bitboard vs, va, ar;
            // Spawn-to-camp walking cannot pass through an altar. Keep the
            // separate altar-root field below unchanged.
            bc::bitboard spawn_wall = wall | bc::map::altars();
            fs.compute(spawn_wall, s.my_spawn & ~spawn_wall, vs);
'''


def _replace_once(text: str, anchor: str, replacement: str) -> str:
    if '\r' in text:
        raise ValueError('Expected LF-normalized source')
    count = text.count(anchor)
    if count != 1:
        raise ValueError(f'Expected exactly one source anchor, found {count}: {anchor!r}')
    return text.replace(anchor, replacement, 1)


def ally_lock(files: dict[str, str]) -> None:
    """Protect possible allied tributes; preserve legal enemy interruption."""
    text = files['utility.h']
    if 'study28_lock_altar_clear' in text:
        raise ValueError('Ally-lock patch is already present')
    anchor = '// Buy only with the remainder left by ordinary shopping, then spend the lock\n'
    text = _replace_once(text, anchor, LOCK_HELPER + anchor)
    anchor = '        int best = -1, rank = 1 << 20;\n'
    text = _replace_once(text, anchor, LOCK_CACHE + anchor)
    anchor = '            const int score = dist(a, s.en_center);\n'
    text = _replace_once(text, anchor, LOCK_CHECK + anchor)
    files['utility.h'] = text


def spawn_path(files: dict[str, str]) -> None:
    """Make the spawn field use legal walking obstacles, without changing fa."""
    files['main.cpp'] = _replace_once(files['main.cpp'], SPAWN_ANCHOR, SPAWN_REPLACEMENT)
