# spf_patch.py SRC MODE : spellfirst-v1. Top 10 Vesper at 4 tiles from the nearest foe casts in 20% of her turns, ours 7%:
# fight::kite steps first (out of reach, often to 5) and only then tries its spells. MODE 1: in kite, with the focus within
# spell range but beyond attack range, cast before the step. MODE 2: also engage() casts at spell range (was 3) on champions.
import sys
src, mode = sys.argv[1], int(sys.argv[2])
p = open(src + '/params.h').read()
p += '\n#ifndef P_SPF\n#define P_SPF %d  // spellfirst-v1\n#endif\n' % mode
open(src + '/params.h', 'w').write(p)
f = open(src + '/fight.h').read()
a = '    if (me.can_cast()) {  // 2. spells: stun whoever can reach us, else damage the focus, else stun it\n'
b = '    if (dist(pos, focus->p) <= range) basic_attack(s, me, focus->c, focus->p);  // 3. shoot\n'
assert f.count(a) == 1 and f.count(b) == 1
i, j = f.index(a), f.index(b)
blk = f[i:j]
f = f[:i] + '    if (!sp_done) spells();\n' + f[j:]
c = '    if (me.can_move()) {  // 1. step: out of every foe\'s reach, focus within spell range, near the team\n'
assert f.count(c) == 1
f = f.replace(c, '    bool sp_done = false;\n    auto spells = [&]() {\n' + blk + '    };\n'
              '    if (P_SPF && me.can_cast() && dist(pos, focus->p) <= SPELL_RANGE && dist(pos, focus->p) > range) {  // spellfirst-v1\n'
              '        spells();\n        sp_done = true;\n    }\n' + c, 1)
open(src + '/fight.h', 'w').write(f)
if mode >= 2:
    m = open(src + '/main.cpp').read()
    e = '    if (d <= (s.melee ? range + 1 : 3)) acted = cast_offense(s, me, tgt, tpos, champ);\n'
    assert m.count(e) == 1
    m = m.replace(e, '    if (d <= (s.melee ? range + 1 : ((P_SPF >= 2 && champ) ? SPELL_RANGE : 3))) acted = cast_offense(s, me, tgt, tpos, champ);\n')
    open(src + '/main.cpp', 'w').write(m)
