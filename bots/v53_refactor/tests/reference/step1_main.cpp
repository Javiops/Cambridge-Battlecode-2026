// CAMBC (cambc2026a) bot - single-file C++ bot using only the documented SDK API.
//
// Strategy in one paragraph:
//   Draft tanky melee farmers first (Varg, Ryth, Vendetta), then Vesper Vale /
//   Marcella / Cassi & Issac and so on, by name, writing the plan into draft
//   memory before every pick. In game, every champion runs the same priority list:
//   shop on spawn (emblem build per champion), heal on spawn, flee or recall
//   when hurt, fight enemy champions only when the local fight looks even or
//   better, tribute at the nearest altar when the bag is big (or late in the
//   game), otherwise farm the best camp group it can clear safely (gem/gold
//   clusters first, then wolves, elk...), capture it and move on. Allies spread
//   over different camps through an 8-byte "claim" table in shared memory.
//
// NOTE: this was written from the API reference only and could not be compiled
// against the real SDK. Names the reference does not spell out (header name,
// enum values) are avoided: champions, items and passives are found by
// iterating enum values and matching to_string() names.

// The SDK header name is not in the API reference, so try the likely ones.
// If none match, replace this block with the #include from a `cambc new` template.
#if defined(CAMBC_LOCAL_STUB)
#include "cambc_stub.hpp"  // offline syntax check only
#elif __has_include(<cambc.hpp>)
#include <cambc.hpp>
#elif __has_include(<cambc/cambc.hpp>)
#include <cambc/cambc.hpp>
#elif __has_include(<cambc.h>)
#include <cambc.h>
#elif __has_include(<cambc/cambc.h>)
#include <cambc/cambc.h>
#elif __has_include(<cambc/sdk.hpp>)
#include <cambc/sdk.hpp>
#elif __has_include(<cambc/bot.hpp>)
#include <cambc/bot.hpp>
#elif __has_include(<cambc/all.hpp>)
#include <cambc/all.hpp>
#elif __has_include(<cambc/api.hpp>)
#include <cambc/api.hpp>
#elif __has_include(<cambc_sdk.hpp>)
#include <cambc_sdk.hpp>
#elif __has_include(<cambc/cambc.hh>)
#include <cambc/cambc.hh>
#elif __has_include(<sdk.hpp>)
#include <sdk.hpp>
#elif __has_include(<bot.hpp>)
#include <bot.hpp>
#elif __has_include(<bc.hpp>)
#include <bc.hpp>
#elif __has_include(<battlecode.hpp>)
#include <battlecode.hpp>
#else
#error "CAMBC SDK header not found: copy the #include line from a `cambc new` template here"
#endif

#include <algorithm>
#include <cmath>
#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <string>
#include <vector>
#include <variant>
#include <cstdio>
#include <exception>

namespace bc = cambc;
using bc::vec2;

namespace {

// Policy implementation sections are included in their original declaration order.
// See ARCHITECTURE.md. Do not reorder: these are not independent translation units.
#include "legacy_config.inc"
#include "runtime_foundation.inc"
#include "draft_impl.inc"
#include "game_state.inc"
#include "setup_shop.inc"
#include "movement_actions.inc"
#include "team_camp_planning.inc"
#include "banking_tactics.inc"
#include "capture_farming.inc"
#include "turn_policy.inc"
#include "diagnostics.inc"
#include "spell_sweep.inc"
#include "utility.h"

[[noreturn]] void run_game() {
    State s;
    bool logged_init = false;
    for (;;) {
        g_mode = "?";
        g_farm = "-";
        try {
#if P_FUELPROF
            fp_begin();
#endif
            if (s.sweep >= 3) spell_sweep(s, true);  // before moving: most targeted spells cannot be cast after a step
#ifdef P_DZLOG
            double dz0 = -1;
            auto dz_now = [&]() -> double {  // ready enemy damage on our tile next round (fight.h volley model)
                double out = -1;
                attempt([&] {
                    bc::champion& me = bc::self();
                    if (!s.ready || !me.is_alive()) return false;
                    std::vector<Threat> th;
                    for (auto& c : bc::vision::champions(*s.en)) {
                        if (!c.is_alive() || s.en_spawn.is_set(c.position())) continue;
                        int ar = static_cast<int>(c.attack_range());
                        th.push_back(threat_of(c, c.position(), ar <= 1 ? 2 : ar + 1));
                    }
                    out = danger_at(th, me.position());
                    return true;
                });
                return out;
            };
            dz0 = dz_now();
#endif
            play_turn(s);
            FP(12, "post-sweep");
#ifdef P_DZLOG
            {
                double dz1 = dz_now();
                attempt([&] {
                    bc::champion& me = bc::self();
                    if (dz1 > 0 || dz0 > 0)
                        std::printf("[dz] %d %s %s %.0f %.0f %.0f\n", static_cast<int>(bc::round_number()), s.name.c_str(), g_mode, me.health(), dz0, dz1);
                    return true;
                });
            }
#endif
            if (s.sweep && s.sweep < 3) spell_sweep(s);
#ifdef P_CDPROBE
            attempt([&] {  // can we read enemy spell cooldowns?
                bc::champion& me = bc::self();
                if (!s.ready || !me.is_alive()) return false;
                for (auto& c : bc::vision::champions(*s.en)) {
                    if (!c.is_alive()) continue;
                    auto abs = c.abilities();
                    for (int k = 0; k < 2; ++k) {
                        int cd = -9;
                        std::string err;
                        try { cd = abs[k].cooldown(); } catch (const std::exception& e) { err = e.what(); }
                        float mod = -1, rg = -1;
                        int kind = -1;
                        try {
                            auto inf = abs[k].info();
                            if (inf) std::visit([&](auto& x) {
                                using T = std::decay_t<decltype(x)>;
                                kind = static_cast<int>(T::kind);
                                if constexpr (requires { x.modifier; }) { mod = x.modifier; rg = x.range; }
                                if constexpr (requires { x.exclusive_with_movement; }) { if (x.exclusive_with_movement) kind += 100; }
                                if constexpr (requires { x.duration; }) { kind += 1000 * x.duration; }
                                if constexpr (requires { x.radius; }) { rg += 100 * x.radius; }
                            }, *inf);
                        } catch (...) {}
                        std::printf("[cd] r=%d %s sees enemy %s slot%d cd=%d kind=%d mod=%.2f rg=%.1f foc=%.0f str=%.0f hp=%.0f %s\n", static_cast<int>(bc::round_number()), s.name.c_str(),
                                    bc::to_string(c.champion_name()).c_str(), k, cd, kind, mod, rg, c.focus(), c.strength(), c.health(), err.c_str());
                    }
                }
                return true;
            });
#endif
#ifdef P_MODELOG
            attempt([&] {  // mode of every turn with an enemy champion within 4 (not on its spawn)
                bc::champion& me = bc::self();
                if (!s.ready || !me.is_alive()) return false;
                int nd = 99;
                for (auto& c : bc::vision::champions(*s.en))
                    if (c.is_alive() && !s.en_spawn.is_set(c.position())) nd = std::min(nd, dist(c.position(), me.position()));
                if (nd <= 4) std::printf("[cm] %s %s %d\n", s.name.c_str(), g_mode, nd);
                return true;
            });
#endif
            if (s.sweep == 5) {
                if (s.rooted_r == static_cast<int>(bc::round_number())) shoot_rooted(s);
                spell_sweep(s);  // spells that still work after our step
            }
            // Newly revealed targets after moving were not in the pre-sweep.
            // This optional extra pass only uses movement-compatible spells.
            if (P_U34_POST_FREE && s.sweep >= 3 && s.sweep != 5 && fuel_ok(12000))
                spell_sweep(s, false, true);
            if (P_R5_LOCK) r5_altar_lock(s);
            if (P_R5_WARD) r5_personal_ward(s);
        } catch (const std::exception& e) {
            note_error(e.what());
        } catch (...) {
            note_error("unknown exception in turn");
        }
        FP(13, "log");
        if (s.ready && !logged_init && (!P_FUELGUARD || fuel_ok(20000))) {
            logged_init = true;
            log_init(s);
        }
#if P_FUELPROF
        FP(14, "end");
        debug_block({
            int r = static_cast<int>(bc::round_number());
            unsigned long long tot = 0;
            for (auto t : g_fp_turn) tot += t;
            if (g_fp_over || tot > 70000) {
                std::printf("[heavy] r=%d %s mode=%s farm=%s over=%s total=%llu", g_fp_round, s.name.c_str(), g_mode, g_farm,
                            g_fp_where >= 0 ? g_fp[g_fp_where].name : "-", tot);
                for (int i = 0; i < 32; ++i)
                    if (g_fp_turn[i] > 3000) std::printf(" %s=%llu", g_fp[i].name, g_fp_turn[i]);
                std::printf("\n");
            }
            if (r % 100 == 0 || r == 1) {
                std::printf("[fuel] r=%d %s", r, s.name.c_str());
                for (auto& c : g_fp)
                    if (c.n || c.over) std::printf(" | %s n=%llu avg=%llu max=%llu over=%llu", c.name, c.n, c.n ? c.sum / c.n : 0, c.mx, c.over);
                std::printf("\n");
            }
        });
#endif
        log_status(s);
        bc::end_turn();
    }
}

}  // namespace

int main() {
    if (bc::is_draft()) run_draft();
    run_game();
}
