#include "types.h"
#include <cstdio>
#include <cstdlib>
#include <map>
#include <stdexcept>
#include <string>
#include <variant>
using namespace tactics;

namespace recorded {
inline int epoch = 100, polls = 0, flip_poll = -1;
inline bool *restricted = nullptr;
inline bool alive = true, awake = true, hidden = false;
inline int lifecycle = 0;
inline std::string advance_on, throw_on;
inline std::vector<std::string> calls;
inline Actor actual;
struct CampSnapshot { int x = 6, y = 5; double health = 120, max_health = 500, strength = 20; };
inline CampSnapshot target;
inline void call(const char *name) {
    if (!restricted || !*restricted)
        throw std::runtime_error("host read before restricted scope");
    calls.push_back(name);
    if (throw_on == name)
        throw std::runtime_error("recorded host error");
    if (advance_on == name)
        ++epoch;
}
inline void reset() {
    epoch = 100; polls = 0; flip_poll = -1; restricted = nullptr;
    alive = awake = true; hidden = false; lifecycle = 0;
    advance_on.clear(); throw_on.clear(); calls.clear(); target = {};
    actual = {};
    actual.id = 7; actual.alive = true; actual.type = 3; actual.pos = {5, 5};
    actual.hp = 600; actual.max_hp = 700; actual.strength = 30; actual.focus = 70;
    actual.range = 3; actual.can_cast = true; actual.can_attack = false;
    actual.can_move = false; actual.shield = 25; actual.shield_ticks = 3;
    actual.spells[0].slot = 0; actual.spells[0].kind = 2; actual.spells[0].amount = 140;
    actual.spells[0].range = 4; actual.spells[0].cooldown = 0;
    actual.spells[0].ready = true; actual.spells[0].exclusive = true;
    actual.spells[1].slot = 1; actual.spells[1].cooldown = 5;
}
inline bool called(const char *name) {
    return std::find(calls.begin(), calls.end(), name) != calls.end();
}
}
namespace bc {
inline int round_number() {
    if (!recorded::restricted || !*recorded::restricted)
        throw std::runtime_error("epoch query before restricted scope");
    if (++recorded::polls == recorded::flip_poll)
        ++recorded::epoch;
    return recorded::epoch;
}
namespace map {
struct camp_group_alive {};
struct camp_group_reward_available {};
struct camp_group_respawning {};
using state = std::variant<camp_group_alive, camp_group_reward_available, camp_group_respawning>;
}
}
namespace tactics {
struct RecordedFlags {
    bool is_alive() const { return recorded::alive; }
    bool is_awake() const { return recorded::awake; }
};
struct RecordedCamp {
    RecordedFlags state() const { recorded::call("camp-flags"); return {}; }
    Pos position() const { recorded::call("camp-position"); return {recorded::target.x, recorded::target.y}; }
};
struct RecordedGroup {
    bc::map::state state() const {
        recorded::call("group-state");
        if (recorded::lifecycle == 1) return bc::map::camp_group_reward_available{};
        if (recorded::lifecycle == 2) return bc::map::camp_group_respawning{};
        return bc::map::camp_group_alive{};
    }
};
struct RecordedSelf {
    Pos position() const { recorded::call("self-position"); return recorded::actual.pos; }
    int attack_range() const { recorded::call("self-range"); return recorded::actual.range; }
};
inline Actor read_actor(const RecordedSelf &) { recorded::call("self-record"); return recorded::actual; }
inline Pos position(Pos at) { return at; }
namespace sdk_222 {
inline std::optional<recorded::CampSnapshot> visible_camp(const RecordedCamp &) {
    recorded::call("camp-record");
    return recorded::hidden ? std::nullopt : std::optional(recorded::target);
}
}
struct World {
    bool restricted_continuation_snapshot = false;
    int restricted_continuation_camp = -1;
    Pos restricted_continuation_at{99, 99};
    struct Spawn { int id = 10; };
    struct Group { std::vector<Spawn> spawns{{}}; };
    struct Geometry { std::vector<Group> groups{{}, {}}; std::vector<RecordedGroup> handles{{}, {}}; } geo;
    struct Metadata { RecordedCamp handle; int group = 0, range = 3; };
    std::map<int, Metadata> camp_metadata{{10, {}}};
    int round = 100, serial = 8, self_type = 3, gold = 17, own_score = 32, enemy_score = 64;
    RecordedSelf me;
    Actor self;
    std::array<Spell, 2> spells;
    Memory memory;
    std::vector<Actor> allies, enemies;
    std::vector<GroupView> groups;
    World() {
        self = recorded::actual; self.hp = 700; self.can_attack = true; self.can_move = true;
        self.shield = 40; self.shield_ticks = 4; spells = self.spells;
        GroupView target; target.state = Lifecycle::Alive; target.seen = 100;
        Camp camp; camp.id = 10; camp.group = 0; camp.pos = {6,5};
        camp.hp = 150; camp.max_hp = 500; camp.strength = 20; camp.range = 3;
        target.camps.push_back(camp); groups.push_back(target);
        target.camps.front().id = 11; target.camps.front().hp = 777;
        groups.push_back(target);
        auto remote = self; remote.id = 8; remote.hp = 333;
        allies = {self, remote}; enemies = {remote};
    }
    std::optional<RecordedCamp> camp(int id) const {
        recorded::call("bound-camp-handle");
        const auto found = camp_metadata.find(id);
        return found == camp_metadata.end() ? std::nullopt : std::optional(found->second.handle);
    }
    void refresh(bool = false) { recorded::call("FORBIDDEN-full-refresh"); }
    // EXACT_RECEIPT_REFRESH
};
struct Execution { Outcome outcome = Outcome::Rejected; };
// EXACT_ANY_BASIC_TARGET
inline Execution restricted_gateway_probe(World &w, const Action &a) {
    Execution result;
    // EXACT_RESTRICTED_GATEWAY
    return result;
}
}
static int checks = 0;
static void require(bool ok, const char *why) {
    ++checks;
    if (!ok) { std::printf("FAIL%d %s\n", checks, why); std::exit(1); }
}
static void watch(World &world) { recorded::restricted = &world.restricted_continuation_snapshot; }
static bool refresh(World &world) { watch(world); return world.refresh_receipt_target(0, 10, 100, 8); }
int main() {
    recorded::reset(); World base; int successful_polls = 0;
    { auto w = base;
      require(refresh(w), "exact current singleton refresh succeeds");
      require(w.restricted_continuation_snapshot && w.restricted_continuation_camp == 10 &&
              w.restricted_continuation_at == Pos{6,5}, "restricted scope and exact target geometry installed");
      require(w.serial == 9 && w.round == 100, "one successful receipt refresh advances serial once");
      require(w.self.hp == 600 && w.self.shield == 25 && w.self.shield_ticks == 3,
              "actual HP/shield/duration replace pre-basic records");
      require(!w.self.can_attack && !w.self.can_move && w.self.can_cast,
              "actual post-basic allowances are observed rather than restored");
      require(w.spells[0].ready && w.spells[1].cooldown == 5, "actual slot readiness/cooldown carried");
      require(w.groups[0].camps.front().hp == 120 && w.groups[0].camps.front().awake,
              "target actual remaining HP/awake state carried");
      require(w.allies[0].hp == 600 && w.allies[1].hp == 333 && w.enemies[0].hp == 333 &&
              w.groups[1].camps.front().hp == 777, "remote records deliberately remain unrefreshed");
      require(w.gold == 17 && w.own_score == 32 && w.enemy_score == 64,
              "unread wallets/scores are not falsely recomputed");
      require(recorded::calls == std::vector<std::string>{"self-record","camp-record","camp-flags","group-state"},
              "only self plus selected target/lifecycle host records are read");
      successful_polls = recorded::polls;
    }
    { recorded::reset(); auto w = base; w.memory.moved_round = 100;
      require(refresh(w) && !w.spells[0].ready, "actual movement exclusion remains enforced"); }
    { recorded::reset(); auto w = base; recorded::actual.can_attack = true;
      recorded::actual.spells[0].cooldown = 8; recorded::actual.spells[0].ready = false;
      require(refresh(w) && w.self.can_attack && !w.spells[0].ready && w.spells[0].cooldown == 8,
              "reset-restored attack and consumed cast are read from host"); }
    for (int adverse = 0; adverse < 10; ++adverse) {
        recorded::reset(); auto w = base; watch(w);
        int group = 0, target = 10, epoch = 100, serial = 8;
        switch (adverse) {
          case 0: epoch = 99; break; case 1: serial = 7; break; case 2: group = -1; break;
          case 3: target = 11; break; case 4: w.geo.groups[0].spawns.push_back({11}); break;
          case 5: w.groups[0].seen = 99; break; case 6: w.groups[0].state = Lifecycle::Reward; break;
          case 7: w.groups[0].camps.push_back(w.groups[0].camps.front()); break;
          case 8: w.camp_metadata.clear(); break; case 9: w.camp_metadata[10].group = 1; break;
        }
        require(!w.refresh_receipt_target(group,target,epoch,serial) && recorded::calls.empty() &&
                w.serial == 8 && w.restricted_continuation_snapshot && w.restricted_continuation_at == Pos{},
                "invalid/stale/partial input stays restricted without host unit reads");
    }
    for (int adverse = 0; adverse < 3; ++adverse) {
        recorded::reset(); auto w = base;
        if (adverse == 0) recorded::actual.alive = false;
        if (adverse == 1) recorded::actual.id = 9;
        if (adverse == 2) recorded::actual.pos = {4,5};
        require(!refresh(w) && w.serial == 8 && !recorded::called("camp-record"),
                "dead/wrong-owner/moved self stops before target access");
    }
    for (int adverse = 0; adverse < 5; ++adverse) {
        recorded::reset(); auto w = base;
        if (adverse == 0) recorded::hidden = true;
        if (adverse == 1) recorded::target.health = 0;
        if (adverse == 2) recorded::alive = false;
        if (adverse == 3) recorded::lifecycle = 1;
        if (adverse == 4) recorded::lifecycle = 2;
        require(!refresh(w) && w.serial == 8 && w.self.hp == 700 &&
                !recorded::called("FORBIDDEN-full-refresh"),
                "hidden/dead/reward/respawn target ends continuation without fallback or fake payout");
    }
    for (const auto *stage : {"self-record","camp-record","camp-flags","group-state"}) {
        recorded::reset(); auto w = base; recorded::advance_on = stage;
        require(!refresh(w) && w.restricted_continuation_snapshot,
                "epoch transition at each host read refuses continuation");
        if (std::string(stage) == "camp-flags")
            require(!recorded::called("group-state"), "epoch is checked before next group API read");
    }
    { recorded::reset(); auto w = base; recorded::flip_poll = successful_polls;
      require(!refresh(w) && w.restricted_continuation_snapshot && recorded::epoch != w.round,
              "epoch change at final commit check stays restricted and returns failure"); }
    { recorded::reset(); auto w = base; recorded::throw_on = "camp-record"; bool threw = false;
      try { (void)refresh(w); } catch (const std::runtime_error &) { threw = true; }
      require(threw && w.restricted_continuation_snapshot && w.serial == 8 &&
              !recorded::called("FORBIDDEN-full-refresh"), "host errors retain restricted fail-closed scope"); }
    { recorded::reset(); auto w = base; require(refresh(w), "restricted gateway setup");
      for (Kind kind : {Kind::BasicCamp,Kind::CastCamp,Kind::CastSelf}) {
          Action action; action.kind = kind; action.target = 10;
          require(restricted_gateway_probe(w,action).outcome != Outcome::Stale,
                  "bound current prepaid camp/reset action passes restricted-kind boundary");
          action.target = 11;
          require(restricted_gateway_probe(w,action).outcome == Outcome::Stale,
                  "other target cannot consume restricted snapshot");
      }
      for (Kind kind : {Kind::Move,Kind::Ward,Kind::Recall,Kind::Tribute,Kind::Buy,Kind::BasicChampion}) {
          Action action; action.kind = kind; action.target = 10;
          require(restricted_gateway_probe(w,action).outcome == Outcome::Stale,
                  "no planning/shopping/movement/other actor action in restricted scope");
      }
      Action ground; ground.kind = Kind::CastGround; ground.target = 10; ground.slot = 0;
      ground.at = {6,5}; w.spells[0].kind = 3; w.spells[0].ground = true;
      w.spells[0].camps = false; w.spells[0].amount = 100;
      require(restricted_gateway_probe(w,ground).outcome != Outcome::Stale,
              "real ground-only camp AoE mask is not converted to an invalid CastCamp");
      ground.at = {5,5};
      require(restricted_gateway_probe(w,ground).outcome == Outcome::Stale,
              "ground cast cannot substitute a different stale center");
      ground.at = {6,5}; w.spells[0].kind = 6;
      require(restricted_gateway_probe(w,ground).outcome == Outcome::Stale,
              "dash cannot use restricted stationary target snapshot");
      w.spells[0].kind = 3; w.spells[0].amount = 0;
      require(restricted_gateway_probe(w,ground).outcome == Outcome::Stale,
              "ground cast needs actual positive damage metadata");
      w.spells[0].amount = std::numeric_limits<double>::infinity();
      require(restricted_gateway_probe(w,ground).outcome == Outcome::Stale,
              "nonfinite ground damage is not an admitted stationary continuation");
      recorded::calls.clear();
      require(any_basic_target(w), "reset utility checks actual bound target");
      require(recorded::calls == std::vector<std::string>{"bound-camp-handle","self-position","camp-position","self-range"},
              "reset utility never scans stale remote actor/group records");
      recorded::target.x = 15;
      require(!any_basic_target(w), "stale other in-range units cannot rescue out-of-range bound target");
    }
    std::printf("%d restricted receipt snapshot checks passed\n", checks);
}
