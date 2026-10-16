#include "actions.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
using namespace tactics;
static void check(bool value, const char *reason) {
    if (!value)
        throw std::runtime_error(reason);
}
int main() {
    Geometry geometry;
    Memory memory;
    std::unique_ptr<World> world;
    bool done = false;
    while (true) {
        if (bc::is_draft()) {
            bc::draft::pick(bc::champion_draft::cassi_and_issac);
            bc::end_turn();
            continue;
        }
        geometry.initialize();
        if (!world)
            world = std::make_unique<World>(geometry, memory);
        World &w = *world;
        w.refresh();
        if (done) {
            bc::end_turn();
            continue;
        }
        check(w.self.alive && (w.self.type == 3 || w.self.type == 4), "fixture requires pair");
        const bool left = w.geo.at(w.geo.home, {1, 1}) == 0;
        const Pos origin{left ? 10 : 21, 10}, midpoint{left ? 11 : 20, 11},
            target{left ? 12 : 19, 12};
        const Pos approach = w.self.type == 3 ? midpoint : origin;
        if (w.self.pos != approach) {
            if (auto step = w.toward(approach)) {
                Action move;
                move.kind = Kind::Move;
                move.at = *step;
                move.reason = "fixture-occupied-dash-approach";
                check(execute(w, move).success, "fixture approach");
            }
            bc::end_turn();
            continue;
        }
        if (w.self.type == 3) {
            // Enter with enough fuel for execute's cheap front check, but less
            // than the final mutation reserve. Recall must remain unattempted.
            const int prior_attempt = memory.channel_attempt_round;
            while (bc::fuel_remaining() > 11000) {
            }
            Action recall;
            recall.kind = Kind::Recall;
            const auto result = execute(w, recall);
            check(result.outcome == Outcome::Stale && !result.success && result.error == 0,
                  "secondary mutation budget gate");
            check(memory.channel_attempt_round == prior_attempt && !w.me.is_recalling(),
                  "budget rejection must not publish a channel attempt");
            std::printf("NATIVE_MUTATION_BUDGET_PASS %d\n", w.self.id);
        } else {
            bool holder = false;
            for (const auto &ally : w.allies)
                holder |= ally.type == 3 && ally.alive && ally.pos == midpoint;
            if (!holder) {
                bc::end_turn();
                continue;
            }
            const auto ability = w.me.abilities()[1];
            check(ability.is_dash() && ability.is_ready(), "native Issac dash readiness");
            check(ability.valid_tiles().is_set(sdk(target)), "range-only mask includes diagonal");
            Action dash;
            dash.kind = Kind::CastGround;
            dash.slot = 1;
            dash.at = target;
            dash.reason = "fixture-unique-occupied-diagonal";
            const int epoch = w.round;
            --w.round;
            const auto stale = execute(w, dash);
            check(stale.outcome == Outcome::Stale && !stale.success, "stale epoch gate");
            w.round = epoch;
            const auto blocked = execute(w, dash);
            check(blocked.outcome == Outcome::Rejected && !blocked.success && blocked.error == 0,
                  "occupied diagonal rejected before SDK mutation");
            check(position(w.me.position()) == origin && ability.cooldown() == 0,
                  "blocked path preserves position and cooldown");
            dash.at = {origin.x, 12};
            const auto legal = execute(w, dash);
            check(legal.success && legal.error == 0 && position(w.me.position()) == dash.at,
                  "legal Issac dash remains possible");
            std::printf("NATIVE_DASH_OCCUPIED_PASS %d\n", w.self.id);
        }
        done = true;
        bc::end_turn();
    }
}
