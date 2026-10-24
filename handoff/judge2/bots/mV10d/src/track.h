// track.h - per-champion memory of the fight situation (P_TRACK, 2026-10-16).
// Each champion's program keeps its globals between turns, so this is private memory: what THIS champion
// has seen. Vision is per champion (bc::vision::champions lists what this body sees; position() of anything
// else throws), so an enemy that steps out of our sight vanishes from the foe list the next round.
//
// Memory, per enemy roster slot (bc::champions(enemy) order, at most 8):
//   p, seen_r       last tile and round we saw it (seen_r == round: visible now)
//   hp, mhp         health and max health when last seen
//   str, foc, rng   strength, focus, attack range (info(), one call)
//   gems            gems it carried
//   dps, stat_r     damage per round estimate (fight::unit_dps: strength + focus x 1.5 / 8), refreshed every 10 rounds
//   alive / dead_r  is_alive() of the handle (readable out of vision), round we saw it dead
// and per ally roster slot: p, seen_r, hp, mhp, ranged, dps (only allies inside our vision update it).
// Included before fight.h (fight.h's safe_step reads remembered allies).
// Fuel: one champions(enemy) + one champions(ally) list a round, one info() per visible foe within
// P_TRACK_STATR tiles, nothing else. With P_TRACK 0 nothing here runs.

// The enemy half of the memory is only kept when a use reads it (FAV, ISO); RET reads allies only.
#define TRACK_ENEMIES (P_TRACK_FAV || P_TRACK_ISO)

namespace track {

struct EnemyMem {
    vec2 p{0, 0};
    int seen_r = -1000;
    int dead_r = -1000;
    bool alive = true;
    float hp = 0, mhp = 1, str = 0, foc = 0;
    int rng = 1, gems = 0;
    double dps = 60;
    int stat_r = -1000;
};
struct AllyMem {
    vec2 p{0, 0};
    int seen_r = -1000;
    float hp = 0, mhp = 1;
    bool ranged = false;
    bool alive = true;
    double dps = 60;
    int stat_r = -1000;
};

struct Memory {
    int round = -1;
    int ne = 0, na = 0;
    EnemyMem en[8];
    AllyMem al[8];
    std::vector<bc::champion> eroster, aroster;
};
inline Memory M;


inline void update(State& s, bc::champion& me, const std::vector<Foe>& foes, vec2 pos, int round) {
    if (!TRACK_ENEMIES) return;  // RET alone keeps its own memory in safe_step, no API calls here
    if (M.eroster.empty())
        attempt([&] {
            M.eroster = bc::champions(*s.en);
            M.aroster = bc::champions(*s.my);
            M.ne = std::min<int>(8, static_cast<int>(M.eroster.size()));
            M.na = std::min<int>(8, static_cast<int>(M.aroster.size()));
            return true;
        });
    M.round = round;
    if (TRACK_ENEMIES) {
    for (int k = 0; k < M.ne; ++k) {
        EnemyMem& e = M.en[k];
        bool al = true;
        attempt([&] { al = M.eroster[k].is_alive(); return true; });
        if (!al && e.alive) {
            e.dead_r = round;
        }
        e.alive = al;
    }
    for (auto& f : foes) {
        int k = -1;
        for (int j = 0; j < M.ne; ++j)
            if (M.eroster[j] == f.c) { k = j; break; }
        if (k < 0) continue;
        EnemyMem& e = M.en[k];
        e.p = f.p;
        e.seen_r = round;
        e.hp = f.hp;
        e.gems = f.gems;
        if (f.d <= P_TRACK_STATR && round - e.stat_r >= 10)  // strength/focus only change with items
            attempt([&] {
                e.mhp = f.c.max_health();
                e.str = f.c.strength();
                e.foc = f.c.focus();
                e.rng = f.c.attack_range();
                e.dps = std::max(10.0, e.str + e.foc * 1.5 / 8.0);  // as fight::unit_dps
                e.stat_r = round;
                return true;
            });
    }
    }
    attempt([&] {
        for (auto& a : my_champs(s)) {
            int k = -1;
            for (int j = 0; j < M.na; ++j)
                if (M.aroster[j] == a) { k = j; break; }
            if (k < 0) continue;
            AllyMem& m = M.al[k];
            try {
                m.p = a.position();
                m.hp = a.health();
                m.seen_r = round;
                if (round - m.stat_r >= 10) {
                    m.mhp = a.max_health();
                    m.ranged = a.attack_range() > 1;
                    m.dps = std::max(10.0, a.strength() + a.focus() * 1.5 / 8.0);
                    m.stat_r = round;
                }
            } catch (...) {
            }
        }
        return true;
    });
    if (TRACK_ENEMIES && round % 4 == 0)  // RET checks is_alive only for the allies it is about to use
        for (int k = 0; k < M.na; ++k) attempt([&] { M.al[k].alive = M.aroster[k].is_alive(); return true; });

}


// ---- uses -------------------------------------------------------------------------------------------
struct Side {
    double hp = 0, dps = 0;
    int n = 0;
    double power() const { return hp * dps; }  // Lanchester square: a side's strength ~ total hp x total damage
};

// Known enemies within r of c: in sight now, or ghosts (seen within P_TRACK_MEM rounds at a tile within r).
inline Side enemies_near(vec2 c, int r, int round) {
    Side o;
    for (int k = 0; k < M.ne; ++k) {
        const EnemyMem& e = M.en[k];
        if (!e.alive || round - e.seen_r > P_TRACK_MEM || dist(e.p, c) > r) continue;
        o.hp += e.hp; o.dps += e.dps; ++o.n;
    }
    return o;
}

// Me plus the allies within r of c: in sight now or seen within P_TRACK_ALLYMEM rounds.
inline Side allies_near(bc::champion& me, vec2 c, int r, int round) {
    Side o;
    vec2 pos = me.position();
    if (dist(pos, c) <= r) {
        o.hp += me.health(); ++o.n;
        attempt([&] { o.dps += std::max(10.0, static_cast<double>(me.strength() + me.focus() * 1.5f / 8.0f)); return true; });
    }
    for (int k = 0; k < M.na; ++k) {
        const AllyMem& a = M.al[k];
        if (M.aroster[k] == me || !a.alive || round - a.seen_r > P_TRACK_ALLYMEM || dist(a.p, c) > r) continue;
        o.hp += a.hp; o.dps += a.dps; ++o.n;
    }
    return o;
}

inline bool favourable(bc::champion& me, vec2 c, int round) {
    Side us = allies_near(me, c, 8, round), them = enemies_near(c, 8, round);
    return us.power() * 100.0 >= P_TRACK_FAV * them.power();
}

// P_TRACK_RET: safe_step's healthy (> 40% hp) allies in sight are remembered with their round; on later back-offs
// the ones seen within P_TRACK_RET rounds are added to the list (they may have walked out of our sight). Reuses the
// positions safe_step already read, so it costs no API call.
struct RetMem {
    vec2 p[8];
    int r[8] = {-1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000};
    int next = 0;
};
inline RetMem R;
inline void remembered_allies(std::vector<vec2>& allies, int round) {
    std::size_t now = allies.size();
    for (int k = 0; k < 8; ++k)
        if (R.r[k] < round && round - R.r[k] <= P_TRACK_RET) allies.push_back(R.p[k]);
    for (std::size_t i = 0; i < now; ++i) {
        R.p[R.next] = allies[i];
        R.r[R.next] = round;
        R.next = (R.next + 1) & 7;
    }
}

// A lone enemy we kill quickly: no other known enemy within 6 of it, the allies within 6 of it (me included)
// kill it within P_TRACK_ISO rounds and before it kills the weakest of them.
template <class Gone>
inline Foe* isolated(State& s, bc::champion& me, std::vector<Foe>& foes, int round, Gone gone) {
    Foe* best = nullptr;
    double best_t = 1e18;
    for (auto& f : foes) {
        if (f.d > 8 || s.en_spawn.is_set(f.p) || gone(f)) continue;
        int k = -1;
        for (int j = 0; j < M.ne; ++j) if (M.eroster[j] == f.c) { k = j; break; }
        if (k < 0) continue;
        if (enemies_near(f.p, 6, round).n > 1) continue;
        Side us = allies_near(me, f.p, 6, round);
        if (us.dps <= 0) continue;
        double t_kill = f.hp / us.dps;
        double weakest = me.health();
        for (int j = 0; j < M.na; ++j) {
            const AllyMem& a = M.al[j];
            if (M.aroster[j] == me || !a.alive || round - a.seen_r > P_TRACK_ALLYMEM || dist(a.p, f.p) > 6) continue;
            weakest = std::min(weakest, static_cast<double>(a.hp));
        }
        double t_die = weakest / std::max(10.0, M.en[k].dps);
        if (t_kill > P_TRACK_ISO || t_kill >= t_die) continue;
        if (t_kill < best_t) { best_t = t_kill; best = &f; }
    }
    return best;
}

}  // namespace track
