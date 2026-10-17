#include "types.h"
#include "resource.h"
#include <cstdlib>
#include <iostream>
#include <map>
namespace tactics {
struct Geometry {
    std::vector<Group> groups;
    std::vector<Pos> altars{{31, 31}};
    std::vector<int> nearest_altar = std::vector<int>(1024, 5);
    std::vector<std::vector<int>> altar_fields{nearest_altar};
    bool monolith_only = false;
    int at(const std::vector<int> &field, Pos p) const {
        return p.x >= 0 && p.y >= 0 && p.x < 32 && p.y < 32 ? field[p.y * 32 + p.x]
                                                                        : unreachable;
    }
};
struct World {
    Geometry geo;
    std::vector<GroupView> groups;
    std::vector<Actor> enemies;
    struct Sighting { Actor actor; int round; };
    std::vector<Sighting> sightings;
    std::map<int, int> routes;
    int round = 1;
    bool on_group(int gi, Pos p) const {
        for (const auto &spawn : geo.groups[gi].spawns)
            if (spawn.pos == p) return true;
        return false;
    }
};
namespace combat_detail {
inline double long_window_reply_upper(const Actor &e, Pos, Pos, int) { return e.strength; }
inline bool recent_sighting(int age) { return age >= 0 && age <= 3; }
inline double coarse_remembered_reply(const Actor &e, int, Pos, int) { return e.strength; }
}
namespace coordination_detail {
inline int cached_distance(const World &w, Pos, Pos target) {
    const auto route = w.routes.find(target.y * 32 + target.x);
    return route == w.routes.end() ? -1 : route->second;
}
// EXACT_ALTERNATIVE
}
}
using namespace tactics;
static int checks = 0;
static void check(bool ok, const char *why) {
    ++checks;
    if (!ok) { std::cerr << "FAIL alternative " << checks << ' ' << why << '\n'; std::exit(1); }
}
static int add(World &w, double hp, double strength, int gems = 22, bool complete = true,
               int route = 3, int bank = 5) {
    const int gi = int(w.groups.size());
    Group group; group.gems = gems;
    Spawn spawn; spawn.id = gi; spawn.pos = {gi % 30, gi / 30};
    spawn.hp = hp; spawn.strength = strength; group.spawns.push_back(spawn);
    w.geo.groups.push_back(group);
    GroupView view; view.state = Lifecycle::Alive; view.seen = 1;
    Camp camp; camp.id = gi; camp.pos = spawn.pos; camp.hp = hp; camp.strength = strength;
    if (complete) view.camps.push_back(camp);
    w.groups.push_back(view);
    if (route >= 0) w.routes[spawn.pos.y * 32 + spawn.pos.x] = route;
    w.geo.nearest_altar[spawn.pos.y * 32 + spawn.pos.x] = bank;
    return gi;
}
struct Result { bool known = false, bank = false; int group = -1; Pos target{}; double rate = 0; };
static Result run(const World &w, const Actor &a, int excluded = -1) {
    Result out;
    out.rate = coordination_detail::alternative(w, a, excluded, out.known, out.group,
                                                out.target, out.bank);
    return out;
}
int main() {
    Actor a; a.id = 3; a.alive = true; a.pos = {20, 20}; a.hp = a.max_hp = 900;
    a.strength = 40; a.move_speed = 1; a.mitigation = a.camp_mitigation = 1;
    World w;
    add(w, 4800, 120); add(w, 2400, 60); const int gem = add(w, 200, 0);
    auto result = run(w, a);
    check(result.known && result.group == gem && result.rate > 0,
          "two unaffordable cached rows cannot consume two useful slots");
    w.groups[0].camps.clear(); w.groups[1].camps.clear();
    result = run(w, a);
    check(result.known && result.group == gem, "incomplete observations cannot hide third real job");
    w.geo.nearest_altar[w.geo.groups[0].spawns[0].pos.x] = unreachable;
    w.geo.nearest_altar[w.geo.groups[1].spawns[0].pos.x] = unreachable;
    result = run(w, a);
    check(result.known && result.group == gem, "unreachable bank rows do not use useful quota");
    result = run(w, a, gem);
    check(!result.known && result.rate == 0, "all unresolved alternatives remain unknown");
    w.routes.erase(w.geo.groups[gem].spawns[0].pos.x);
    check(!run(w, a).known, "uncached feasible icon does not build a route or become known");
    w.routes[w.geo.groups[gem].spawns[0].pos.x] = 3;
    w.groups[gem].seen = 0;
    check(!run(w, a).known, "stale real job does not resolve opportunity");
    w.groups[gem].seen = 1;
    a.move_speed = 2;
    result = run(w, a);
    const double expected2 = 22.0 / (2 + 5 + 6 + 3 + tribute_ticks(22));
    check(result.known && std::abs(result.rate - expected2) < 1e-12,
          "both job travel and bank travel use ceil owner opportunities at speed two");
    a.move_speed = 3;
    result = run(w, a);
    const double expected3 = 22.0 / (1 + 5 + 6 + 2 + tribute_ticks(22));
    check(result.known && std::abs(result.rate - expected3) < 1e-12,
          "speed three does not pay raw bank steps");
    World bank_only; a.gems = 22; a.move_speed = 2;
    result = run(bank_only, a);
    check(result.known && result.bank && result.group == -1 &&
              std::abs(result.rate - 22.0 / (3 + tribute_ticks(22) + 1)) < 1e-12,
          "direct bank rounds partial speed movement upward");
    a.gems = 0; a.move_speed = 1;
    World positive; add(positive, 40, 0, 5); add(positive, 40, 0, 10);
    add(positive, 40, 0, 200);
    result = run(positive, a);
    check(result.known && result.group == 1,
          "only first two fully priced positives are compared; no global best claim");
    World bounded;
    for (int i = 0; i < 257; ++i) add(bounded, 2400, 60, 22, false);
    add(bounded, 40, 0);
    check(!run(bounded, a).known, "work exhausted before unseen tail remains unknown");
    World costly; add(costly, 40, 0);
    costly.geo.groups[0].spawns.resize(300, costly.geo.groups[0].spawns[0]);
    const int cheap = add(costly, 40, 0);
    check(run(costly, a).group == cheap, "oversized unresolved row can be skipped for later cheap job");
    World danger; add(danger, 40, 0);
    Actor enemy; enemy.id = 10; enemy.strength = 1000; danger.enemies.push_back(enemy);
    check(!run(danger, a).known, "credible reply cannot manufacture a feasible alternative");
    std::cout << checks << " separate-opportunity checks passed\n";
}
