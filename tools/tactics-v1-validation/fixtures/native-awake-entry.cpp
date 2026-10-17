// Lawful waking/outside-range prelude, then an unchanged production Bot::turn.
// No edits to World, stats, inventory, score, mission, claims or Bot memory.
#define main retained_production_main
#include "production-main.h"
#undef main
#include <cstdio>
using namespace tactics;
static void demand(bool value,const char*why){if(!value){std::printf("AWAKE_MAIN_FAIL %s\n",why);throw std::runtime_error(why);}}
int main(){Bot bot;Geometry geo;Memory memory;std::unique_ptr<World>ptr;int gi=-1,phase=0;Pos goal{};bool done=false;
while(true){try{
 if(bc::is_draft()){bc::draft::pick(bc::champion_draft::varg);bc::end_turn();continue;}
 if(done){bc::end_turn();continue;}
 if(phase==3){if(bc::global_submitted_gems(bc::team::ally)>=22){std::printf("AWAKE_MAIN_BANKED %d %d score=%u\n",identity(bc::self()),int(bc::round_number()),bc::global_submitted_gems(bc::team::ally));done=true;}else bot.turn();bc::end_turn();continue;}
 if(!geo.initialized){geo.initialize();bc::end_turn();continue;}
 if(gi<0){int nearest=unreachable;for(unsigned k=0;k<geo.groups.size();++k){const auto&g=geo.groups[k];if(g.spawns.size()==1&&g.initial_strength>0&&g.gems>0){const int d=geo.at(geo.home,g.spawns.front().pos);if(d<nearest){nearest=d;gi=k;}}}demand(gi>=0,"actual native singleton");goal=geo.groups[gi].spawns.front().pos;}
 if(!geo.goal_field(goal,0)||bc::fuel_remaining()<75000){bc::end_turn();continue;}
 if(!ptr)ptr=std::make_unique<World>(geo,memory);auto&w=*ptr;w.refresh();
 if(phase==0){if(distance(w.self.pos,goal)>w.self.range){if(auto next=w.toward(goal,w.self.range))demand(w.me.move_absolute(sdk(*next)),"lawful native approach");}else phase=1;}
 else if(phase==1){const auto&c=w.groups[gi].camps.front();demand(!c.awake&&w.self.hp==w.self.max_hp,"lawful sleeping camp primer");auto h=w.camp(c.id);demand(h&&w.me.can_attack(),"actual native primer available");w.me.attack(*h);phase=2;}
 else if(phase==2){const auto&c=w.groups[gi].camps.front();demand(c.awake,"actual awake before handoff");Pos outside{w.self.pos.x+(bc::detail::sdk_my_team()==0?-1:1),w.self.pos.y};demand(w.free(outside)&&distance(outside,c.pos)==w.self.range+1,"real outside-basic-range native endpoint");demand(w.me.move_absolute(sdk(outside)),"native prelude move");std::printf("AWAKE_MAIN_HANDOFF %d %d at=%d,%d camp=%d,%d campHP=%.0f campRange=%d hp=%.0f\n",w.self.id,w.round,outside.x,outside.y,c.pos.x,c.pos.y,c.hp,c.range,w.self.hp);phase=3;}
}catch(const std::exception&e){std::printf("AWAKE_MAIN_EXCEPTION %s\n",e.what());done=true;}bc::end_turn();}}
