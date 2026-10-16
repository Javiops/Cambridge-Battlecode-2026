#include "types.h"
#include <cstdio>
#include <cstdlib>
#include <map>
namespace tactics {
namespace bc { namespace constants { constexpr int winning_gems=1000,max_rounds=2000,submit_gems_range=1; } }
Pos sdk(Pos p){return p;}
struct Visibility { bool is_set(Pos)const{return false;} };
struct Lock { int hits_remaining()const{return 3;} };
struct Geometry {
    std::vector<Pos> altars;
    std::vector<std::vector<std::uint16_t>> altar_fields;
    int at(const std::vector<std::uint16_t>&f,Pos)const{return f.empty()?unreachable:f[0];}
};
struct World {
    Actor self;Memory memory;Geometry geo;Visibility visible;
    int own_score=995,round=10;
    bool safe=true;
    std::vector<Actor> enemies;
    std::map<std::pair<int,int>,Pos> steps;
    std::map<std::pair<int,int>,double> damage;
    std::vector<Pos> requested;
    std::optional<Action> escape;
    std::optional<Lock> enemy_lock(Pos){return std::nullopt;}
    std::optional<Pos> toward(Pos target,int) {
        requested.push_back(target);auto it=steps.find({target.x,target.y});
        return it==steps.end()?std::nullopt:std::optional(it->second);
    }
};
int current_tribute_ticks(int) {return 1;}
bool safe_channel(World&w,int,bool){return w.safe;}
double incoming_damage(World&w,Pos p){return w.damage[{p.x,p.y}];}
std::optional<Action> escape_action(World&w){return w.escape;}
Proposal economic(Action a,Mission m,Priority p,double value) {
    Proposal out;out.action=a;out.mission=m;out.priority=p;out.value=value;out.valid=true;return out;
}
Action moving(Pos p,const char*reason){Action a;a.kind=Kind::Move;a.at=p;a.reason=reason;return a;}
// INSERT_PRODUCTION_ALTAR_AND_DELIVERY
}
using namespace tactics;
int checks=0;
void check(bool value,const char*message){++checks;if(!value){std::fprintf(stderr,"FAIL %s\n",message);std::exit(1);}}
World example() {
    World w;w.self.pos={0,0};w.self.alive=true;w.self.hp=500;w.self.max_hp=1000;w.self.gems=5;
    w.geo.altars={{5,0},{0,5}};w.geo.altar_fields={{4},{5}};
    w.steps[{5,0}]={1,0};w.steps[{0,5}]={0,1};return w;
}
int main(){
    Memory m;World w=example();auto p=delivery(w,m);
    check(p&&p->mission.target==Pos{5,0},"lowest-cost legal altar remains incumbent choice");
    w=example();w.steps.erase({5,0});p=delivery(w,m);
    check(p&&p->mission.target==Pos{0,5},"blocked first approach falls back to second shortlisted altar");
    check(w.requested.size()==2,"both bounded legal proposals actually considered");
    w=example();w.damage[{1,0}]=w.self.hp;p=delivery(w,m);
    check(p&&p->mission.target==Pos{0,5},"exact-lethal first landing cannot erase safe second bank route");
    w=example();w.steps.clear();p=delivery(w,m);
    check(!p,"no route to either altar does not fabricate delivery");
    w=example();w.damage[{1,0}]=w.self.hp;w.damage[{0,1}]=w.self.hp;p=delivery(w,m);
    check(!p,"both lethal approaches rejected");
    w=example();w.geo.altars.push_back({8,8});w.geo.altar_fields.push_back({9});w.steps[{8,8}]={1,1};
    w.steps.erase({5,0});w.steps.erase({0,5});p=delivery(w,m);
    check(!p&&w.requested.size()==2,"search remains explicitly bounded to two geodesic shortlist candidates");
    w=example();w.self.gems=0;p=delivery(w,m);
    check(!p&&w.requested.empty(),"empty bag cannot create a delivery mission");
    w=example();w.self.pos={5,0};p=delivery(w,m);
    check(p&&p->action.kind==Kind::Tribute&&p->priority==Priority::Deciding,"available legal winning bank starts immediately");
    w=example();w.self.pos={5,0};w.safe=false;Action exit;exit.kind=Kind::Move;exit.at={4,0};w.escape=exit;p=delivery(w,m);
    check(p&&p->mission.target==Pos{0,5}&&p->priority==Priority::Deciding,"feasible alternative delivery checked before escape fallback from unsafe first altar");
    w=example();w.self.pos={5,0};w.safe=false;w.escape=exit;w.steps.clear();p=delivery(w,m);
    check(p&&p->priority==Priority::Survival&&p->action.at==Pos{4,0},"actual escape retained if neither altar offers a legal bank action");
    w=example();w.self.pos={5,0};w.memory.channel_attempt_round=w.round;p=delivery(w,m);
    check(p&&p->mission.target==Pos{0,5}&&p->action.kind==Kind::Move,"first altar hold does not hide second legal approach");
    w=example();w.own_score=0;w.self.gems=1;p=delivery(w,m);
    check(!p,"small ordinary bag still needs an actual delivery trigger");
    std::printf("%d delivery checks passed\n",checks);
}
