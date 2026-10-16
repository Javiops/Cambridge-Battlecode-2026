#define TACTICS_COMBAT_MODEL_ONLY
#include "combat.h"
#include <cstdlib>
#include <iostream>
using namespace tactics;
using namespace tactics::combat_detail;
static int checks = 0;
static void check(bool value, const char *why) {
  ++checks;
  if (!value) {
    std::cerr << "combat sequence check " << checks << ": " << why << '\n';
    std::exit(1);
  }
}
static bool near(double a, double b) { return std::abs(a - b) < .0001; }
static Actor actor(int id, Pos pos) {
  Actor a;
  a.id = id;
  a.alive = true;
  a.hp = a.max_hp = 1000;
  a.pos = pos;
  a.strength = 50;
  a.range = 3;
  a.can_attack = a.can_cast = a.can_move = true;
  return a;
}
static Spell spell(int kind, int slot, double amount = 0) {
  Spell s;
  s.kind = kind;
  s.slot = slot;
  s.amount = amount;
  s.range = 4;
  s.ready = true;
  s.cooldown = 0;
  s.recharge = 8;
  s.enemies = kind != 1;
  s.self = kind == 1;
  return s;
}
int main() {
  auto own = actor(1, {0, 0}), enemy = actor(2, {2, 0});
  enemy.shield = 25;
  auto single = sequence_exchange(own, enemy, 50);
  check(near(single.hp_damage, 25) && near(single.shield_damage, 25),
        "shield then HP");
  auto twice = sequence_exchange(own, enemy, 50, 50);
  check(near(twice.hp_damage, 75) && near(twice.shield_damage, 25) &&
            twice.hits == 2,
        "shield consumed once across sequence");
  enemy.type = ren_type;
  enemy.focus = 100;
  own.shield = 25;
  check(near(sequence_exchange(own, enemy, 50, 50).returned, 15),
        "attacker shield consumed once across two returns");
  enemy.hp = 10;
  enemy.shield = 0;
  auto lethal = sequence_exchange(own, enemy, 50, 50);
  check(lethal.lethal && lethal.hits == 1 && near(lethal.returned, 0),
        "no hit follows a lethal target");
  enemy = actor(2, {2, 0});
  enemy.shield = 25;
  own.shield = 0;
  own.spells[0] = spell(1, 0);
  own.spells[1] = spell(2, 1, 90);
  auto plans = stationary_sequences(own, enemy);
  check(plans.size() == 3, "basic, reset sequence and damage sequence compete");
  const auto reset = std::find_if(plans.begin(), plans.end(),
                                  [](auto p) { return p.actions == 3; });
  check(reset != plans.end() && reset->exchange.hits == 2 &&
            near(reset->exchange.hp_damage, 75),
        "one reset adds one basic");
  const auto damage = std::find_if(plans.begin(), plans.end(), [](auto p) {
    return p.first.kind == Kind::CastChampion;
  });
  check(damage != plans.end() && damage->exchange.hits == 2 &&
            near(damage->exchange.hp_damage, 115),
        "cast then basic without extra reset");
  own.can_attack = false;
  plans = stationary_sequences(own, enemy);
  check(plans.size() == 2, "spent ordinary basic still permits reset or cast");
  check(std::any_of(plans.begin(), plans.end(),
                    [](auto p) {
                      return p.first.kind == Kind::CastSelf && p.actions == 2 &&
                             p.exchange.hits == 1;
                    }),
        "post-walk ranged reset restores one shot");
  own.can_cast = false;
  check(stationary_sequences(own, enemy).empty(),
        "spent cast and basic leave no invented sequence");
  own.can_attack = true;
  check(stationary_sequences(own, enemy).size() == 1,
        "spent cast retains real basic");
  enemy.stunned = true;
  enemy.stun_ticks = 0;
  check(added_control_windows(enemy, 1) == 1,
        "zero timer expires at next owner start");
  enemy.stun_ticks = 2;
  check(added_control_windows(enemy, 1) == 0 &&
            added_control_windows(enemy, 3) == 1,
        "only actual extra control windows counted");
  enemy.stun_ticks = -1;
  check(added_control_windows(enemy, 3) == 0,
        "unknown control timer does not certify extension");
  enemy.type = marcella_type;
  check(added_control_windows(enemy, 3) == 0,
        "Marcella immunity removes control value");
  auto area = spell(3, 0, 100);
  area.duration = 1;
  own.type = 0;
  check(applies_control(own, area), "Ryth area is a real stun");
  own.type = 5;
  check(!applies_control(own, area),
        "Stellar lasting area is not assumed to stun");
  own = actor(1, {0, 0});
  own.range = 5;
  own.spells[0] = spell(2, 0, 90);
  check(near(cumulative_reply_upper(own, own.pos, {3, 0}, 1), 140),
        "one-opportunity native-compatible volley");
  check(near(cumulative_reply_upper(own, own.pos, {3, 0}, 8), 490),
        "eight-turn spell charged once in eight opportunities");
  own.spells[1] = spell(2, 1, 60);
  check(near(cumulative_reply_upper(own, own.pos, {3, 0}, 1), 140),
        "two slots share one cast now");
  check(near(cumulative_reply_upper(own, own.pos, {3, 0}, 2), 250),
        "two slots can cast on different future opportunities");
  own.spells[0].recharge = 2;
  own.spells[1] = {};
  check(near(cumulative_reply_upper(own, own.pos, {3, 0}, 5), 520),
        "known recharge bounds repeated casts");
  own.spells[0].recharge = -1;
  check(near(cumulative_reply_upper(own, own.pos, {3, 0}, 5), 700),
        "unknown recharge preserves conservative uncertainty");
  own.spells[0].recharge = 8;
  own.spells[0].ready = false;
  own.spells[0].cooldown = 4;
  check(near(cumulative_reply_upper(own, own.pos, {3, 0}, 3), 150),
        "known cooldown outside forecast");
  check(near(cumulative_reply_upper(own, own.pos, {3, 0}, 4), 290),
        "cooldown boundary enters forecast");
  own.stunned = true;
  own.stun_ticks = 1;
  check(near(cumulative_reply_upper(own, own.pos, {3, 0}, 1), 0),
        "actual next-window stun removes reply");
  own.stun_ticks = 0;
  check(near(cumulative_reply_upper(own, own.pos, {3, 0}, 1), 50),
        "zero-timer stun expires before next reply");
  own = actor(1, {0, 0});
  own.range = 1;
  own.spells[0] = spell(6, 0);
  own.spells[0].range = 2;
  check(near(reply_raw(own, {4, 0}, 4), 50),
        "melee walk plus dash plus basic is one legal cast sequence");
  const std::vector<Pos> now{{0, 0}}, next{{1, 0}};
  check(near(region_reply_raw(own, now, next, {4, 0}), 50),
        "region model retains walk-dash reply");
  std::cout << checks << " combat sequence checks passed\n";
}
