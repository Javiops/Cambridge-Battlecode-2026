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

#ifndef P_PV
#define P_PV 0
#endif
#ifndef P_PV_LEAVE
#define P_PV_LEAVE 80
#endif
#ifndef P_PV_FIGHT
#define P_PV_FIGHT 125
#endif
#ifndef P_PV_R
#define P_PV_R 6
#endif
#ifndef P_PV_GAP
#define P_PV_GAP 4
#endif
#ifndef P_PV_ER
#define P_PV_ER 8   // enemies counted in the ratio: within this many tiles
#endif
#ifndef P_PVSP
#define P_PVSP 0    // 1 = the ratio counts real spell damage (modifier x focus per cooldown, plus the volley ready now)
#endif
#ifndef P_PVSP_H
#define P_PVSP_H 6  // rounds of fight the ready volley is spread over
#endif
#ifndef P_PVSP_ITEMS
#define P_PVSP_ITEMS 1  // 1 = durability emblems (10% less incoming damage each) raise that side's effective health
#endif
#ifndef P_PV_REJUDGE
#define P_PV_REJUDGE 0  // 1 = a "no verdict" engagement is re-judged every round: leave if the ratio drops under P_PV_LEAVE x 0.75
#endif
#ifndef P_PV_KEEPCAP
#define P_PV_KEEPCAP 0  // 1 = a "leave" verdict does not pull a champion off a capture unless a foe is within 3
#endif

namespace pv {

// Each champion runs its own program, so these globals are per champion.
inline int g_verdict = 0;    // 0 none (v52 rules), 1 fight, 2 leave
inline int g_last = -100;    // last round with an enemy champion within 8
inline bool g_judged = false;

// P_PVSP (2026-10-17, user: "ten en cuenta el daño real de los hechizos"): unit_dps counts 1.5 x focus every
// 8 rounds for everyone, but Stellar, Tavi and Cassi hit 2.0-2.2 x focus, an attack reset adds a basic attack, and
// a ready volley lands at once. Damage per round = strength + strength / 8 per attack reset + modifier x focus / 8
// per damage spell, plus the spells ready now spread over P_PVSP_H rounds.
inline double real_dps(const bc::champion& c) {
    double str = 60, foc = 0;
    attempt([&] {
        str = c.strength();
        foc = c.focus();
        return true;
    });
    const ChampSpells& cs = spells_of(c);
    double d = str, ready = 0;
    bool known = false;
    for (int k = 0; k < 2; ++k) {
        const SpellInfo& si = cs.k[k];
        if (si.kind != 1 && si.kind != 2) continue;
        known = true;
        d += (si.kind == 1 ? str : si.mod * foc) / 8.0;
    }
    if (known)
        attempt([&] {
            auto abs = c.abilities();
            for (int k = 0; k < 2; ++k) {
                const SpellInfo& si = cs.k[k];
                if (si.kind != 1 && si.kind != 2) continue;
                try {
                    if (abs[k].cooldown() <= 0) ready += si.kind == 1 ? str : si.mod * foc;
                } catch (...) {
                }
            }
            return true;
        });
    if (!known) return fight::unit_dps(c);
    return std::max(10.0, d + ready / P_PVSP_H);
}

// Effective health: each durability emblem cuts incoming damage by 10%.
inline double eff_hp(const bc::champion& c, double hp) {
    if (!P_PVSP_ITEMS) return hp;
    int n = 0;
    attempt([&] {
        auto cnt = c.item_count();
        n = static_cast<int>(cnt[bc::item_type::durability_emblem_of_strength]) +
            static_cast<int>(cnt[bc::item_type::durability_emblem_of_focus]) +
            static_cast<int>(cnt[bc::item_type::durability_emblem_of_health]);
        return true;
    });
    double m = 1.0;
    for (int i = 0; i < n && i < 3; ++i) m *= 0.9;
    return hp / m;
}

inline double side_dps(const bc::champion& c) { return P_PVSP ? real_dps(c) : fight::unit_dps(c); }
inline double side_hp(const bc::champion& c, double hp) { return P_PVSP ? eff_hp(c, hp) : hp; }

// Health x damage of me + allies within 6 (alive, not recalling) over the enemies in view within 8.
inline double power_ratio(State& s, bc::champion& me, const std::vector<Foe>& foes) {
    vec2 pos = me.position();
    double oh = side_hp(me, me.health()), od = side_dps(me), th = 0, td = 0;
    attempt([&] {
        for (auto& a : bc::vision::champions(*s.my)) {
            try {
                if (a == me || !a.is_alive() || a.is_recalling()) continue;
                if (dist(a.position(), pos) > 6) continue;
                oh += side_hp(a, a.health());
                od += side_dps(a);
            } catch (...) {
            }
        }
        return true;
    });
    for (auto& f : foes)
        if (f.d <= P_PV_ER && !s.en_spawn.is_set(f.p)) {
            th += side_hp(f.c, f.hp);
            td += side_dps(f.c);
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
        if (round - g_last > P_PV_GAP) { g_verdict = 0; g_judged = false; }
        return g_verdict;
    }
    if (round - g_last > P_PV_GAP) { g_verdict = 0; g_judged = false; }
    g_last = round;
    if (on_spawn) return g_verdict;
    if (!g_judged) {
        if (nearest > P_PV_R) return 0;
        g_judged = true;
        double r = power_ratio(s, me, foes) * 100.0;
        g_verdict = r < P_PV_LEAVE ? 2 : (P_PV >= 2 && r >= P_PV_FIGHT ? 1 : 0);
        return g_verdict;
    }
    if (P_PV_REJUDGE && !g_verdict && nearest <= P_PV_R) {  // packs r110-120: judged 2.6 at contact, then 0.1, never re-judged
        double r = power_ratio(s, me, foes) * 100.0;
        if (r < P_PV_LEAVE * 0.75) g_verdict = 2;
        return g_verdict;
    }
    if (g_verdict) {
        double r = power_ratio(s, me, foes) * 100.0;
        if (g_verdict == 2 && r >= P_PV_FIGHT * 1.5) g_verdict = P_PV >= 2 ? 1 : 0;
        else if (g_verdict == 1 && r < P_PV_LEAVE * 0.75) g_verdict = 2;
    }
    return g_verdict;
}

}  // namespace pv
