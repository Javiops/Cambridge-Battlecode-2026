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
#ifndef P_TRACK
#define P_TRACK 0
#endif
#ifndef P_TRACK_LOG
#define P_TRACK_LOG 0
#endif
#ifndef P_TRACK_STATR
#define P_TRACK_STATR 10
#endif
#ifndef P_TRACK_MEM
#define P_TRACK_MEM 3     // rounds an unseen enemy keeps counting at its last tile (ghost)
#endif

#ifndef P_TRACK_FAV
#define P_TRACK_FAV 0     // >0: engage verdict = Lanchester power (sum hp x sum dps) of us vs them around the target,
#endif                    //     known enemies (visible + ghosts) included; favourable when ours*100 >= this * theirs
#ifndef P_TRACK_ISO
#define P_TRACK_ISO 0     // >0: target a lone enemy (no other known enemy within 6) that the allies near it kill
#endif                    //     within this many rounds, faster than it can kill the weakest of them
#ifndef P_TRACK_RET
#define P_TRACK_RET 0     // >0: backing off steps toward healthy allies remembered within this many rounds, not only
#endif                    //     the ones in sight (safe_step's tie-break toward an ally)
#ifndef P_TRACK_ALLYMEM
#define P_TRACK_ALLYMEM 2 // rounds a remembered ally still counts at its last tile
#endif

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

// A remembered enemy that is not in sight now: seen within P_TRACK_MEM rounds, alive as far as we know.
inline bool ghost(int k, int round) {
    const EnemyMem& e = M.en[k];
    return e.alive && e.seen_r < round && round - e.seen_r <= P_TRACK_MEM;
}

#if P_TRACK_LOG
struct Log {
    long turns = 0, contact = 0, ghost_turns = 0, ghost_near = 0, vis_tiles = 0, vis_n = 0;
    long al_alive = 0, al_vis = 0, deaths = 0, death_ghost = 0, death_vis = 0, death_foes = 0;
    long fav_flip = 0, dead_seen = 0, dead_unseen = 0, fuel = 0;
    int last_alive_r = -1, last_vis8 = 0, last_ghost8 = 0;
};
inline Log L;
#endif

inline void update(State& s, bc::champion& me, const std::vector<Foe>& foes, vec2 pos, int round) {
#if P_TRACK_LOG
    std::uint64_t f0 = bc::fuel_remaining();
#endif
    if (M.eroster.empty())
        attempt([&] {
            M.eroster = bc::champions(*s.en);
            M.aroster = bc::champions(*s.my);
            M.ne = std::min<int>(8, static_cast<int>(M.eroster.size()));
            M.na = std::min<int>(8, static_cast<int>(M.aroster.size()));
            return true;
        });
    M.round = round;
    for (int k = 0; k < M.ne; ++k) {
        EnemyMem& e = M.en[k];
        bool al = true;
        attempt([&] { al = M.eroster[k].is_alive(); return true; });
        if (!al && e.alive) {
            e.dead_r = round;
#if P_TRACK_LOG
            if (round - e.seen_r <= 1) ++L.dead_seen; else ++L.dead_unseen;
#endif
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
    attempt([&] {
        for (auto& a : bc::vision::champions(*s.my)) {
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
    if (round % 4 == 0)
        for (int k = 0; k < M.na; ++k) attempt([&] { M.al[k].alive = M.aroster[k].is_alive(); return true; });

#if P_TRACK_LOG
    ++L.turns;
    L.fuel += static_cast<long>(f0 - bc::fuel_remaining());
    int vis8 = 0, gh8 = 0;
    for (auto& f : foes) if (f.d <= 8) ++vis8;
    for (int k = 0; k < M.ne; ++k) if (ghost(k, round) && dist(M.en[k].p, pos) <= 8) ++gh8;
    if (vis8) { ++L.contact; if (gh8) ++L.ghost_turns; L.ghost_near += gh8; }
    if (round % 50 == 0) attempt([&] { L.vis_tiles += me.visible_tiles().count(); ++L.vis_n; return true; });
    for (int k = 0; k < M.na; ++k) if (M.al[k].alive && !(M.aroster[k] == me)) { ++L.al_alive; if (M.al[k].seen_r == round) ++L.al_vis; }
    L.last_alive_r = round; L.last_vis8 = vis8; L.last_ghost8 = gh8;
    if (round % 250 == 0 || round == 1999)
        std::printf("[track] r=%d %s turns=%ld contact=%ld ghost_turns=%ld ghosts=%ld vis=%.0f allies_vis=%ld/%ld deaths=%ld d_vis=%ld d_ghost=%ld dead_seen=%ld dead_unseen=%ld fuel=%ld\n",
                    round, s.name.c_str(), L.turns, L.contact, L.ghost_turns, L.ghost_near,
                    L.vis_n ? double(L.vis_tiles) / L.vis_n : 0.0, L.al_vis, L.al_alive, L.deaths, L.death_vis, L.death_ghost, L.dead_seen, L.dead_unseen, L.turns ? L.fuel / L.turns : 0);
#endif
}

#if P_TRACK_LOG
inline void on_dead(int round) {  // called on a dead turn: the first one after a live turn counts a death
    if (L.last_alive_r == round - 1) { ++L.deaths; L.death_vis += L.last_vis8; L.death_ghost += L.last_ghost8; }
    L.last_alive_r = -5;
}
#endif

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

// P_TRACK_RET: healthy (> 40% hp) allies we saw within P_TRACK_RET rounds and do not see now.
inline void remembered_allies(bc::champion& me, std::vector<vec2>& out, int round) {
    for (int k = 0; k < M.na; ++k) {
        const AllyMem& a = M.al[k];
        if (M.aroster[k] == me || !a.alive || a.seen_r == round || round - a.seen_r > P_TRACK_RET) continue;
        if (a.hp > 0.4f * a.mhp) out.push_back(a.p);
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
