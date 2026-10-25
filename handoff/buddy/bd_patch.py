# bd_patch.py SRC W : buddy-v1. Followers (roster slots 1, 3, 4) value their leader's claimed camp group (slot 0, 2, 3)
# at W%, past the share cap and the cluster solo rule, so pairs finish a camp together and walk to the next one together.
import sys
src, w = sys.argv[1], sys.argv[2]
p = open(src + '/params.h').read()
p += '\n#ifndef P_BD\n#define P_BD %s       // buddy-v1: follower score %% for its leader\'s claimed group (0 = off)\n#endif\n#define P_BD_FROM 30\n#define P_BD_UNTIL 300\n' % w
open(src + '/params.h', 'w').write(p)
m = open(src + '/main.cpp').read()
a = '    bool cached = s.pd_pos == pos && s.pd_gd.size() == s.groups.size();\n'
assert m.count(a) == 1
m = m.replace(a, '''    // buddy-v1 (top 10 vs band 30-60, near maps r30-150: walking rounds paired 55-57%, ours 37-39%; at a camp both 61%):
    // a follower takes its leader's claimed group, so the pair leaves a camp together and walks to the next together.
    int bd_g = -1;
    if (P_BD && round >= P_BD_FROM && round <= P_BD_UNTIL && s.ally_idx >= 1) {
        const int lead_k = (s.ally_idx & 1) ? s.ally_idx - 1 : (s.ally_idx == 4 ? 3 : -1);
        if (lead_k >= 0 && lead_k < claim_slots(s) && lead_k < s.roster) {
            const int claim = claim_value(s, sm, lead_k);
            if (claim > 0 && claim - 1 < static_cast<int>(s.groups.size())) bd_g = claim - 1;
        }
    }
''' + a, 1)
b = '        if (claimers >= cap && i != s.target && !lead) continue;\n'
assert m.count(b) == 1
m = m.replace(b, '        if (claimers >= cap && i != s.target && !lead && static_cast<int>(i) != bd_g) continue;\n')
c = '&& !(P_RC2 && g.gems >= 20)) score *= pack ? 1.0 : 0.3;'
assert m.count(c) == 1
m = m.replace(c, '&& !(P_RC2 && g.gems >= 20) && static_cast<int>(i) != bd_g) score *= pack ? 1.0 : 0.3;')
d = '#if P_E2 == 1\n        if (g.wolf_only)'
assert m.count(d) == 1
m = m.replace(d, '        if (static_cast<int>(i) == bd_g) score *= P_BD / 100.0;\n' + d)
open(src + '/main.cpp', 'w').write(m)
