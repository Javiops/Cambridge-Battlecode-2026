"""The macro genome: farming and economy parameters the genetic algorithm may change (tools/ga/mga.py).

Same contract as genome.py (the fight genome), so ga.py runs it unchanged: GENES, LITERALS, NAMES, MAGIC and the
helpers. The default genome equals the base bot (ga65a6 = study27-economy + the evolved fight params, online as v44),
so `mga.py check` should show only fuel-chaos differences against the base build.

Genes cover camp choice, stacking, banking/chaining, recall trips, shop timing and the shop plan, gold pickup and
the draft threshold. Fight genes (flee, engage, kite, danger spots, bail) stay with the fight GA and are not here.
Map-specific hard-coding is not added: thresholds read map features (camp hp, walking distances, spawn path).
P_GA_* names replace literal constants of the base code (see LITERALS) with the same default value.
"""

# name: (default, lo, hi, what it decides)
GENES = {
    # camp choice (choose_target)
    'P_GOLD_W_EARLY':  (25, 0, 80,      'gold worth this % of a gem in camp choice, early'),
    'P_GOLD_W_LATE':   (24, 0, 80,      '... and late'),
    'P_GA_GOLD_ROUND': (600, 200, 1500, 'round where the early gold weight ends'),
    'P_NOGOLD':        (1, 0, 1,        'skip gold-only clusters'),
    'P_MAX_SHARE':     (4, 1, 5,        'champions allowed on one monster group'),
    'P_SHAREEXP':      (75, 30, 100,    'a joiner values a big camp at gems / team^(this/100)'),
    'P_STACK_HP':      (3000, 800, 8000, 'camps with this much hp count as big (stacking)'),
    'P_PAIR':          (2, 1, 3,        'champions on a gem cluster'),
    'P_RESERVE_PCT':   (-60, -150, 50,  'squad sizing: hp each member may lose, % of max (negative = more than max)'),
    'P_HALF':          (30, 10, 100,    'score x this % for camps on the enemy half'),
    'P_GA_HALF_D':     (6, 0, 15,       '... a camp is on their half when this much nearer their spawn'),
    'P_GA_DOOR':       (60, 20, 100,    'score x this % for camps near the enemy spawn'),
    'P_GA_DOOR_D':     (8, 0, 16,       '... within this many tiles'),
    'P_STICK':         (125, 100, 200,  'score bonus % for the current target (hysteresis)'),
    'P_RESPAWN':       (4, 0, 15,       'walk to a respawning camp when it is back within walk + this'),
    'P_GA_NEEDCO':     (70, 30, 100,    'score x this % when the camp still needs company'),
    'P_GA_SOLO':       (30, 10, 100,    'score x this % for a claimed gem cluster (solo job)'),
    'P_GA_CYCLE':      (8, 0, 30,       'cost of a heal trip: this + walk from spawn'),
    'P_GA_OVERHEAD':   (6, 0, 20,       'fixed rounds added per camp (capture, overhead)'),
    'P_BANKW':         (0, 0, 300,      'camp cost adds this % of the round trip to the nearest altar'),
    'P_R34_BANKCOST':  (300, 0, 600,    'same, expanse only (known-map rule)'),
    'P_HOLD':          (200, 100, 400,  'caster draft: score x this % for camps around the held centre altar'),
    'P_HOLD_R':        (6, 3, 10,       '... camps within this of that altar'),
    'P_E_RETARGET':    (6, 2, 20,       're-choose a camp we are only walking to every this many rounds'),
    'P_ONE_CAP':       (1, 0, 1,        'one champion per capture reward'),
    # banking and chaining
    'P_TRIBUTE_GEMS':  (12, 5, 60,      'walk to an altar once carrying this many gems'),
    'P_TRIBUTE_NEAR':  (8, 0, 20,       'bank a smaller bag when an altar is this close...'),
    'P_GA_NEAR_GEMS':  (10, 1, 30,      '... of at least this many gems'),
    'P_CHAIN':         (36, 0, 100,     'with fewer gems than this, take a near solo camp before banking'),
    'P_CHAIN_R':       (8, 3, 20,       '... within this many tiles'),
    'P_BAG':           (0, 0, 100,      'no enemy seen for P_BAG_QUIET rounds: carry this many gems before banking'),
    'P_BAG_QUIET':     (40, 10, 150,    '... rounds'),
    'P_LATE_ROUND':    (1850, 1500, 1990, 'after this round bank any gems'),
    'P_OWN_ALTAR':     (20, 0, 60,      'altar choice: penalty for altars on the enemy half'),
    'P_TELE':          (0, 0, 30,       '>0: recall instead of walking to the altar when that is shorter by this'),
    # recall trips
    'P_GA_TRIB_RC_GEMS': (10, 1, 40,    'before a recall, bank first with this many gems...'),
    'P_GA_TRIB_RC_D':  (12, 0, 30,      '... if the altar is this close'),
    'P_CAPRECALL':     (2, 0, 2,        'recall on capture tiles: 1 when needed, 2 also for a cheap heal/shop'),
    'P_CAPRECALL_DELAY': (1, 0, 5,      'rounds on the capture tiles before that recall'),
    'P_GA_CR_HEAL':    (90, 50, 100,    'optional capture recall below this % hp (minus walk cost)'),
    'P_GA_CR_GOLD':    (90, 30, 300,    'optional capture recall with this much gold (+3 per tile of walk)'),
    # shop
    'P_SHOP_GOLD':     (240, 100, 600,  'recall to shop with this much gold when hurt'),
    'P_GA_SHOP_HP':    (50, 0, 100,     '... below this % hp'),
    'P_SHOP_RECALL':   (180, 0, 600,    'shop trip at any hp with this much gold (0 = never)'),
    'P_SHOP_PLAN':     (3, 0, 3,        'item plan: 0 own, 1 top teams, 2 tank, 3 top-10 winners'),
    'P_SHOPUNI':       (1, 0, 1,        'casters buy power-f like the #1'),
    'P_NE_POWER_OPEN': (1, 0, 1,        'melee opens with a power emblem'),
    'P_JACKPOT':       (350, 0, 900,    'hold off a jackpot group (half the map gems, contested) until this round (I042)'),
    # draft
    'P_UNI_PATH':      (45, 0, 120,     'caster draft when the spawn-to-spawn walk is at most this'),
    'P_GA_DRAFT_FARM': (0, 0, 2,        'draft on the other maps: 0 own list, 1 Cassi&Issac + Stellar first, '
                                        '2 Stellar, Cassi&Issac, Ren, Tavi (the top-10 winners)'),
}

_RETARGET_OLD = """#if defined(P_E_RETARGET) && P_E_RETARGET > 0
    target_refresh = P_E_RETARGET;
#endif"""
_RETARGET_NEW = """    target_refresh = P_E_RETARGET;"""

_POWER_OLD = """#if defined(P_NE_POWER_OPEN) && P_NE_POWER_OPEN > 0
    // One offensive opening emblem, then the complete original melee core.
    // Preserve Jungle camp mitigation and Bruiser health for later farming.
    if (starts_with(s.name, "ryth") || starts_with(s.name, "varg") || starts_with(s.name, "vendetta"))
        s.plan = {{"power", 's', 1}, {"durab", 's', 1}, {"jungle", 's', 1},
                  {"bruiser", 'h', 1}, {"power", 's', 99}};
#endif"""
_POWER_NEW = """    // One offensive opening emblem, then the complete original melee core.
    // Preserve Jungle camp mitigation and Bruiser health for later farming.
    if (P_NE_POWER_OPEN && (starts_with(s.name, "ryth") || starts_with(s.name, "varg") || starts_with(s.name, "vendetta")))
        s.plan = {{"power", 's', 1}, {"durab", 's', 1}, {"jungle", 's', 1},
                  {"bruiser", 'h', 1}, {"power", 's', 99}};"""

# Literal constants (and two preprocessor switches) of the base code turned into genes: (file, old, new).
# Each old text must occur exactly once in the base source.
LITERALS = [
    ('main.cpp', '''        std::printf("[draft] uni ts=%d spawn_path=%d fight=%d\\n", ts, sp, fight_map ? 1 : 0);
        if (fight_map) {''',
                 '''        std::printf("[draft] uni ts=%d spawn_path=%d fight=%d\\n", ts, sp, fight_map ? 1 : 0);
        if (!fight_map && P_GA_DRAFT_FARM) {
            if (P_GA_DRAFT_FARM == 1) prefs = {"cassi", "stellar"};
            else prefs = {"stellar", "cassi", "ren", "tavi"};
            for (const char* p : PREFS) prefs.push_back(p);
        }
        if (fight_map) {'''),
    ('main.cpp', 'double gold_w = (round < 600 ?', 'double gold_w = (round < P_GA_GOLD_ROUND ?'),
    ('main.cpp', 'if (needed > 1 + claimers) score *= 0.7;', 'if (needed > 1 + claimers) score *= P_GA_NEEDCO / 100.0;'),
    ('main.cpp', 'score *= pack ? 1.0 : 0.3;  // clusters are a solo job',
                 'score *= pack ? 1.0 : P_GA_SOLO / 100.0;  // clusters are a solo job'),
    ('main.cpp', 'if (dist(g.center, s.en_center) < 8) score *= 0.6;',
                 'if (dist(g.center, s.en_center) < P_GA_DOOR_D) score *= P_GA_DOOR / 100.0;'),
    ('main.cpp', 'dist(g.center, s.spawn_center) - dist(g.center, s.en_center) > 6)',
                 'dist(g.center, s.spawn_center) - dist(g.center, s.en_center) > P_GA_HALF_D)'),
    ('main.cpp', 'double cycle = 8.0 + (P_PATHD', 'double cycle = P_GA_CYCLE + (P_PATHD'),
    ('main.cpp', 'double rounds = travel + t_clear + 6.0 +', 'double rounds = travel + t_clear + P_GA_OVERHEAD +'),
    ('main.cpp', _RETARGET_OLD, _RETARGET_NEW),
    ('main.cpp', _POWER_OLD, _POWER_NEW),
    ('main.cpp', '(gems >= 10 && ad <= (s.de_map == v34de::Rows ? 4 : P_TRIBUTE_NEAR))',
                 '(gems >= P_GA_NEAR_GEMS && ad <= (s.de_map == v34de::Rows ? 4 : P_TRIBUTE_NEAR))'),
    ('main.cpp', """        if (gems >= 10) {
            auto a = best_altar(s, pos, round);
            if (a && br_altar_distance(s, *a, pos, round) <= std::min(home, 12)) {""",
                 """        if (gems >= P_GA_TRIB_RC_GEMS) {
            auto a = best_altar(s, pos, round);
            if (a && br_altar_distance(s, *a, pos, round) <= std::min(home, P_GA_TRIB_RC_D)) {"""),
    ('main.cpp', '(gold >= P_SHOP_GOLD && hpr < 0.5f)', '(gold >= P_SHOP_GOLD && hpr * 100 < P_GA_SHOP_HP)'),
    ('main.cpp', 'const float heal_cutoff = std::clamp(0.9f - 0.006f * return_walk, 0.65f, 0.9f);',
                 'const float heal_cutoff = std::clamp(P_GA_CR_HEAL / 100.0f - 0.006f * return_walk, '
                 'std::min(0.65f, P_GA_CR_HEAL / 100.0f), P_GA_CR_HEAL / 100.0f);'),
    ('main.cpp', 'const int gold_cutoff = 90 + 3 * std::min(return_walk, 50);',
                 'const int gold_cutoff = P_GA_CR_GOLD + 3 * std::min(return_walk, 50);'),
]

NAMES = list(GENES)
MAGIC = (0x324D4147, 0x5EED5678)  # 'GAM2' (the fight genome is 'GAM1'), then a second word


def default():
    return {k: v[0] for k, v in GENES.items()}


def to_unit(g):
    return [(g[k] - GENES[k][1]) / (GENES[k][2] - GENES[k][1]) for k in NAMES]


def from_unit(x):
    out = {}
    for k, u in zip(NAMES, x):
        lo, hi = GENES[k][1], GENES[k][2]
        out[k] = int(round(lo + min(1.0, max(0.0, u)) * (hi - lo)))
    return out


def diff(g, base=None):
    base = base or default()
    return {k: g[k] for k in NAMES if g[k] != base[k]}
