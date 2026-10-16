// Production assembly producer and consumer with explicit finite World
// projections under initialized SDK. Projected actions are never executed.
#include "coordinator.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
using namespace tactics;
static void check(bool ok,const char*name){if(!ok){std::printf("NATIVE_ASSEMBLY_BUDGET_FAIL %s\n",name);std::fflush(stdout);throw std::runtime_error(name);}}
static void drain(unsigned target){volatile unsigned n=7;while(bc::fuel_remaining()>target)for(int k=0;k<16;++k)n=n*1664525u+k;}
int main(){Geometry geo;Memory m;std::unique_ptr<World>world;int stage=0,elk=-1,gold=-1,helper=-1;Mission pending;
 while(true){
  if(bc::is_draft()){bc::draft::pick(bc::champion_draft::cassi_and_issac);bc::end_turn();continue;}
  if(stage>=10){bc::end_turn();continue;}geo.initialize();if(!geo.initialized){bc::end_turn();continue;}
  if(!world){world=std::make_unique<World>(geo,m);for(unsigned i=0;i<geo.groups.size();++i)for(const auto&s:geo.groups[i].spawns){if(s.type==1&&geo.groups[i].spawns.size()==1&&elk<0)elk=i;if(s.type==3&&gold<0)gold=i;}for(const auto&c:world->ally_handles)if(identity(c)!=identity(world->me))helper=identity(c);check(elk>=0&&gold>=0&&helper>=0,"actual typed groups and two public allied handles");world->self.id=identity(world->me);}
  World&w=*world;const Pos target=geo.groups[elk].spawns[0].pos,other=geo.groups[gold].spawns[0].pos;
  if(!geo.goal_cache.contains({geo.index(target),0})){geo.goal_field(target,0);bc::end_turn();continue;}
  if(!geo.goal_cache.contains({geo.index(other),0})){geo.goal_field(other,0);bc::end_turn();continue;}
  // All following actor/claim inputs are explicit fixture projections. The
  // actual SDK bodies remain stationary/alive, with no gameplay mutations.
  // Start these samples on a fresh clock rather than charge an unnecessary
  // linked-roster snapshot against the chosen65k/80k controlled entry budget.
  if(bc::fuel_remaining()<90000){bc::end_turn();continue;}
  w.round=bc::round_number();++w.serial;
  m={};w.self.type=2;w.self.hp=w.self.max_hp=150;w.self.strength=30;w.self.focus=0;
  w.self.mitigation=w.self.camp_mitigation=1;w.self.shield=0;w.self.alive=true;
  w.self.stunned=w.self.completed=w.self.enhanced=false;w.self.channel=Channel::None;
  w.self.can_move=w.self.can_attack=w.self.can_cast=true;w.self.range=1;w.self.move_speed=1;w.self.gems=0;
  w.self.spells={};auto&reset=w.self.spells[0];reset.kind=1;reset.slot=0;reset.self=true;reset.ready=true;reset.cooldown=0;reset.recharge=8;
  auto&dash=w.self.spells[1];dash.kind=6;dash.slot=1;dash.ground=true;dash.ready=true;dash.cooldown=0;dash.recharge=9;dash.range=2;w.spells=w.self.spells;
  w.self.pos={target.x-2,target.y};Actor ally=w.self;ally.id=helper;ally.pos={target.x+1,target.y};ally.hp=ally.max_hp=350;ally.strength=60;
  w.allies={w.self,ally};w.enemies.clear();w.sightings.clear();w.own_score=w.enemy_score=0;w.claims={};
  w.visible_bytes.assign((geo.width*geo.height+7)/8,255);w.occupied_bytes.assign(w.visible_bytes.size(),0);
  auto occupy=[&](Pos p,bool value){auto i=geo.index(p);if(value)w.occupied_bytes[i/8]|=1u<<(i%8);else w.occupied_bytes[i/8]&=~(1u<<(i%8));};for(const auto&a:w.allies)occupy(a.pos,true);
  for(auto&v:w.groups){v.seen=w.round;v.state=Lifecycle::Respawning;v.respawn_ticks=100;v.camps.clear();v.known_dead.clear();}
  auto&g=geo.groups[elk];g.gems=500;g.gold=1000;g.initial_hp=240;g.initial_strength=60;
  auto&v=w.groups[elk];v.state=Lifecycle::Alive;Camp c;c.id=g.spawns[0].id;c.pos=target;c.hp=c.max_hp=240;c.strength=60;c.range=1;c.awake=false;v.camps={c};
  geo.groups[gold].gems=1;geo.groups[gold].gold=0;w.groups[gold].state=Lifecycle::Reward;
  ClaimBytes claims{};for(int i=0;i<w.ally_count;++i){auto next=encode_claim(claims,i,w.ally_count,geo.groups.size(),elk);check(bool(next),"actual claim layout");claims=*next;}std::copy(claims.begin(),claims.end(),w.claims.begin());
  m.mission.group=gold;m.mission.phase=Phase::Travel;m.mission.start=w.round-1;m.mission.expiry=w.round+100;m.mission.last_progress=w.round-1;m.mission.target=other;m.mission.rate=.001;++w.serial;
  try { if(stage==0){
   auto arrival=assembly_detail::contribution_arrival(w,w.self,c.pos);check(arrival.known,"cached actual-terrain contribution path");auto body=w.self;body.pos=arrival.at;
   const auto bound=optimistic_solo_impossibility(body,c,w.self.shield);check(bound.impossible,"supported optimistic solo impossibility proof");
   drain(65000);const auto before=bc::fuel_remaining();auto quote=local_assembly_candidate(w,m,elk,.001);const auto after=bc::fuel_remaining();
   check(quote&&quote->known&&!quote->clear_ready&&after>24000&&w.round==int(bc::round_number()),"65k supported solo proof reaches pair and priced quote with action reserve");
   std::printf("NATIVE_ASSEMBLY_BUDGET_CASE_PASS funded-pair-quote %d %u %u\n",w.self.id,unsigned(before),unsigned(after));
  }else if(stage==1){
   drain(80000);const auto before=bc::fuel_remaining();auto chosen=choose_mission(w,m);const auto after=bc::fuel_remaining();
   check(chosen&&chosen->mission.assembly_pending&&chosen->mission.phase==Phase::Assemble&&chosen->action.kind==Kind::Move,"unchanged65k consumer gate reaches real pending move proposal");
   check(after>12000&&w.round==int(bc::round_number()),"coordinator move retains native mutation allowance");pending=chosen->mission;
   std::printf("NATIVE_ASSEMBLY_BUDGET_CASE_PASS coordinator-move %d %u %u\n",w.self.id,unsigned(before),unsigned(after));
  }else if(stage==2){
   m.mission=pending;m.mission.expiry=w.round+3;m.mission.last_progress=w.round;
   occupy(w.self.pos,false);w.self.pos={target.x-1,target.y};occupy(w.self.pos,true);w.allies[0]=w.self;
   drain(65000);const auto before=bc::fuel_remaining();auto ready=propose_local_assignment(w,elk);const auto after=bc::fuel_remaining();
   std::printf("NATIVE_ASSEMBLY_BUDGET_DETAIL ready=%d self=%d accepted=%d uncertain=%d before=%u after=%u\n",ready.ready,ready.self_selected,ready.locally_accepted,ready.uncertain,unsigned(before),unsigned(after));
   check(ready.ready&&ready.self_selected&&ready.locally_accepted,"current physical pair readiness stays funded after known solo impossibility");
   std::printf("NATIVE_ASSEMBLY_BUDGET_CASE_PASS current-pair-readiness %d %u %u\n",w.self.id,unsigned(before),unsigned(after));
  }else if(stage==3){
   m.mission=pending;m.mission.expiry=w.round+3;m.mission.last_progress=w.round;
   occupy(w.self.pos,false);w.self.pos={target.x-1,target.y};occupy(w.self.pos,true);w.allies[0]=w.self;
   drain(65000);const auto before=bc::fuel_remaining();auto chosen=farming(w,m);const auto after=bc::fuel_remaining();
   std::printf("NATIVE_ASSEMBLY_BUDGET_DETAIL consumer_phase=%d kind=%d pending=%d before=%u after=%u\n",chosen?int(chosen->mission.phase):-1,chosen?int(chosen->action.kind):-1,chosen?chosen->mission.assembly_pending:-1,unsigned(before),unsigned(after));
   check(chosen&&!chosen->mission.assembly_pending&&chosen->mission.phase==Phase::Clear&&chosen->action.kind==Kind::BasicCamp,"actual present claim and ready pair authorize first basic through consumer");
   std::printf("NATIVE_ASSEMBLY_BUDGET_CASE_PASS current-ready-consumer %d\n",w.self.id);
  }else if(stage==4||stage==5){
   m.mission=pending;m.mission.expiry=w.round+3;m.mission.last_progress=w.round;
   occupy(w.self.pos,false);w.self.pos={target.x-1,target.y};occupy(w.self.pos,true);w.allies[0]=w.self;
   if(stage==4)w.allies={w.self};else w.groups[elk].seen=w.round-1;
   auto chosen=farming(w,m);
   check(!chosen||chosen->mission.group!=elk||chosen->action.kind!=Kind::BasicCamp,"missing or stale local help cannot authorize first hit");
   std::printf("NATIVE_ASSEMBLY_BUDGET_CASE_PASS %s %d\n",stage==4?"missing-helper-declines":"stale-camp-declines",w.self.id);
  }else if(stage==6){
   g.gems=0;w.self.gems=0;w.geo.monolith_only=true;drain(65000);
   check(!local_assembly_candidate(w,m,elk,.001),"unpriced gold-only monolith fallback cannot request scored crew");
   std::printf("NATIVE_ASSEMBLY_BUDGET_CASE_PASS gold-only-declines %d\n",w.self.id);
  }else if(stage==8||stage==9){
   occupy(w.self.pos,false);w.self.pos={target.x-1,target.y};occupy(w.self.pos,true);
   w.self.hp=w.self.max_hp=900;w.self.strength=70;w.allies[0]=w.self;
   w.allies[1].type=8;w.allies[1].range=3;w.allies[1].pos={target.x-2,target.y-1};w.allies[1].hp=w.allies[1].max_hp=700;w.allies[1].strength=45;
   w.allies[1].spells[1]=w.self.spells[0];
   w.allies[1].spells[0].kind=5;w.allies[1].spells[0].self=false;w.allies[1].spells[0].allies=true;w.allies[1].spells[0].amount=315;w.allies[1].spells[0].range=4;
   g.initial_hp=2400;v.camps[0].hp=v.camps[0].max_hp=2400;
   if(stage==9){
    m.mission=pending;m.mission.expiry=w.round+3;m.mission.last_progress=w.round;
    drain(65000);const auto before=bc::fuel_remaining();auto chosen=choose_mission(w,m);const auto after=bc::fuel_remaining();
    check((!chosen||chosen->mission.group!=elk||chosen->action.kind!=Kind::BasicCamp)&&after>12000&&w.round==int(bc::round_number()),"65k committed long coordinator may decline unknown without spending mutation reserve");
    std::printf("NATIVE_ASSEMBLY_BUDGET_CASE_PASS pending-long-coordinator %d %u %u phase=%d kind=%d\n",w.self.id,unsigned(before),unsigned(after),chosen?int(chosen->mission.phase):-1,chosen?int(chosen->action.kind):-1);
    ++stage;bc::end_turn();continue;
   }
   drain(65000);const auto before=bc::fuel_remaining();auto ready=propose_local_assignment(w,elk);const auto after=bc::fuel_remaining();
   std::printf("NATIVE_ASSEMBLY_BUDGET_DETAIL long_ready=%d uncertain=%d before=%u after=%u\n",ready.ready,ready.uncertain,unsigned(before),unsigned(after));
   check(!ready.ready&&ready.uncertain&&after>32000&&w.round==int(bc::round_number()),"long forecast stops unknown before consuming useful action reserve");
   std::printf("NATIVE_ASSEMBLY_BUDGET_CASE_PASS long-rollout-budget %d %u %u\n",w.self.id,unsigned(before),unsigned(after));
  }else{
   w.self.spells[0].kind=7;w.self.spells[0].amount=100;w.spells=w.self.spells;w.allies[0]=w.self;drain(65000);
   check(!local_assembly_candidate(w,m,elk,.001),"unsupported defensive kit does not call unfunded generic solo rollout");
   check(w.round==int(bc::round_number())&&bc::fuel_remaining()>24000,"unsupported case preserves owner budget as unknown");
   std::printf("NATIVE_ASSEMBLY_BUDGET_CASE_PASS unsupported-declines %d\n",w.self.id);std::printf("NATIVE_ASSEMBLY_BUDGET_PASS %d\n",w.self.id);
  }
  } catch(const std::exception&){stage=10;bc::end_turn();continue;}
  ++stage;bc::end_turn();
 }
}

