#define TACTICS_COORDINATION_MODEL_ONLY
#define TACTICS_SOLO_MODEL_ONLY
#include "solo.h"
#include "information.h"
#include <cstdio>
#include <cstdlib>
#include <string_view>
using namespace tactics;
namespace bc {
inline int now = 100;
inline int round_number() { return now; }
inline unsigned fuel_remaining() { return 100000; }
}
inline bool fuel(int) { return true; }
struct World {
    struct Geo { int index(Pos p) const { return p.y * 20 + p.x; } } geo;
    Memory &memory;
    Actor self;
    std::array<Spell, 2> spells;
    std::vector<GroupView> groups;
    std::vector<std::uint8_t> visible_bytes = std::vector<std::uint8_t>(50, 255);
    int round = 100, serial = 7;
    explicit World(Memory &m) : memory(m) {}
    bool free(Pos) const { return true; }
};
inline bool farm_safe(World &, int) { return true; }
inline double incoming_damage(World &, Pos) { return 0; }
inline bool current_solo_quote(const World &w, const SoloFarmQuote &q, int gi) {
    return q.group == gi && q.owner == w.self.id && q.round == w.round &&
           q.serial == w.serial && q.origin == w.self.pos;
}
inline Proposal economic(const Action &a, const Mission &m, Priority p, double value) {
    Proposal out; out.action = a; out.mission = m; out.priority = p;
    out.value = value; out.valid = true; return out;
}
inline Action moving(Pos at, const char *reason) {
    Action out; out.kind = Kind::Move; out.at = at; out.reason = reason; return out;
}
static int cast_calls = 0;
// Explicit model stand-in for expensive World route/visibility checks. The
// actual fixed-position certificate and required-slot filter are production.
inline SoloFarmQuote quote_solo_cast_farm(World &w, int gi, bool current_only) {
    ++cast_calls;
    SoloFarmQuote out;
    const auto &camp = w.groups[gi].camps.front();
    const auto clear = certify_cast_only_clear(w.self, camp, w.self.pos, 0, {}, 0, 2000,
                                               true, current_only ? w.memory.mission.solo_slot : -1);
    if (!clear.known || !clear.feasible)
        return out;
    out.group = gi; out.owner = w.self.id; out.round = w.round; out.serial = w.serial;
    out.origin = out.stage = w.self.pos; out.target = camp.pos;
    out.mode = SoloFarmMode::DirectCastOnly; out.slot = clear.slot;
    out.current_only = current_only; out.known = out.feasible = true;
    out.ready_now = clear.ready_now; out.rate = .5; return out;
}
// EXACT_CURRENT_DISPATCH
// EXACT_TYPED_SOLO_CONSUMER
static int checks = 0;
static void require(bool ok, const char *why) {
    ++checks;
    if (!ok) { std::fprintf(stderr, "FAIL%d %s\n", checks, why); std::exit(1); }
}
static SoloFarmQuote manual_basic(World &w) {
    SoloFarmQuote q; q.group = 0; q.owner = w.self.id; q.round = w.round;
    q.serial = w.serial; q.origin = q.stage = w.self.pos;
    q.target = w.groups[0].camps.front().pos;
    q.known = q.feasible = q.ready_now = true; q.rate = .5; return q;
}
int main() {
    Memory m; World w(m);
    w.self.id = 6; w.self.type = 3; w.self.alive = true;
    w.self.can_attack = w.self.can_cast = true; w.self.pos = {3, 3};
    w.self.range = 3; w.self.strength = 30; w.self.hp = w.self.max_hp = 700;
    for (int k = 0; k < 2; ++k) {
        auto &s = w.self.spells[k]; s.slot = k; s.kind = 2; s.camps = true;
        s.range = 4; s.amount = k ? 1000 : 140; s.recharge = 8;
        s.cooldown = k ? 0 : 5; s.ready = k != 0;
    }
    w.spells = w.self.spells;
    Camp camp; camp.id = 3; camp.pos = {5, 3}; camp.hp = camp.max_hp = 500;
    camp.range = 0; camp.strength = 0;
    GroupView view; view.state = Lifecycle::Alive; view.seen = 100;
    view.camps.push_back(camp); w.groups.push_back(view);
    require(distance(w.self.pos, camp.pos) > camp.range &&
            distance(w.self.pos, camp.pos) <= w.self.range,
            "explicit generic overlap supports both safe direct casting and a legal basic");
    require(m.mission.solo_mode == SoloFarmMode::None && m.mission.solo_slot == -1,
            "an unpriced mission has no implicit direct or combined controller");
    m.mission.group = 0; m.mission.phase = Phase::Clear;
    m.mission.solo_mode = SoloFarmMode::Combined;
    cast_calls = 0;
    auto dispatch = current_solo_dispatch(w, 0);
    require(!dispatch && cast_calls == 0,
            "actual Combined dispatch reaches scalar body without probing a cast-only alternative");
    const auto scalar = certify_solo_clear(w.self, camp, w.self.pos, 0, true);
    require(scalar.known && scalar.feasible && scalar.current_followup == Kind::CastCamp &&
            scalar.current_slot == 1,
            "Combined scalar retains its actual basic plus useful current cast credit");
    auto combined = manual_basic(w); combined.current_only = true;
    combined.current_followup = scalar.current_followup; combined.current_slot = scalar.current_slot;
    auto p = solo_farm_proposal(w, m, combined);
    require(p && p->action.kind == Kind::BasicCamp && p->mission.solo_mode == SoloFarmMode::Combined &&
            p->mission.solo_slot == -1 && p->solo_current_slot == 1,
            "Combined common consumer executes basic and preserves the credited followup");
    m.mission.solo_mode = SoloFarmMode::DirectCastOnly; m.mission.solo_slot = 0;
    cast_calls = 0; dispatch = current_solo_dispatch(w, 0);
    require(dispatch && dispatch->known && dispatch->mode == SoloFarmMode::DirectCastOnly &&
            dispatch->slot == 0 && !dispatch->ready_now && cast_calls == 1,
            "actual Direct dispatch preserves stored cooldown slot instead of ready stronger slot");
    p = solo_farm_proposal(w, m, *dispatch);
    require(p && p->action.kind == Kind::None && p->mission.phase == Phase::Clear &&
            p->mission.solo_mode == SoloFarmMode::DirectCastOnly && p->mission.solo_slot == 0,
            "Direct cooldown hold cannot substitute a legal in-range basic");
    w.self.spells[0].ready = true; w.self.spells[0].cooldown = 0; w.spells = w.self.spells;
    dispatch = current_solo_dispatch(w, 0); p = solo_farm_proposal(w, m, *dispatch);
    require(p && p->action.kind == Kind::CastCamp && p->action.slot == 0,
            "Direct ready owner executes the exact committed slot");
    w.self.spells[0].cooldown = -1; w.spells = w.self.spells;
    dispatch = current_solo_dispatch(w, 0);
    require(dispatch && !dispatch->known,
            "failed Direct slot proof returns invalid without falling into Combined");
    w.self.spells[0].cooldown = 5; w.self.spells[0].ready = false; w.spells = w.self.spells;
    const auto bound = certify_cast_only_clear(w.self, camp, w.self.pos, 0, {}, 0, 2000, true, 0);
    const auto reprice = certify_cast_only_clear(w.self, camp, w.self.pos, 0);
    require(bound.known && bound.slot == 0 && bound.first_delay == 5 && !bound.ready_now,
            "production direct certificate honors exact bound cooldown");
    require(reprice.known && reprice.slot == 1 && reprice.ready_now,
            "a separate full quote may explicitly compare another ready slot");
    require(!certify_cast_only_clear(w.self,camp,w.self.pos,0,{},0,2000,true,2).known,
            "invalid required slot stays unknown");
    m.mission.solo_mode = SoloFarmMode::None; m.mission.solo_slot = -1;
    cast_calls = 0; dispatch = current_solo_dispatch(w, 0);
    require(dispatch && !dispatch->known && cast_calls == 0,
            "unknown current controller requires ordinary full repricing");
    m.mission.solo_mode = SoloFarmMode::DirectCastOnly;
    require(current_solo_mode(m.mission,0) == SoloFarmMode::None,
            "missing stored direct slot is not an accepted controller");
    m.mission.solo_slot = 0; m.mission.phase = Phase::Travel;
    require(current_solo_mode(m.mission,0) == SoloFarmMode::None,
            "travel intention is not current-only readiness");
    m.mission.phase = Phase::Clear;
    require(current_solo_mode(m.mission,1) == SoloFarmMode::None,
            "another group's controller cannot be inherited");
    combined.current_only = true;
    require(!solo_farm_proposal(w,m,combined),
            "current-only Combined proof cannot replace a committed Direct controller");
    combined.current_only = false; p = solo_farm_proposal(w,m,combined);
    require(p && p->mission.solo_mode == SoloFarmMode::Combined && p->mission.solo_slot == -1,
            "a newly fully paid Combined quote explicitly reselects the controller");
    auto manual = manual_basic(w);
    require(manual.mode == SoloFarmMode::Combined && manual.current_followup == Kind::None &&
            manual.current_slot == -1, "manual BasicOnly quote defaults retain no optional cast obligation");
    p = solo_farm_proposal(w,m,manual);
    require(p && p->action.kind == Kind::BasicCamp && p->mission.solo_mode == SoloFarmMode::Combined &&
            p->solo_current_followup == Kind::None,
            "manual BasicOnly is not downgraded to Direct by ready kit metadata");
    auto future = manual_basic(w); future.stage = {4,3}; future.ready_now = false;
    future.route[0] = w.self.pos; future.route[1] = future.stage; future.route_length = 2;
    w.self.can_move = true;
    p = solo_farm_proposal(w,m,future);
    require(p && p->action.kind == Kind::Move && p->mission.phase == Phase::Travel &&
            p->mission.solo_mode == SoloFarmMode::Combined && p->mission.solo_slot == -1,
            "future Combined route retains mode without minting a present hit");
    future.mode = SoloFarmMode::DirectCastOnly; future.slot = 0;
    p = solo_farm_proposal(w,m,future);
    require(p && p->action.kind == Kind::Move && p->mission.solo_mode == SoloFarmMode::DirectCastOnly &&
            p->mission.solo_slot == 0, "future Direct route retains its selected controller slot");
    m.mission.solo_mode = SoloFarmMode::DirectCastOnly; m.mission.solo_slot = 0;
    auto stale_direct = *current_solo_dispatch(w,0); stale_direct.slot = 1;
    require(!solo_farm_proposal(w,m,stale_direct),
            "current-only Direct proof cannot substitute another selected slot");
    m.mission.solo_mode = SoloFarmMode::None; m.mission.solo_slot = -1;
    manual.current_only = true;
    require(!solo_farm_proposal(w,m,manual),
            "legacy unstamped Clear requires a fresh complete quote instead of current-only promotion");
    manual.current_only = false; manual.mode = SoloFarmMode::None;
    require(!solo_farm_proposal(w,m,manual), "invalid quote mode does not default to Combined execution");
    m.mission.solo_mode = static_cast<SoloFarmMode>(99);
    require(current_solo_mode(m.mission,0) == SoloFarmMode::None,
            "unrecognized controller metadata remains unknown");
    LocalAssignment assignment; assignment.ready = assignment.self_selected = assignment.locally_accepted = true;
    assignment.selected_ids = {6}; assignment.rollout.proof = ClearProofKind::BasicOnly;
    Mission crew; crew.group = 0; crew.solo_mode = SoloFarmMode::DirectCastOnly; crew.solo_slot = 0;
    require(name_current_crew(crew,assignment,6) && crew.solo_mode == SoloFarmMode::None && crew.solo_slot == -1,
            "actual crew controller clears stale solo mode and slot");
    assignment.ready = false; crew.solo_mode = SoloFarmMode::DirectCastOnly; crew.solo_slot = 0;
    require(!name_current_crew(crew,assignment,6) && crew.solo_mode == SoloFarmMode::DirectCastOnly &&
            crew.solo_slot == 0, "failed crew proof cannot erase a retained solo controller");
    std::printf("%d committed solo mode checks passed\n", checks);
}
