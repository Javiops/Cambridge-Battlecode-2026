// verify_channel_risk.py inserts the exact current production risk function here.
#define TACTICS_COMBAT_MODEL_ONLY
#include "combat.h"
#include <cstdio>
#include <cstdlib>
#include <map>
#include <array>
#include <span>
#include <tuple>
namespace tactics {
struct Sighting { Actor actor; int round; };
struct World {
    Actor self;
    int round = 10, native_queries = 0;
    std::vector<Actor> enemies;
    std::vector<Sighting> sightings;
    std::map<std::pair<int, int>, std::vector<Pos>> visible_regions;
    std::map<std::tuple<int, int, bool>, std::vector<Pos>> missing_regions;
};
bool sufficient_fuel = true;
bool fuel(int) { return sufficient_fuel; }
namespace combat_detail {
const std::vector<Pos>& enemy_positions(World& w, const Actor& e, int horizon) {
    ++w.native_queries;
    return w.visible_regions[{e.id, horizon}];
}
const std::vector<Pos>& remembered_positions(World& w, const Sighting& s, int horizon, bool future) {
    ++w.native_queries;
    return w.missing_regions[{s.actor.id, future ? horizon : 0, future}];
}
}
// INSERT_PRODUCTION_CHANNEL_FUNCTION
}
using namespace tactics;
int checks = 0;
void check(bool actual, bool expected, const char* message) {
    ++checks;
    if (actual != expected) {
        std::fprintf(stderr, "FAIL %s (got %d expected %d)\n", message, actual, expected);
        std::exit(1);
    }
}
Actor control_enemy() {
    Actor a; a.id = 44; a.alive = true; a.pos = {0,5}; a.move_speed = 1;
    a.range = 1; a.strength = 0;
    a.spells[0].kind = 4; a.spells[0].range = 4; a.spells[0].cooldown = 0;
    a.spells[0].ready = true; a.spells[0].enemies = true;
    return a;
}
World visible_world(Actor e) {
    World w; w.self.pos = {5,5}; w.self.alive = true; w.self.type = 0;
    w.enemies = {e};
    w.visible_regions[{e.id,0}] = {e.pos};
    w.visible_regions[{e.id,1}] = {{1,5}};
    w.visible_regions[{e.id,2}] = {{2,5}};
    return w;
}
World hidden_world(Actor e, int age = 1) {
    World w; w.self.pos = {5,5}; w.self.alive = true; w.self.type = 0;
    w.sightings = {{e,w.round-age}};
    w.missing_regions[{e.id,0,false}] = {{1,5}};
    w.missing_regions[{e.id,1,true}] = {{2,5}};
    w.missing_regions[{e.id,2,true}] = {{3,5}};
    return w;
}
int main() {
    Actor e = control_enemy(); World w = visible_world(e);
    check(channel_interruption_risk(w,1,true),true,"pure zero-damage compatible control interrupts tribute");
    check(channel_interruption_risk(w,0,true),false,"expired channel has no fabricated future action window");
    w.enemies[0].spells[0].exclusive = true;
    check(channel_interruption_risk(w,1,true),false,"exclusive control cannot follow same-window normal movement");
    check(channel_interruption_risk(w,2,true),true,"earlier walking can precede later exclusive control");
    w.self.type = combat_detail::marcella_type;
    check(channel_interruption_risk(w,2,true),false,"stun-immune channel owner ignores stun control");
    e.spells[0].kind = 2; e.spells[0].amount = 80;
    w = visible_world(e);
    check(channel_interruption_risk(w,1,true),false,"ordinary damage does not interrupt tribute");
    check(channel_interruption_risk(w,1,false),true,"ordinary damage interrupts recall");
    e.spells = {}; e.range = 5; e.strength = 50;
    w = visible_world(e);
    check(channel_interruption_risk(w,1,false),true,"stationary ranged basic interrupts recall");
    e.range = 1; e.type = combat_detail::marcella_type; e.pos = {4,5}; e.enhanced = true;
    w = visible_world(e); w.visible_regions[{e.id,0}] = {{4,5}};
    w.visible_regions[{e.id,1}] = {{4,5}};
    check(channel_interruption_risk(w,1,true),true,"enhanced Marcella basic stuns without an additional cast");
    w.enemies[0].enhanced = false;
    check(channel_interruption_risk(w,1,true),false,"ordinary Marcella basic is not assumed enhanced");
    w.enemies[0].spells[0].kind = 1; w.enemies[0].spells[0].ready = true;
    w.enemies[0].spells[0].cooldown = 0;
    check(channel_interruption_risk(w,1,true),true,"ready Marcella reset can prepare stunning basic");
    e = control_enemy(); w = hidden_world(e);
    check(channel_interruption_risk(w,1,true),true,"one-round missing pure control remains a channel threat");
    w = hidden_world(e,3);
    check(channel_interruption_risk(w,1,true),true,"three-round boundary missing control retained");
    w = hidden_world(e,4);
    check(channel_interruption_risk(w,1,true),false,"older sighting outside declared local horizon");
    w = hidden_world(e); w.missing_regions[{e.id,0,false}] = {};
    check(channel_interruption_risk(w,1,true),false,"personal visible absence disproves all current origins");
    w = hidden_world(e); w.enemies = {e}; w.enemies[0].pos = {40,40};
    w.enemies[0].spells = {}; w.visible_regions[{e.id,0}] = {{40,40}};
    w.visible_regions[{e.id,1}] = {{39,39}};
    check(channel_interruption_risk(w,1,true),false,"visible identity suppresses its stale ghost");
    e.spells[0].ready = false; e.spells[0].cooldown = 6;
    w = hidden_world(e,1);
    check(channel_interruption_risk(w,1,true),false,"known long control cooldown respected after sighting age");
    e.spells[0].cooldown = 5; w = hidden_world(e,3);
    check(channel_interruption_risk(w,2,true),true,"known cooldown can expire within later channel window");
    e = control_enemy(); e.pos = {0,5}; e.spells[0].exclusive = true;
    w = visible_world(e); w.self.pos = {15,5};
    check(channel_interruption_risk(w,12,true),true,"long channel search bound retains possible future exclusive control");
    e.move_speed = 3; w = visible_world(e); w.self.pos = {13,5};
    check(channel_interruption_risk(w,4,true),true,"native eight-tile bound cannot truncate speed-three four-window approach");
    check(w.native_queries != 0,false,"speed-times-window overflow uses scalar bound without truncated native query");
    w.self.pos = {14,5};
    check(channel_interruption_risk(w,4,true),false,"exclusive cast still reserves the last owner window from normal movement");
    e.move_speed = 1;
    w = hidden_world(e,1); sufficient_fuel = false;
    check(channel_interruption_risk(w,1,true),true,"low fuel keeps conservative missing-control threat");
    check(w.native_queries != 0,false,"low-fuel missing threat makes no reach-host query");
    w = visible_world(e);
    check(channel_interruption_risk(w,2,true),true,"low fuel keeps future visible exclusive threat");
    check(w.native_queries != 0,false,"low-fuel visible threat makes no reach-host query");
    e.pos = {100,100}; w = hidden_world(e,1);
    check(channel_interruption_risk(w,1,true),false,"low-fuel temporal envelope does not invent distant contact");
    sufficient_fuel = true;
    std::printf("%d channel-risk checks passed\n",checks);
}
