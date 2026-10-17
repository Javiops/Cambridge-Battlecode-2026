// Production helpers under the actual SDK/engine. The awake-camp threat used
// for policy selection is explicitly projected; death is an actual camp kill.
#include "coordinator.h"
#include "actions.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
using namespace tactics;
static void check(bool value, const char *message) {
    if (!value) {
        std::printf("NATIVE_EPOCH_FAIL %s\n", message);
        std::fflush(stdout);
        throw std::runtime_error(message);
    }
}
static void projected_threat(World &w, const Actor &alive, const Spell &dash, bool current) {
    w.self = alive;
    w.self.can_move = w.self.can_attack = false;
    w.self.can_cast = true;
    w.self.channel = Channel::None;
    w.self.spells = {};
    w.self.spells[dash.slot] = dash;
    w.spells = w.self.spells;
    w.round = static_cast<int>(bc::round_number()) - (current ? 0 : 1);
    w.enemies.clear(); w.sightings.clear(); w.allies = {w.self};
    for (auto &group : w.groups) { group.camps.clear(); group.seen = w.round; }
    check(!w.groups.empty(), "native scenario has a group");
    Camp camp;
    camp.id = -100; camp.pos = w.self.pos; camp.range = 0;
    camp.hp = camp.max_hp = 100; camp.strength = 60; camp.awake = true;
    w.groups.front().camps = {camp};
    ++w.serial;
}
int main() {
    Geometry geometry; Memory memory; std::unique_ptr<World> world;
    int stage = 0, elk = -1; bool provoked = false;
    Actor alive; Spell dash;
    while (true) {
        if (bc::is_draft()) { bc::draft::pick(bc::champion_draft::ren); bc::end_turn(); continue; }
        if (stage >= 3) { bc::end_turn(); continue; }
        geometry.initialize();
        if (!geometry.initialized) { bc::end_turn(); continue; }
        if (!world) {
            world = std::make_unique<World>(geometry, memory);
            int best = unreachable;
            for (unsigned i = 0; i < geometry.groups.size(); ++i)
                for (const auto &spawn : geometry.groups[i].spawns)
                    if (spawn.type == 1 && geometry.at(geometry.home, spawn.pos) < best) {
                        best = geometry.at(geometry.home, spawn.pos); elk = i;
                    }
            check(elk >= 0, "actual elk metadata exists");
        }
        World &w = *world; w.refresh();
        if (w.round != static_cast<int>(bc::round_number()) || bc::fuel_remaining() < 65000) {
            bc::end_turn(); continue;
        }
        if (stage == 0) {
            check(w.self.alive, "live dash probe uses actual living owner");
            alive = w.self;
            for (const auto &spell : w.spells) if (spell.kind == 6 && spell.ready && spell.ground) dash = spell;
            check(dash.slot >= 0, "actual Ren ready ground dash");
            projected_threat(w, alive, dash, true);
            const auto result = escape_action(w);
            check(result && result->kind == Kind::CastGround && result->slot == dash.slot,
                  "funded current native dash remains selectable");
            check(result->at != alive.pos, "dash has a distinct legal safe landing");
            std::printf("NATIVE_EPOCH_CASE_PASS live-dash-selected %d %d %d %llu\n", alive.id,
                        result->at.x, result->at.y, (unsigned long long)bc::fuel_remaining());
            stage = 1; bc::end_turn(); continue;
        }
        if (!w.self.alive) {
            if (stage == 1) {
                check(provoked, "actual camp damage caused death");
                bool reproduced = false;
                try { (void)w.me.abilities()[dash.slot].valid_tiles(); }
                catch (const bc::error &error) {
                    check(static_cast<int>(error.code()) == 5, "expected native dead-mask error code");
                    reproduced = true;
                }
                check(reproduced, "control reproduces actual dead-owner range-mask error5");
                std::printf("NATIVE_EPOCH_CASE_PASS expected-dead-mask-5 %d\n", alive.id);
                projected_threat(w, alive, dash, false);
                check(!escape_action(w, 18000), "old-alive escape declines before actual dead ability");
                check(!combat_proposal(w, memory), "old-alive combat declines");
                w.self.channel = Channel::Recall;
                check(!useful_channel_cancel(w, 3), "old-alive optional channel cancel declines");
                std::printf("NATIVE_EPOCH_CASE_PASS old-alive-all-decline %d\n", alive.id);
                stage = 2;
            } else {
                // Deliberately contradictory current-round/alive projection on a
                // dead actual owner isolates the funding guard. It is not a valid
                // World snapshot or a claim that a real death keeps this epoch.
                projected_threat(w, alive, dash, true);
                volatile unsigned sink = 17;
                while (bc::fuel_remaining() > 23500)
                    for (unsigned i = 0; i < 16; ++i) sink = sink * 1664525u + i;
                check(bc::fuel_remaining() > 18000, "low-budget fixture retains cleanup reserve");
                check(!escape_action(w, 18000), "unfunded dash declines before native mask");
                std::printf("NATIVE_EPOCH_CASE_PASS low-budget-declines %d %llu %u\n", alive.id,
                            (unsigned long long)bc::fuel_remaining(), (unsigned)sink);
                std::printf("NATIVE_EPOCH_PASS %d\n", alive.id); stage = 3;
            }
            bc::end_turn(); continue;
        }
        alive = w.self;
        if (!provoked) {
            const auto target = geometry.groups[elk].spawns.front().pos;
            std::optional<Camp> monster;
            for (const auto &camp : w.groups[elk].camps) if (camp.hp > 0) monster = camp;
            if (monster && distance(w.self.pos, monster->pos) <= w.self.range && w.self.can_attack) {
                Action action; action.kind = Kind::BasicCamp; action.target = monster->id;
                action.reason = "fixture-actual-wake"; provoked = execute(w, action).success;
            } else if (auto step = w.toward(target, 1)) {
                Action action; action.kind = Kind::Move; action.at = *step;
                action.reason = "fixture-actual-approach"; execute(w, action);
            }
        }
        bc::end_turn();
    }
}
