#include "actions.h"
#include "combat.h"
#include <memory>
#include <cstdio>
#include <stdexcept>
using namespace tactics;
#include "peel-extracted.h"
static void check(bool ok,const char*why){if(!ok){std::printf("NATIVE_PEEL_FAIL %s\n",why);std::fflush(stdout);throw std::runtime_error(why);}}
static void burn(unsigned left){volatile unsigned x=1;while(bc::fuel_remaining()>left)x=x*1664525u+1013904223u;}
static Pos endpoint(int id,int round){const Pos initial[]={{5,10},{11,10},{12,11},{10,11},{13,11},{10,10},{11,11},{12,10}};if(id==0&&round>=140)return {8,10};if(round>=110&&(id==4||id==6||id==7))return {25+(id%3),26};return initial[id];}
int main(){Geometry geo;Memory m;std::unique_ptr<World>world;int tests=0;
 while(true){if(bc::is_draft()){const int picks[]={3,8,4};auto size=bc::draft::current_draft(bc::team::ally).size();bc::draft::pick(static_cast<bc::champion_draft>(picks[size]));bc::end_turn();continue;}geo.initialize();if(!geo.initialized){bc::end_turn();continue;}const int id=identity(bc::self()),round=bc::round_number();const Pos target=endpoint(id,round);if(!geo.goal_field(target,0)){bc::end_turn();continue;}if(!world)world=std::make_unique<World>(geo,m);world->refresh();auto&w=*world;
 if(w.self.pos!=target){if(auto step=w.toward(target)){Action a;a.kind=Kind::Move;a.at=*step;auto result=execute(w,a);check(result.outcome==Outcome::Applied,"native staging move");}bc::end_turn();continue;}
 if(id==5){for(const auto&e:w.enemies)if(e.id==1&&e.hp>40&&distance(w.self.pos,e.pos)<=1){Action a;a.kind=Kind::BasicChampion;a.target=1;auto result=execute(w,a);check(result.outcome==Outcome::Applied,"actual ally health preparation");}}
 if(id==0&&(round==100||round==101||round==150||round==151)){
  check(w.self.can_cast&&w.spells[1].ready&&w.spells[1].kind==4&&w.spells[1].range==4,"actual ready Cassi control kit");
  const Actor*ally=nullptr;for(const auto&a:w.allies)if(a.id==1)ally=&a;check(ally&&ally->hp==20,"actual endangered ally20HP");
  const char*name=round==100?"far":round==101?"empty":round==150?"immune":"positive";
  if(round==101){w.enemies.clear();w.sightings.clear();++w.serial;}
  if(round==150){for(auto&e:w.enemies)e.type=7;++w.serial;}
  const double incoming=incoming_damage(w,w.self.pos);check(incoming<w.self.hp,"caster itself nonlethal");burn(65000);const unsigned start=bc::fuel_remaining();auto p=exact_peel(w,m,incoming,55000);const unsigned end=bc::fuel_remaining();check(round==int(bc::round_number()),"same-owner exact policy");
  if(round!=151)check(!p,"no impossible peel proposal");else{check(p&&p->action.kind==Kind::CastChampion&&p->action.slot==1&&p->action.target==5&&p->priority==Priority::Survival,"actual legal lethal peel selected");auto result=execute(w,p->action);check(result.outcome==Outcome::Applied,"actual native selected control applies");auto target=w.champion(5);check(target&&target->buffs().has_stun(),"actual enemy receives stun");}
  std::printf("NATIVE_PEEL_CASE %s %u %u %d %d %d\n",name,start,end,p?int(p->action.kind):0,p?p->action.target:-1,p?int(p->priority):0);++tests;
  if(round==100){auto target=w.champion(5);check(target.has_value(),"negative range target visible");bool rejected=false;try{w.me.abilities()[1].use(*target);}catch(const bc::error&){rejected=true;}check(rejected&&w.me.abilities()[1].cooldown()==0,"actual SDK range5 rejection preserves cooldown");std::printf("NATIVE_PEEL_RANGE_REJECTED\n");}
  if(tests==4)std::printf("NATIVE_PEEL_PASS %d\n",tests);
 }
 bc::end_turn();}
}
