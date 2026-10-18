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
#include "turn_helpers.inc"
#include "turn_policy.inc"
#include "turn_labels.inc"
#include "diagnostics.inc"
#include "spell_sweep.inc"
#include "utility.h"

#include "run_loop.inc"

}  // namespace

int main() {
    if (bc::is_draft()) run_draft();
    run_game();
}
