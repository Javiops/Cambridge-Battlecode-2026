#include <awake_entry.h>
#include <cstdio>
#include <stdexcept>
using namespace tactics;
static int count=0;
static void check(bool value,const char*why){++count;if(!value){std::printf("LEASE_TEST_FAIL %d %s\n",count,why);std::fflush(stdout);throw std::runtime_error(why);}}
int main(){Actor actor;actor.id=0;actor.alive=true;actor.can_move=true;actor.hp=actor.max_hp=1000;actor.pos={1,1};actor.move_speed=2;actor.range=1;const std::array<Pos,3> path{{{1,1},{2,1},{3,1}}};
 check(complete_awake_entry_route(actor,path,{3,1},[](Pos){return true;}),"whole visible legal path");
 check(!complete_awake_entry_route(actor,std::span(path.data(),2),{3,1},[](Pos){return true;}),"partial prefix cannot replace paid endpoint");
 check(!complete_awake_entry_route(actor,path,{3,1},[](Pos p){return p!=Pos{3,1};}),"blocked final destination declines, no partial move");
 check(!complete_awake_entry_route(actor,path,{3,1},[](Pos p){return p!=Pos{2,1};}),"blocked intermediate declines");
 actor.move_speed=1;check(!complete_awake_entry_route(actor,path,{3,1},[](Pos){return true;}),"two-owner path cannot enter one-owner receipt");actor.move_speed=2;
 const std::array<Pos,2> jump{{{1,1},{3,1}}};check(!complete_awake_entry_route(actor,jump,{3,1},[](Pos){return true;}),"native path must be adjacent");
 const AwakeEntryContract contract{0,2,7,100,{3,1},{4,1}};Camp camp;camp.id=7;camp.pos={4,1};camp.hp=1000;
 Proposal move;move.valid=true;move.action.kind=Kind::Move;move.action.at={3,1};move.mission.group=2;move.mission.phase=Phase::Travel;move.mission.expiry=102;move.mission.awake_entry=contract;
 Memory m;m.mission=move.mission;commit_awake_entry(m,move,false,100);check(!awake_entry_active(m.awake_entry),"failed native Move cannot install receipt");commit_awake_entry(m,move,true,100);check(same_awake_entry(m.awake_entry,contract),"only accepted Move installs fixed receipt");
 {Memory v;commit_awake_entry(v,move,true,101);check(!awake_entry_active(v.awake_entry),"stale source-round cannot install accepted entry receipt");}
 {Memory v;auto bad=move;bad.action.at={2,1};commit_awake_entry(v,bad,true,100);check(!awake_entry_active(v.awake_entry),"partial or changed actual endpoint cannot install receipt");}
 {Memory v;auto bad=move;bad.mission.group=3;commit_awake_entry(v,bad,true,100);check(!awake_entry_active(v.awake_entry),"retargeted mission cannot install other-group receipt");}
 check(!future_awake_entry_available(m,2,100)&&!future_awake_entry_available(m,3,100),"pending receipt cannot renew via same or changed group");
 auto revised=move;revised.mission.awake_entry.round=101;revised.mission.awake_entry.stage={4,1};commit_awake_entry(m,revised,true,101);check(same_awake_entry(m.awake_entry,contract),"accepted repeated intent cannot extend source deadline or stage");
 actor.pos=contract.stage;check(observe_awake_entry(m,actor,100,true,&camp,false)==AwakeEntryObservation::Pending,"fresh actual accepted endpoint may revalidate");
 check(observe_awake_entry(m,actor,101,true,&camp,false)==AwakeEntryObservation::Pending,"one next-owner opportunity retained");
 check(observe_awake_entry(m,actor,102,false,&camp,false)==AwakeEntryObservation::Stale&&awake_entry_active(m.awake_entry),"stale snapshot cannot mutate receipt");
 m.mission.expiry=99999;check(observe_awake_entry(m,actor,102,true,&camp,false)==AwakeEntryObservation::Expired,"ordinary job expiry cannot renew one-owner source time");check(!awake_entry_active(m.awake_entry)&&m.mission.group==-1&&m.failed_group==2&&m.failed_until==102+Settings::job_lease,"expiry releases only pending work and installs real group backoff");
 check(!future_awake_entry_available(m,2,103)&&future_awake_entry_available(m,2,m.failed_until),"finite backoff boundary");
 m.failed_group=3;m.failed_until=9999;check(!future_awake_entry_available(m,2,103),"unrelated generic failure cannot erase dedicated one-owner entry backoff");
 check(future_awake_entry_available(m,2,m.awake_entry_backoff_until),"dedicated entry backoff releases exactly at fixed boundary");
 for(int kind=0;kind<4;++kind){Memory v;v.awake_entry=contract;v.mission=move.mission;Actor a=actor;Camp c=camp;if(kind==0)a.pos={2,1};if(kind==1)c.id=8;if(kind==2)c.pos={4,2};const Camp*cp=kind==3?nullptr:&c;check(observe_awake_entry(v,a,101,true,cp,false)==AwakeEntryObservation::Invalid&&!awake_entry_active(v.awake_entry)&&v.failed_group==2,"changed stage, identity, moved target or missing physical target invalidates without renewal");}
 {Memory v;v.awake_entry=contract;v.mission=move.mission;v.mission.phase=Phase::Collect;v.hold_group=2;check(observe_awake_entry(v,actor,101,true,nullptr,true)==AwakeEntryObservation::Protected&&v.mission.phase==Phase::Collect&&v.hold_group==2&&v.failed_group==-1,"actual capture or Reward transition keeps protected work and no suppression");}
 {Memory v;v.awake_entry=contract;v.mission=move.mission;v.mission.group=4;v.mission.phase=Phase::Deliver;check(observe_awake_entry(v,actor,102,true,nullptr,true)==AwakeEntryObservation::Protected&&v.mission.group==4&&v.mission.phase==Phase::Deliver,"pending expiry never discards actual protected delivery");}
 Proposal current;current.valid=true;current.action.kind=Kind::BasicCamp;current.mission.group=2;current.mission.phase=Phase::Clear;current.awake_entry_current_certified=true;
 {Memory v;v.awake_entry=contract;v.mission=move.mission;commit_awake_entry(v,current,false,101);check(awake_entry_active(v.awake_entry),"rejected current certificate cannot resolve receipt");v.mission=current.mission;commit_awake_entry(v,current,true,101);check(!awake_entry_active(v.awake_entry)&&v.mission.phase==Phase::Clear&&v.failed_group==-1,"accepted fresh actual-current full certificate resolves to productive clear");}
 {Memory v;v.awake_entry=contract;v.mission=move.mission;auto hold=current;hold.action.kind=Kind::None;hold.mission={};commit_awake_entry(v,hold,true,101);check(awake_entry_active(v.awake_entry),"None and even a tagged unexecuted hold cannot erase receipt");v.mission={};check(!future_awake_entry_available(v,2,101),"ordinary empty mission cannot erase durable receipt");}
 {Memory v;v.awake_entry=contract;v.mission=move.mission;Proposal observation;observation.action.kind=Kind::Move;observation.mission.phase=Phase::Observe;observation.mission.group=3;commit_awake_entry(v,observation,true,101);check(awake_entry_active(v.awake_entry),"unpriced observation movement cannot manufacture resolution");}
 {Memory v;v.awake_entry=contract;v.mission=move.mission;Proposal work;work.action.kind=Kind::Move;work.mission.group=3;work.mission.phase=Phase::Travel;work.mission.rate=2;commit_awake_entry(v,work,true,101);check(awake_entry_active(v.awake_entry),"raw positive rate or retargeted Move cannot assert independently certified work");work.action.kind=Kind::BasicCamp;work.mission.phase=Phase::Clear;work.solo_clear_certified=true;commit_awake_entry(v,work,true,101);check(!awake_entry_active(v.awake_entry),"accepted separately certified actual current action replaces old pending entry");}
 {Memory v;v.awake_entry=contract;v.mission=move.mission;abandon_awake_entry(v,101);check(v.failed_group==2&&!awake_entry_active(v.awake_entry)&&v.mission.group==-1,"fresh known current reserve failure releases original entry");}
 std::printf("%d awake entry lease checks passed\n",count);
}
