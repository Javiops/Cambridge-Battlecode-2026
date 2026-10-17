#include "coordinator.h"
#include "actions.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
using namespace tactics;
static void need(bool v,const char* why){if(!v){std::printf("EARLY_SOLO_FAIL %s\n",why);std::fflush(stdout);throw std::runtime_error(why);}}
int main(){
 Geometry geo; Memory memory; std::unique_ptr<World> world; int gi=-1,phase=0;
 while(true){
  if(bc::is_draft()){
   auto old=bc::draft::current_draft(bc::team::ally);
   for(auto p:{bc::champion_draft::cassi_and_issac,bc::champion_draft::varg,bc::champion_draft::ryth,bc::champion_draft::vendetta,bc::champion_draft::tavi})
    if(std::find(old.begin(),old.end(),p)==old.end()){bc::draft::pick(p);break;}
  }else if(phase<3){
   geo.initialize();if(!geo.initialized){bc::end_turn();continue;}
   if(gi<0){int best=unreachable;for(int i=0;i<int(geo.groups.size());++i){auto&g=geo.groups[i];if(g.spawns.size()==1&&g.initial_hp==1350&&g.initial_strength==20&&g.gems>0){int d=geo.at(geo.home,g.spawns[0].pos);if(d<best){best=d;gi=i;}}}need(gi>=0,"singleton-Wolf");}
   Pos at=geo.groups[gi].spawns[0].pos;
   if(!geo.goal_field(at,0)){bc::end_turn();continue;}
   if(!world)world=std::make_unique<World>(geo,memory);
   auto&w=*world;w.refresh();if(w.self.type!=4){phase=3;bc::end_turn();continue;}
   if(distance(w.self.pos,at)>w.self.range){if(auto p=w.toward(at,w.self.range)){need(bc::fuel_remaining()>16000,"walk-reserve");need(w.me.move_absolute(sdk(*p)),"actual-walk");}}
   else {
    need(w.self.hp==900&&w.self.strength==40,"actual-Issac-900-40");need(w.groups[gi].fresh(w.round)&&w.groups[gi].camps.size()==1,"fresh-Wolf");
    need(w.groups[gi].camps[0].hp==1350,"actual-Wolf-1350");
    memory.mission={};memory.mission.group=gi;memory.mission.phase=Phase::Travel;memory.mission.expiry=w.round-1;memory.mission.target=at;
    while(bc::fuel_remaining()>62000){}
    const auto before=bc::fuel_remaining();
    if(phase==0){
     auto field=geo.goal_cache.extract({geo.index(at),0});auto route=geo.route_cache.extract(geo.index(at));
     auto q=quote_solo_farm(w,gi);need(q.known&&q.feasible&&q.ready_now,"cold-local-route-complete");
     need(geo.goal_cache.find({geo.index(at),0})==geo.goal_cache.end()&&geo.route_cache.find(geo.index(at))==geo.route_cache.end(),"no-partial-cache-insertion");
     need(bc::fuel_remaining()>32000,"cold-proposal-floor");
     geo.goal_cache.insert(std::move(field));geo.route_cache.insert(std::move(route));
     std::printf("EARLY_SOLO_CASE cold-route %d %u %u\n",w.self.id,unsigned(before),unsigned(bc::fuel_remaining()));phase=1;
    }else if(phase==1){
     auto q=quote_solo_farm(w,gi);need(q.known&&q.feasible&&q.ready_now,"warm-62k-quote");need(q.remaining_hp>225&&q.rate>0&&q.total_ticks>q.clear_ticks,"finite-completed-cycle");
     auto p=solo_farm_proposal(w,memory,q);need(p&&p->action.kind==Kind::BasicCamp&&p->solo_clear_certified,"common-ready-builder");
     auto stale=q;++stale.serial;need(!solo_farm_proposal(w,memory,stale),"stale-quote-rejected");
     std::printf("EARLY_SOLO_CASE warm-quote %d %u %u %.0f %.0f\n",w.self.id,unsigned(before),unsigned(bc::fuel_remaining()),q.clear_ticks,q.remaining_hp);phase=2;
    }else{
     need(early_solo_eligible(w.self,memory.mission,w.round,false,false,false),"expired-travel-eligible");
     auto p=early_solo_proposal(w,memory);need(p&&p->mission.group==gi&&p->action.kind==Kind::BasicCamp,"early-real-SOLO-firsthit");
     need(bc::fuel_remaining()>16000,"gateway-reserve");
     std::printf("EARLY_SOLO_CASE early-proposal %d %u %u\n",w.self.id,unsigned(before),unsigned(bc::fuel_remaining()));
     std::printf("EARLY_SOLO_PASS %d\n",w.self.id);phase=3;
    }
   }
  }
  bc::end_turn();
 }
}
