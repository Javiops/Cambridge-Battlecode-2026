// Production farming under explicit World projections; no physical payout claim.
#include "coordinator.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
using namespace tactics;
static void check(bool value,const char*message){if(!value){std::printf("NATIVE_FARM_POLICY_FAIL %s\n",message);std::fflush(stdout);throw std::runtime_error(message);}}
int main(){Geometry geometry;Memory memory;std::unique_ptr<World> world;int stage=0;std::vector<Group> original;
 while(true){
  if(bc::is_draft()){bc::draft::pick(bc::champion_draft::ryth);bc::end_turn();continue;}
  if(stage>=3){bc::end_turn();continue;}
  geometry.initialize();if(!world){world=std::make_unique<World>(geometry,memory);original=geometry.groups;}
  World&w=*world;w.refresh();
  if(stage<3){
   geometry.groups=original;memory={};w.round=100;w.enemies.clear();w.sightings.clear();w.allies.clear();
   w.self.hp=w.self.max_hp=1200;w.self.strength=100;w.self.camp_mitigation=w.self.mitigation=1;w.self.shield=0;w.self.alive=true;w.self.stunned=false;w.self.channel=Channel::None;w.self.can_move=w.self.can_attack=true;w.self.range=1;w.self.move_speed=1;w.self.can_cast=false;w.self.gems=0;w.spells={};
   int gold=-1,elk=-1;
   for(unsigned gi=0;gi<geometry.groups.size();++gi){for(const auto&s:geometry.groups[gi].spawns){if(s.type==3&&gold<0)gold=gi;if(s.type==1&&elk<0)elk=gi;}w.groups[gi].seen=w.round;w.groups[gi].state=Lifecycle::Respawning;w.groups[gi].respawn_ticks=100;w.groups[gi].camps.clear();w.groups[gi].known_dead.clear();}
   check(gold>=0&&elk>=0,"fixture native typed groups");
   auto ready_group=[&](int gi){auto&g=geometry.groups[gi];g.initial_hp=1;g.initial_strength=0;g.gems=22;g.gold=0;w.groups[gi].state=Lifecycle::Alive;Camp c;c.id=g.spawns[0].id;c.pos=g.spawns[0].pos;c.hp=1;c.strength=0;c.range=1;c.awake=false;w.groups[gi].camps={c};};
   ready_group(elk);Pos target=geometry.groups[elk].spawns[0].pos;w.self.pos={target.x-1,target.y};
   if(stage==0){
    ready_group(gold);geometry.groups[gold].gems=10000;memory.mission.group=gold;memory.mission.phase=Phase::Travel;memory.mission.start=90;memory.mission.expiry=200;memory.failed_group=gold;memory.failed_until=120;
    auto result=farming(w,memory);check(result.has_value(),"suppressed incumbent must leave a feasible alternative");check(result->mission.group==elk,"failed incumbent cannot bypass suppression through shortlist/lease preference");check(result->action.kind==Kind::BasicCamp,"alternative ready native camp has immediate productive proposal");
    std::puts("NATIVE_FARM_POLICY_CASE_PASS suppressed-incumbent");
   }else if(stage==1){
    memory.mission.group=elk;memory.mission.phase=Phase::Travel;memory.mission.start=1;memory.mission.expiry=200;memory.mission.last_progress=1;memory.mission.last_camp_hp=-1;
    auto result=farming(w,memory);check(result.has_value(),"first clear arrival cannot be rejected as pre-existing stagnation");check(result->mission.phase==Phase::Clear&&result->action.kind==Kind::BasicCamp,"first actual clear arrival starts a productive clear");check(memory.failed_group!=elk,"travel duration is not failed attack progress");
    std::puts("NATIVE_FARM_POLICY_CASE_PASS first-clear-arrival");
   }else if(stage==2){
    // A ready gem job that cannot finish before the horizon has zero value.
    // It must not replace an unready positive-value gold job solely on readiness.
    w.round=static_cast<int>(bc::constants::max_rounds)-2;
    for(auto&g:w.groups)g.seen=w.round;
    ready_group(gold);geometry.groups[gold].gems=0;geometry.groups[gold].gold=35;
    geometry.groups[gold].initial_hp=100000;geometry.groups[gold].initial_strength=1000;
    geometry.groups[gold].spawns[0].pos=target;
    w.groups[gold].camps[0].pos=target;w.groups[gold].camps[0].hp=100000;w.groups[gold].camps[0].strength=1000;
    const auto positive=evaluate_farm(w,gold),expired=evaluate_farm(w,elk);
    check(positive.rate>0&&!positive.ready,"deadline fixture has positive unready alternative");
    check(expired.rate==0&&expired.ready,"deadline fixture has ready zero-rate gem job");
    auto result=farming(w,memory);
    check(result.has_value()&&result->mission.group==gold,"zero-rate readiness cannot erase positive farm job");
    check(result->mission.phase==Phase::Assemble,"positive unready alternative gets assembly lease");
    std::puts("NATIVE_FARM_POLICY_CASE_PASS deadline-zero-ready");
   }
   ++stage;if(stage==3)std::printf("NATIVE_FARM_POLICY_PASS %d\n",w.self.id);
  }
  bc::end_turn();
 }
}
