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
#ifndef P_PVSIM
#define P_PVSIM 0   // 1 = the ratio comes from a fight model of both sides over P_PVSIM_H rounds (see sim_ratio)
#endif
#ifndef P_PVSIM_H
#define P_PVSIM_H 8
#endif
#ifndef P_PVLOG
#define P_PVLOG 0   // 1 = print the old, P_PVSP and P_PVSIM ratios at each first contact (analysis builds only: costs fuel)
#endif
#ifndef P_PV_REJUDGE
#define P_PV_REJUDGE 0  // 1 = a "no verdict" engagement is re-judged every round: leave if the ratio drops under P_PV_LEAVE x 0.75
#endif
#ifndef P_PV_NEWFOE
#define P_PV_NEWFOE 0  // 1 = judged again (both ways, same cuts) whenever more foes are within P_PV_ER than at the last judgement
#endif
#ifndef P_PV_KEEPCAP
#define P_PV_KEEPCAP 0  // 1 = a "leave" verdict does not pull a champion off a capture unless a foe is within 3
#endif

namespace pv {

// Each champion runs its own program, so these globals are per champion.
inline int g_verdict = 0;    // 0 none (v52 rules), 1 fight, 2 leave
inline int g_last = -100;    // last round with an enemy champion within 8
inline bool g_judged = false;
inline int g_nth = 0;        // P_PV_NEWFOE: foes within P_PV_ER at the last judgement

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

inline double side_dps(const bc::champion& c, bool sp) { return sp ? real_dps(c) : fight::unit_dps(c); }
inline double side_hp(const bc::champion& c, double hp, bool sp) { return sp ? eff_hp(c, hp) : hp; }


// P_PVSIM (2026-10-17, user: "debemos tener en cuenta el daño real de los rivales como el nuestro, los cd, las
// pasivas de los emblemas y cuantos items estan dando focus"): a fight model of both groups over P_PVSIM_H rounds.
// Per champion (live values, so shards bought already show in strength, focus and health):
//   basic attack every round = strength; every ability cast whose cooldown comes round inside the window, from its
//   live remaining cooldown and its configured max cooldown: attack reset = one more basic attack, damage and
//   damage-cc spells = modifier x focus, stuns (cc, with or without damage) remove one round of one enemy's damage;
//   Ren's passive returns 0.2 x focus per basic attack it takes (its share of the enemy attacks);
//   durability emblems: 10% less damage taken each (item_count, visible champions);
//   Cassi & Issac die together: the pair counts twice the health of the weaker body.
// Ratio = rounds the enemies need to kill us / rounds we need to kill them (Lanchester: hp x damage on each side).
struct SimSpell {
    int kind = 0;  // 1 attack reset, 2 damage (with or without stun), 3 pure stun
    bool stun = false;
    double mod = 0;
    int maxcd = 8;
};
struct SimType {
    int type = -1;
    SimSpell k[2];
};
inline const SimType& sim_type(const bc::champion& c) {
    static std::vector<SimType> cache;
    int type = -2;
    attempt([&] {
        type = static_cast<int>(combat_identity_type(c));
        return true;
    });
    for (auto& t : cache)
        if (t.type == type) return t;
    SimType st;
    st.type = type;
    attempt([&] {
        auto abs = c.abilities();
        for (int k = 0; k < 2; ++k) {
            try {
                auto inf = abs[k].info();
                if (!inf) continue;
                std::visit([&](auto& x) {
                    using T = std::decay_t<decltype(x)>;
                    SimSpell& sp = st.k[k];
                    sp.maxcd = std::max(1, static_cast<int>(x.max_cooldown));
                    if constexpr (T::kind == bc::ability_kind::attack_reset) {
                        sp.kind = 1;
                    } else if constexpr (T::kind == bc::ability_kind::damage || T::kind == bc::ability_kind::aoe_damage) {
                        sp.mod = x.modifier;
                        if (x.modifier > 0) sp.kind = 2;
                    } else if constexpr (T::kind == bc::ability_kind::cc) {
                        sp.mod = x.modifier;
                        sp.stun = true;
                        sp.kind = x.modifier > 0 ? 2 : 3;
                    }
                }, *inf);
            } catch (...) {
            }
        }
        return true;
    });
    if (type == -2) {
        static SimType tmp;
        tmp = st;
        return tmp;
    }
    cache.push_back(st);
    return cache.back();
}

struct SimUnit {
    double hp = 0, dmg = 0, stuns = 0, foc = 0, take = 1.0;  // dmg over the window; take = damage-taken multiplier
    bool ren = false, cassi = false, issac = false;
};

inline SimUnit sim_unit(const bc::champion& c, double hp) {
    SimUnit u;
    u.hp = hp;
    double str = 60;
    attempt([&] {
        str = c.strength();
        u.foc = c.focus();
        return true;
    });
    std::string nm;
    attempt([&] {
        nm = norm(bc::to_string(combat_identity_type(c)));
        return true;
    });
    u.ren = starts_with(nm, "ren");
    u.cassi = starts_with(nm, "cassi");
    u.issac = starts_with(nm, "issac");
    const int H = P_PVSIM_H;
    u.dmg = H * str;
    const SimType& st = sim_type(c);
    int cd[2] = {0, 0};
    attempt([&] {
        auto abs = c.abilities();
        for (int k = 0; k < 2; ++k) {
            try {
                cd[k] = std::max(0, static_cast<int>(abs[k].cooldown()));
            } catch (...) {
                cd[k] = st.k[k].maxcd;
            }
        }
        return true;
    });
    for (int k = 0; k < 2; ++k) {
        const SimSpell& sp = st.k[k];
        if (!sp.kind || cd[k] >= H) continue;
        double casts = 1 + (H - 1 - cd[k]) / sp.maxcd;
        if (sp.kind == 1) u.dmg += casts * str;
        else if (sp.kind == 2) u.dmg += casts * sp.mod * u.foc;
        if (sp.stun) u.stuns += casts;
    }
    if (P_PVSP_ITEMS) {
        int n = 0;
        attempt([&] {
            auto cnt = c.item_count();
            n = static_cast<int>(cnt[bc::item_type::durability_emblem_of_strength]) +
                static_cast<int>(cnt[bc::item_type::durability_emblem_of_focus]) +
                static_cast<int>(cnt[bc::item_type::durability_emblem_of_health]);
            return true;
        });
        for (int i = 0; i < n && i < 3; ++i) u.take *= 0.9;
    }
    return u;
}

// Health that has to be removed from a side: Cassi & Issac count twice the weaker body; scaled by the side's armour.
inline double side_life(const std::vector<SimUnit>& v) {
    double hp = 0, c = -1, i = -1;
    for (auto& u : v) {
        double e = u.hp / u.take;
        if (u.cassi) c = e;
        else if (u.issac) i = e;
        else hp += e;
    }
    if (c >= 0 && i >= 0) hp += 2 * std::min(c, i);
    else hp += std::max(0.0, c) + std::max(0.0, i);
    return hp;
}

// Damage a side deals over the window, after the other side's stuns and with Ren's retaliation.
inline double side_damage(const std::vector<SimUnit>& us, const std::vector<SimUnit>& them) {
    const int H = P_PVSIM_H;
    double d = 0, basic_them = 0, stuns_them = 0;
    for (auto& u : us) d += u.dmg;
    for (auto& t : them) { stuns_them += t.stuns; }
    double per_round_unit = us.empty() ? 0 : d / (H * static_cast<double>(us.size()));
    d -= std::min(0.5 * d, stuns_them * per_round_unit);  // each stun = one enemy round of one of our champions
    (void)basic_them;
    return d;
}
inline double ren_return(const std::vector<SimUnit>& side, const std::vector<SimUnit>& foes) {
    const int H = P_PVSIM_H;
    double r = 0;
    if (side.empty()) return 0;
    for (auto& u : side)
        if (u.ren) r += 0.2 * u.foc * H * static_cast<double>(foes.size()) / static_cast<double>(side.size());
    return r;
}

inline double sim_ratio(State& s, bc::champion& me, const std::vector<Foe>& foes) {
    vec2 pos = me.position();
    std::vector<SimUnit> us, them;
    us.push_back(sim_unit(me, me.health()));
    attempt([&] {
        for (auto& a : combat_allies(s)) {
            try {
                if (a == me || !a.is_alive() || a.is_recalling()) continue;
                if (dist(a.position(), pos) > 6) continue;
                us.push_back(sim_unit(a, a.health()));
            } catch (...) {
            }
        }
        return true;
    });
    for (auto& f : foes)
        if (f.d <= P_PV_ER && !s.en_spawn.is_set(f.p)) them.push_back(sim_unit(f.c, f.hp));
    if (them.empty()) return 99.0;
    double our_dmg = side_damage(us, them) + ren_return(us, them);
    double their_dmg = side_damage(them, us) + ren_return(them, us);
    double our_life = side_life(us), their_life = side_life(them);
    if (their_dmg <= 1) return 99.0;
    if (our_dmg <= 1) return 0.0;
    return (our_life / their_dmg) / (their_life / our_dmg);
}

// Health x damage of me + allies within 6 (alive, not recalling) over the enemies in view within 8.
inline double power_ratio(State& s, bc::champion& me, const std::vector<Foe>& foes, bool sp = P_PVSP) {
    vec2 pos = me.position();
    double oh = side_hp(me, me.health(), sp), od = side_dps(me, sp), th = 0, td = 0;
    attempt([&] {
        for (auto& a : bc::vision::champions(*s.my)) {
            try {
                if (a == me || !a.is_alive() || a.is_recalling()) continue;
                if (dist(a.position(), pos) > 6) continue;
                oh += side_hp(a, a.health(), sp);
                od += side_dps(a, sp);
            } catch (...) {
            }
        }
        return true;
    });
    for (auto& f : foes)
        if (f.d <= P_PV_ER && !s.en_spawn.is_set(f.p)) {
            th += side_hp(f.c, f.hp, sp);
            td += side_dps(f.c, sp);
        }
    if (th <= 0) return 99.0;
    return (oh * od) / (th * td);
}

// Called once per turn at the start of step 3. Returns the verdict held for this engagement.
inline double judge(State& s, bc::champion& me, const std::vector<Foe>& foes) {
    return P_PVSIM ? sim_ratio(s, me, foes) : power_ratio(s, me, foes);
}

inline int count_near(State& s, const std::vector<Foe>& foes) {
    int n = 0;
    for (auto& f : foes)
        if (f.d <= P_PV_ER && !s.en_spawn.is_set(f.p)) ++n;
    return n;
}

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
        double r = judge(s, me, foes) * 100.0;
        if (P_PVLOG) {
            int nus = 1, nth = 0;
            attempt([&] {
                for (auto& a : bc::vision::champions(*s.my))
                    try {
                        if (!(a == me) && a.is_alive() && !a.is_recalling() && dist(a.position(), me.position()) <= 6) ++nus;
                    } catch (...) {
                    }
                return true;
            });
            for (auto& f : foes)
                if (f.d <= P_PV_ER && !s.en_spawn.is_set(f.p)) ++nth;
            vec2 p = me.position();
            std::printf("[pvlog] r=%d me=%s x=%d y=%d hp=%.0f nus=%d nth=%d old=%.3f sp=%.3f sim=%.3f\n", round,
                        s.name.c_str(), static_cast<int>(X(p)), static_cast<int>(Y(p)), me.health(), nus, nth,
                        power_ratio(s, me, foes, false), power_ratio(s, me, foes, true), sim_ratio(s, me, foes));
        }
        g_verdict = r < P_PV_LEAVE ? 2 : (P_PV >= 2 && r >= P_PV_FIGHT ? 1 : 0);
        if (P_PV_NEWFOE) g_nth = count_near(s, foes);
        return g_verdict;
    }
    if (P_PV_NEWFOE) {  // user 2026-10-17: a fight judged 2v2 is not the same fight once a third enemy walks in
        int n = count_near(s, foes);
        if (n > g_nth) {
            g_nth = n;
            double r = judge(s, me, foes) * 100.0;
            g_verdict = r < P_PV_LEAVE ? 2 : (P_PV >= 2 && r >= P_PV_FIGHT ? 1 : 0);
            return g_verdict;
        }
    }
    if (P_PV_REJUDGE && !g_verdict && nearest <= P_PV_R) {  // packs r110-120: judged 2.6 at contact, then 0.1, never re-judged
        double r = judge(s, me, foes) * 100.0;
        if (r < P_PV_LEAVE * 0.75) g_verdict = 2;
        return g_verdict;
    }
    if (g_verdict) {
        double r = judge(s, me, foes) * 100.0;
        if (g_verdict == 2 && r >= P_PV_FIGHT * 1.5) g_verdict = P_PV >= 2 ? 1 : 0;
        else if (g_verdict == 1 && r < P_PV_LEAVE * 0.75) g_verdict = 2;
    }
    return g_verdict;
}

}  // namespace pv
