// P_MITEMACRO: on the 9 official maps, play #1 Mite's macro from its replays instead of our own: its draft, and per
// champion the same ordered list of camp groups to farm (with its recall-on-capture), recalls and tributes at the same
// altars (mite_macro.h, built by tools/mitemacro). Everything else is still ours: shop, healing, fleeing, hp recalls,
// fights, channel cancels. So two versions with the switch on differ only in micro and mid-game decisions.
// A step is skipped, before we start it, when we are more than P_MM_SLACK rounds behind Mite's schedule (after a death or a long fight),
// so the team stays in sync with the plan; when the list ends (Mite's game was over) our own macro takes over.
#pragma once
#include "mite_macro.h"

#ifndef P_MM_SLACK
#define P_MM_SLACK 60
#endif
#ifndef P_MM_RALLY
#define P_MM_RALLY 12  // rounds a champion waits at a camp it cannot take alone before it moves on to its next step
#endif
#ifndef P_MM_SHOP
#define P_MM_SHOP 1    // also Mite's item build (emblem families and counts from its game summary)
#endif
#ifndef P_MM_EARLY
#define P_MM_EARLY 20  // an ally's capture counts for our step only from this many rounds before Mite's first hit on it
#endif



const char* mm_draft(int family) {
    for (auto& sc : mitemacro::scripts)
        if (sc.family == family) return sc.draft;
    return nullptr;
}

void mm_setup(State& s, bc::champion& me) {
    s.mm_init = true;
    if (!s.de_map) return;
    for (auto& sc : mitemacro::scripts) {
        if (sc.family != s.de_map) continue;
        int side = s.my_spawn.is_set(vec2(sc.ax, sc.ay)) ? 0 : 1;
        if (side != sc.side) continue;
        for (int k = 0; k < sc.nc; ++k)
            if (starts_with(s.name, sc.champs[k].name)) s.mm = &sc.champs[k];
        if (!s.mm) break;
        if (P_MM_SHOP && s.mm->shop[0]) {  // Mite's emblems for this champion, in its buying order
            static const char* const fams[] = {"jungle", "durab", "bruiser", "power", "monster", "treasure", "home"};
            std::vector<Step> plan;
            std::string all = s.mm->shop, cur;
            for (char ch : all + ",") {
                if (ch != ',') { cur += ch; continue; }
                auto a = cur.find(':'), b = cur.rfind(':');
                if (a != std::string::npos && b > a) {
                    std::string f = cur.substr(0, a);
                    for (const char* lit : fams)
                        if (f == lit) plan.push_back({lit, cur[a + 1], std::atoi(cur.c_str() + b + 1)});
                }
                cur.clear();
            }
            if (!plan.empty()) s.plan = plan;
        }
        int bad = 0;
        s.mm_group.assign(s.mm->n, -1);
        for (int i = 0; i < s.mm->n; ++i) {
            const auto& st = s.mm->s[i];
            if (st.k != 'C') continue;
            for (int g = 0; g < static_cast<int>(s.groups.size()); ++g)
                if (s.groups[g].mask.is_set(vec2(st.x, st.y))) s.mm_group[i] = g;
            if (s.mm_group[i] < 0) ++bad;
        }
        std::printf("[mm] %s side %c script %s: %d steps, %d unmatched camps (%s)\n", s.name.c_str(), side ? 'b' : 'a',
                    sc.draft, s.mm->n, bad, sc.src);
        break;
    }
}

// Is the step at s.mm_i finished or not worth doing any more?
bool mm_step_over(State& s, bc::champion& me, int round) {
    const auto& st = s.mm->s[s.mm_i];
    int gems = static_cast<int>(me.gem_count());
    if (st.k == 'T') return gems <= 0;  // a bank is never late
    if (s.mm_start < 0 && st.r1 + P_MM_SLACK < round) return true;  // too late to start; a step under way is finished
    if (st.k == 'R') {
        if (s.mm_start < 0) s.mm_start = round;
        return s.my_spawn.is_set(me.position());
    }
    int gi = s.mm_group[s.mm_i];
    if (gi < 0) return true;
    if (s.mm_got == gi) return true;  // we took its reward ourselves
    if (round < st.r0 - P_MM_EARLY) return false;  // well before Mite's time: an earlier cycle of the same group is not this step
    Group& g = s.groups[gi];
    if (s.mm_start < 0) {
        s.mm_start = round;
        s.mm_nok = g.next_ok;
        s.mm_up = g.next_ok <= round;
        s.mm_bad = g.bad_until;
    }
    if (g.next_ok <= round) s.mm_up = true;
    if (g.next_ok > round && (s.mm_up || g.next_ok > s.mm_nok + 5)) return true;  // captured since the step began
    if (s.mm_try > P_MM_RALLY) return true;  // nobody came to help with a camp we cannot take alone
    if (g.bad_until > round && g.bad_until != s.mm_bad) return true;  // farm() gave it up in this step (too strong, an ally takes the reward, bail)
    return false;
}

// true while the script still has a step for this champion
bool mm_active(State& s, bc::champion& me, int round) {
    if (!s.mm_init) mm_setup(s, me);
    if (!s.mm || P_MITEMACRO == 2) return false;  // 2: Mite's draft and items only, our own routes
    while (s.mm_i < s.mm->n && mm_step_over(s, me, round)) {
#ifdef P_MM_LOG
        const auto& st = s.mm->s[s.mm_i];
        std::printf("[mm] r%d %s step %d %c (%d,%d) mite r%d-%d over\n", round, s.name.c_str(), s.mm_i, st.k, st.x, st.y, st.r0, st.r1);
#endif
        ++s.mm_i;
        s.mm_start = -1;
        s.mm_try = 0;
        s.mm_got = -1;
    }
    return s.mm_i < s.mm->n;
}

// the current step is a capture with Mite's recall on the capture tiles
bool mm_caprecall(State& s) {
    if (!s.mm || s.mm_i >= s.mm->n) return false;
    const auto& st = s.mm->s[s.mm_i];
    return st.k == 'C' && st.cr && s.mm_group[s.mm_i] == s.target;
}

// the current step is a capture whose reward Mite's champion took
bool mm_iscap(State& s) {
    if (!s.mm || s.mm_i >= s.mm->n) return false;
    const auto& st = s.mm->s[s.mm_i];
    return st.k == 'C' && st.cap && s.mm_group[s.mm_i] == s.target;
}

void mm_turn(State& s, bc::champion& me, int round, const std::vector<bc::camp>& camps, bool rsafe, int nearest_foe) {
    const auto& st = s.mm->s[s.mm_i];
    vec2 pos = me.position();
    if (st.k == 'R') {
        g_mode = "mm-recall";
        if (rsafe && attempt([&] {
                me.recall();
                return true;
            })) {
            ++s.mm_i;
            s.mm_start = -1;
            return;
        }
        if (nearest_foe > 3 && ++s.mm_try < 12) flee(s, me);  // walk home until the recall is safe
        else { ++s.mm_i; s.mm_start = -1; }
        return;
    }
    if (st.k == 'T') {
        g_mode = "mm-tribute";
        vec2 a(st.x, st.y);
        bool known = false;
        for (std::size_t i = 0; i < s.altars.size(); ++i)
            if (s.altars[i] == a && s.altar_ok[i] && s.lock_until[i] <= round) known = true;
        if (!known) { go_tribute(s, me, round); return; }
        if (dist(pos, a) <= 1) {
            attempt([&] {
                me.submit_gems(a);
                return true;
            });
            return;
        }
        bc::bitboard ring;
        ring.draw_chebyshev(a, 1.0f);
        step_towards(s, me, ring, true);
        if (dist(me.position(), a) <= 1)
            attempt([&] {
                me.submit_gems(a);
                return true;
            });
        return;
    }
    // 'C': farm that group (farm() does the attacking, rallying, capture and reward sharing)
    g_mode = "mm-farm";
    int gi = s.mm_group[s.mm_i];
    Group& g = s.groups[gi];
    if (g.next_ok > round + dist(pos, g.center) + P_RESPAWN) {  // respawning: walk there and wait off its tiles
        g_farm = "mm-wait";
        if (s.target != gi) { s.target = gi; s.cap_start = -1; s.target_round = round; write_claim(s, gi); }
        bc::bitboard r4, r2;
        for (auto t : g.tiles) {
            r4.draw_chebyshev(t, 4.0f);
            r2.draw_chebyshev(t, 2.0f);
        }
        bc::bitboard ring = r4 & ~r2;
        if (!ring.is_set(pos)) step_towards(s, me, ring, false);
        return;
    }
    g_mm_force = gi;
    g_mm_cap = st.cap;
    farm(s, me, round, camps);
    g_mm_force = -1;
    g_mm_cap = false;
}
