#include "solo.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
using namespace tactics;
static void require(bool ok,const char* why){if(!ok){std::printf("SOLO_CLOCK_FAIL %s\n",why);throw std::runtime_error(why);}}
int main(){Geometry geo;Memory memory;std::unique_ptr<World>ptr;int group=-1,phase=0,owners=0,casts=0,start=-1;double initial=0;Pos target{};
while(true){try{
if(bc::is_draft()){auto old=bc::draft::current_draft(bc::team::ally);for(auto p:{bc::champion_draft::cassi_and_issac,bc::champion_draft::ryth,bc::champion_draft::willow})if(std::find(old.begin(),old.end(),p)==old.end()){bc::draft::pick(p);break;}}
else if(bc::detail::sdk_my_team()==0&&int(bc::self().champion_name())==3&&phase<3){
if(!geo.initialized){geo.initialize();bc::end_turn();continue;}
if(group<0){int d=unreachable;for(unsigned i=0;i<geo.groups.size();++i)if(geo.groups[i].spawns.size()==1&&geo.groups[i].initial_strength>0){int next=geo.at(geo.home,geo.groups[i].spawns.front().pos);if(next<d){d=next;group=i;}}require(group>=0,"native singleton");target=geo.groups[group].spawns.front().pos;}
if(!geo.goal_field(target,1)||bc::fuel_remaining()<65000){bc::end_turn();continue;}
if(!ptr)ptr=std::make_unique<World>(geo,memory);auto&w=*ptr;w.refresh();
if(phase==0){if(distance(w.self.pos,target)<=1)phase=1;else if(auto next=w.toward(target,1))require(w.me.move_absolute(sdk(*next)),"actual approach");}
else{require(w.groups[group].camps.size()==1,"actual visible singleton");const auto camp=w.groups[group].camps.front();auto handle=w.camp(camp.id);require(handle.has_value(),"actual camp handle");
if(phase==1){require(w.self.hp==700&&w.self.strength==30&&w.self.focus==70&&camp.hp==1350&&camp.strength==20&&!camp.awake,"unmodified native Cassi/Wolf metadata");const auto q=certify_solo_clear(w.self,camp,w.self.pos,0,true);require(q.known&&q.feasible&&q.clear_ticks==27&&q.damage_taken==520&&q.remaining_hp==180,"production scalar predicts27owners26futurecampresponses");initial=w.self.hp;start=w.round;phase=2;std::printf("SOLO_CLOCK_CERT round=%d hp=%.0f owners=%.0f damage=%.0f remaining=%.0f\n",w.round,initial,q.clear_ticks,q.damage_taken,q.remaining_hp);}
require(w.round==start+owners,"consecutive actual owner phases");require(w.self.hp==initial-20*owners,"actual camp phase ledger before each action");
if(w.me.can_attack())w.me.attack(*handle);
if(handle->is_alive()){auto ability=w.me.abilities()[0];if(ability.is_ready()){require(ability.use(*handle),"actual Cassi direct damage cast");++casts;}}
++owners;
if(!handle->is_alive()){require(owners==27&&casts==4&&w.me.health()==180,"native27owner clear pays26futurecampresponses");std::printf("SOLO_CLOCK_PASS owners=%d futurePhases=%d casts=%d hp=%.0f round=%d\n",owners,owners-1,casts,w.me.health(),int(bc::round_number()));phase=3;}
}}
}catch(const std::exception&e){std::printf("SOLO_CLOCK_EXCEPTION %s\n",e.what());phase=3;}bc::end_turn();}}
