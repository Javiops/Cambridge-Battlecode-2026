#include "actions.h"
#include "vision.h"
#include <cstdio>
#include <memory>
using namespace tactics;
int main(){Geometry geometry;Memory memory;WardState state;std::unique_ptr<World> world;bool done=false;
 while(true){
  if(bc::is_draft()){bc::draft::pick(bc::champion_draft::ryth);bc::end_turn();continue;}
  geometry.initialize();if(!geometry.initialized){bc::end_turn();continue;}if(!world)world=std::make_unique<World>(geometry,memory);World&w=*world;w.refresh();
  if(!done&&w.self.alive){
   Mission mission;mission.phase=Phase::Travel;mission.target={15,15};
   geometry.goal_field(mission.target,0);
   if(bc::fuel_remaining()<65000){bc::end_turn();continue;}
   if(auto ward=ward_proposal(w,mission,state)){
    auto result=execute(w,*ward);if(!result.success)throw std::runtime_error("native ward rejected");
    w.refresh();ward_after_action(w,*ward,true,state);
    bool found=false;for(auto p:w.me.ward_positions())found|=position(p)==ward->at;
    if(!found||w.me.ward_cooldown()<=0)throw std::runtime_error("native ward state absent");
    std::printf("NATIVE_WARD_POLICY_PASS %d %d %d %d\n",w.self.id,w.round,ward->at.x,ward->at.y);done=true;
   }else if(auto step=w.toward(mission.target)){Action a;a.kind=Kind::Move;a.at=*step;a.reason="fixture-ward-approach";execute(w,a);}
  }
  bc::end_turn();
 }
}
