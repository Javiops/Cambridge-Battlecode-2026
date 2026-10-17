#define RESIZE_BURN_TO_65
// Controlled physical scheduling witness, not unchanged production Bot main.
// All stats/HP/permissions/rewards are read from the native engine. Camp HP is
// earned by actual basics; intent/claim and the controlled clear script are
// fixture protocol, never a projected future readiness certificate.
#define main retained_production_main
#include "retained-main.h"
#undef main
// Bot::turn is compiled for source affinity, but this fixture calls the
// production World adapter and normal action gateway directly.
#include <cstdio>
#include <memory>
using namespace tactics;
static void require(bool ok, const char *why) {
    if (!ok) {
        std::printf("RESIZE_FAIL %s\n", why);
        throw std::runtime_error(why);
    }
}
static void accepted_solo_bundle(World &w, Memory &m, const Proposal &p,
                                 bool required_reset = false) {
    const auto before = bc::fuel_remaining();
    auto basic = make_solo_basic_receipt(w, p);
    const bool paid_reset = basic.valid;
    bool needs_reset = false;
    for (const auto &s : w.self.spells)
        needs_reset |= s.kind == 1 && s.self && s.ready && w.self.can_cast;
    if (required_reset && needs_reset && p.action.kind == Kind::BasicCamp &&
        w.groups[p.mission.group].camps.front().hp > w.self.strength)
        require(basic.valid, "funded exact basic/reset receipt before modeled first hit");
    m.mission = p.mission;
    auto hit = execute(w, p.action);
    require(hit.success, "normal gateway accepts actual solo first hit");
    w.publish_claim(m.mission.group);
    if (!basic.valid && bc::fuel_remaining() < 50000) {
        std::printf("RESIZE_BUNDLE %d %d fuel=%u,%u reset=0 deferred-refresh=1\n", w.self.id,
                    w.round, unsigned(before), unsigned(bc::fuel_remaining()));
        return;
    }
    w.refresh();
    if (basic.valid) {
        auto reset = solo_basic_reset_followup(w, m, basic, true);
        require(reset.has_value(), "actual paid basic effect opens exact reset receipt");
        auto last = make_solo_reset_receipt(w, reset->mission, reset->action);
        require(last.valid, "funded actual self-reset before final basic");
        require(execute(w, reset->action).success, "actual self reset accepted");
        w.refresh(true);
        auto second = solo_reset_basic_followup(w, m, last, true);
        require(second.has_value(), "actual reset effect opens priced second basic");
        require(execute(w, second->action).success, "actual reset-receipt second basic accepted");
    }
    std::printf("RESIZE_BUNDLE %d %d fuel=%u,%u reset=%d\n", w.self.id, w.round, unsigned(before),
                unsigned(bc::fuel_remaining()), int(paid_reset));
}
static bool seed_actual_current(World &w, Memory &m, int gi) {
    const Actor *ally = nullptr;
    for (const auto &a : w.allies)
        if (a.id != w.self.id && a.alive)
            ally = &a;
    if (!ally || !w.matching_claim(ally->id, gi))
        return false;
    CampClearBody self, other;
    self.actor = w.self;
    other.actor = *ally;
    const auto &camp = w.groups[gi].camps.front();
    const std::array<CampClearMonster, 1> monsters{{{camp, true}}};
    const auto proof =
        basic_clear_rollout(std::array<CampClearBody, 2>{{self, other}}, monsters, w.self.id);
    if (!proof)
        return false;
    LocalAssignment assignment;
    assignment.ready = assignment.self_selected = assignment.locally_accepted = true;
    assignment.rollout = *proof;
    assignment.selected_ids = proof->selected_ids;
    assignment.collector_id = w.self.type == 3 ? w.self.id : ally->id;
    Mission job;
    job.group = gi;
    job.phase = Phase::Clear;
    job.start = job.last_progress = w.round;
    job.expiry = w.round + Settings::job_lease;
    job.last_camp_hp = camp.hp;
    job.rate = 24. / (proof->ticks + 14);
    job.target = camp.pos;
    require(name_current_crew(job, assignment, w.self.id),
            "actual fixed crew proof installs typed collector metadata");
    Action hit;
    hit.kind = Kind::BasicCamp;
    hit.target = camp.id;
    require(execute(w, hit).success,
            "actual accepted first hit activates controlled current contract");
    m.mission = job;
    std::printf("RESIZE_SEEDED %d %d %d\n", w.self.id, w.round, job.planned_collector);
    return true;
}
static CurrentResizeCycle priced_current(const CampRollout &r, const World &w, int group,
                                         int collector, Pos capture, Pos bank, int capture_steps,
                                         int bank_steps) {
    CurrentResizeCycle c;
    c.owner = w.self.id;
    c.group = group;
    c.round = w.round;
    c.serial = w.serial;
    c.collector = collector;
    c.count = int(r.selected_ids.size());
    for (int k = 0; k < c.count; ++k)
        c.ids[k] = r.selected_ids[k];
    c.capture = capture;
    c.bank = bank;
    c.reward_once = c.collector_reward = 24;
    c.recipients = 1;
    c.collector_conversion_priced = true;
    c.clear_ticks = r.ticks;
    c.capture_ticks = capture_steps + bc::constants::capture_time + 1;
    c.bank_ticks = bank_steps + current_tribute_ticks(24);
    c.known = r.complete;
    c.sufficient = r.ready;
    c.complete = capture_steps >= 0 && bank_steps >= 0 && capture_steps != unreachable &&
                 bank_steps != unreachable;
    return c;
}
int main() {
    Geometry geo;
    Memory memory;
    std::unique_ptr<World> world;
    int current = -1, other = -1, phase = 0;
    bool seeded = false, compared = false, banked = false;
    const bool mirror = bc::detail::sdk_my_team() == 1;
    const auto at = [&](int x, int y) { return mirror ? Pos{47 - x, 47 - y} : Pos{x, y}; };
    const Pos current_at = at(10, 9), other_at = at(10, 11), cassi_stage = at(8, 9),
              issac_stage = at(9, 10), altar = at(8, 8);
    while (true) {
        try {
            if (bc::is_draft()) {
                bc::draft::pick(bc::champion_draft::cassi_and_issac);
                bc::end_turn();
                continue;
            }
            if (banked) {
                bc::end_turn();
                continue;
            }
            geo.initialize();
            if (!geo.initialized) {
                bc::end_turn();
                continue;
            }
            if (current < 0)
                for (unsigned gi = 0; gi < geo.groups.size(); ++gi) {
                    const auto p = geo.groups[gi].spawns.front().pos;
                    if (p == current_at)
                        current = int(gi);
                    if (p == other_at)
                        other = int(gi);
                }
            require(current >= 0 && other >= 0,
                    "actual public current and alternate Gem groups exist");
            bool fields = true;
            for (auto p : {current_at, other_at, cassi_stage, issac_stage})
                fields = geo.goal_field(p, 0) && fields;
            if (!fields || bc::fuel_remaining() < 70000) {
                bc::end_turn();
                continue;
            }
            if (!world)
                world = std::make_unique<World>(geo, memory);
            world->refresh();
            auto &w = *world;
            if (w.round != int(bc::round_number()) || bc::fuel_remaining() < 45000) {
                bc::end_turn();
                continue;
            }
            const bool is_cassi = w.self.type == 3, is_issac = w.self.type == 4;
            require(is_cassi || is_issac, "actual duo body");
            w.me.set_priority(
                is_issac ? 1 : 0); // Actual next-round priority, not simulated owner order.
            const Pos stage = is_cassi ? cassi_stage : issac_stage;
            if (phase == 0) {
                if (w.self.pos != stage) {
                    if (auto next = w.toward(stage)) {
                        require(w.me.move_absolute(sdk(*next)), "lawful physical staging");
                    }
                    bc::end_turn();
                    continue;
                }
                phase = 1;
            }
            w.publish_claim(is_issac && phase >= 2 ? other : current);
            if (phase == 1) {
                const auto &v = w.groups[current];
                if (!v.fresh(w.round) || v.camps.empty()) {
                    bc::end_turn();
                    continue;
                }
                const Camp camp = v.camps.front();
                if (!seeded) {
                    seeded = seed_actual_current(w, memory, current);
                    bc::end_turn();
                    continue;
                }
                renew_crew_clear_lease(memory.mission, w.round, v.seen, true, camp.hp);
                if (is_cassi) {
                    if (camp.hp > 20.001) {
                        require(w.self.strength == 30 && w.self.hp == 700,
                                "actual unupgraded Cassi basic kit");
                        Action a;
                        a.kind = Kind::BasicCamp;
                        a.target = camp.id;
                        require(execute(w, a).success, "actual30 basic earns the final20HP state");
                    } else if (camp.hp > 0) {
#ifdef RESIZE_OLD_DISPATCH_PROBE
                        const auto old = farming(w, memory);
                        std::printf("RESIZE_OLD_DISPATCH %d %d kind=%d phase=%d\n", w.self.id,
                                    w.round, old ? int(old->action.kind) : -1,
                                    old ? int(old->mission.phase) : -1);
                        require(old && old->action.kind != Kind::BasicCamp,
                                "old crew-first path returns a hold before solo fallback");
                        Action a;
                        a.kind = Kind::BasicCamp;
                        a.target = camp.id;
                        require(execute(w, a).success, "diagnostic actual direct final hit");
#else
#ifdef RESIZE_BURN_TO_65
                        while (bc::fuel_remaining() > 65500)
                            bc::round_number();
#endif
                        const auto before = bc::fuel_remaining();
                        auto retained = current_resize_proposal(w, memory, false);
                        require(
                            retained && retained->action.kind == Kind::BasicCamp &&
                                retained->mission.assembly_count == 0,
                            "retained actual collector recertifies its own immediate current job");
                        memory.mission = retained->mission;
                        require(execute(w, retained->action).success,
                                "new current collector gateway accepts real final hit");
                        std::printf("RESIZE_RETAINED %d %d fuel=%u,%u\n", w.self.id, w.round,
                                    unsigned(before), unsigned(bc::fuel_remaining()));
#endif
                        phase = 3;
                        std::printf("RESIZE_REMAINING_KILL %d %d\n", w.self.id, w.round);
                    }
                } else if (!compared && camp.hp <= 20.001) {
                    const Actor *remaining = nullptr;
                    for (const auto &a : w.allies)
                        if (a.type == 3 && a.alive)
                            remaining = &a;
                    require(remaining && remaining->id < w.self.id,
                            "actual stable lower-ID remaining collector");
                    require(w.self.hp == 900 && w.self.strength == 40 && w.self.pos == issac_stage,
                            "actual unupgraded Issac state");
                    require(w.groups[other].fresh(w.round) && w.groups[other].camps.size() == 1,
                            "actual visible alternate singleton");
                    require(w.geo.groups[current].spawns.size() == 1 &&
                                !w.on_group(current, w.self.pos) &&
                                !w.on_group(other, remaining->pos),
                            "distinct singleton regions; self departure does not retain capture "
                            "eligibility");
                    require(!current_resize_proposal(w, memory, true) &&
                                memory.mission.group == current,
                            "active transaction declines without stealing the current job");
#ifdef RESIZE_BURN_TO_65
                    while (bc::fuel_remaining() > 65500)
                        bc::round_number();
#endif
                    const auto before_runtime = bc::fuel_remaining();
                    require(before_runtime >= 65000,
                            "fixture native budget remains available for runtime adapter");
                    auto proposal = current_resize_proposal(w, memory, false);
                    require(proposal && proposal->action.kind == Kind::BasicCamp &&
                                proposal->mission.group == other,
                            "actual runtime adapter chooses finite different job");
                    std::printf("RESIZE_RUNTIME %d %d fuel=%u,%u\n", w.self.id, w.round,
                                unsigned(before_runtime), unsigned(bc::fuel_remaining()));
                    accepted_solo_bundle(w, memory, *proposal);
                    std::printf("RESIZE_SPLIT %d %d hp=%.0f\n", w.self.id, w.round, camp.hp);
                    compared = true;
                    phase = 2;
                }
                bc::end_turn();
                continue;
            }
            const int selected = is_cassi ? current : other;
            const Pos capture = is_cassi ? current_at : other_at;
            if (phase == 2) {
                if (w.groups[selected].fresh(w.round) &&
                    w.groups[selected].state == Lifecycle::Alive) {
                    auto p = solo_clear_followup(w, memory);
                    require(p.has_value(), "actual alternate remains freshly affordable");
                    accepted_solo_bundle(w, memory, *p);
                    bc::end_turn();
                    continue;
                } else if (w.groups[selected].fresh(w.round) &&
                           w.groups[selected].state == Lifecycle::Reward)
                    phase = 3;
                else {
                    bc::end_turn();
                    continue;
                }
            }
            if (phase == 3) {
                if (w.self.gems > 0) {
                    require(w.self.gems == 24, "actual distinct24 gem payout");
                    phase = 4;
                    std::printf("RESIZE_CAPTURE %d %d %d\n", w.self.id, w.round, w.self.gems);
                } else {
                    if (w.self.pos != capture)
                        if (auto next = w.toward(capture))
                            require(w.me.move_absolute(sdk(*next)),
                                    "actual collector path after clear");
                    bc::end_turn();
                    continue;
                }
            }
            if (phase == 4) {
                if (w.self.gems == 0) {
                    std::printf("RESIZE_BANK %d %d team=%u\n", w.self.id, w.round,
                                bc::global_submitted_gems(bc::team::ally));
                    banked = true;
                } else if (distance(w.self.pos, altar) <= int(bc::constants::submit_gems_range)) {
                    if (w.self.channel == Channel::None) {
                        Action a;
                        a.kind = Kind::Tribute;
                        a.at = altar;
                        require(execute(w, a).success, "actual tribute accepted");
                    }
                } else if (auto next = w.toward(altar, bc::constants::submit_gems_range))
                    require(w.me.move_absolute(sdk(*next)), "actual physical bank route");
            }
        } catch (const std::exception &e) {
            std::printf("RESIZE_EXCEPTION %s\n", e.what());
            banked = true;
        }
        bc::end_turn();
    }
}
