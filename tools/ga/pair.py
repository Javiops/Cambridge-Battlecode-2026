"""Pair genes: stay with an ally in a fight (micro family).

Why (DQN thread, 16 Oct, /mnt/project-files/analysis/dqn-2026-10-16/README.md): in like-for-like situations we die
1.75x as often as the top two teams (7.0% vs 4.0% within 10 rounds). With an ally within 4 their death rate halves;
ours does not move. These genes let the islands find whether staying in pairs closes that gap. Each default keeps
the base bot as it is (P_PAIR_N 0 turns the two pair rules off).

- P_GA_SS_ALLY / P_GA_SS_HOME: backing off (safe step) picks the tile the fewest foes can reach, then the one closest
  to an ally (weight 10) and to spawn (weight 1). These are those weights: retreat toward the ally or toward home.
- P_PAIR_N: "alone" = no ally within this many tiles (0 = pair rules off).
- P_PAIR_STICK: alone with a foe within P_PAIR_FOE and a visible ally: step toward that ally (fewest threats first)
  instead of backing off or fighting, unless the target is killable. Runs at the start of the AVOID rule.
- P_PAIR_ENGAGE: do not engage alone, unless the target is killable or channeling.
"""

GENES = {
    'P_GA_SS_ALLY': (10, 0, 30, 'int',  'back off: weight of the distance to the nearest ally (10 = base)'),
    'P_GA_SS_HOME': (1, 0, 5, 'int',    'back off: weight of the distance to spawn (1 = base)'),
    'P_PAIR_N':     (0, 0, 8, 'int',    'alone = no ally within this many tiles (0 = pair rules off)'),
    'P_PAIR_FOE':   (6, 2, 10, 'int',   'pair stick: only with a foe within this many tiles'),
    'P_PAIR_STICK': (0, 0, 1, 'bool',   'alone in contact: step toward the nearest ally first'),
    'P_PAIR_ENGAGE': (0, 0, 1, 'bool',  'alone: do not engage unless the target is killable or channeling'),
}
NAMES = list(GENES)

PAIR_STEP = '''// P_PAIR_STICK (tools/ga/pair.py): step toward an ally through the tile the fewest foes can reach, hitting first
// if a hit is ready. False when no neighbouring tile is better than staying.
inline bool pair_off(State& s, bc::champion& me, const std::vector<Foe>& foes, vec2 ally) {
    if (!me.can_move()) return false;
    vec2 pos = me.position();
    std::vector<int> reaches;
    reaches.reserve(foes.size());
    for (auto& f : foes) reaches.push_back(reach(f));
    auto score = [&](vec2 t) { return threats_at(t, foes, reaches) * 1000 + dist(t, ally) * 10; };
    std::optional<vec2> best;
    int bests = score(pos);
    for (int dx = -1; dx <= 1; ++dx)
        for (int dy = -1; dy <= 1; ++dy) {
            if (!dx && !dy) continue;
            vec2 t = pos + vec2(dx, dy);
            if (!bc::map::is_in_bounds(t) || s.blocked.is_set(t)) continue;
            int sc = score(t);
            if (sc < bests) { bests = sc; best = t; }
        }
    if (!best) return false;
    bool hit = P_HITFIRST && hit_now(s, me, foes);
    if (!attempt([&] { return me.move_absolute(*best); })) return false;
    if (!hit) shoot_back(s, me, foes);
    return true;
}

'''

# (file, old, new), applied after struct.patch (structure.write_src), like macro.LITERALS
LITERALS = [
    ('fight.h', 'return threats_at(t, foes, reaches) * 1000 + ally * 10 + dist(t, s.spawn_center);',
                'return threats_at(t, foes, reaches) * 1000 + ally * P_GA_SS_ALLY + dist(t, s.spawn_center) * P_GA_SS_HOME;'),
    ('fight.h', '// Backing off: optionally hit first, then step (safe tile, retreat or flee), then hit if we have not yet.',
                PAIR_STEP + '// Backing off: optionally hit first, then step (safe tile, retreat or flee), then hit if we have not yet.'),
    ('main.cpp', '''    auto r_avoid = [&]() -> bool {
        g_mode = "fight";
        if (foes.empty()) return false;
        if (fight_ctx()) return true;''',
                 '''    // P_PAIR_N (tools/ga/pair.py): the nearest ally, and whether we are alone (no ally within P_PAIR_N)
    int pair_d = 99;
    vec2 pair_p = pos;
    for (auto& ap : allies)
        if (dist(ap, pos) < pair_d) { pair_d = dist(ap, pos); pair_p = ap; }
    const bool alone = P_PAIR_N > 0 && pair_d > P_PAIR_N;
    auto r_avoid = [&]() -> bool {
        g_mode = "fight";
        if (foes.empty()) return false;
        if (fight_ctx()) return true;
        if (P_PAIR_STICK && alone && pair_d <= 15 && !on_spawn && !cx.killable && nearest_foe <= P_PAIR_FOE &&
            fight::pair_off(s, me, foes, pair_p)) {
            g_mode = "pair";
            return true;
        }'''),
    ('main.cpp', '''        if (want) {
            bool acted = engage(s, me, tgt->c, tgt->p, true, true);''',
                 '''        if (want && P_PAIR_ENGAGE && alone && !cx.killable && !tgt->channeling) want = false;
        if (want) {
            bool acted = engage(s, me, tgt->c, tgt->p, true, true);'''),
]
