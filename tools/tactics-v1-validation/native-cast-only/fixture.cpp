#include "solo_poke.h"
#include "sdk_world.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
using namespace tactics;
static void require(bool ok,const char* why){if(!ok){std::printf("CAST_ONLY_FAIL %s\n",why);throw std::runtime_error(why);}}
int main(){Geometry geo;Memory memory;std::unique_ptr<World>ptr;int group=-1,phase=0,owners=0,casts=0,start=-1;const Pos target{54,64},stage{58,65};
while(true){try{
if(bc::is_draft()){auto old=bc::draft::current_draft(bc::team::ally);for(auto p:{bc::champion_draft::cassi_and_issac,bc::champion_draft::ryth,bc::champion_draft::willow})if(std::find(old.begin(),old.end(),p)==old.end()){bc::draft::pick(p);break;}}
else if(bc::detail::sdk_my_team()==1&&int(bc::self().champion_name())==3&&phase<3){
if(!geo.initialized){geo.initialize();bc::end_turn();continue;}
if(group<0)for(unsigned i=0;i<geo.groups.size();++i)if(geo.groups[i].spawns.size()==1&&geo.groups[i].spawns.front().pos==target)group=i;
require(group>=0,"actual singleton Elk54,64 on retained Expanse geometry");
if(!geo.goal_field(stage,0)||bc::fuel_remaining()<65000){bc::end_turn();continue;}
if(!ptr)ptr=std::make_unique<World>(geo,memory);auto&w=*ptr;w.refresh();
if(phase==0){if(w.self.pos==stage)phase=1;else if(auto next=w.toward(stage))require(w.me.move_absolute(sdk(*next)),"actual approach to outer cast tile");}
else{require(w.groups[group].camps.size()==1,"actual visible singleton");const auto camp=w.groups[group].camps.front();auto handle=w.camp(camp.id);require(handle.has_value(),"actual visible camp handle");
if(phase==1){require(w.self.hp==700&&w.self.strength==30&&w.self.focus==70&&camp.hp==2400&&camp.strength==60&&!camp.awake,"native unmodified Cassi and Elk metadata");require(!w.in_spawn(stage)&&w.self.pos==stage&&distance(stage,camp.pos)==4&&camp.range==3,"actual nonspawn distance4 outside camp range3");
const auto q=certify_cast_only_clear(w.self,camp,stage,0);require(q.known&&q.feasible&&q.ready_now&&q.shots==18&&q.clear_ticks==137&&q.remaining_hp==700,"actual cast-only analytic quote");start=w.round;phase=2;std::printf("CAST_ONLY_CERT round=%d shots=%d owners=%d hp=%.0f\n",w.round,q.shots,q.clear_ticks,q.remaining_hp);}
require(w.round==start+owners,"consecutive actual owner phases");require(w.me.health()==700&&position(w.me.position())==stage&&!w.in_spawn(stage),"actual safe fixed outer tile never loses HP or heals on spawn");
auto ability=w.me.abilities()[0];if(ability.is_ready()){require(w.round==start+8*casts,"known8owner spell cadence");require(ability.use(*handle),"native direct cast accepted at range4");++casts;}
++owners;
if(!handle->is_alive()){require(owners==137&&casts==18&&w.me.health()==700,"actual18cast137owner zero-pressure clear");std::printf("CAST_ONLY_PASS owners=%d casts=%d hp=%.0f round=%d\n",owners,casts,w.me.health(),int(bc::round_number()));phase=3;}
}}
}catch(const std::exception&e){std::printf("CAST_ONLY_EXCEPTION %s\n",e.what());phase=3;}bc::end_turn();}}
