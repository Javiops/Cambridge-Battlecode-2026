// Actual production choose_mission under the initialized official SDK.
// Explicit policy projections: HP, bag, visible threats and mission are input
// cases, not native earned resources. No projected action is submitted.
#include "coordinator.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
using namespace tactics;
static void require(bool ok,const char* message){if(!ok){std::printf("SURVIVAL_FAIL %s\n",message);std::fflush(stdout);throw std::runtime_error(message);}}
static void setup(World&w,Memory&m,Pos p){
 const int id=w.self.id;m={};w.self={};w.self.id=id;w.self.type=77;
 w.self.pos=p;w.self.hp=100;w.self.max_hp=1000;w.self.strength=30;
 w.self.focus=0;w.self.range=1;w.self.move_speed=1;
 w.self.mitigation=w.self.camp_mitigation=1;
 w.self.alive=w.self.can_move=w.self.can_attack=true;
 w.self.can_cast=w.self.stunned=false;w.self.channel=Channel::None;w.self.gems=24;
 w.spells={};w.enemies.clear();w.sightings.clear();w.allies={w.self};
 w.own_score=w.enemy_score=0;w.occupied.clear();
 w.occupied_bytes.assign((w.geo.width*w.geo.height+7)/8,0);
 w.visible_bytes.assign(w.occupied_bytes.size(),255);
 for(auto&g:w.groups){g.seen=w.round;g.state=Lifecycle::Respawning;g.respawn_ticks=100;g.camps.clear();g.known_dead.clear();}
 m.mission.phase=Phase::Deliver;m.mission.group=-1;m.mission.target=w.geo.altars.front();
 m.mission.start=w.round-2;m.mission.expiry=w.round+6;
 w.combat_damage_cache.clear();++w.serial;
}
static void threat(World&w,Pos p){
 Actor e;e.id=99;e.type=77;e.pos=p;e.hp=e.max_hp=1000;e.strength=200;
 e.range=1;e.move_speed=1;e.alive=e.can_move=e.can_attack=true;
 e.mitigation=e.camp_mitigation=1;w.enemies={e};
}
static void burn(unsigned remaining){volatile unsigned sink=1;while(bc::fuel_remaining()>remaining)for(int i=0;i<8;++i)sink=sink*1664525u+i;}
int main(){Geometry geo;Memory memory;std::unique_ptr<World> world;int stage=0;
 while(true){
  if(bc::is_draft()){bc::draft::pick(bc::champion_draft::ren);bc::end_turn();continue;}
  if(stage>=16){bc::end_turn();continue;} require(bc::round_number()<80,"all projected cases must activate before watchdog");
  geo.initialize();if(!geo.initialized){bc::end_turn();continue;}
  if(stage==7){
   const Pos actual=position(bc::self().position());int gi=0;
   for(unsigned i=1;i<geo.groups.size();++i)
    if(distance(actual,geo.groups[i].spawns.front().pos)<distance(actual,geo.groups[gi].spawns.front().pos))gi=i;
   const Pos target=geo.groups[gi].spawns.front().pos;geo.goal_field(target,0);
   if(geo.goal_cache.contains({geo.index(target),0}))stage=8;
   bc::end_turn();continue;
  }
  if(!world)world=std::make_unique<World>(geo,memory);auto&w=*world;w.refresh();
  if(w.round!=int(bc::round_number())||bc::fuel_remaining()<60000){bc::end_turn();continue;}
  const Pos altar=geo.altars.front();const int owner=w.self.id;
  Pos p{altar.x-3,altar.y-3};setup(w,memory,p);
  unsigned budget=stage==1?51000:47000;
  if(stage<=1){threat(w,{p.x+2,p.y});}
  else if(stage==2||stage==3){
   w.self.pos={altar.x,altar.y-1};w.allies={w.self};w.visible.set(sdk(altar));
   if(stage==3)w.own_score=990;
  }else if(stage==4){
   w.self.pos={altar.x,altar.y-1};w.allies={w.self};w.visible.set(sdk(altar));
   threat(w,{altar.x,altar.y-3});
  }else if(stage==5){
   w.self.pos=position(w.me.position());w.allies={w.self};w.self.gems=0;
  }else if(stage==6){
   // A real reward holder keeps the collection contract instead of the
   // non-holder health shortcut. Native capture timing is tested separately.
   w.self.pos=geo.groups.front().spawns.front().pos;w.allies={w.self};w.self.gems=0;
   memory.hold_group=0;memory.hold_since=w.round;memory.hold_last=w.round;
   memory.mission.phase=Phase::Collect;memory.mission.group=0;
   memory.mission.target=w.self.pos;memory.mission.start=w.round;
   w.groups.front().state=Lifecycle::Reward;budget=65000;
  }
  else if(stage==8){
   const Pos actual=position(w.me.position());int gi=0;
   for(unsigned i=1;i<geo.groups.size();++i)
    if(distance(actual,geo.groups[i].spawns.front().pos)<distance(actual,geo.groups[gi].spawns.front().pos))gi=i;
   const auto spawn=geo.groups[gi].spawns.front();
   w.self.pos={spawn.pos.x+(actual.x>spawn.pos.x?1:-1),spawn.pos.y};w.self.hp=400;w.self.gems=0;w.allies={w.self};
   auto&g=geo.groups[gi];g.gems=22;g.initial_hp=10;g.initial_strength=0;
   Camp camp;camp.id=spawn.id;camp.group=gi;camp.type=0;camp.pos=spawn.pos;
   camp.hp=camp.max_hp=10;camp.strength=0;camp.range=1;camp.awake=false;
   auto&view=w.groups[gi];view.state=Lifecycle::Alive;view.camps={camp};view.known_dead.clear();
   memory.mission.phase=Phase::Clear;memory.mission.group=gi;memory.mission.target=spawn.pos;
   memory.mission.start=w.round;memory.mission.expiry=w.round+6;budget=65000;
  }
  else if(stage>=9&&stage<=12){
   // Healthy owners must still fund a real defense before distant banking
   // when the actual next enemy reply is lethal. Holder status does not
   // require sacrificing the body before its pending capture completes.
   w.self.hp=950;w.self.gems=24;
   if(stage>=11){
    w.self.pos=geo.groups.front().spawns.front().pos;
    memory.hold_group=0;memory.hold_since=w.round;memory.hold_last=w.round;
    memory.mission.phase=Phase::Collect;memory.mission.group=0;
    memory.mission.target=w.self.pos;memory.mission.start=w.round;
    w.groups.front().state=Lifecycle::Reward;
   }
   w.allies={w.self};threat(w,{w.self.pos.x+2,w.self.pos.y});
   w.enemies.front().strength=2000;budget=(stage==10||stage==12)?51000:47000;
  }
  else if(stage==13){
   w.self.hp=950;w.self.gems=0;w.self.mitigation=.1;
   w.self.pos=geo.groups.front().spawns.front().pos;
   w.self.can_move=w.self.can_attack=false;w.allies={w.self};
   memory.hold_group=0;memory.hold_since=w.round;memory.hold_last=w.round;
   memory.mission.phase=Phase::Collect;memory.mission.group=0;
   memory.mission.target=w.self.pos;memory.mission.start=w.round;
   w.groups.front().state=Lifecycle::Reward;
   threat(w,{w.self.pos.x+2,w.self.pos.y});w.enemies.front().strength=1200;budget=65000;
  }
  else if(stage==14||stage==15){
   // Exact incoming damage already subtracts this actual-input shield:
   //1100 raw -200 shield ==900 HP loss, lethal at900 current HP.
   // Comparing that900 against HP+shield would incorrectly enter delivery.
   w.self.hp=900;w.self.shield=200;w.self.shield_ticks=1;w.self.gems=24;
   w.allies={w.self};threat(w,{w.self.pos.x+2,w.self.pos.y});
   w.enemies.front().strength=1100;budget=stage==15?51000:47000;
  }
  burn(budget);const unsigned start=bc::fuel_remaining();const int round=w.round;
  auto chosen=choose_mission(w,memory);const unsigned end=bc::fuel_remaining();
  std::printf("SURVIVAL_CASE %d %d %d %u %u epoch=%d,%d action=%d phase=%d\n",owner,stage,round,start,end,round,int(bc::round_number()),chosen?int(chosen->action.kind):-1,chosen?int(chosen->mission.phase):-1);
  require(round==int(bc::round_number()),"choose must not exhaust/resume a different owner epoch");
  require(chosen.has_value(),"required response is returned from the actual coordinator");
  require(end>=12000,"actual execution/owner-end reserve remains");
  if(stage<=1)require(chosen->action.kind==Kind::Move&&chosen->priority==Priority::Survival,"funded threatened carrier has a real defense before elective delivery");
  else if(stage==2)require(chosen->action.kind==Kind::Tribute,"safe immediate bank remains available below ordinary HP");
  else if(stage==3)require(chosen->action.kind==Kind::Tribute&&chosen->priority==Priority::Deciding,"safe deciding bag retains bank priority");
  else if(stage==4)require(chosen->action.kind!=Kind::Tribute&&chosen->priority==Priority::Survival,"adjacency alone never proves unsafe bank");
  else if(stage==5)require(chosen->mission.phase==Phase::Recover&&chosen->action.kind==Kind::None,"spawn heal is retained");
  else if(stage==6)require(chosen->mission.phase==Phase::Collect,"live capture holder is not emptied by ordinary healing");
  else if(stage==8)require(chosen->mission.phase==Phase::Clear&&chosen->action.kind==Kind::BasicCamp,"paid current fixed-position singleton clear is preserved");
  else if(stage>=9&&stage<=12)require(chosen->action.kind==Kind::Move&&chosen->priority==Priority::Survival,"healthy lethal-contact owner receives a funded real defense before delivery or capture");
  else if(stage==13)require(chosen->mission.phase==Phase::Collect,"mitigated non-lethal raw warning does not force a healthy holder to leave");
  else if(stage==14||stage==15)require(chosen->action.kind==Kind::Move&&chosen->priority==Priority::Survival,"post-shield lethal HP loss receives funded survival before delivery");
  std::printf("SURVIVAL_CASE_PASS %d %d\n",owner,stage);++stage;bc::end_turn();
 }
}
