#define main retained_production_entry
#include "production_main.inc"
#undef main
#include <cstdio>
using namespace tactics;
int main(){
 Bot autonomous;Geometry prelude_geometry;Memory prelude_memory;std::unique_ptr<World> prelude;
 bool handed=false;int group=-1;
 while(true){try{
  if(bc::is_draft())bc::draft::pick(bc::champion_draft::vendetta);
  else if(handed)autonomous.turn();
  else{
   prelude_geometry.initialize();if(!prelude_geometry.initialized){bc::end_turn();continue;}
   if(group<0){for(int gi=0;gi<int(prelude_geometry.groups.size());++gi)
      if(prelude_geometry.groups[gi].spawns.size()==1&&prelude_geometry.groups[gi].spawns[0].pos==Pos{5,12})group=gi;
      if(group<0)throw std::runtime_error("prelude group unavailable");}
   if(!prelude_geometry.goal_field({5,12},0)){bc::end_turn();continue;}
   if(!prelude)prelude=std::make_unique<World>(prelude_geometry,prelude_memory);
   auto&w=*prelude;w.refresh();
   if(w.self.gems>=24){std::printf("CHAIN_LAWFUL_HANDOFF %d %d %d %d %.2f %d\n",w.round,w.self.id,w.self.pos.x,w.self.pos.y,w.self.hp,w.self.gems);handed=true;}
   else if(w.groups[group].fresh(w.round)&&w.groups[group].state==Lifecycle::Reward){
      if(w.self.pos!=Pos{5,12})if(auto p=w.toward({5,12})){Action a=moving(*p,"fixture-prelude-capture");execute(w,a);}}
   else if(w.groups[group].fresh(w.round)&&!w.groups[group].camps.empty()&&distance(w.self.pos,Pos{5,12})<=w.self.range){
      if(w.self.can_attack){Action a;a.kind=Kind::BasicCamp;a.target=w.groups[group].camps.front().id;a.reason="fixture-prelude-first-resource";execute(w,a);}}
   else if(auto p=w.toward({5,12},w.self.range)){Action a=moving(*p,"fixture-prelude-walk");execute(w,a);}
  }
 }catch(const std::exception&e){std::printf("CHAIN_FIXTURE_ERROR %s\n",e.what());}
 bc::end_turn();}
}
