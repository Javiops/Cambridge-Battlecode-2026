#define main tactics_unused_production_main
#include "production-main.h"
#undef main
#include <cstdio>
#include <stdexcept>
static void require(bool ok, const char *why) {
    if (!ok) {
        std::printf("CAST_ONLY_FAIL %s\n", why);
        throw std::runtime_error(why);
    }
}
int main() {
    using namespace tactics;
    Geometry geo;
    Memory memory;
    std::unique_ptr<World> ptr;
    Bot bot;
    int group = -1, phase = 0, owners = 0, casts = 0, start = -1;
    const Pos target{54, 64}, stage{58, 65};
    std::optional<bc::camp> handle;
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
                       phase < 4) {
                if (phase == 0) {
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
                    require(group >= 0, "actual singleton Elk54,64 on original Expanse");
                    if (!geo.goal_field(stage, 0) || bc::fuel_remaining() < 65000) {
                        bc::end_turn();
                        continue;
                    }
                    if (!ptr)
                        ptr = std::make_unique<World>(geo, memory);
                    auto &w = *ptr;
                    w.refresh();
                    if (w.self.pos != stage) {
                        if (auto next = w.toward(stage))
                            require(w.me.move_absolute(sdk(*next)),
                                    "actual lawful prelude approach");
                    } else {
                        require(w.self.hp == 700 && w.self.strength == 30 && w.self.focus == 70,
                                "native unmodified Cassi metadata");
                        require(w.groups[group].camps.size() == 1, "actual visible Elk");
                        handle = w.camp(w.groups[group].camps.front().id);
                        require(handle && handle->health() == 2400, "actual untouched target");
                        phase = 1;
                        std::printf("CAST_ONLY_CERT wholemain-ready round=%d hp=700\n", w.round);
                    }
                } else if (phase <= 2) {
                    require(handle && handle->is_alive(),
                            "native Elk alive before production owner");
                    const double before = handle->health();
                    const int round = int(bc::round_number());
                    if (start >= 0) {
                        require(position(bc::self().position()) == stage &&
                                    bc::self().health() == 700,
                                "full main keeps safe outer tile while clearing");
                        ++owners;
                    }
                    bot.turn();
                    require(bc::self().health() == 700,
                            "actual production clear preserves zero-pressure HP");
                    const bool alive = handle->is_alive();
                    const double after = alive ? handle->health() : 0;
                    if (after < before) {
                        require(position(bc::self().position()) == stage,
                                "actual damage originated from distance4");
                        if (start < 0) {
                            start = round;
                            owners = 1;
                        }
                        require(round == start + 8 * casts,
                                "full main preserves real8owner cast schedule");
                        ++casts;
                        phase = 2;
                    }
                    if (!alive) {
                        require(casts == 18 && owners == 137 && round == start + 136,
                                "wholemain18casts137owners exact native clear");
                        phase = 3;
                        std::printf("CAST_ONLY_CLEAR owners=%d casts=%d hp=700 round=%d\n", owners,
                                    casts, round);
                    }
                } else {
                    bot.turn();
                    if (bc::global_submitted_gems(bc::team::ally) >= 36) {
                        std::printf(
                            "CAST_ONLY_PASS owners=%d casts=%d hp=%.0f round=%d banked=%d\n",
                            owners, casts, bc::self().health(), int(bc::round_number()),
                            int(bc::global_submitted_gems(bc::team::ally)));
                        phase = 4;
                    }
                }
            }
        } catch (const std::exception &e) {
            std::printf("CAST_ONLY_EXCEPTION %s\n", e.what());
            phase = 4;
        }
        bc::end_turn();
    }
}
