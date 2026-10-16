"""Macro genes: the economy side of the bot (tributes, shop, camp choice and sharing, recall trips, draft, holding).

genome.py holds the fight weights and structure.py the fight structure; these are the remaining run-time P_* macros
of bots/study27-economy that decide where the gems come from. Each default equals the base bot's value, so the
default genome is still the base bot. Macros used in `#if` (P_E_RETARGET, P_CALLHELP, P_FM) are not genes: a
patchable genome can only change what the bot reads at run time.
"""

# name: (default, lo, hi, kind, what it decides). kind 'bool' flips on mutation, 'int' takes a gaussian step.
MACRO = {
    'P_TRIBUTE_GEMS':  (12, 4, 40,      'int',  'walk to an altar once carrying this many gems'),
    'P_TRIBUTE_NEAR':  (8, 2, 16,       'int',  'tribute 10+ gems when an altar is this close'),
    'P_LATE_ROUND':    (1850, 1500, 1990, 'int', 'after this round, tribute any gems at all'),
    'P_CHAIN':         (36, 0, 80,      'int',  'below this many gems, chain to the next camp before an altar (0 = off)'),
    'P_CHAIN_R':       (8, 3, 14,       'int',  'chain only to a camp this close'),
    'P_SHOP_GOLD':     (240, 100, 500,  'int',  'recall to shop with this much gold when under half hp'),
    'P_SHOP_RECALL':   (180, 0, 400,    'int',  'shop trip home with this much gold when safe (0 = off)'),
    'P_SHOP_PLAN':     (3, 0, 3,        'int',  'item plan: 0 old, 1 emblem then power, 2 tank build, 3 top-10 winners'),
    'P_SHOPUNI':       (1, 0, 1,        'bool', 'Ren, Prism and Stellar buy power + durability'),
    'P_SAFE_RECALL':   (1, 0, 1,        'bool', 'recall only with no foe within 8 and not hit for 2 rounds'),
    'P_CAPRECALL':     (2, 0, 2,        'int',  'recall on the capture tiles: 0 off, 1 when wanted, 2 also free heal/shop trips'),
    'P_CAPRECALL_DELAY': (1, 0, 5,      'int',  'turns on the capture tiles before starting that recall'),
    'P_MAX_SHARE':     (4, 1, 5,        'int',  'at most this many of us on one monster camp'),
    'P_SHAREEXP':      (75, 30, 100,    'int',  'big camp value = gems / team^(this/100) for each joiner'),
    'P_STACK_HP':      (3000, 1500, 6000, 'int', 'big camp = this much monster hp (stacking allowed)'),
    'P_PAIR':          (2, 0, 3,        'int',  'gem clusters take this many of us (0 = one)'),
    'P_ONE_CAP':       (1, 0, 1,        'bool', 'a free reward needs only one of us'),
    'P_GOLD_W_EARLY':  (25, 0, 80,      'int',  'camp value: gold worth this % of a gem before round 600'),
    'P_GOLD_W_LATE':   (24, 0, 80,      'int',  'camp value: gold worth this % of a gem after round 600'),
    'P_NOGOLD':        (1, 0, 1,        'bool', 'skip gold-only clusters'),
    'P_PATHD':         (1, 0, 1,        'bool', 'camp choice by walking distance instead of straight line'),
    'P_HALF':          (30, 0, 100,     'int',  'camps on the enemy half score x this % (0 = no penalty)'),
    'P_STICK':         (125, 100, 200,  'int',  'keep the current camp target unless another scores this % more'),
    'P_RESPAWN':       (4, 0, 10,       'int',  'walk to a camp that respawns within the walk + this many rounds'),
    'P_RESERVE_PCT':   (-60, -100, 40,  'int',  'camp fight budget: keep this % of max hp in reserve'),
    'P_OWN_ALTAR':     (20, 0, 60,      'int',  'extra distance cost of an altar on the enemy half'),
    'P_LEAN_RADIUS':   (12, 6, 20,      'int',  'camps within this many tiles are rescanned each turn'),
    'P_DRAFTUNI':      (2, 0, 2,        'int',  'draft: 0 old, 1 caster draft always, 2 caster draft on short maps'),
    'P_UNI_PATH':      (45, 20, 90,     'int',  'short map = spawn-to-spawn path at most this long (caster draft)'),
    'P_HOLD':          (200, 0, 400,    'int',  'hold the centre altar: camps near it score x this % (0 = off)'),
    'P_HOLD_R':        (6, 2, 12,       'int',  'camps within this of the held altar count as held'),
    'P_SWEEP':         (3, 0, 3,        'int',  'cast ready spells at foes in range: 0 off .. 3 cast first'),
    'P_AOE':           (2, 0, 2,        'int',  'area spell aim: 0 at the target, 1 covering it, 2 most foes'),
    'P_U34_RESET_LIVE': (2, 0, 2,       'int',  'spend the attack reset only on a live target: 0 never, 1 some maps, 2 all'),
    'P_R34_BANKCOST':  (300, 100, 600,  'int',  'banking cost used by the monolith plan'),
    'P_MONO':          (1, 0, 1,        'bool', 'contest fix: gold first, then the whole team on the monolith'),
    'P_UNSTICK':       (30, 0, 60,      'int',  'standing still this many turns away from fights: move (0 = off)'),
}

NAMES = list(MACRO)
