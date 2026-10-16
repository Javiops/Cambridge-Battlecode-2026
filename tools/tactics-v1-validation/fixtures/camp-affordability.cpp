#include "squads.h"
#include <cstdlib>
#include <iostream>

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
  std::cout << checks << " camp affordability checks passed\n";
}
