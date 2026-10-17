// Explicit policy projections under initialized official SDK. No projected
// action is executed; actual payout is covered by the separate cycle fixture.
#include "coordinator.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
using namespace tactics;
static void check(bool value,const char*message){if(!value){std::printf("NATIVE_BANK_FAIL %s\n",message);std::fflush(stdout);throw std::runtime_error(message);}}
static void project(World&w,Actor body){
 w.self=body;w.self.type=77;w.self.hp=w.self.max_hp=1000;w.self.strength=30;w.self.focus=0;
 w.self.mitigation=w.self.camp_mitigation=1;w.self.move_speed=1;w.self.range=1;
 w.self.alive=w.self.can_move=true;w.self.can_attack=w.self.can_cast=w.self.stunned=false;
 w.self.channel=Channel::None;w.self.gems=22;w.self.spells={};w.spells={};
 w.own_score=w.enemy_score=0;w.enemies.clear();w.sightings.clear();w.allies={w.self};
 w.visible_bytes.assign((w.geo.width*w.geo.height+7)/8,255);
 w.occupied_bytes.assign(w.visible_bytes.size(),0);w.occupied.clear();
 for(auto&g:w.groups){g.seen=w.round;g.state=Lifecycle::Respawning;g.respawn_ticks=100;g.camps.clear();}
 ++w.serial;
}
int main(){Geometry geo;Memory memory;std::unique_ptr<World>world;int stage=0;
 while(true){
  if(bc::is_draft()){bc::draft::pick(bc::champion_draft::ren);bc::end_turn();continue;}
  if(stage>=7){bc::end_turn();continue;}geo.initialize();if(!geo.initialized){bc::end_turn();continue;}
  if(world&&stage==5){
   // Fixture-only registry construction is sliced before the timed policy
   // sample. Copying128 nested vectors in one owner budget is not a policy call.
   auto&w=*world;
   if(geo.groups.capacity()<128)geo.groups.reserve(128);
   if(w.groups.capacity()<128)w.groups.reserve(128);
   while(geo.groups.size()<128&&bc::fuel_remaining()>80000){
    const unsigned i=geo.groups.size();Group g=geo.groups.front();g.spawns[0].pos={int(i%20)+5,int(i/20)+5};
    geo.groups.push_back(std::move(g));w.groups.emplace_back();
   }
   if(geo.groups.size()==128)stage=6;
   bc::end_turn();continue;
  }
  if(world&&stage==6){
   auto&w=*world;w.round=bc::round_number();memory={};
   for(auto&v:w.groups){v.state=Lifecycle::Alive;v.seen=w.round;}
   volatile unsigned sink=7;while(bc::fuel_remaining()>65000)for(int i=0;i<16;++i)sink=sink*1664525u+i;
   const auto before=bc::fuel_remaining();auto plans=altar_plans(w);const auto after=bc::fuel_remaining();
   std::printf("NATIVE_BANK_COST %d %u %u epoch=%d,%d\n",w.self.id,unsigned(before),unsigned(after),w.round,int(bc::round_number()));
   check(w.round==int(bc::round_number())&&after>30000&&before-after<12000,"128-job bank quote at65k remains bounded and preserves actual action budget");
   std::printf("NATIVE_BANK_CASE_PASS bounded-cost %d %u %u %u\n",w.self.id,unsigned(before),unsigned(after),unsigned(sink));
   std::printf("NATIVE_BANK_PASS %d\n",w.self.id);stage=7;bc::end_turn();continue;
  }
  if(!world)world=std::make_unique<World>(geo,memory);World&w=*world;w.refresh();
  if(w.round!=int(bc::round_number())||bc::fuel_remaining()<80000){bc::end_turn();continue;}
  check(geo.altars.size()>=2,"actual map has two independent altar choices");
  const Pos altar=geo.altars.front();const Actor actual=w.self;project(w,actual);
  if(stage==0){
   memory={};w.self.pos={altar.x,altar.y-1};w.self.hp=600;
   memory.mission.phase=Phase::Deliver;memory.mission.target=altar;
   Camp c;c.pos={altar.x-1,altar.y-1};c.hp=c.max_hp=100;c.strength=250;c.range=1;c.awake=true;
   w.groups.front().state=Lifecycle::Alive;w.groups.front().camps={c};
   const auto chosen=choose_mission(w,memory);
   check(chosen&&chosen->mission.phase==Phase::Deliver&&chosen->action.kind==Kind::Move,"actual coordinator retains committed safe ring relocation priority");
   check(distance(chosen->action.at,altar)<=bc::constants::submit_gems_range&&distance(chosen->action.at,c.pos)>c.range,"chosen ring step leaves current lethal camp footprint");
   check(w.self.pos==Pos{altar.x,altar.y-1},"forecast never mutates owner position");
   std::printf("NATIVE_BANK_CASE_PASS ring-coordinator %d %d %d\n",actual.id,chosen->action.at.x,chosen->action.at.y);
  }else if(stage==1){
   memory={};w.self.pos={altar.x-2,altar.y-2};w.self.hp=100;
   memory.mission.phase=Phase::Deliver;memory.mission.target=altar;
   const auto chosen=choose_mission(w,memory);
   check(chosen&&chosen->mission.phase==Phase::Recover,"necessary recovery actually wins current arbitration");
   check(memory.failed_bank_altar==0&&memory.failed_bank_until>w.round&&memory.failed_bank_window==w.self.pos,"real recovery-selection hook records finite bank failure");
   memory.mission=chosen->mission;
   std::printf("NATIVE_BANK_CASE_PASS recovery-hook %d\n",actual.id);
  }else if(stage==2){
   w.self.pos=position(w.me.position());w.visible_bytes.assign(w.visible_bytes.size(),0);
   check(failed_bank_window_active(w,0),"healed recalled projection cannot erase distant failure with empty local vision");
   auto bank=delivery(w,memory);
   check(bank&&bank->mission.bank_altar!=0,"bounded bank replan considers another actual altar");
   std::printf("NATIVE_BANK_CASE_PASS healed-backoff %d\n",actual.id);
  }else if(stage==3){
   memory={};memory.mission.phase=Phase::Channel;memory.mission.bank_reentry_group=0;
   memory.mission.bank_reentry_target=geo.groups[0].spawns[0].pos;memory.mission.bank_reentry_rate=1;
   memory.prior_channel=Channel::Tribute;memory.prior_alive=true;memory.last_gems=22;
   memory.observed_round=w.round-1;w.self.channel=Channel::Tribute;w.self.channel_ticks=1;
   observe_progress(w,memory);
   check(memory.mission.phase==Phase::Channel&&memory.mission.bank_reentry_group==0,"accepted active bank start retains future job without entering it");
   std::printf("NATIVE_BANK_CASE_PASS accepted-start-not-complete %d\n",actual.id);
  }else if(stage==4){
   memory.prior_channel=Channel::Tribute;memory.prior_alive=true;memory.last_gems=22;
   memory.observed_round=w.round-1;w.self.gems=0;w.groups[0].state=Lifecycle::Alive;
   observe_progress(w,memory);
   check(memory.mission.phase==Phase::Reenter&&memory.mission.group==0&&memory.mission.expiry==w.round+Settings::job_lease,"observed completed-bank input enters finite named reentry");
   std::printf("NATIVE_BANK_CASE_PASS completed-bank-reentry %d\n",actual.id);
  }
  ++stage;bc::end_turn();
 }
}
