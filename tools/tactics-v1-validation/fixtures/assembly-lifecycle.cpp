#include "information.h"
#include "resource.h"
#if __has_include("awake_entry.h")
#include "awake_entry.h"
#define TACTICS_LIFECYCLE_HAS_AWAKE 1
#endif
#include <cstdio>
#include <cstdlib>
#include <utility>
// Explicit native epoch input. It is independent from the mock World round,
// so the exact production maintenance path can also exercise a stale snapshot.
namespace bc {
inline unsigned native_round = 100;
inline unsigned round_number() { return native_round; }
}
namespace tactics {
struct TestGeometry {
    std::vector<Group> groups;
    std::vector<std::uint16_t> home;
    std::vector<Pos> altars;
    std::vector<std::vector<std::uint16_t>> altar_fields;
    std::vector<std::pair<std::pair<int,int>,std::vector<std::uint16_t>>> goal_cache;
    mutable int route_queries=0;bool monolith_only=false;std::vector<Pos> prepared;
    bool blocked(Pos)const{return false;}
    void goal_field(Pos p,int){prepared.push_back(p);}
    bool valid(Pos p)const{++route_queries;return p.x>=0&&p.y>=0;}
    int index(Pos p)const{return p.y*64+p.x;}
    int at(const std::vector<std::uint16_t>&,Pos)const{return 1;}
};
struct World {
    Actor self;int round=100,physical_group=-1,publish_calls=0,published_claim=100;
    TestGeometry geo;std::vector<GroupView>groups;std::vector<Actor>enemies;
    bool home=false;
    bool on_group(int gi,Pos p)const{return gi==physical_group&&p==self.pos;}
    bool in_spawn(Pos)const{return home;}
    void publish_claim(int gi){++publish_calls;published_claim=gi;}
};
struct LogLine{explicit LogLine(const char*){}template<class T>LogLine&field(T){return *this;}void emit(){}};
// EXACT_LIFECYCLE
struct TestBot {
    TestGeometry geometry_;Memory memory_;Pos fallback_route_{};
    int fallback_route_round_=-1000,fallback_group_=-1;
    // EXACT_PREPARE_ROUTE
};
}
using namespace tactics;
struct Case {
    World w;Memory m;
    Case(){w.self.id=3;w.self.alive=true;w.self.can_move=true;w.self.hp=w.self.max_hp=900;w.self.pos={4,61};
        m.mission.phase=Phase::Assemble;m.mission.group=5;m.mission.start=100;m.mission.expiry=106;
        m.mission.last_progress=100;m.mission.target={7,62};m.mission.last_pos=w.self.pos;}
};
int main(){int checks=0;auto ck=[&](bool okay,const char*label){++checks;if(!okay){std::fprintf(stderr,"FAIL %s\n",label);std::exit(1);}};
{Case c;for(int r=100;r<106;++r){c.w.round=r;observe_progress(c.w,c.m);ck(c.m.mission.phase==Phase::Assemble,"finite initial no-motion grace preserved");}c.w.round=106;observe_progress(c.w,c.m);ck(c.m.mission.phase==Phase::Unassigned&&c.m.mission.group==-1,"expired no-progress Assemble releases with no optional planner invocation");ck(c.m.failed_group==5&&c.m.failed_until==112,"release records existing bounded failed-group backoff");ck(c.w.publish_calls==1&&c.w.published_claim==-1,"stale intent claim cleared at same new-owner maintenance");ck(c.w.geo.route_queries==0,"maintenance independent of cached routes and expensive geometric planner");for(int r=107;r<700;++r){c.w.round=r;observe_progress(c.w,c.m);}ck(c.w.publish_calls==1&&c.m.mission.phase==Phase::Unassigned,"zero-planner-budget future owners cannot retain or resurrect old intent");}
{Case c;c.w.round=106;c.m.mission.last_progress=106;c.m.mission.expiry=112;observe_progress(c.w,c.m);ck(c.m.mission.group==-1,"intent/claim timestamp and rolling expiry do not simulate real movement");}
{Case c;c.m.moved_round=105;c.w.round=106;observe_progress(c.w,c.m);ck(c.m.mission.group==5&&c.m.mission.last_progress==100&&c.m.mission.expiry==106,"recent accepted actual movement preserves job and existing timers");c.w.round=111;observe_progress(c.w,c.m);ck(c.m.mission.group==-1,"movement grants only finite existing six-owner progress window");}
{Case c;c.m.moved_round=90;c.w.round=106;observe_progress(c.w,c.m);ck(c.m.mission.group==-1,"movement before current intent cannot renew waiting");}
{Case c;c.m.mission.start=104;c.m.mission.expiry=105;c.w.round=105;observe_progress(c.w,c.m);ck(c.m.mission.group==-1,"explicit expired intent released without waiting extra birth grace");}
{Case c;c.m.mission.phase=Phase::Clear;c.m.mission.assembly_count=2;c.w.round=200;observe_progress(c.w,c.m);ck(c.m.mission.phase==Phase::Clear&&c.w.publish_calls==0,"paid current Clear not governed by unnamed waiting expiry");}
{Case c;c.m.mission.assembly_pending=true;c.w.round=200;observe_progress(c.w,c.m);ck(c.m.mission.phase==Phase::Assemble&&c.w.publish_calls==0,"named pending rendezvous retains separate fresh route and lease contract");}
{Case c;c.w.self.channel=Channel::Recall;c.w.round=200;observe_progress(c.w,c.m);ck(c.m.mission.phase==Phase::Assemble&&c.w.publish_calls==0,"active channel excluded from ordinary intent maintenance");}
{Case c;c.w.round=106;c.w.physical_group=5;c.w.groups.resize(6);c.w.groups[5].seen=106;c.w.groups[5].state=Lifecycle::Reward;observe_progress(c.w,c.m);ck(c.m.hold_group==5&&c.m.mission.group==5&&c.w.publish_calls==0,"actual live reward holder continuity precedes release");}
{Case c;c.w.round=106;c.m.mission.chain_used=true;c.w.self.gems=22;observe_progress(c.w,c.m);ck(c.m.mission.chain_used&&c.m.mission.bank_after_reward,"failed additional-reward intent terminates onto existing bag conversion");}
{Case c;c.w.round=106;c.m.mission.bank_after_reward=true;observe_progress(c.w,c.m);ck(c.m.mission.bank_after_reward,"preexisting conversion obligation preserved");}
{Case c;c.w.round=105;observe_progress(c.w,c.m);auto prior=c.m;c.m.mission.start=90;c.m.mission.expiry=96;observe_progress(c.w,c.m);ck(c.m.mission.group==5&&c.w.publish_calls==0,"same owner secondary arbitration does not run new-owner release twice");c.w.round=106;observe_progress(c.w,c.m);ck(c.m.mission.group==-1,"next new owner performs previously deferred maintenance");}
{Case c;c.m.mission.target={8,63};c.m.mission.last_progress=106;c.w.round=106;observe_progress(c.w,c.m);ck(c.m.mission.group==-1,"target change without accepted movement cannot count as physical progress");}
{Case c;TestBot b;Group g;g.gems=22;g.initial_hp=100;g.initial_strength=10;Spawn s;s.pos={7,62};g.spawns={s};b.geometry_.groups={g,g};b.geometry_.groups[1].spawns.front().pos={8,60};b.memory_.failed_group=0;b.memory_.failed_until=106;b.fallback_group_=0;b.fallback_route_={7,62};b.fallback_route_round_=99;c.w.round=100;b.prepare_route(c.w);ck(b.fallback_group_==1&&b.geometry_.prepared.back()==Pos{8,60},"cached ordinary fallback for newly failed group cannot survive bounded backoff");}
{Case c;TestBot b;Group g;g.gems=22;g.initial_hp=100;g.initial_strength=10;Spawn s;s.pos={7,62};g.spawns={s};b.geometry_.groups={g};b.memory_.failed_group=0;b.memory_.failed_until=106;b.fallback_group_=0;b.fallback_route_={7,62};b.fallback_route_round_=99;c.w.round=100;b.prepare_route(c.w);ck(b.fallback_group_==-1&&b.geometry_.prepared.empty(),"no other legal group means no stale failed-field preparation");c.w.round=106;b.prepare_route(c.w);ck(b.fallback_group_==0&&b.geometry_.prepared.back()==Pos{7,62},"existing bounded suppression expires without new timing constants");}
{Case c;TestBot b;Group g;g.gems=22;Spawn s;s.pos={7,62};g.spawns={s};b.geometry_.groups={g};b.memory_.failed_group=0;b.memory_.failed_until=106;b.memory_.mission.phase=Phase::Assemble;b.memory_.mission.group=0;b.memory_.mission.target=s.pos;c.w.round=100;b.prepare_route(c.w);ck(b.geometry_.prepared.empty(),"invalidated ordinary incumbent cannot retain its goal merely through mission target");}
{Case c;TestBot b;Group g;g.gems=22;Spawn s;s.pos={7,62};g.spawns={s};b.geometry_.groups={g};b.memory_.failed_group=0;b.memory_.failed_until=106;b.memory_.mission.phase=Phase::Collect;b.memory_.mission.group=0;b.memory_.mission.target=s.pos;c.w.round=100;c.w.physical_group=0;c.w.groups.resize(1);c.w.groups[0].seen=100;c.w.groups[0].state=Lifecycle::Reward;b.prepare_route(c.w);ck(b.geometry_.prepared.size()==1&&b.geometry_.prepared.back()==s.pos,"actual fresh holder continuity overrides ordinary failed-group route suppression");}
for(Phase phase:{Phase::Deliver,Phase::Recover,Phase::Channel}){Case c;TestBot b;Group g;g.gems=22;b.geometry_.groups={g};b.memory_.failed_group=0;b.memory_.failed_until=106;b.memory_.mission.phase=phase;b.memory_.mission.group=0;b.memory_.mission.target={20,20};b.prepare_route(c.w);ck(b.geometry_.prepared.size()==1&&b.geometry_.prepared.back()==Pos{20,20},"failed farm suppression does not overwrite delivery recovery or channel destination");}
{Case c;c.w.round=101;c.m.mission.chain_used=true;c.m.last_gems=24;c.w.self.gems=24;c.w.groups.resize(6);c.w.groups[5].seen=101;c.w.groups[5].state=Lifecycle::Respawning;observe_progress(c.w,c.m);ck(c.m.mission.chain_used&&!c.m.mission.bank_after_reward,"another recipient's payout is not our own extra gem receipt");}
{Case c;c.w.round=101;c.m.mission.chain_used=true;c.m.last_gems=24;c.w.self.gems=48;c.w.groups.resize(6);c.w.groups[5].seen=101;c.w.groups[5].state=Lifecycle::Respawning;observe_progress(c.w,c.m);ck(c.m.mission.chain_used&&c.m.mission.bank_after_reward,"actual personal bag increase after native payout enables obligatory conversion");}
#ifdef TACTICS_LIFECYCLE_HAS_AWAKE
auto pending=[](Case&c){c.w.round=101;bc::native_round=101;c.m.mission.phase=Phase::Travel;
 c.m.awake_entry={3,5,9,100,c.w.self.pos,{7,62}};c.w.groups.resize(6);
 c.w.groups[5].seen=101;c.w.groups[5].state=Lifecycle::Alive;
 Camp camp;camp.id=9;camp.hp=100;camp.awake=true;camp.pos={7,62};c.w.groups[5].camps={camp};};
{Case c;pending(c);observe_progress(c.w,c.m);ck(awake_entry_active(c.m.awake_entry),"exact maintenance retains fresh fixed next-owner awake receipt");}
{Case c;pending(c);bc::native_round=102;observe_progress(c.w,c.m);ck(awake_entry_active(c.m.awake_entry)&&c.m.awake_entry_backoff_group==-1,"native epoch mismatch does not mutate paid entry from stale World");}
{Case c;pending(c);c.w.round=102;bc::native_round=102;c.m.observed_round=102;observe_progress(c.w,c.m);ck(!awake_entry_active(c.m.awake_entry)&&c.m.awake_entry_backoff_group==5,"fixed entry deadline expires before duplicate-owner maintenance shortcut");}
{Case c;pending(c);c.w.groups[5].camps.clear();observe_progress(c.w,c.m);ck(!awake_entry_active(c.m.awake_entry)&&c.m.awake_entry_backoff_group==5,"fresh World missing actual named camp invalidates rather than defers entry");}
{Case c;pending(c);c.w.physical_group=5;c.w.groups[5].state=Lifecycle::Reward;observe_progress(c.w,c.m);ck(!awake_entry_active(c.m.awake_entry)&&c.m.hold_group==5&&c.m.awake_entry_backoff_group==-1,"actual Reward conversion clears entry without suppressing live holder");}
#endif
std::printf("%d assembly lifecycle checks passed\n",checks);}
