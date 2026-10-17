#define TACTICS_COORDINATION_MODEL_ONLY
#include "camp_collateral.h"
#include "coordination.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
namespace tactics {
// EXACT_ADMISSION
}
static int checks = 0;
static void need(bool value, const char *why) {
    ++checks;
    if (!value) {
        std::fprintf(stderr, "FAIL %s\n", why);
        std::exit(1);
    }
}
static Actor caster() {
    Actor a;
    a.id = 4;
    a.type = 0;
    a.pos = {1, 4};
    a.hp = a.max_hp = 1200;
    a.strength = 50;
    a.focus = 100;
    a.range = 1;
    a.alive = a.can_attack = a.can_cast = true;
    a.camp_mitigation = 1;
    auto &s = a.spells[0];
    s.slot = 0;
    s.kind = 3;
    s.ground = true;
    s.camps = false;
    s.ready = true;
    s.range = 4;
    s.radius = 1;
    s.amount = 100;
    s.duration = 1;
    s.cooldown = 0;
    s.recharge = 8;
    return a;
}
static std::vector<Camp> pair() {
    std::vector<Camp> out;
    for (int i = 0; i < 2; ++i) {
        Camp c;
        c.id = 30 + i;
        c.pos = {4, 4 + i};
        c.hp = 100;
        c.max_hp = 2400;
        c.strength = 60;
        c.range = 3;
        c.awake = true;
        out.push_back(c);
    }
    return out;
}
static CampRollout roll(const Actor &a, std::span<const Camp> camps, bool funded = true) {
    CampClearBody b;
    b.actor = a;
    std::vector<CampClearMonster> v;
    for (auto &c : camps)
        v.push_back({c, true});
    return rollout_camp_clear(std::span(&b, 1), v, a.id, 512, [&] { return funded; });
}
int main() {
    auto a = caster();
    auto camps = pair();
    const Pos target = camps[0].pos;
    need(distance(a.pos, target) == 3 && a.range + 1 == 2,
         "actual useful cast center lies beyond basicRange+1");
    need(current_camp_contribution(a, camps, true).ready, "current actual ground cast is useful");
    const BasicCampBody body{&a, 0};
    std::array<BasicCampMonster, 2> views{{{&camps[0], true}, {&camps[1], true}}};
    need(!sufficient_basic_clear(std::span(&body, 1), views, a.id).ready,
         "correct basic-only fallback cannot fund this cast");
    const auto action = stationary_camp_action(a, camps);
    need(action.kind == Kind::CastGround && action.slot == 0,
         "actual shared executor selects legal ground");
    for (const auto &c : camps)
        need(camp_action_damage(a, action, camps, c) == 100,
             "one actual ground kills each observed partially-cleared camp");
    const auto proof = roll(a, camps);
    need(proof.ready && proof.complete && proof.proof == ClearProofKind::DetailedBundle &&
             proof.ticks == 1,
         "exact detailed production model certifies one-cast clear");
    need(proof.damage_taken[0] == 0 && proof.remaining_hp[0] == 1200,
         "no extra tick-zero response is invented");
    need(!(distance(a.pos, target) <= a.range + 1),
         "frozen25r1 caller excludes the useful detailed proof");
    need(current_camp_assignment_candidate(a, camps, target, true, true, Lifecycle::Alive, 48000),
         "narrow candidate admits same exact current action at unchanged floor");
    need(!current_camp_assignment_candidate(a, camps, target, true, true, Lifecycle::Alive, 47999),
         "one-below existing floor still declines");
    need(!current_camp_assignment_candidate(a, camps, target, true, false, Lifecycle::Alive, 90000),
         "stale personal group is never admitted");
    need(
        !current_camp_assignment_candidate(a, camps, target, true, true, Lifecycle::Unknown, 90000),
        "unknown lifecycle is never alive proof");
    a.can_cast = false;
    need(!current_camp_assignment_candidate(a, camps, target, true, true, Lifecycle::Alive, 90000),
         "spent cast permission cannot widen current range");
    a.can_cast = true;
    a.completed = true;
    need(!current_camp_assignment_candidate(a, camps, target, true, true, Lifecycle::Alive, 90000),
         "completed actor cannot widen range");
    a.completed = false;
    a.stunned = true;
    need(!current_camp_assignment_candidate(a, camps, target, true, true, Lifecycle::Alive, 90000),
         "stunned actor cannot widen range");
    a.stunned = false;
    a.spells[0].ready = false;
    a.spells[0].cooldown = 1;
    need(!current_camp_assignment_candidate(a, camps, target, true, true, Lifecycle::Alive, 90000),
         "future cooldown is not a current ready contribution");
    a.spells[0].ready = true;
    a.spells[0].cooldown = 0;
    a.spells[0].exclusive = true;
    need(!current_camp_assignment_candidate(a, camps, target, false, true, Lifecycle::Alive, 90000),
         "spent movement vetoes exclusive cast extension");
    a.spells[0].exclusive = false;
    a.spells[0].range = 2;
    a.spells[0].radius = 4;
    need(!current_camp_assignment_candidate(a, camps, target, true, true, Lifecycle::Alive, 90000),
         "AoE radius cannot borrow cast-center range");
    a = caster();
    auto unknown = roll(a, camps, false);
    need(!unknown.ready && unknown.uncertain,
         "unfunded exact forecast remains Unknown after admission");
    Group selected;
    Group outside;
    outside.spawns.push_back({40, 0, {5, 4}, 500, 20, 3});
    std::array groups{selected, outside};
    need(external_camp_collateral(a, camps, groups, 0),
         "actual area hitting other group retains existing collateral veto");
    groups[1].spawns[0].pos = {9, 9};
    need(!external_camp_collateral(a, camps, groups, 0),
         "safe out-of-radius external group remains admissible to full proof");
    // Direct cast variant: a two-member original group with one remaining lowHP
    // member is still outside singleton-only SOLO routing; current direct cast
    // must be able to ask for the exact stationary certificate too.
    a = caster();
    a.spells[0].kind = 2;
    a.spells[0].ground = false;
    a.spells[0].camps = true;
    a.spells[0].radius = 0;
    camps.resize(1);
    need(current_camp_assignment_candidate(a, camps, target, true, true, Lifecycle::Alive, 48000),
         "legal current direct cast also admits detailed model");
    auto direct = roll(a, camps);
    need(direct.ready && direct.ticks == 1,
         "exact direct cast can finish actual observed remaining member");
    a = caster();
    a.pos = {3, 4};
    a.can_cast = false;
    need(current_camp_assignment_candidate(a, camps, target, true, true, Lifecycle::Alive, 48000),
         "existing ordinary basic neighborhood remains unchanged");
    std::printf("%d detailed-admission checks passed\n", checks);
}
