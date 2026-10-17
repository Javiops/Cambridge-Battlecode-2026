#include "actions.h"
#include "coordinator.h"
#include "sdk_world.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
using namespace tactics;
static void require(bool ok, const char *why) {
    if (!ok) {
        std::printf("CAST_ONLY_FAIL %s\n", why);
        throw std::runtime_error(why);
    }
}
int main() {
    Geometry geo;
    Memory memory;
    std::unique_ptr<World> ptr;
    int group = -1, phase = 0, owners = 0, casts = 0, start = -1, primed = -1;
    const Pos target{54, 64}, stage{58, 65};
    while (true) {
        try {
            if (bc::is_draft()) {
                auto old = bc::draft::current_draft(bc::team::ally);
                for (auto p : {bc::champion_draft::cassi_and_issac, bc::champion_draft::ryth,
                               bc::champion_draft::willow})
                    if (std::find(old.begin(), old.end(), p) == old.end()) {
                        bc::draft::pick(p);
                        break;
                    }
            } else if (bc::detail::sdk_my_team() == 1 && int(bc::self().champion_name()) == 3 &&
                       phase < 3) {
                if (!geo.initialized) {
                    geo.initialize();
                    bc::end_turn();
                    continue;
                }
                if (group < 0)
                    for (unsigned i = 0; i < geo.groups.size(); ++i)
                        if (geo.groups[i].spawns.size() == 1 &&
                            geo.groups[i].spawns.front().pos == target)
                            group = i;
                require(group >= 0, "actual singleton Elk54,64 on retained Expanse geometry");
                if (!geo.goal_field(stage, 0) || bc::fuel_remaining() < 65000) {
                    bc::end_turn();
                    continue;
                }
                if (!ptr)
                    ptr = std::make_unique<World>(geo, memory);
                auto &w = *ptr;
                w.refresh();
                if (phase == 0) {
                    if (w.self.pos == stage) {
                        if (primed < 0) {
                            require(w.groups[group].camps.size() == 1,
                                    "actual prime target visible");
                            auto h = w.camp(w.groups[group].camps.front().id);
                            require(h && w.me.abilities()[0].use(*h),
                                    "lawful real cast primes known cooldown");
                            primed = w.round;
                        } else if (w.round - primed == 2)
                            phase = 1;
                    } else if (auto next = w.toward(stage))
                        require(w.me.move_absolute(sdk(*next)),
                                "actual approach to outer cast tile");
                } else {
                    std::optional<SoloFarmQuote> prepaid;
                    require(w.groups[group].camps.size() == 1, "actual visible singleton");
                    const auto camp = w.groups[group].camps.front();
                    auto handle = w.camp(camp.id);
                    require(handle.has_value(), "actual visible camp handle");
                    if (phase == 1) {
                        require(w.self.hp == 700 && w.self.strength == 30 && w.self.focus == 70 &&
                                    camp.hp == 2260 && camp.strength == 60 && !camp.awake,
                                "native unmodified Cassi and Elk metadata");
                        require(!w.in_spawn(stage) && w.self.pos == stage &&
                                    distance(stage, camp.pos) == 4 && camp.range == 3,
                                "actual nonspawn distance4 outside camp range3");
                        require(w.spells[0].cooldown == 5,
                                "actual initial cooldown5 after native three owner ends");
                        const auto q = quote_solo_farm(w, group);
                        require(q.known && q.feasible && !q.ready_now &&
                                    q.mode == SoloFarmMode::DirectCastOnly && q.slot == 0 &&
                                    q.clear_ticks == 134 && q.remaining_hp == 700 &&
                                    q.total_ticks > 137 && q.rate > 0,
                                "actual shared quote chooses complete outer cycle over "
                                "unaffordable basic");
                        prepaid = q;
                        start = w.round;
                        phase = 2;
                        std::printf("CAST_ONLY_CERT round=%d shots=17 owners=%.0f hp=%.0f "
                                    "total=%.0f rate=%.6f\n",
                                    w.round, q.clear_ticks, q.remaining_hp, q.total_ticks, q.rate);
                    }
                    require(w.round == start + owners, "consecutive actual owner phases");
                    require(w.me.health() == 700 && position(w.me.position()) == stage &&
                                !w.in_spawn(stage),
                            "actual safe fixed outer tile never loses HP or heals on spawn");
                    auto q = prepaid ? *prepaid
                                     : (memory.mission.phase == Phase::Clear
                                            ? quote_current_solo_clear(w, group)
                                            : quote_solo_farm(w, group));
                    require(q.known && q.feasible && q.mode == SoloFarmMode::DirectCastOnly &&
                                q.slot == 0,
                            "fresh typed current quote including real cooldowns");
                    auto p = solo_farm_proposal(w, memory, q);
                    require(bool(p), "shared actual proposal builder accepts typed quote");
                    if (p->action.kind == Kind::CastCamp) {
                        require(w.round == start + 5 + 8 * casts && p->action.slot == 0,
                                "same selected direct slot on exact native cadence");
                        memory.mission = p->mission;
                        require(execute(w, p->action).success,
                                "actual shared gateway accepts cast");
                        ++casts;
                    } else {
                        require(p->action.kind == Kind::None && !q.ready_now &&
                                    p->mission.phase == Phase::Clear,
                                "cooldown is stationary Clear hold without basic/AoE substitution");
                        memory.mission = p->mission;
                    }

                    ++owners;
                    if (!handle->is_alive()) {
                        require(owners == 134 && casts == 17 && w.me.health() == 700,
                                "actual initiallyCD5 17cast134owner zero-pressure clear");
                        std::printf("CAST_ONLY_PASS owners=%d casts=%d hp=%.0f round=%d\n", owners,
                                    casts, w.me.health(), int(bc::round_number()));
                        phase = 3;
                    }
                }
            }
        } catch (const std::exception &e) {
            std::printf("CAST_ONLY_EXCEPTION %s\n", e.what());
            phase = 3;
        }
        bc::end_turn();
    }
}
