#define TACTICS_COORDINATION_MODEL_ONLY
#include "coordination.h"
#include "farm_observation.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
namespace bc {
inline unsigned remaining = 100000;
inline int now = 100;
inline unsigned fuel_remaining() {
    return remaining;
}
inline int round_number() {
    return now;
}
namespace constants {
inline constexpr int capture_time = 5, max_rounds = 2000;
}
} // namespace bc
namespace tactics {
// EXACT_FUNDING
struct SoloFarmQuote {};
// EXACT_TYPES
struct World {
    int round = 100, serial = 5;
    Actor self;
    std::vector<GroupView> groups;
    std::vector<Actor> allies, enemies;
    struct Sighting {
        Actor actor;
        int round;
    };
    std::vector<Sighting> sightings;
    struct Geo {
        int width = 16, height = 16;
        std::vector<Group> groups;
        bool routes = true;
        std::optional<int> cached_steps(Pos a, Pos b) const {
            return routes ? std::optional<int>(distance(a, b)) : std::nullopt;
        }
    } geo;
    std::vector<std::uint8_t> visible_bytes = std::vector<std::uint8_t>(32, 255);
    LocalAssignment assignment;
    int probes = 0, consumers = 0;
    unsigned model_cost = 0;
    bool warning = false, wrong_epoch = false, mutate_before_consumer = false;
    bool warning_near(Pos, int) const {
        return warning;
    }
    bool on_group(int i, Pos p) const {
        for (const auto &s : geo.groups[i].spawns)
            if (s.pos == p)
                return true;
        return false;
    }
    int altar_distance(Pos) const {
        return 3;
    }
    int home_distance(Pos) const {
        return 2;
    }
};
namespace combat_detail {
inline bool recent_sighting(int age) {
    return age >= 1 && age <= 3;
}
} // namespace combat_detail
inline int current_recall_ticks(const Actor &a) {
    return a.home ? 3 : 5;
}
inline int current_tribute_ticks(int gems) {
    return tribute_ticks(gems);
}
inline LocalAssignment
propose_local_assignment(World &w, int, AssignmentFunding funding = AssignmentFunding::Ordinary) {
    ++w.probes;
    if (funding != AssignmentFunding::OneCurrentCast)
        std::abort();
    bc::remaining -= std::min(bc::remaining, w.model_cost);
    if (w.wrong_epoch)
        ++bc::now;
    return w.assignment;
}
// EXACT_VALIDITY
inline std::optional<Proposal> farming(World &w, Memory &m, const SoloFarmQuote *,
                                       CurrentCastFarmQuote *q) {
    ++w.consumers;
    if (w.mutate_before_consumer)
        ++w.serial;
    if (!current_cast_quote_valid(w, m, *q))
        return std::nullopt;
    Proposal p;
    p.valid = p.crew_clear_certified = true;
    p.crew_clear_proof = q->assignment.rollout.proof;
    p.mission = m.mission;
    p.mission.rate = q->farm.rate;
    p.mission.phase = Phase::Clear;
    p.action.kind = Kind::CastGround;
    q->serial = -1;
    return p;
}
// EXACT_EARLY
} // namespace tactics
static int checks = 0;
static void need(bool v, const char *why) {
    ++checks;
    if (!v) {
        std::fprintf(stderr, "FAIL %s\n", why);
        std::exit(1);
    }
}
static World setup() {
    bc::remaining = 100000;
    bc::now = 100;
    World w;
    auto &a = w.self;
    a.id = 0;
    a.type = 0;
    a.pos = {1, 4};
    a.hp = a.max_hp = 1200;
    a.strength = 50;
    a.focus = 100;
    a.range = 1;
    a.alive = a.can_attack = a.can_cast = true;
    auto &s = a.spells[0];
    s.slot = 0;
    s.kind = 3;
    s.ground = s.ready = s.camps = true;
    s.amount = 100;
    s.range = 4;
    s.radius = 1;
    s.cooldown = 0;
    s.recharge = 8;
    Group g;
    g.gems = 36;
    g.gold = 100;
    GroupView v;
    v.state = Lifecycle::Alive;
    v.seen = 100;
    for (int i = 0; i < 2; ++i) {
        Camp c;
        c.id = 30 + i;
        c.pos = {4, 4 + i};
        c.hp = 100;
        c.max_hp = 2400;
        c.strength = 60;
        c.range = 3;
        c.awake = true;
        v.camps.push_back(c);
        g.spawns.push_back({c.id, 0, c.pos, c.max_hp, c.strength, c.range});
    }
    w.geo.groups.push_back(g);
    w.groups.push_back(v);
    auto &r = w.assignment;
    r.ready = r.self_selected = r.locally_accepted = true;
    r.selected_ids = {0};
    r.clear_ticks = 1;
    r.rollout.ready = r.rollout.complete = true;
    r.rollout.proof = ClearProofKind::DetailedBundle;
    r.rollout.selected_ids = {0};
    r.rollout.remaining_hp = {1200};
    r.rollout.damage_taken = {0};
    return w;
}
static Memory mem() {
    Memory m;
    m.mission.group = 0;
    m.mission.phase = Phase::Observe;
    m.mission.start = 99;
    m.mission.expiry = 106;
    m.mission.rate = 999999;
    return m;
}
int main() {
    need(assignment_planning_floor(false, 100000, AssignmentFunding::Ordinary) == 88000,
         "ordinary forecast retains exact12k optional slice");
    need(assignment_planning_floor(false, 100000, AssignmentFunding::OneCurrentCast) == 70000,
         "only named current cast gets exact30k measured slice");
    need(assignment_planning_floor(false, 56000, AssignmentFunding::OneCurrentCast) == 32000,
         "named allowance never borrows hard32k action reserve");
    need(assignment_planning_floor(false, 48000, AssignmentFunding::Ordinary) == 36000,
         "ordinary48k entry keeps original12k slice");
    need(assignment_planning_floor(false, 48000, AssignmentFunding::OneCurrentCast) == 32000,
         "named48k entry clips to hard32k not negative budget");
    need(assignment_planning_floor(true, 80000, AssignmentFunding::Ordinary) == 32000,
         "existing committed crew budget unchanged");
    need(assignment_planning_floor(true, 80000, AssignmentFunding::OneCurrentCast) == 32000,
         "named flag cannot enlarge committed hard floor");
    {
        auto w = setup();
        auto m = mem();
        auto p = early_current_cast_farm_proposal(w, m, false);
        need(p && p->crew_clear_proof == ClearProofKind::DetailedBundle,
             "funded exact current cast reaches common proof consumer");
        need(w.probes == 1 && w.consumers == 1,
             "one current hypothesis and no repeated ordinary ranking");
        need(p->mission.rate > 0 && p->mission.rate < 3,
             "complete cached gem cycle replaces raw Observe999999 rate");
    }
    for (auto phase :
         {Phase::Clear, Phase::Collect, Phase::Deliver, Phase::Recover, Phase::Channel}) {
        auto w = setup();
        auto m = mem();
        m.mission.phase = phase;
        need(!early_current_cast_farm_proposal(w, m, false) && w.probes == 0,
             "protected phase is not re-entered as elective current cast");
    }
    {
        auto w = setup();
        auto m = mem();
        need(!early_current_cast_farm_proposal(w, m, true) && w.probes == 0,
             "transaction/receipt/chain protection precedes payload/probe");
    }
    {
        auto w = setup();
        auto m = mem();
        bc::remaining = 55999;
        need(!early_current_cast_farm_proposal(w, m, false) && w.probes == 0,
             "unfunded entry declines without native forecast");
    }
    {
        auto w = setup();
        auto m = mem();
        bc::remaining = 56000;
        need(early_current_cast_farm_proposal(w, m, false).has_value(),
             "declared current entry can fund known bounded proof");
    }
    {
        auto w = setup();
        auto m = mem();
        w.model_cost = 69000;
        need(!early_current_cast_farm_proposal(w, m, false) && w.consumers == 0,
             "model consuming hard action reserve cannot publish proof");
    }
    {
        auto w = setup();
        auto m = mem();
        w.wrong_epoch = true;
        need(!early_current_cast_farm_proposal(w, m, false) && w.consumers == 0,
             "epoch boundary invalidates paid quote before consumer");
    }
    {
        auto w = setup();
        auto m = mem();
        w.mutate_before_consumer = true;
        need(!early_current_cast_farm_proposal(w, m, false),
             "changed World serial cannot reuse old completed quote");
    }
    {
        auto w = setup();
        auto m = mem();
        w.geo.routes = false;
        need(!early_current_cast_farm_proposal(w, m, false),
             "missing cached capture route remains Unknown");
    }
    {
        auto w = setup();
        auto m = mem();
        w.assignment.ready = false;
        w.assignment.uncertain = true;
        need(!early_current_cast_farm_proposal(w, m, false) && w.consumers == 0,
             "unknown detailed forecast cannot fall back to coarse readiness");
    }
    {
        auto w = setup();
        auto m = mem();
        w.assignment.locally_accepted = false;
        need(!early_current_cast_farm_proposal(w, m, false),
             "no actual current permission never becomes first hit");
    }
    for (double hp : {std::numeric_limits<double>::quiet_NaN(),
                      std::numeric_limits<double>::infinity(), 0.0, -1.0}) {
        auto w = setup();
        auto m = mem();
        w.self.hp = hp;
        need(!early_current_cast_farm_proposal(w, m, false) && w.probes == 0,
             "nonfinite/nonpositive actual HP rejected before payload/probe");
    }
    for (double maxhp : {std::numeric_limits<double>::quiet_NaN(),
                         std::numeric_limits<double>::infinity(), 0.0, -1.0}) {
        auto w = setup();
        auto m = mem();
        w.self.max_hp = maxhp;
        need(!early_current_cast_farm_proposal(w, m, false) && w.probes == 0,
             "nonfinite/nonpositive actual maxHP rejected before payload/probe");
    }
    {
        auto w = setup();
        auto m = mem();
        w.assignment.rollout.remaining_hp = {1199};
        w.assignment.rollout.damage_taken = {1};
        need(!early_current_cast_farm_proposal(w, m, false) && w.consumers == 0,
             "modeled HP-loss/recovery cycle outside initial early-cast scope");
    }
    {
        auto w = setup();
        auto m = mem();
        w.assignment.rollout.remaining_hp = {1200};
        w.assignment.rollout.damage_taken = {1};
        need(!early_current_cast_farm_proposal(w, m, false) && w.consumers == 0,
             "future modeled heal cannot disguise injury as free recovery");
    }
    {
        auto w = setup();
        auto m = mem();
        w.assignment.rollout.remaining_hp = {std::numeric_limits<double>::quiet_NaN()};
        need(!early_current_cast_farm_proposal(w, m, false),
             "nonfinite forecast cannot authorize cycle");
    }
    {
        auto w = setup();
        auto m = mem();
        w.assignment.selected_ids = {0, 1};
        need(!early_current_cast_farm_proposal(w, m, false),
             "helper-dependent proof is outside bounded self-only current extension");
    }
    {
        auto w = setup();
        auto m = mem();
        w.assignment.rollout.proof = ClearProofKind::BasicOnly;
        need(!early_current_cast_farm_proposal(w, m, false),
             "ordinary BasicOnly path does not become cast bundle");
    }
    {
        auto w = setup();
        auto m = mem();
        w.self.pos = {3, 4};
        need(!early_current_cast_farm_proposal(w, m, false) && w.probes == 0,
             "existing useful basic controller retained");
    }
    {
        auto w = setup();
        auto m = mem();
        w.self.can_cast = false;
        need(!early_current_cast_farm_proposal(w, m, false),
             "spent current cast cannot trigger future-cooldown forecast");
    }
    {
        auto w = setup();
        auto m = mem();
        w.self.completed = true;
        need(!early_current_cast_farm_proposal(w, m, false), "completed owner excluded");
    }
    {
        auto w = setup();
        auto m = mem();
        w.self.stunned = true;
        need(!early_current_cast_farm_proposal(w, m, false), "stunned owner excluded");
    }
    {
        auto w = setup();
        auto m = mem();
        w.self.gems = 1;
        need(!early_current_cast_farm_proposal(w, m, false), "actual bag conversion retained");
    }
    {
        auto w = setup();
        auto m = mem();
        m.mission.assembly_pending = true;
        need(!early_current_cast_farm_proposal(w, m, false), "accepted rendezvous retained");
    }
    {
        auto w = setup();
        auto m = mem();
        m.mission.assembly_count = 1;
        need(!early_current_cast_farm_proposal(w, m, false),
             "named paid crew retains existing current controller");
    }
    {
        auto w = setup();
        auto m = mem();
        m.hold_group = 0;
        need(!early_current_cast_farm_proposal(w, m, false), "actual holder retained");
    }
    {
        auto w = setup();
        auto m = mem();
        m.mission.expiry = 100;
        need(!early_current_cast_farm_proposal(w, m, false),
             "expired unpriced intent cannot start new selected job");
    }
    {
        auto w = setup();
        auto m = mem();
        m.failed_group = 0;
        m.failed_until = 101;
        need(!early_current_cast_farm_proposal(w, m, false),
             "suppressed failed objective retained");
    }
    {
        auto w = setup();
        auto m = mem();
        w.groups[0].seen = 99;
        need(!early_current_cast_farm_proposal(w, m, false), "stale observation excluded");
    }
    {
        auto w = setup();
        auto m = mem();
        w.visible_bytes.assign(32, 0);
        need(!early_current_cast_farm_proposal(w, m, false),
             "group lifecycle alone does not prove personal members");
    }
    {
        auto w = setup();
        auto m = mem();
        w.geo.groups[0].gems = 0;
        need(!early_current_cast_farm_proposal(w, m, false), "unpriced gold is not score income");
    }
    {
        auto w = setup();
        auto m = mem();
        w.warning = true;
        need(!early_current_cast_farm_proposal(w, m, false), "danger warning protects entry");
    }
    {
        auto w = setup();
        auto m = mem();
        w.enemies.push_back(w.self);
        need(!early_current_cast_farm_proposal(w, m, false),
             "observed threat uses ordinary survival decision");
    }
    {
        auto w = setup();
        auto m = mem();
        w.sightings.push_back({w.self, 99});
        need(!early_current_cast_farm_proposal(w, m, false),
             "recent unseen threat remains known caution");
    }
    {
        auto w = setup();
        auto m = mem();
        w.groups.push_back({});
        w.geo.groups.push_back({});
        w.groups[1].seen = 100;
        Camp c;
        c.hp = 100;
        c.awake = true;
        c.strength = 20;
        c.range = 3;
        c.pos = {1, 5};
        w.groups[1].camps.push_back(c);
        need(!early_current_cast_farm_proposal(w, m, false) && w.probes == 0,
             "external awake pressure cannot hide behind selected-group proof");
    }
    std::printf("%d funded-current-cast checks passed\n", checks);
}
