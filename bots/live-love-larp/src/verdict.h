// verdict.h - decide a fight once, at first contact, and hold the decision (2026-10-16, thread
// "Decidir la pelea antes de empezar"). Included by main.cpp after fight.h.
//
// Why (63 online v52 games, 1,843 of our fight episodes, first contact = first round an enemy champion is
// within 6): our own hp at first contact does not predict a lost fight (AUC 0.51) but the power ratio of the
// two groups does (health x damage of us + allies within 6 against the enemies in view). Below 0.8 we lose
// 40% and win 4%; we stay in 85% of those fights; the few times we left at once we lost 24%; our rivals leave
// at once 42% of the time and lose 19%. Above 4 we win only 24% where the top two win 41%.
//
//   P_PV        0 off (v52 unchanged); 1 = leave verdict only; 2 = leave and fight verdicts
//   P_PV_LEAVE  ratio x100 below which the first-contact verdict is "leave" (held until contact ends)
//   P_PV_FIGHT  ratio x100 at or above which the verdict is "fight": v52's "unfavourable" back-offs stop
//   P_PV_R      first contact = nearest enemy champion within this many tiles
//   P_PV_GAP    rounds without an enemy within 8 that end the engagement
//   P_PV_ER     enemies within this many tiles enter the ratio (8 = all in view)
//   P_PV_KEEPCAP 1: a leave verdict waits while capturing, unless a foe is within 3
// Hysteresis: "leave" flips to "fight" only if the ratio climbs to P_PV_FIGHT x 1.5 (allies arrived);
// "fight" flips to "leave" if it drops under P_PV_LEAVE x 0.75 (enemies arrived). The hp cuts of step 2
// (P_FLEE_PCT, P_UNI_FLEE) and P_LOWHP still apply.


namespace pv {

// Each champion runs its own program, so these globals are per champion.
inline int g_verdict = 0;    // 0 none (v52 rules), 1 fight, 2 leave
inline int g_last = -100;    // last round with an enemy champion within 8
inline bool g_judged = false;
inline bool g_v14 = false;   // t10plan-v14: the current leave came from the every-turn judgement
inline int g_v14n = 0;       // t10plan-v14: firings this game

// Health x damage of me + allies within 6 (alive, not recalling) over the enemies in view within 8.
inline double power_ratio(State& s, bc::champion& me, const std::vector<Foe>& foes) {
    vec2 pos = me.position();
    double oh = me.health(), od = fight::unit_dps(me), th = 0, td = 0;
    attempt([&] {
        for (auto& a : vis_champions(*s.my)) {
            try {
                if (a == me || !a.is_alive() || a.is_recalling()) continue;
                if (dist(a.position(), pos) > 6) continue;
                oh += a.health();
                od += fight::unit_dps(a);
            } catch (...) {
            }
        }
        return true;
    });
    for (auto& f : foes)
        if (f.d <= P_PV_ER && !s.en_spawn.is_set(f.p)) {
            th += f.hp;
            td += fight::unit_dps(f.c);
        }
    if (th <= 0) return 99.0;
    return (oh * od) / (th * td);
}

// Called once per turn at the start of step 3. Returns the verdict held for this engagement.
inline int verdict(State& s, bc::champion& me, const std::vector<Foe>& foes, int round, bool on_spawn) {
    int nearest = 99;
    for (auto& f : foes)
        if (!s.en_spawn.is_set(f.p)) nearest = std::min(nearest, f.d);
    if (nearest > 8) {
        if (round - g_last > P_PV_GAP) { g_verdict = 0; g_judged = false; g_v14 = false; }
        return g_verdict;
    }
    if (round - g_last > P_PV_GAP) { g_verdict = 0; g_judged = false; g_v14 = false; }
    g_last = round;
    if (on_spawn) return g_verdict;
    if (!g_judged) {
        if (nearest > P_PV_R) return 0;
        g_judged = true;
        double r = power_ratio(s, me, foes) * 100.0;
        g_verdict = r < P_PV_LEAVE ? 2 : false;
        return g_verdict;
    }
    if (g_verdict) {
        double r = power_ratio(s, me, foes) * 100.0;
        if (g_verdict == 2 && r >= P_PV_FIGHT * 1.5) { g_verdict = P_PV >= 2 ? 1 : 0; g_v14 = false; }
        else if (g_verdict == 1 && r < P_PV_LEAVE * 0.75) g_verdict = 2;
    }
    return g_verdict;
}

// t10plan-v14: judged every turn from r30 (state14.py: our champion kills begin as an even contact; the 2nd and 3rd rival
// arrive over the next 10 rounds and the held "stay" is never looked at again). With 2+ foes within P_PV_ER and the power
// ratio under P_V14_RATIO, or alone under P_V14_LOWHP % hp with any foe within P_PV_ER and the ratio under 1, the verdict
// becomes "leave" and holds like a first-contact leave (ends P_PV_GAP rounds after the last foe within 8).
// t10plan-v16: online v14 deaths r30-150 (death15.py, 80 games): fled and caught by a dash 0.24/game (kvvl 0.12, local 0.03);
// killers HoR / Vendetta, already within 1-2 tiles for the 8 rounds before the death. A melee foe with a dash ready reaches
// 2 (dash) + 1 (hit) + 1 (move) = 4 tiles: with 2+ foes within P_PV_ER and such a foe within P_V16_D, leave at ratio < P_V16_RATIO.
inline bool v16_dash_foe(const Foe& f) {
    bool d = false;
    attempt([&] {
        if (f.c.attack_range() > 1) return true;
        for (const auto& ab : f.c.abilities())
            if (ab.is_dash() && ab.cooldown() <= 1) d = true;
        return true;
    });
    return d;
}
inline int g_v16n = 0;
inline bool g_v16 = false;  // the current leave came from the v16 rule (flee by safe_step while a dash foe is near)

inline void v14_judge(State& s, bc::champion& me, const std::vector<Foe>& foes, int round, bool on_spawn, float hpr) {
    if (on_spawn || g_verdict == 2) return;
    int n = 0;
    for (auto& f : foes)
        if (f.d <= P_PV_ER && !s.en_spawn.is_set(f.p)) ++n;
    if (n == 0) return;
    int al = 0;
    vec2 pos = me.position();
    attempt([&] {
        for (auto& a : vis_champions(*s.my)) {
            try {
                if (a == me || !a.is_alive() || a.is_recalling()) continue;
                if (dist(a.position(), pos) <= 6) ++al;
            } catch (...) {
            }
        }
        return true;
    });
    if (!(n >= 2 || (al == 0 && hpr * 100 < P_V14_LOWHP))) return;
    double r = power_ratio(s, me, foes) * 100.0;
    bool leave = (n >= 2 && r < P_V14_RATIO) || (al == 0 && hpr * 100 < P_V14_LOWHP && r < 100);
    g_v16 = false;
    if (!leave && P_V16 && round >= P_V16_R && n >= 2 && r < P_V16_RATIO) {
        int dd = 99;
        for (auto& f : foes)
            if (f.d <= P_V16_D && !s.en_spawn.is_set(f.p) && v16_dash_foe(f)) dd = std::min(dd, f.d);
        if (dd <= P_V16_D) {
            leave = true;
            g_v16 = true;
            std::printf("[v16-dash] r=%d ch=%s foes=%d allies=%d ratio=%d hp=%d d=%d n=%d\n", round, s.name.c_str(), n, al,
                        static_cast<int>(r), static_cast<int>(hpr * 100), dd, ++g_v16n);
        }
    }
    if (!leave) return;
    g_verdict = 2;
    g_judged = true;
    g_last = round;
    g_v14 = true;
    ++g_v14n;
    if (g_v16) return;
    std::printf("[v14-leave] r=%d ch=%s foes=%d allies=%d ratio=%d hp=%d n=%d\n", round, s.name.c_str(), n, al, static_cast<int>(r),
                static_cast<int>(hpr * 100), g_v14n);
}

}  // namespace pv
