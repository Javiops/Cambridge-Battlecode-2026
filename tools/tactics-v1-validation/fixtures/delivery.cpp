#include "types.h"
#include "resource.h"
#include <cstdio>
#include <cstdlib>
#include <map>
#include <bit>
#include <tuple>
namespace tactics {
namespace bc { inline unsigned remaining=110000;inline int actual_round=10;inline unsigned fuel_remaining(){return remaining;}inline int round_number(){return actual_round;}namespace constants { constexpr int winning_gems=1000,max_rounds=2000,submit_gems_range=1,capture_time=5; } }
Pos sdk(Pos p){return p;}
struct Visibility { bool is_set(Pos)const{return false;} };
struct Lock { int hits_remaining()const{return 3;} };
struct Geometry {
    int width=20,height=20;
    bool monolith_only=false;
    std::vector<Pos> altars;
    std::vector<Group> groups;
    std::vector<std::vector<std::uint16_t>> altar_fields;
    std::map<std::tuple<int,int,int,int>,int> cached;
    int at(const std::vector<std::uint16_t>&f,Pos)const{return f.empty()?unreachable:f[0];}
    bool valid(Pos p)const{return p.x>=0&&p.y>=0&&p.x<width&&p.y<height;}
    int index(Pos p)const{return p.y*width+p.x;}
    bool blocked(Pos p)const{return !valid(p)||std::find(altars.begin(),altars.end(),p)!=altars.end();}
    std::optional<int> cached_steps(Pos p,Pos q)const{auto it=cached.find({p.x,p.y,q.x,q.y});return it==cached.end()?std::nullopt:std::optional(it->second);}
};
struct ExitGradient {bool known=true,viable=true;int earliest_contact=unreachable,owner_eta=1;};
struct World {
    Actor self;Memory memory;Geometry geo;Visibility visible;
    int own_score=995,round=10;
    bool safe=true;
    std::vector<Actor> enemies;
    std::vector<GroupView> groups;
    std::vector<std::uint8_t> visible_bytes=std::vector<std::uint8_t>(50,0);
    std::map<std::pair<int,int>,bool> safe_at;
    std::map<std::pair<int,int>,int> contact;
    std::map<std::pair<int,int>,Pos> steps;
    std::map<std::pair<int,int>,double> damage;
    std::vector<Pos> requested;
    std::optional<Action> escape;
    bool in_spawn(Pos p)const{return p==Pos{0,0};}
    bool free(Pos p)const{return !geo.blocked(p);}
    double exposure(Pos p)const{auto it=damage.find({p.x,p.y});return it==damage.end()?0:it->second;}
    int home_distance(Pos p)const{return distance(p,{0,0});}
    bool warning_near(Pos,int) const { return false; }
    std::optional<Lock> enemy_lock(Pos){return std::nullopt;}
    std::optional<Pos> toward(Pos target,int) {
        requested.push_back(target);auto it=steps.find({target.x,target.y});
        return it==steps.end()?std::nullopt:std::optional(it->second);
    }
};
int current_tribute_ticks(int) {return 1;}
bool safe_channel(World&w,int,bool){return w.safe;}
bool safe_channel_at(World&w,Pos p,int,bool){auto it=w.safe_at.find({p.x,p.y});return it==w.safe_at.end()?w.safe:it->second;}
int observed_contact_eta(const World&w,Pos p,int,bool=true){auto it=w.contact.find({p.x,p.y});return it==w.contact.end()?unreachable:it->second;}
ExitGradient known_exit_prefix(const World&,Pos,bool){return {};}
int current_recall_ticks(const Actor&a){return a.home?3:5;}
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
    w=example();m={};w.geo.groups.resize(1);auto&g=w.geo.groups[0];g.gems=10;g.initial_hp=10;g.spawns.push_back({0,0,{8,8}});
    w.groups.resize(1);w.groups[0].seen=w.round;w.groups[0].state=Lifecycle::Alive;w.self.strength=10;
    w.geo.cached[{0,0,8,8}]=1;
    for(int y=0;y<20;++y)for(int x=0;x<20;++x)w.geo.cached[{x,y,8,8}]=x>=4?20:1;
    m.mission.group=0;m.mission.rate=1;p=delivery(w,m);
    check(p&&p->mission.target==Pos{0,5},"same named productive endpoint can beat shorter immediate bank");
    check(p&&p->mission.bank_reentry_group==0&&p->mission.bank_reentry_target==Pos{8,8},"priced next job survives the bank start as typed intention");
    const auto saved=g.gems;g.gems=0;g.gold=10000;
    check(named_bank_continuation(w,m.mission).group<0,"current carried bag cannot score a pure-gold job after completed bank");
    w.geo.monolith_only=true;
    check(named_bank_continuation(w,m.mission).group<0,"unpriced monolith gold fallback cannot become named scored bank reentry");
    w.geo.monolith_only=false;g.gems=saved;g.gold=0;
    auto next=bank_completion_reentry(p->mission,w.round,false);
    check(next.phase==Phase::Unassigned,"accepted start cannot enter bank continuation");
    next=bank_completion_reentry(p->mission,w.round,true);
    check(next.phase==Phase::Reenter&&next.group==0&&!next.chain_used&&next.expiry==w.round+Settings::job_lease,"actual bank completion releases finite reentry without chain renewal");
    w.geo.cached.erase({4,0,8,8});p=delivery(w,m);
    check(p&&p->mission.target==Pos{5,0}&&p->mission.bank_reentry_group<0,"unknown return leg is not a free zero-cost endpoint");
    w=example();m={};w.self.pos={4,0};w.self.can_move=true;w.safe=false;w.safe_at[{4,1}]=true;w.steps.clear();p=delivery(w,m);
    check(p&&p->action.kind==Kind::Move&&p->action.at==Pos{4,1},"unsafe current ring tile can select actual legal safe ring neighbor");
    check(p&&p->mission.phase==Phase::Deliver&&p->action.kind!=Kind::Tribute,"ring movement remains a delivery approach, never completed tribute");
    bc::remaining=54000;p=delivery(w,m);check(p&&p->action.kind==Kind::None,"unfunded optional ring forecast preserves action reserve");bc::remaining=110000;
    w.self.can_move=false;p=delivery(w,m);check(p&&p->action.kind==Kind::None,"spent movement cannot promise ring relocation");
    w=example();m={};w.self.pos={3,0};m.mission.phase=Phase::Deliver;m.mission.target={5,0};note_failed_bank_window(w,m);w.memory=m;
    check(failed_bank_window_active(w,0),"actual needed recovery records finite failed bank window");
    w.self.hp=w.self.max_hp;w.self.pos={0,0};check(failed_bank_window_active(w,0),"Recall and heal do not erase an unchanged window");
    w.self.strength+=1;check(!failed_bank_window_active(w,0),"actual power change permits a new feasible bank quote");w.self.strength-=1;
    w.round=m.failed_bank_until;check(!failed_bank_window_active(w,0),"finite bank backoff expires without permanent altar ban");w.round=10;
    w.visible_bytes.assign(50,255);w.contact[{3,0}]=0;check(failed_bank_window_active(w,0),"fresh view of still threatened recorded window is not safe absence");
    w.contact.clear();check(!failed_bank_window_active(w,0),"fresh safe personal view of recorded failure window may reopen it");
    w=example();m={};w.own_score=0;w.self.gems=12;w.self.pos={3,0};m.mission.phase=Phase::Deliver;m.mission.target={5,0};note_failed_bank_window(w,m);w.memory=m;p=delivery(w,m);
    check(p&&p->mission.target==Pos{0,5},"unchanged failed window reopens the bounded alternative altar choice");
    w.own_score=995;p=delivery(w,m);check(p&&p->mission.target==Pos{5,0},"deciding delivery bypasses an ordinary uncertainty backoff");
    w=example();m={};w.contact[{5,0}]=0;auto plans=altar_plans(w,&m.mission);
    check(plans.size()==2&&plans[0].index==1,"observed earlier spell/movement contact reprices bounded altar choice");
    w.contact[{5,0}]=unreachable;plans=altar_plans(w,&m.mission);
    check(plans[0].index==0,"absent contact does not manufacture an exposure penalty");
    w.contact[{5,0}]=100;plans=altar_plans(w,&m.mission);
    check(plans[0].index==0,"contact after completion does not alter ordinary ranking");
    w.contact[{5,0}]=5;plans=altar_plans(w,&m.mission);
    auto found=std::find_if(plans.begin(),plans.end(),[](const AltarPlan&p){return p.index==0;});
    check(found!=plans.end()&&found->cost==6,"contact at final completion phase charges one exposure unit");
    std::printf("%d delivery checks passed\n",checks);
}
