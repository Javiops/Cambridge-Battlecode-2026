#include "camp_collateral.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
static int checks = 0;
static void check(bool value, const char *why) {
    ++checks;
    if (!value) { std::fprintf(stderr, "FAIL %s\n", why); std::exit(1); }
}
int main() {
    Actor actor;
    actor.type = 0;
    std::vector<Camp> selected(1);
    selected[0].id = 10;
    selected[0].pos = {10, 10};
    selected[0].hp = 500;
    std::vector<Group> groups(2);
    groups[0].spawns.push_back({10, 2, {10, 10}, 500, 0, 3});
    groups[1].spawns.push_back({11, 0, {11, 10}, 1350, 20, 3});
    const auto collateral = [&] { return external_camp_collateral(actor, selected, groups, 0); };
    check(!collateral(), "ordinary single-target damage does not wake an adjacent group");
    actor.type = 10;
    check(collateral(), "Varg adjacent splash must price another group's monster");
    groups[1].spawns[0].pos = {12, 10};
    check(!collateral(), "Varg one-tile splash does not reach a two-tile neighbor");
    actor.type = 0;
    auto &area = actor.spells[0];
    area.kind = 3; area.amount = 100; area.ground = true; area.radius = 2;
    check(collateral(), "ground-only area can wake a different group");
    area.ready = false; area.cooldown = 8;
    check(collateral(), "a long clear cannot treat a cooling area as permanently absent");
    groups[1].spawns[0].pos = {13, 10};
    check(!collateral(), "neighbor beyond the real area radius is not collateral");
    groups[1].spawns[0].pos = {11, 10};
    area.kind = 2;
    check(!collateral(), "single-target spell metadata does not acquire an area radius");
    area.kind = 3;
    selected[0].hp = 0;
    check(!collateral(), "dead selected monster cannot be a planned area center");
    selected[0].hp = 500;
    groups.resize(1);
    check(!collateral(), "members in the selected group are already in its clear forecast");
    groups.resize(2);
    groups[1].spawns.push_back({11, 0, {22, 22}, 1350, 20, 3});
    std::vector<GroupView> views(2);
    Camp moved; moved.id = 11; moved.pos = {11, 10}; moved.hp = 1300;
    views[1].camps.push_back(moved); views[1].seen = 8;
    check(external_camp_collateral(actor, selected, groups, 0, views, 8),
          "fresh wandering neighbor is checked beyond its public original spawn");
    check(!external_camp_collateral(actor, selected, groups, 0, views, 9),
          "old precise position is not a current exact collision certificate");
    views[1].camps[0].hp = 0;
    check(!external_camp_collateral(actor, selected, groups, 0, views, 8),
          "fresh dead wandering monster contributes no observed collateral");
    groups[1].spawns[0].pos = {11, 10}; views[1].state = Lifecycle::Reward;
    check(external_camp_collateral(actor, selected, groups, 0, views, 8),
          "possible public respawn is not waived by a currently empty region");

    Actor enemy; enemy.range = 1; enemy.move_speed = 2;
    check(camp_enemy_contact(enemy, 3) == 7, "three movement rounds plus actual basic range");
    enemy.spells[0].kind = 3; enemy.spells[0].range = 4;
    enemy.spells[0].radius = 2; enemy.spells[0].cooldown = 2;
    check(camp_enemy_contact(enemy, 3) == 12, "known timely area extends possible contact");
    enemy.spells[0].cooldown = 4;
    check(camp_enemy_contact(enemy, 3) == 7, "known cooldown beyond finish cannot supply that cast");
    enemy.spells[0].kind = 6; enemy.spells[0].range = 3;
    enemy.spells[0].cooldown = 2; enemy.spells[0].recharge = 8;
    check(camp_enemy_contact(enemy, 3) == 10, "one timely dash has its own observed range");
    enemy.spells[0].ready = true; enemy.spells[0].cooldown = 0;
    enemy.spells[0].recharge = 2;
    check(camp_enemy_contact(enemy, 4) >= 18, "repeated known dash casts cannot be reduced to one dash");
    enemy.spells[0].recharge = 10;
    enemy.spells[1] = enemy.spells[0]; enemy.spells[1].range = 2;
    check(camp_enemy_contact(enemy, 4) >= 14,
          "two distinct dashes on separate turns cannot be bounded by only the larger skill");
    enemy.spells[1] = {}; enemy.spells[0].recharge = -1;
    check(camp_enemy_contact(enemy, 4) >= 21,
          "unknown recharge cannot imply a safer one-dash clear window");
    enemy.spells = {};
    check(camp_enemy_contact(enemy, -3) == 1, "negative horizon is clamped before arithmetic");
    std::printf("%d camp collateral checks passed\n", checks);
}
