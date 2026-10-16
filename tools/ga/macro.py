"""Macro genes: the economy side of the bot (tributes, shop, camp choice and sharing, recall trips, draft, holding).

genome.py holds the fight weights and structure.py the fight structure; these are the remaining run-time P_* macros
of bots/study27-economy that decide where the gems come from. Each default equals the base bot's value, so the
default genome is still the base bot. Macros used in `#if` are only genes where macro_genome.LITERALS rewrites the `#if` (P_E_RETARGET, P_NE_POWER_OPEN): a
patchable genome can only change what the bot reads at run time.
"""

import macro_genome as MG  # the macro GA's gene table (thread "GA macro", PR #24): single source for shared genes

BOOLS = {'P_NOGOLD', 'P_ONE_CAP', 'P_SHOPUNI', 'P_NE_POWER_OPEN'}
# name: (default, lo, hi, kind, what it decides). kind 'bool' flips on mutation, 'int' takes a gaussian step.
MACRO = {k: (d, lo, hi, 'bool' if k in BOOLS else 'int', doc) for k, (d, lo, hi, doc) in MG.GENES.items()}
# genes only the farm evolves (not in PR #24's table)
EXTRA = {
    'P_SAFE_RECALL':   (1, 0, 1,        'bool', 'recall only with no foe within 8 and not hit for 2 rounds'),
    'P_PATHD':         (1, 0, 1,        'bool', 'camp choice by walking distance instead of straight line'),
    'P_LEAN_RADIUS':   (12, 6, 20,      'int',  'camps within this many tiles are rescanned each turn'),
    'P_DRAFTUNI':      (2, 0, 2,        'int',  'draft: 0 old, 1 caster draft always, 2 caster draft on short maps'),
    'P_SWEEP':         (3, 0, 3,        'int',  'cast ready spells at foes in range: 0 off .. 3 cast first'),
    'P_AOE':           (2, 0, 2,        'int',  'area spell aim: 0 at the target, 1 covering it, 2 most foes'),
    'P_U34_RESET_LIVE': (2, 0, 2,       'int',  'spend the attack reset only on a live target: 0 never, 1 some maps, 2 all'),
    'P_MONO':          (1, 0, 1,        'bool', 'contest fix: gold first, then the whole team on the monolith'),
    'P_UNSTICK':       (30, 0, 60,      'int',  'standing still this many turns away from fights: move (0 = off)'),
}
for k, v in EXTRA.items():
    MACRO.setdefault(k, v)

NAMES = list(MACRO)
LITERALS = MG.LITERALS  # literal constants / #if switches of the base turned into P_GA_* genes
