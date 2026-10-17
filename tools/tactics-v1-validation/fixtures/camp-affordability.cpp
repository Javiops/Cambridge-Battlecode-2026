#include "squads.h"
#include <cstdlib>
#include <iostream>
#include <cstdint>

// Exact pre-repair exhaustive implementation; comparison oracle only.
namespace tactics {
inline ReadySquad legacy_ready_camp_squad(std::vector<CampContributor> candidates, int self_id,
                                           double camp_hp,
                                           const std::vector<CampPressure> &monsters) {
    ReadySquad result;
    if (self_id < 0 || !std::isfinite(camp_hp) || camp_hp < 0)
        return result;
    candidates.erase(std::remove_if(candidates.begin(), candidates.end(),
                                    [](const auto &c) {
                                        const auto &b = c.contribution;
                                        return b.id < 0 || !b.ready || !std::isfinite(b.dps) ||
                                               b.dps <= 0 || !std::isfinite(b.opportunity_cost) ||
                                               b.opportunity_cost < 0 || !std::isfinite(c.hp) ||
                                               c.hp <= 0 || !std::isfinite(c.mitigation) ||
                                               c.mitigation <= 0 || !std::isfinite(c.enemy_reply) ||
                                               c.enemy_reply < 0;
                                    }),
                     candidates.end());
    std::sort(candidates.begin(), candidates.end(),
              [](const auto &a, const auto &b) { return a.contribution.id < b.contribution.id; });
    if (candidates.empty() || candidates.size() > 6)
        return result;
    int self_index = -1;
    for (unsigned i = 0; i < candidates.size(); ++i) {
        if (i && candidates[i - 1].contribution.id == candidates[i].contribution.id)
            return result;
        if (candidates[i].contribution.id == self_id)
            self_index = i;
    }
    if (self_index < 0)
        return result;
    for (const auto &m : monsters)
        if (!std::isfinite(m.strength) || m.strength < 0 || m.range < 0)
            return result;
    for (unsigned mask = 1; mask < (1u << candidates.size()); ++mask) {
        if (!(mask & (1u << self_index)))
            continue;
        ReadySquad current;
        double cost_per_tick = 0;
        for (unsigned i = 0; i < candidates.size(); ++i)
            if (mask & (1u << i)) {
                current.ids.push_back(candidates[i].contribution.id);
                current.dps += candidates[i].contribution.dps;
                cost_per_tick += candidates[i].contribution.opportunity_cost;
            }
        current.clear_ticks = camp_hp == 0 ? 0 : std::ceil(camp_hp / current.dps);
        std::array<double, 6> pressure{};
        for (const auto &monster : monsters) {
            if (!monster.observed) {
                // A hidden member is not certified out of range or shielded by
                // a helper. Preserve the pessimistic self exposure instead.
                pressure[self_index] += monster.strength;
                continue;
            }
            int nearest = std::numeric_limits<int>::max();
            for (unsigned i = 0; i < candidates.size(); ++i)
                if (mask & (1u << i))
                    nearest = std::min(nearest, std::max(std::abs(candidates[i].x - monster.x),
                                                         std::abs(candidates[i].y - monster.y)));
            if (nearest > monster.range)
                continue; // Native camps do not chase or gain range with time.
            for (unsigned i = 0; i < candidates.size(); ++i)
                if ((mask & (1u << i)) &&
                    std::max(std::abs(candidates[i].x - monster.x),
                             std::abs(candidates[i].y - monster.y)) == nearest)
                    pressure[i] += monster.strength; // Full charge for every tie.
        }
        bool safe = true;
        for (unsigned i = 0; i < candidates.size(); ++i)
            if (mask & (1u << i)) {
                const auto &body = candidates[i];
                // Full group clear duration is deliberately conservative: no
                // speculative early monster death, heal, or future tank swap.
                const double damage = current.clear_ticks * pressure[i] * body.mitigation;
                safe &= damage + body.enemy_reply + 1 < body.hp * .75;
            }
        if (!safe)
            continue;
        current.ready = true;
        current.person_turn_cost = current.clear_ticks * cost_per_tick;
        const bool smaller = !result.ready || current.ids.size() < result.ids.size();
        const bool same = result.ready && current.ids.size() == result.ids.size();
        const bool cheaper = same && current.person_turn_cost < result.person_turn_cost - 1e-9;
        const bool tied =
            same && std::abs(current.person_turn_cost - result.person_turn_cost) <= 1e-9;
        if (smaller || cheaper || (tied && current.ids < result.ids))
            result = std::move(current);
    }
    return result;
}
}


static int checks = 0;
static void check(bool value) {
  ++checks;
  if (!value) {
    std::cerr << "camp affordability check " << checks << " failed\n";
    std::exit(1);
  }
}
int main() {
  using namespace tactics;
  const CampPressure elk{0, 0, 3, 30, true};
  CampContributor self{{1, 10, 1, true}, 4, 0, 200, 1, 0};
  auto ranged = minimum_ready_camp_squad({self}, 1, 100, {elk});
  check(ranged.ready && ranged.ids == std::vector<int>{1});
  self.x = 2;
  check(!minimum_ready_camp_squad({self}, 1, 100, {elk}).ready);
  CampContributor tank{{2, 10, 1, true}, 1, 0, 1000, 1, 0};
  auto pair = minimum_ready_camp_squad({self, tank}, 1, 100, {elk});
  check(pair.ready && pair.ids == std::vector<int>({1, 2}) &&
        pair.clear_ticks == 5);
  tank.hp = 100;
  check(!minimum_ready_camp_squad({self, tank}, 1, 100, {elk}).ready);
  tank.hp = 200;
  self.x = 1;
  tank.x = -1;
  check(!minimum_ready_camp_squad({self, tank}, 1, 200, {elk}).ready);
  self.x = 4;
  tank.x = 1;
  tank.hp = 1000;
  auto hidden = elk;
  hidden.observed = false;
  check(!minimum_ready_camp_squad({self, tank}, 1, 100, {hidden}).ready);
  self.x = 2;
  self.contribution.dps = 100;
  tank.contribution.dps = 1;
  tank.hp = 5000;
  CampContributor ranged_helper{{3, 200, 1, true}, 4, 0, 1000, 1, 0};
  auto stronger_elk = elk;
  stronger_elk.strength = 60;
  auto retained = minimum_ready_camp_squad({self, tank, ranged_helper}, 1, 1000,
                                           {stronger_elk});
  check(retained.ready && retained.ids == std::vector<int>({1, 2}));
  tank.contribution.ready = false;
  check(!minimum_ready_camp_squad({self, tank, ranged_helper}, 1, 1000,
                                  {stronger_elk})
             .ready);
  self.x = 4;
  self.enemy_reply = 160;
  check(!minimum_ready_camp_squad({self}, 1, 100, {elk}).ready);
  self.enemy_reply = 0;
  auto duplicate = self;
  check(!minimum_ready_camp_squad({self, duplicate}, 1, 100, {elk}).ready);
  self.x = 2;
  self.mitigation = .1;
  check(minimum_ready_camp_squad({self}, 1, 1000, {elk}).ready);

  // Actual Ryth0/Corners/R12 input from the retained native23 pause.
  const std::vector<CampContributor> native_crew{
    {{0,12.5,1,true},8,38,1200,1,0},{{1,60,1,true},11,38,750,1,0},
    {{2,50,1,true},12,38,700,1,0},{{3,15.625,1,true},8,39,880,1,0},
    {{4,62.5,1,true},10,38,750,1,0}};
  const std::vector<CampPressure> native_monsters{{10,41,3,20,true}};
  const auto native_old=legacy_ready_camp_squad(native_crew,0,1295,native_monsters);
  const auto native_new=minimum_ready_camp_squad(native_crew,0,1295,native_monsters);
  check(native_old.ids==std::vector<int>({0,1}) && native_old.ready && native_old.dps==72.5 &&
        native_old.clear_ticks==18 && native_old.person_turn_cost==36);
  check(native_new.ids==native_old.ids && native_new.ready==native_old.ready &&
        native_new.dps==native_old.dps && native_new.clear_ticks==native_old.clear_ticks &&
        native_new.person_turn_cost==native_old.person_turn_cost);
  std::uint32_t seed = 0x421fc23u;
  auto random = [&] { seed ^= seed << 13; seed ^= seed >> 17; seed ^= seed << 5; return seed; };
  for (int trial = 0; trial < 5000; ++trial) {
    const int count = 1 + random() % 7;
    std::vector<CampContributor> crew;
    for (int i = 0; i < count; ++i) {
      CampContributor c{{i * 3 + 1, double(1 + random() % 150), double(random() % 5), true},
                         int(random() % 15)-7, int(random() % 15)-7,
                         double(1 + random() % 3500), .25 * (1 + random() % 4), double(random() % 100)};
      if (random() % 17 == 0) c.contribution.ready = false;
      if (random() % 41 == 0) c.contribution.dps = 0;
      if (random() % 67 == 0) c.hp = 0;
      crew.push_back(c);
    }
    const int self_id = crew[random() % crew.size()].contribution.id;
    if (trial % 53 == 0 && crew.size() > 1) crew.back().contribution.id = crew.front().contribution.id;
    for (unsigned i = 0; i < crew.size(); ++i) std::swap(crew[i],crew[random() % crew.size()]);
    std::vector<CampPressure> pressure;
    for (unsigned i = 0, n = random() % 12; i < n; ++i)
      pressure.push_back({int(random()%15)-7,int(random()%15)-7,int(random()%6),double(random()%100),bool(random()%4)});
    const double hp = trial % 31 == 0 ? 0 : random() % 6000;
    const auto expected = legacy_ready_camp_squad(crew, self_id, hp, pressure);
    const auto actual = minimum_ready_camp_squad(crew, self_id, hp, pressure);
    const auto uninterrupted = []<class T>(const T &value) {
      if constexpr (requires { value.interrupted; }) return !value.interrupted;
      else return true;
    };
    check(uninterrupted(actual) && actual.ready == expected.ready && actual.ids == expected.ids &&
          actual.dps == expected.dps && actual.clear_ticks == expected.clear_ticks &&
          actual.person_turn_cost == expected.person_turn_cost);
  }
  std::vector<CampContributor> funded_crew;
  for (int i = 0; i < 6; ++i) funded_crew.push_back({{i,100.,1.,true},i,0,10000.,1.,0.});
  // Every smaller subset fails the same self-tank reserve; the last six-body
  // subset is feasible. Interrupt every point of a full exhaustive pass too.
  funded_crew[0].hp=300;
  const std::vector<CampPressure> funded_monsters{{0,0,3,34.,true},{0,0,3,34.,true},{0,0,3,34.,false}};
  [&]<class Crew, class Monsters>(const Crew &crew, const Monsters &monsters) {
    if constexpr (requires { minimum_ready_camp_squad(crew,0,1100.,monsters,[] { return true; }); }) {
  int full_calls = 0;
  const auto full = minimum_ready_camp_squad(crew,0,1100.,monsters,[&]{++full_calls;return true;});
  check(full.ready && !full.interrupted);
  for (int cutoff = 0; cutoff < full_calls; ++cutoff) {
    int calls = 0;
    const auto interrupted = minimum_ready_camp_squad(crew,0,1100.,monsters,[&]{return calls++ < cutoff;});
    check(interrupted.interrupted && !interrupted.ready && interrupted.ids.empty() &&
          interrupted.dps == 0 && interrupted.clear_ticks == 0 && interrupted.person_turn_cost == 0);
  }
    }
  }(funded_crew,funded_monsters);
  std::cout << checks << " camp affordability checks passed\n";
}
