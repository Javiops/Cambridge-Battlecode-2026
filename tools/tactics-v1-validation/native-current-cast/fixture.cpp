// Controlled actual SDK witness. Priming damage, positions, cooldowns, HP,
// World and every mutation are native. Only a finite Observe intent is seeded
// to isolate farming's late assignment caller from global job selection.
#include "coordinator.h"
#include "actions.h"
#include "crew_sequence.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
using namespace tactics;
static void need(bool ok,const char*why){if(!ok){std::printf("ADMISSION26_FAIL %s\n",why);throw std::runtime_error(why);}}
static void act(World&w,Action a){const auto r=execute(w,a);need(r.success,"actual native mutation accepted");}
int main(){Geometry geo;Memory memory;std::unique_ptr<World> world;int gi=-1,phase=0,casts=0;Pos center{},stage{};
 while(true){try{
  if(bc::is_draft()){
   const auto old=bc::draft::current_draft(bc::team::ally);
   for(auto p:{bc::champion_draft::ryth,bc::champion_draft::ren,bc::champion_draft::varg,bc::champion_draft::vendetta,bc::champion_draft::tavi})
    if(std::find(old.begin(),old.end(),p)==old.end()){bc::draft::pick(p);break;}
  }else if(bc::detail::sdk_my_team()==0&&int(bc::self().champion_name())==0&&phase<99){
   if(!geo.initialized){geo.initialize();bc::end_turn();continue;}
   if(gi<0){int nearest=unreachable;
    for(unsigned i=0;i<geo.groups.size();++i){const auto&g=geo.groups[i];if(g.spawns.size()!=3||g.gems<=0)continue;
     const int d=geo.at(geo.home,g.spawns.front().pos);if(d<nearest){nearest=d;gi=int(i);}}
    need(gi>=0,"native public3-member gem group");const auto&g=geo.groups[gi];
    center=std::min_element(g.spawns.begin(),g.spawns.end(),[](const Spawn&a,const Spawn&b){return a.hp<b.hp;})->pos;
    int best=unreachable;bool found=false;
    for(int dy=-4;dy<=4;++dy)for(int dx=-4;dx<=4;++dx){Pos p{center.x+dx,center.y+dy};
     if(!geo.valid(p)||geo.blocked(p)||distance(p,center)>4)continue;bool safe=true;
     for(const auto&s:g.spawns)safe&=distance(p,s.pos)>s.range&&distance(p,s.pos)<=4;
     const int home=geo.at(geo.home,p);if(safe&&home<best){best=home;stage=p;found=true;}}
    need(found,"actual fixed outer stage outside all camp response ranges");
   }
   if(!geo.goal_field(stage,0)||!geo.goal_field(center,0)||bc::fuel_remaining()<65000){bc::end_turn();continue;}
   if(!world)world=std::make_unique<World>(geo,memory);auto&w=*world;w.refresh();
   if(w.round!=int(bc::round_number())||bc::fuel_remaining()<50000){bc::end_turn();continue;}
   need(w.self.alive,"actual caster survives all preparation");
   if(phase==0){if(w.self.pos!=stage){if(auto next=w.toward(stage))act(w,moving(*next,"native-lawful-outer-prelude"));}
    else{need(w.groups[gi].fresh(w.round)&&w.groups[gi].camps.size()==3,"actual three members personally visible");
     need(w.self.range==1&&w.spells[0].kind==3&&w.spells[0].range==4&&w.spells[0].radius==1&&w.spells[0].amount==100,"native Ryth exact ground metadata");
     std::printf("ADMISSION26_STAGE %d %d %d %d %d %.0f\n",w.round,w.self.id,gi,stage.x,stage.y,w.self.hp);phase=1;}
   }else if(phase==1){
    need(w.self.pos==stage,"stationary priming does not borrow move permission");
    need(w.groups[gi].fresh(w.round)&&w.groups[gi].state==Lifecycle::Alive,"actual incomplete group before witness");
    for(const auto&c:w.groups[gi].camps)need(distance(w.self.pos,c.pos)>c.range,"no actual unpriced camp response at outer stage");
    if(w.self.can_cast&&w.spells[0].ready){
     const auto planned=stationary_camp_action(w.self,w.groups[gi].camps);
     bool final=planned.kind==Kind::CastGround;
     for(const auto&c:w.groups[gi].camps)if(c.hp>0)final&=camp_action_damage(w.self,planned,w.groups[gi].camps,c)>=c.hp;
     if(final){
      memory.mission={};memory.mission.group=gi;memory.mission.phase=Phase::Observe;
      memory.mission.target=center;memory.mission.rate=1;memory.mission.start=memory.mission.last_progress=w.round;memory.mission.expiry=w.round+6;
      std::printf("ADMISSION26_WITNESS %d %d %d %d %d %.0f %d %u",w.round,w.self.id,gi,w.self.pos.x,w.self.pos.y,w.self.hp,casts,unsigned(bc::fuel_remaining()));
      for(const auto&c:w.groups[gi].camps)std::printf(" camp=%d,%d,%d,%.0f",c.id,c.pos.x,c.pos.y,c.hp);std::printf("\n");
      phase=2;bc::end_turn();continue;
     }
     Action a;
     if(casts<23){a.kind=Kind::CastGround;a.slot=0;a.at=center;a.reason="native-actual-area-preparation";}
     else{a=planned;need(a.kind==Kind::CastGround,"actual remaining camp can be primed by legal outer ground");}
     need(distance(w.self.pos,a.at)>w.self.range+1,"real priming is outside missed basic neighborhood");act(w,a);++casts;
    }
   }else if(phase==2){
    need(w.self.can_cast&&w.spells[0].ready,"fresh real current spell permission after prelude");
    const unsigned before=bc::fuel_remaining();
#ifdef EXPECT_ADMITTED
    auto chosen=early_current_cast_farm_proposal(w,memory,false);
#else
    auto chosen=farming(w,memory);
#endif
    const unsigned after=bc::fuel_remaining();
    const bool exact=chosen&&chosen->mission.group==gi&&chosen->mission.phase==Phase::Clear&&
     chosen->action.kind==Kind::CastGround&&chosen->crew_clear_certified&&chosen->crew_clear_proof==ClearProofKind::DetailedBundle;
    std::printf("ADMISSION26_CALL %d %u %u %d %d %d %d\n",w.round,before,after,bool(chosen),chosen?int(chosen->mission.phase):-1,chosen?int(chosen->action.kind):-1,exact);
#ifdef EXPECT_ADMITTED
    need(exact,"production farming must consume exact detailed ground beyond basic range");
    auto receipt=make_crew_turn_receipt(w,*chosen);need(!receipt.required||receipt.valid,"actual unchanged main receipt gate funded");
    need(distance(w.self.pos,chosen->action.at)>w.self.range+1,"actual chosen cast remains outside old gate");
    memory.mission=chosen->mission;act(w,chosen->action);phase=3;
#else
    need(!exact,"frozen25r1 range gate rejects otherwise exact current clear");
    std::printf("ADMISSION26_CONTROL_PASS %d\n",w.round);phase=99;
#endif
   }else if(phase==3){
    if(w.self.gems>0){std::printf("ADMISSION26_CAPTURE %d %d\n",w.round,w.self.gems);phase=4;}
    else{auto chosen=farming(w,memory);if(chosen){memory.mission=chosen->mission;if(chosen->action.kind!=Kind::None)act(w,chosen->action);}}
   }else if(phase==4){
    if(w.self.gems==0&&w.own_score>0){std::printf("ADMISSION26_PASS %d %d\n",w.round,w.own_score);phase=99;}
    else if(w.self.channel==Channel::None){auto bank=delivery(w,memory,true);if(bank){memory.mission=bank->mission;if(bank->action.kind!=Kind::None)act(w,bank->action);}}
   }
  }
 }catch(const std::exception&e){std::printf("ADMISSION26_EXCEPTION %s\n",e.what());phase=99;}
 bc::end_turn();}
}
