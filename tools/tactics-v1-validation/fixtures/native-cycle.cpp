#include "actions.h"
#include "coordinator.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
using namespace tactics;
static void check(bool pass,const char* label){if(!pass)throw std::runtime_error(label);}
int main(){
 Geometry geometry;Memory memory;std::unique_ptr<World> world;
 int group=-1,stage=0,start=-1,bag_before=0,score_before=0;Pos altar{};
 bool immediate_started=false,overlap_started=false,bank_started=false;
 while(true){
  if(bc::is_draft()){bc::draft::pick(bc::champion_draft::ryth);bc::end_turn();continue;}
  geometry.initialize();if(!world)world=std::make_unique<World>(geometry,memory);
  World&w=*world;w.refresh();observe_progress(w,memory);
  check(w.self.alive,"native cycle fixture must stay alive");
  if(group<0){
   int closest=unreachable;
   for(unsigned i=0;i<geometry.groups.size();++i)
    if(geometry.groups[i].gems>0&&geometry.groups[i].spawns.size()==1){
     const int d=w.home_distance(geometry.groups[i].spawns[0].pos);
     if(d<closest){closest=d;group=i;}
    }
   check(group>=0,"single-tile gem group exists");
   const Pos target=geometry.groups[group].spawns[0].pos;
   int nearest=unreachable;
   for(auto p:geometry.altars)if(distance(p,target)<nearest){nearest=distance(p,target);altar=p;}
   check(nearest==1,"fixture altar beside capture region");
  }
  const auto&g=geometry.groups[group];const Pos target=g.spawns[0].pos;
  auto move_to=[&](Pos destination,int range=0){
   if(auto step=w.toward(destination,range)){
    Action a;a.kind=Kind::Move;a.at=*step;a.reason="native-cycle-fixture-move";
    const auto result=execute(w,a);check(result.success,"fixture move accepted");
    w.refresh();observe_progress(w,memory);return true;
   }return false;
  };
  auto recall=[&](const char*marker){
   const int before=w.self.gems,score=w.own_score,expected=current_recall_ticks(w.self);
   Action a;a.kind=Kind::Recall;a.reason="native-cycle-fixture-recall";
   const auto result=execute(w,a);check(result.success&&result.outcome==Outcome::Started,"actual recall start accepted");
   w.refresh();check(w.self.channel==Channel::Recall,"accepted recall remains an active channel");
   check(w.self.channel_ticks==expected,"actual remaining recall duration matches production inventory helper");
   check(w.self.gems==before&&w.own_score==score&&!w.in_spawn(w.self.pos),"accepted recall is neither departure nor payout nor bank");
   start=w.round;std::printf("%s %d %d %d %d\n",marker,w.self.id,w.round,expected,memory.hold_since);
  };
  if(stage==0){
   memory.mission.group=group;memory.mission.phase=Phase::Collect;
   if(w.groups[group].fresh(w.round)&&w.groups[group].state==Lifecycle::Reward){
    if(!w.on_group(group,w.self.pos))move_to(target);
    if(w.on_group(group,w.self.pos)&&w.self.channel==Channel::None){
     check(memory.hold_since==w.round,"negative case begins with no prior hold interval");
     recall("NATIVE_IMMEDIATE_RECALL_STARTED");immediate_started=true;stage=1;
    }
   }else{
    std::optional<Camp> monster;for(const auto&c:w.groups[group].camps)if(c.hp>0)monster=c;
    if(monster&&w.self.can_attack&&distance(w.self.pos,monster->pos)<=w.self.range){
     Action a;a.kind=Kind::BasicCamp;a.target=monster->id;a.reason="native-cycle-fixture-clear";
     check(execute(w,a).success,"actual camp basic accepted");
    }else move_to({target.x<16?target.x-1:target.x+1,target.y});
   }
  }else if(stage==1){
   if(w.self.channel==Channel::None&&w.in_spawn(w.self.pos)){
    check(immediate_started&&w.round>start&&w.self.gems==0&&w.own_score==0,"early departure forfeits immature single-body capture");
    check(memory.last_recall==w.round,"production observer recognizes actual recall completion");
    std::printf("NATIVE_EARLY_DEPARTURE_NO_PAYOUT %d %d\n",w.self.id,w.round);stage=2;
   }
  }else if(stage==2){
   memory.mission.group=group;memory.mission.phase=Phase::Collect;
   if(!w.on_group(group,w.self.pos))move_to(target);
   if(w.on_group(group,w.self.pos)&&w.self.channel==Channel::None){
    check(w.groups[group].fresh(w.round)&&w.groups[group].state==Lifecycle::Reward,"forfeited reward still awaits a continuous hold");
    const int needed=overlap_hold(bc::constants::capture_time,current_recall_ticks(w.self));
    check(needed>0,"actual capture setup interval must not be omitted");
    if(memory.hold_since>=0&&w.round-memory.hold_since>=needed){
     recall("NATIVE_GUARDED_OVERLAP_STARTED");overlap_started=true;stage=3;
    }
   }
  }else if(stage==3){
   if(w.self.channel==Channel::None&&w.in_spawn(w.self.pos)){
    check(overlap_started&&w.self.gems==g.gems&&w.own_score==0,"continuous guarded overlap pays carried gems before recall departure without banking them");
    check(memory.last_recall==w.round,"production observer recognizes overlap recall completion");
    std::printf("NATIVE_CAPTURE_BEFORE_RECALL_DEPARTURE %d %d %d\n",w.self.id,w.round,w.self.gems);stage=4;
   }
  }else if(stage==4){
   if(distance(w.self.pos,altar)>bc::constants::submit_gems_range)move_to(altar,bc::constants::submit_gems_range);
   if(distance(w.self.pos,altar)<=bc::constants::submit_gems_range){
    bag_before=w.self.gems;score_before=w.own_score;const int expected=current_tribute_ticks(bag_before);
    Action a;a.kind=Kind::Tribute;a.at=altar;a.reason="native-cycle-fixture-bank";
    const auto result=execute(w,a);check(result.success&&result.outcome==Outcome::Started,"actual tribute start accepted");
    w.refresh();check(w.self.channel==Channel::Tribute&&w.self.channel_ticks==expected,"actual tribute duration matches production helper");
    check(w.self.gems==bag_before&&w.own_score==score_before,"accepted tribute start is not completed conversion");
    std::printf("NATIVE_TRIBUTE_STARTED_NOT_BANKED %d %d %d %d\n",w.self.id,w.round,bag_before,expected);
    bank_started=true;start=w.round;stage=5;
   }
  }else if(stage==5&&w.self.channel==Channel::None){
   check(bank_started&&w.round>start&&w.self.gems==0&&w.own_score==score_before+bag_before,"actual later tribute completes bag-to-score conversion");
   check(memory.last_bank==w.round,"production observer recognizes actual tribute completion");
   std::printf("NATIVE_ACTUAL_BANK_COMPLETED %d %d %d\n",w.self.id,w.round,w.own_score);stage=6;
  }
  check(stage==6||w.round<160,"native cycle fixture must reach all phases promptly");
  remember(w,memory);bc::end_turn();
 }
}
