# bw_patch.py SRC : buddy-walk. On the way to our camp, a buddy (slots 0-1, 2-3, 4-3) seen 4-12 tiles away whose claimed
# camp is within P_PF_R of ours: step next to it, at most P_BW_WAIT rounds per target. Real positions only (vision).
import sys
src = sys.argv[1]
p = open(src + '/params.h').read()
p += '\n#ifndef P_BW\n#define P_BW 1\n#endif\n#define P_BW_WAIT 8\n#define P_BW_UNTIL 300\n'
open(src + '/params.h', 'w').write(p)
m = open(src + '/main.cpp').read()
a = '    if (P_PF_WALK && pf_on(round) && !on_spawn && foes.empty()'
assert m.count(a) == 1
m = m.replace(a, '''    if (P_BW && round >= 30 && round <= P_BW_UNTIL && !on_spawn && foes.empty() && s.ally_idx >= 0 && s.target >= 0 &&
        s.target < static_cast<int>(s.groups.size()) && me.can_move() && dist(pos, s.groups[s.target].center) >= 4) {
        static int bw_target[8] = {-1, -1, -1, -1, -1, -1, -1, -1}, bw_n[8] = {0, 0, 0, 0, 0, 0, 0, 0};
        const int me_k = std::min(s.ally_idx, 7);
        if (bw_target[me_k] != s.target) { bw_target[me_k] = s.target; bw_n[me_k] = 0; }
        const int bk = s.ally_idx == 4 ? 3 : (s.ally_idx ^ 1);
        std::optional<vec2> mate;
        if (bw_n[me_k] < P_BW_WAIT && bk < s.roster && bk < claim_slots(s)) {
            const int claim = claim_value(s, read_sm(), bk);
            if (claim > 0 && claim - 1 < static_cast<int>(s.groups.size()) && dist(s.groups[claim - 1].center, s.groups[s.target].center) <= P_PF_R)
                attempt([&] {
                    auto allies = my_roster(s);
                    if (bk >= static_cast<int>(allies.size()) || !allies[bk].is_alive()) return true;
                    const vec2 ap = allies[bk].position();  // throws when out of vision
                    const int d = dist(ap, pos);
                    if (d >= 4 && d <= 12 && !s.my_spawn.is_set(ap)) mate = ap;
                    return true;
                });
        }
        if (mate) {
            bc::bitboard ring;
            ring.draw_chebyshev(*mate, 2.0f);
            ring &= ~s.en_spawn;
            if (step_towards(s, me, ring, false)) {
                ++bw_n[me_k];
                g_mode = "bw-walk";
                return;
            }
        }
    }
''' + a, 1)
open(src + '/main.cpp', 'w').write(m)
