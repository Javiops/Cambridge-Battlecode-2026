#include "types.h"
#include <cstdio>
#include <cstdlib>
#include <map>
namespace tactics {
struct SpawnMask {
    std::vector<Pos> points;
    const std::vector<Pos>& positions() const { return points; }
};
struct Geometry {
    SpawnMask own_spawn;
    int route_requests = 0;
    std::map<std::pair<int,int>,int> distances;
    int estimate(Pos,Pos p) const { auto it=distances.find({p.x,p.y}); return it==distances.end()?unreachable:it->second; }
    void ensure_route(Pos) { ++route_requests; }
};
struct World {
    Actor self;
    Geometry geo;
    int round = 10, home = 0, after = 0, channel_queries = 0;
    Memory memory;
    bool safe_recall = true;
    double landing_damage = 0;
    Pos step{}, requested_target{};
    std::vector<Pos> occupied;
    bool in_spawn(Pos p) const {
        return std::find(geo.own_spawn.points.begin(),geo.own_spawn.points.end(),p)!=geo.own_spawn.points.end();
    }
    int home_distance(Pos p) const { return p==self.pos ? home : after; }
    int walk(Pos,Pos target) { return geo.estimate(self.pos,target); }
    bool free(Pos p) const { return std::find(occupied.begin(),occupied.end(),p)==occupied.end(); }
    std::optional<Pos> toward(Pos p,int,bool) { requested_target=p;return step.x>=0?std::optional(step):std::nullopt; }
};
Pos position(Pos p) { return p; }
int current_recall_ticks(const Actor& a) { return a.home ? 3 : 5; }
bool needs_recovery(World& w) { return w.self.health_fraction()<Settings::ordinary_heal; }
bool safe_channel(World& w,int,bool) { ++w.channel_queries;return w.safe_recall; }
double incoming_damage(World& w,Pos) { return w.landing_damage; }
Proposal economic(Action a,Mission m,Priority p,double value) {
    Proposal out;out.action=a;out.mission=m;out.priority=p;out.value=value;out.valid=true;return out;
}
Action moving(Pos p,const char* reason) { Action out;out.kind=Kind::Move;out.at=p;out.reason=reason;return out; }
// INSERT_PRODUCTION_RECOVERY_FUNCTION
}
using namespace tactics;
int checks=0;
void check(bool value,const char* message) { ++checks;if(!value){std::fprintf(stderr,"FAIL %s\n",message);std::exit(1);} }
World example(int home=1) {
    World w;w.self.id=1;w.self.alive=true;w.self.pos={5,5};w.self.hp=400;w.self.max_hp=1000;w.self.can_move=true;
    w.self.move_speed=1;w.home=home;w.after=std::max(0,home-1);w.geo.own_spawn.points={{4,5}};
    w.geo.distances[{4,5}]=home;w.step={4,5};return w;
}
int main() {
    Memory m;World w=example();auto p=recovery(w,m);
    check(p&&p->action.kind==Kind::Move,"one-step legal walk beats five-tick recall");
    check(w.channel_queries==0,"faster safe walk needs no full recall search");
    w=example(9);w.self.move_speed=3;p=recovery(w,m);
    check(p&&p->action.kind==Kind::Move,"actual speed-three walking ETA beats normal recall");
    w=example(5);w.step={4,4};p=recovery(w,m);
    check(p&&p->action.kind==Kind::Recall,"equal five-window walk retains safe recall");
    w=example(4);w.self.home=true;w.step={4,4};p=recovery(w,m);
    check(p&&p->action.kind==Kind::Recall,"Home three-tick recall beats four-window walk");
    w=example(2);w.self.home=true;p=recovery(w,m);
    check(p&&p->action.kind==Kind::Move,"two-window walk beats Home recall");
    w=example(9);w.safe_recall=false;w.step={4,4};p=recovery(w,m);
    check(p&&p->action.kind==Kind::Move,"safe walking remains available when channel unsafe");
    w=example();w.landing_damage=w.self.hp;p=recovery(w,m);
    check(p&&p->action.kind==Kind::Recall,"exact-lethal walking landing rejected in favor of safe recall");
    w=example();w.safe_recall=false;w.landing_damage=w.self.hp;p=recovery(w,m);
    check(!p,"neither unsafe path is fabricated as safe recovery");
    w=example(unreachable);w.geo.distances.clear();w.step={};p=recovery(w,m);
    check(p&&p->action.kind==Kind::Recall,"disconnected walking region does not veto legal safe recall");
    w=example(3);w.geo.own_spawn.points={{4,5},{7,5}};w.geo.distances[{4,5}]=20;w.geo.distances[{7,5}]=3;
    w.step={6,5};p=recovery(w,m);
    check(p&&p->action.kind==Kind::Move&&p->mission.target==Pos{7,5},"spawn destination uses geodesic path rather than nearer center through wall");
    check(w.geo.route_requests==0,"spawn recovery reuses immutable home field without rebuilding a source field");
    w=example(2);w.geo.own_spawn.points={{4,5},{7,5}};w.geo.distances[{4,5}]=1;w.geo.distances[{7,5}]=2;
    w.occupied={{4,5}};w.step={6,5};p=recovery(w,m);
    check(p&&p->mission.target==Pos{7,5},"currently occupied closest spawn endpoint skipped");
    w=example();w.after=w.home;w.step={5,4};p=recovery(w,m);
    check(p&&p->action.kind==Kind::Recall,"sideways retreat is not priced as certified progress home");
    w=example(9);w.safe_recall=true;w.step={4,4};m.channel_attempt_round=w.round;p=recovery(w,m);
    check(p&&p->action.kind==Kind::Move,"a prior channel attempt does not erase safe walk fallback");
    m={};w=example();w.self.alive=false;p=recovery(w,m);
    check(!p&&w.geo.route_requests==0,"dead body cannot begin a return operation");
    w=example();w.self.pos={4,5};p=recovery(w,m);
    check(p&&p->action.kind==Kind::None,"on-spawn needed heal remains a hold");
    w.self.hp=1000;p=recovery(w,m);check(!p,"ready spawn body does not keep recovering");
    m={};w=example(9);w.self.hp=w.self.max_hp;
    p=recovery(w,m);check(!p,"healthy body with no certified investment does not return");
    m.upgrade_gem_unlock=true;
    p=recovery(w,m);check(p&&p->mission.phase==Phase::Recover,
        "certified completed-gem unlock permits elective return without invented saved turns");
    std::printf("%d recovery checks passed\n",checks);
}
