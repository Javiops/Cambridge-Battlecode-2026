// Physical native rendezvous: all World data and all executed actions are real.
// Scripted teammate/preparation isolates local readiness from macro strength.
#include "coordinator.h"
#include "actions.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
using namespace tactics;
static void require(bool ok,const char*why){if(!ok){std::printf("NATIVE_ASSEMBLY_FAIL %s\n",why);throw std::runtime_error(why);}}
static bool act(World&w,Action a){auto r=execute(w,a);require(r.success,"actual legal fixture action accepted");return r.success;}
static void walk(World&w,Pos to,int range=0){if(auto p=w.toward(to,range))act(w,moving(*p,"fixture-physical-stage"));}
int main(){Geometry g;Memory m;std::unique_ptr<World> world;int elk=-1,gold=-1,other=-1,stage=0;bool ready_seen=false,first_hit=false,producer=false;double hp_before=-1;
 while(true){try{
  if(bc::is_draft()){bc::draft::pick(bc::draft::current_draft(bc::team::ally).empty()?bc::champion_draft::vendetta:bc::champion_draft::willow);bc::end_turn();continue;}
  if(stage==99){bc::end_turn();continue;}g.initialize();if(!g.initialized){bc::end_turn();continue;}
  if(!world)world=std::make_unique<World>(g,m);World&w=*world;w.refresh();
  if(w.round!=int(bc::round_number())||bc::fuel_remaining()<60000){bc::end_turn();continue;}
  if(elk<0){int de=unreachable,dg=unreachable,do_=unreachable;for(unsigned i=0;i<g.groups.size();++i)for(const auto&s:g.groups[i].spawns){int d=w.home_distance(s.pos);if(s.type==1&&d<de){elk=i;de=d;}if(s.type==3&&d<dg){gold=i;dg=d;}if(s.type==2&&d<do_){other=i;do_=d;}}require(elk>=0&&gold>=0&&other>=0,"real public fixture groups");}
  const Pos e=g.groups[elk].spawns.front().pos,prep=g.groups[gold].spawns.front().pos;
  const bool left=e.x<16;const int sign=left?-1:1;
  const Pos helper_stage{e.x+2*sign,e.y-1},request_stage{e.x+2*sign,e.y},home=left?Pos{3,3}:Pos{28,3};
  const bool healer=w.self.type==8;require(w.self.alive,"fixture keeps actual bodies alive");
  if(healer){
   w.publish_claim(elk);
   if(w.self.pos!=helper_stage){walk(w,helper_stage);bc::end_turn();continue;}
   if(!ready_seen){std::printf("NATIVE_ASSEMBLY_CASE_PASS physical-helper-stage %d %d %d\n",w.self.id,w.self.pos.x,w.self.pos.y);ready_seen=true;}
   const Actor*target=nullptr;for(const auto&a:w.allies)if(a.type==2&&a.alive)target=&a;
   bool healed=false;if(target&&target->hp<target->max_hp-100)for(const auto&s:w.spells)if(s.ready&&s.kind==5&&s.allies&&distance(w.self.pos,target->pos)<=s.range){Action a;a.kind=Kind::CastChampion;a.target=target->id;a.slot=s.slot;a.reason="fixture-real-team-heal";act(w,a);healed=true;break;}
   if(!healed&&w.groups[elk].fresh(w.round))for(const auto&c:w.groups[elk].camps)if(c.awake&&c.hp>0&&w.self.can_attack&&distance(w.self.pos,c.pos)<=w.self.range){Action a;a.kind=Kind::BasicCamp;a.target=c.id;a.reason="fixture-real-helper-damage";act(w,a);break;}
   bc::end_turn();continue;
  }
  if(stage==0){
   const int count=int(w.me.item_count()[bc::item_type::monster_shard_of_health]);
   if(count<1&&w.gold>=30&&w.in_spawn(w.self.pos)){Action a;a.kind=Kind::Buy;a.item=4;a.reason="fixture-real-health-precondition";act(w,a);bc::end_turn();continue;}
   if(count>=1&&w.self.hp>=w.self.max_hp){stage=1;std::printf("NATIVE_ASSEMBLY_CASE_PASS real-upgrade-healed %d %.0f\n",w.self.id,w.self.hp);}
   else if(count>=1||w.gold>=30-30*count){walk(w,home);bc::end_turn();continue;}
   else{
    if(w.groups[gold].fresh(w.round)&&w.groups[gold].state==Lifecycle::Reward){walk(w,prep);}
    else{bool attacked=false;for(const auto&c:w.groups[gold].camps)if(c.hp>0&&w.self.can_attack&&distance(w.self.pos,c.pos)<=w.self.range){Action a;a.kind=Kind::BasicCamp;a.target=c.id;a.reason="fixture-real-preparation-clear";act(w,a);attacked=true;break;}if(!attacked)walk(w,prep,w.self.range);}
    bc::end_turn();continue;
   }
  }
  w.publish_claim(elk);
  if(stage==1){if(w.self.pos!=request_stage){walk(w,request_stage);bc::end_turn();continue;}stage=2;}
  // Complete immutable public fields before a fresh native observation/planner.
  bool fields=true;for(const Pos p:{e,g.groups[other].spawns.front().pos})if(!g.goal_cache.contains({g.index(p),0})){g.goal_field(p,0);fields=false;break;}if(!fields){bc::end_turn();continue;}
  if(stage==2){
   const auto other_job=evaluate_farm(w,other);m.mission={};m.mission.group=other;m.mission.phase=Phase::Travel;m.mission.target=g.groups[other].spawns.front().pos;m.mission.rate=other_job.rate;m.mission.start=w.round;m.mission.expiry=w.round+10;m.mission.last_progress=w.round;
   std::printf("NATIVE_ASSEMBLY_DETAIL actual-alternative rate=%.5f ready=%d fuel=%u\n",other_job.rate,other_job.ready,unsigned(bc::fuel_remaining()));
   stage=20;bc::end_turn();continue;
  }
  if(stage==20){
   if(bc::fuel_remaining()>=65000){auto q=local_assembly_candidate(w,m,elk,std::max(.001,m.mission.rate));if(q){
    producer=true;std::printf("NATIVE_ASSEMBLY_CASE_PASS physical-priced-producer %d %.5f\n",w.self.id,q->rate);
    Mission job;job.phase=Phase::Assemble;job.group=q->group;job.target=q->target;job.start=q->start;job.expiry=q->expiry;job.last_progress=w.round;job.last_pos=w.self.pos;job.rate=q->rate;job.assembly_pending=true;job.assembly_signature=q->signature;job.assembly_anchor=q->anchor_id;job.assembly_helper=q->helper_id;job.assembly_route=q->route;job.assembly_route_length=q->route_length;
    if(auto p=assembly_step(w,job)){act(w,moving(*p,"fixture-actual-priced-rally"));m.mission=job;std::printf("NATIVE_ASSEMBLY_CASE_PASS actual-priced-rally-move %d %d %d\n",w.self.id,p->x,p->y);}
   }}
   // A declined price is recorded, never converted into fictional acceptance.
   stage=3;bc::end_turn();continue;
  }
  if(stage==3){if(distance(w.self.pos,e)>w.self.range){walk(w,e,w.self.range);bc::end_turn();continue;}stage=4;}
  if(stage==4){
   const auto before=bc::fuel_remaining();auto ready=propose_local_assignment(w,elk);const auto after=bc::fuel_remaining();
   if(!ready.ready||!ready.self_selected||!ready.locally_accepted){std::printf("NATIVE_ASSEMBLY_WAIT ready=%d uncertain=%d fuel=%u,%u round=%d\n",ready.ready,ready.uncertain,unsigned(before),unsigned(after),w.round);bc::end_turn();continue;}
   std::printf("NATIVE_ASSEMBLY_CASE_PASS actual-claimed-pair-ready %d %u %u\n",w.self.id,unsigned(before),unsigned(after));
   require(w.groups[elk].fresh(w.round)&&!w.groups[elk].camps.empty(),"fresh personally observed monster");const auto&c=w.groups[elk].camps.front();hp_before=c.hp;Action a;a.kind=Kind::BasicCamp;a.target=c.id;a.reason="fixture-production-ready-first-hit";act(w,a);first_hit=true;stage=5;
   std::printf("NATIVE_ASSEMBLY_CASE_PASS actual-first-hit %d %.0f\n",w.self.id,hp_before);bc::end_turn();continue;
  }
  if(stage==5){
   if(w.groups[elk].fresh(w.round)&&w.groups[elk].state==Lifecycle::Reward){stage=6;std::printf("NATIVE_ASSEMBLY_CASE_PASS actual-clear %d\n",w.self.id);}
   else{bool attacked=false;for(const auto&c:w.groups[elk].camps)if(c.hp>0&&w.self.can_attack&&distance(w.self.pos,c.pos)<=w.self.range){Action a;a.kind=Kind::BasicCamp;a.target=c.id;a.reason="fixture-real-continuing-clear";act(w,a);attacked=true;break;}require(attacked,"clear retains actual visible legal target");bc::end_turn();continue;}
  }
  if(stage==6){if(w.on_group(elk,w.self.pos)&&w.self.gems>=g.groups[elk].gems){require(first_hit,"capture follows actual first hit");std::printf("NATIVE_ASSEMBLY_CASE_PASS actual-capture-payout %d %d\n",w.self.id,w.self.gems);std::printf("NATIVE_ASSEMBLY_PASS %d producer=%d\n",w.self.id,producer);stage=99;}else walk(w,e);}
  bc::end_turn();
 }catch(const std::exception&e){std::printf("NATIVE_ASSEMBLY_FAIL exception=%s\n",e.what());stage=99;bc::end_turn();}}
}

