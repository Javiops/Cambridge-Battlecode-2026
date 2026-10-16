// P_HUNT: sparring-only specialist "intercepts farming champions at camps and altars".
// The first P_HUNT_N champions (draft order) stop farming between rounds P_HUNT_FROM and P_HUNT_TO and patrol
// the enemy's farm: the camp groups nearest the enemy spawn and the altars they bank on, in pairs (hunter k>0
// walks to hunter 0 when more than 3 away). On sight they chase a foe within P_HUNT_CHASE (gem carriers first).
// Off (P_HUNT 0) the bot is unchanged.
#ifndef P_HUNT_N
#define P_HUNT_N 2
#endif
#ifndef P_HUNT_FROM
#define P_HUNT_FROM 0
#endif
#ifndef P_HUNT_TO
#define P_HUNT_TO 2000
#endif
#ifndef P_HUNT_SEE
#define P_HUNT_SEE 8
#endif
#ifndef P_HUNT_CHASE
#define P_HUNT_CHASE 10
#endif
#ifndef P_HUNT_ODDS
#define P_HUNT_ODDS 1
#endif
#ifndef P_HUNT_K
#define P_HUNT_K 4
#endif
namespace hunt {
inline int n_hunters(const State& s) {
    int n = P_HUNT_N;
    if (s.roster <= 3) n = std::min(n, 1);
    return n;
}
inline bool is_hunter(const State& s, int round) {
    return round >= P_HUNT_FROM && round < P_HUNT_TO && s.ally_idx >= 0 && s.ally_idx < n_hunters(s);
}
// Patrol points: the P_HUNT_K camp groups nearest the enemy spawn (not on it) and the 2 altars nearest it.
inline std::vector<vec2> patrol(const State& s) {
    std::vector<std::pair<int, vec2>> gs, as;
    for (auto& g : s.groups) {
        if (g.monolith || s.en_spawn.is_set(g.center)) continue;
        gs.push_back({dist(g.center, s.en_center), g.center});
    }
    for (auto& a : s.altars) as.push_back({dist(a, s.en_center), a});
    std::sort(gs.begin(), gs.end(), [](auto& x, auto& y) { return x.first < y.first; });
    std::sort(as.begin(), as.end(), [](auto& x, auto& y) { return x.first < y.first; });
    std::vector<vec2> out;
    for (int i = 0; i < static_cast<int>(gs.size()) && i < P_HUNT_K; ++i) out.push_back(gs[i].second);
    for (int i = 0; i < static_cast<int>(as.size()) && i < 2; ++i) out.push_back(as[i].second);
    return out;
}
inline bool walk(State& s, bc::champion& me, int round, const std::vector<Foe>& foes) {
    vec2 pos = me.position();
    // chase the best visible prey (gems first, then nearest)
    const Foe* prey = nullptr;
    for (auto& f : foes) {
        if (f.d > P_HUNT_CHASE || s.en_spawn.is_set(f.p)) continue;
        if (!prey || f.gems > prey->gems || (f.gems == prey->gems && f.d < prey->d)) prey = &f;
    }
    bc::bitboard goal;
    if (prey) {
        goal.draw_chebyshev(prey->p, 1.0f);
        return step_towards(s, me, goal, true);
    }
    // pairs: follow the lead hunter
    if (s.ally_idx > 0) {
        bool done = false;
        attempt([&] {
            auto allies = bc::champions(*s.my);
            if (!allies.empty() && allies[0].is_alive() && !allies[0].is_recalling()) {
                vec2 lp = allies[0].position();
                if (!s.my_spawn.is_set(lp) && dist(lp, pos) > 3) {
                    bc::bitboard r;
                    r.draw_chebyshev(lp, 1.0f);
                    done = step_towards(s, me, r, false);
                }
            }
            return true;
        });
        if (done) return true;
    }
    auto pts = patrol(s);
    if (pts.empty()) return false;
    // visit points in turn; the leg changes every 25 rounds or on arrival
    static int leg = 0, leg_r = -100;
    if (round - leg_r >= 25 || dist(pos, pts[leg % pts.size()]) <= 2) { ++leg; leg_r = round; }
    goal.draw_chebyshev(pts[leg % pts.size()], 2.0f);
    return step_towards(s, me, goal, false);
}
}  // namespace hunt
