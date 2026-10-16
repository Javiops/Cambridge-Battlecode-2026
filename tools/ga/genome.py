"""The genome: fight ("micro") parameters of the bot that the genetic algorithm may change.

Everything else (draft, shop, camp choice, tributes: the macro) stays as the base bot has it.

Each gene is an int macro the bot reads at run time. `default` must equal the base bot's value, so the default
genome is the base bot (`ga.py check` compares their games; only fuel-chaos differences are expected). Genes named P_GA_* do not exist in the base
source: they replace a literal constant of the fight code (see LITERALS) with the same default value.
"""

# name: (default, lo, hi, what it decides)
GENES = {
    'P_FLEE_PCT':      (25, 5, 50,   'run/recall below this % hp (non-caster drafts)'),
    'P_UNI_FLEE':      (35, 5, 70,   'run/recall below this % hp (caster draft)'),
    'P_RECALL_PCT':    (55, 20, 85,  'recall below this % hp when safe / out of the fight'),
    'P_RECALL_NEAR':   (5, 2, 10,    'recall allowed with the nearest foe this many tiles away (caster draft)'),
    'P_BAIL_PCT':      (18, 0, 45,   'abandon a camp fight below this % hp'),
    'P_AVOID_DIST':    (4, 0, 9,     'back away from an unfavourable group this close'),
    'P_GA_AVOID_HP':   (60, 20, 95,  'back away from an unfavourable group below this % hp'),
    'P_ENGAGE2':       (120, 50, 250, 'favourable fight = our hp near the target >= this % of theirs'),
    'P_GA_FAV':        (90, 50, 160, 'favourable fight without a target = our hp >= this % of theirs within 8'),
    'P_GA_KILL_X':     (20, 5, 40,   'killable target = its hp <= our strength x this / 10 (always engage)'),
    'P_LOWHP':         (50, 0, 85,   'below this % hp with a foe within 6: back off'),
    'P_GA_SPAWN_HEAL': (95, 50, 100, 'stay on spawn healing until this % hp'),
    'P_FRONT_ZONE':    (3, 1, 6,     'front line: a foe this close means we are in the fight'),
    'P_FRONT_OUT':     (130, 60, 260, 'front line: give up when their hp is above this % of ours'),
    'P_KITE_ZONE':     (4, 2, 8,     'kite: nobody within this many tiles and not hit = keep farming'),
    'P_KITE_OUT':      (2, 0, 4,     'kite: give up when they outnumber us by more than this...'),
    'P_GA_KITE_HP':    (130, 60, 250, '...and their hp is above this % of ours'),
    'P_VOLLEY':        (70, 20, 160, 'pathing avoids tiles where ready enemy damage >= this % of our hp'),
    'P_CHASE_GEMS':    (150, 30, 400, 'chase a foe only when it carries this many gems'),
    'P_DANGER':        (3, 2, 5,     'this many enemy champions together mark a danger spot'),
    'P_DANGER_T':      (40, 8, 120,  'a danger spot lasts this many rounds'),
    'P_DANGER_R':      (6, 2, 12,    'camps within this of a danger spot are skipped'),
}

# Literal constants of the base fight code turned into genes: (file, old text, new text). Each old text must
# occur exactly once in the base source.
LITERALS = [
    ('main.cpp', '(hpr < 0.6f || nearest_foe <= P_AVOID_DIST)',
                 '(hpr * 100 < P_GA_AVOID_HP || nearest_foe <= P_AVOID_DIST)'),
    ('main.cpp', 'bool killable = tgt && tgt->hp <= me.strength() * 2.0f;',
                 'bool killable = tgt && tgt->hp <= me.strength() * (P_GA_KILL_X / 10.0f);'),
    ('main.cpp', 'bool favourable = ours >= 0.9 * theirs;',
                 'bool favourable = ours * 100.0 >= P_GA_FAV * theirs;'),
    ('main.cpp', 'if (on_spawn && hpr < 0.95f) {',
                 'if (on_spawn && hpr * 100 < P_GA_SPAWN_HEAL) {'),
    ('fight.h', 'if (fc > mc + P_KITE_OUT && tc > oc * 1.3) return false;',
                'if (fc > mc + P_KITE_OUT && tc * 100.0 > oc * P_GA_KITE_HP) return false;'),
]

NAMES = list(GENES)

# Known genomes that can replace the defaults as the centre of the search (`ga.py prepare --center NAME`).
PRESETS = {
    # v44, online since 16 Oct 10:46 (exported genome 65a6d152b6)
    'ga65a6': {"P_FLEE_PCT": 29, "P_UNI_FLEE": 44, "P_RECALL_PCT": 54, "P_RECALL_NEAR": 7, "P_BAIL_PCT": 12,
               "P_AVOID_DIST": 4, "P_GA_AVOID_HP": 60, "P_ENGAGE2": 74, "P_GA_FAV": 83, "P_GA_KILL_X": 5,
               "P_LOWHP": 50, "P_GA_SPAWN_HEAL": 87, "P_FRONT_ZONE": 3, "P_FRONT_OUT": 145, "P_KITE_ZONE": 4,
               "P_KITE_OUT": 2, "P_GA_KITE_HP": 128, "P_VOLLEY": 43, "P_CHASE_GEMS": 144, "P_DANGER": 4,
               "P_DANGER_T": 45, "P_DANGER_R": 5},
}


def set_center(g):
    """Make genome g the default (= the control and the centre of the search). Literal defaults in LITERALS stay
    those of the base source; the instrumented build patches them at run time anyway."""
    for k, v in g.items():
        d, lo, hi, what = GENES[k]
        GENES[k] = (v, lo, hi, what)
MAGIC = (0x314D4147, 0x5EED1234)  # 'GAM1', then a second word: marks the genome array inside the wasm


def default():
    return {k: v[0] for k, v in GENES.items()}


def to_unit(g):
    """Genome dict -> list of floats in [0, 1]."""
    return [(g[k] - GENES[k][1]) / (GENES[k][2] - GENES[k][1]) for k in NAMES]


def from_unit(x):
    """List of floats in [0, 1] -> genome dict of ints."""
    out = {}
    for k, u in zip(NAMES, x):
        lo, hi = GENES[k][1], GENES[k][2]
        out[k] = int(round(lo + min(1.0, max(0.0, u)) * (hi - lo)))
    return out


def diff(g, base=None):
    base = base or default()
    return {k: g[k] for k in NAMES if g[k] != base[k]}
