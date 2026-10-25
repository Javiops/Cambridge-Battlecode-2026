# bd_resync.py SRC : buddy-v1 resync. A follower that is not committed re-chooses once whenever its leader's claim changes
# to a group other than its own target (the target is sticky, so without this a pair stays apart until the next refresh).
import sys
src = sys.argv[1]
m = open(src + '/main.cpp').read()
a = "    bool refresh = !committed && round - s.target_round >= (ball_on(s, round) ? 3 : target_refresh);\n"
assert m.count(a) == 1
m = m.replace(a, a + '''    if (P_BD && !committed && !refresh && round >= P_BD_FROM && round <= P_BD_UNTIL && s.ally_idx >= 1 && s.ally_idx < 8) {
        static int bd_seen[8] = {-1, -1, -1, -1, -1, -1, -1, -1};
        const int lead_k = (s.ally_idx & 1) ? s.ally_idx - 1 : (s.ally_idx == 4 ? 3 : -1);
        if (lead_k >= 0 && lead_k < claim_slots(s) && lead_k < s.roster) {
            const int lc = static_cast<int>(claim_value(s, read_sm(), lead_k)) - 1;
            if (lc != bd_seen[s.ally_idx]) {
                bd_seen[s.ally_idx] = lc;
                if (lc >= 0 && lc != s.target) refresh = true;
            }
        }
    }
''', 1)
open(src + '/main.cpp', 'w').write(m)
