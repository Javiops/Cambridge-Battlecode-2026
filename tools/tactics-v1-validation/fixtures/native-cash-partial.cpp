// Native prelude earns and spends all resources. Production Bot::turn is
// unchanged after the real4-shard/zero-wallet starting state is observed.
#define main retained_production_main
#include "retained-main.h"
#undef main
#include <cstdio>
#include <memory>
using namespace tactics;
int main(){Bot bot;Geometry geo;Memory mem;std::unique_ptr<World>world;int phase=0,cash=-1,elk=-1;bool preview=false;
while(true){try{
if(bc::is_draft()){bc::draft::pick(bc::champion_draft::ryth);bc::end_turn();continue;}
if(phase==4){bc::end_turn();continue;}
if(phase==3){if(bc::global_submitted_gems(bc::team::ally)>=36){std::printf("PC20_COMPLETE %d %d %u\n",identity(bc::self()),int(bc::round_number()),bc::global_submitted_gems(bc::team::ally));phase=4;}else bot.turn();bc::end_turn();continue;}
geo.initialize();if(!geo.initialized){bc::end_turn();continue;}
if(cash<0){int dc=unreachable,de=unreachable;for(unsigned i=0;i<geo.groups.size();++i){const auto&g=geo.groups[i];int d=geo.at(geo.home,g.spawns.front().pos);if(g.gold==35&&g.gems==0&&d<dc){cash=i;dc=d;}if(g.spawns.size()==1&&g.spawns[0].type==1&&d<de){elk=i;de=d;}}if(cash<0||elk<0)throw std::runtime_error("native cash/Elk groups missing");}
const Pos target=geo.groups[cash].spawns.front().pos;
if(!geo.goal_field(target,0)){bc::end_turn();continue;}
if(!world)world=std::make_unique<World>(geo,mem);world->refresh();auto&w=*world;if(w.round!=int(bc::round_number())||bc::fuel_remaining()<30000){bc::end_turn();continue;}
if(phase==25){if(w.groups[cash].fresh(w.round)&&w.groups[cash].state==Lifecycle::Alive){std::printf("PC20_HANDOVER %d %d wallet=%u cashAlive=1\n",w.self.id,w.round,w.me.gold_count());phase=3;}bc::end_turn();continue;}
if(!preview){preview=true;auto inv=shop_inventory(w.me.item_count());const auto growth=w.me.base_stats();const auto d4=upgrade_delta(28,inv,growth,4);auto b4=project_bundle_actor(w.self,d4);b4=project_bundle_actor(b4,upgrade_delta(10,inv,growth,3));inv.count[28]=4;inv.count[10]=3;const auto b5=project_bundle_actor(b4,upgrade_delta(28,inv,growth,1));const auto&g=geo.groups[elk];Camp c;c.id=g.spawns.front().id;c.pos=g.spawns.front().pos;c.hp=c.max_hp=g.initial_hp;c.strength=g.initial_strength;c.range=g.spawns.front().range;c.awake=false;Pos at{c.pos.x+(bc::detail::sdk_my_team()==0?-1:1),c.pos.y};const auto q4=certify_solo_clear(b4,c,at,16,false),q5=certify_solo_clear(b5,c,at,16,false);std::printf("PC20_PREVIEW %d known=%d,%d feasible=%d,%d beforeHP=%.2f beforeSTR=%.2f nextHP=%.2f nextSTR=%.2f nextMIT=%.2f ticks=%.0f,%.0f damage=%.0f,%.0f\n",w.self.id,q4.known,q5.known,q4.feasible,q5.feasible,b4.max_hp,b4.strength,b5.max_hp,b5.strength,b5.camp_mitigation,q4.clear_ticks,q5.clear_ticks,q4.damage_taken,q5.damage_taken);if(!(q4.known&&!q4.feasible&&q5.known&&q5.feasible)){std::printf("PC20_PREVIEW_DECLINED %d\n",w.self.id);phase=4;bc::end_turn();continue;}}
if(phase==0){
if(w.gold>=210){std::printf("PC20_EARNED %d %d %d\n",w.self.id,w.round,w.gold);phase=1;}
else{const auto&v=w.groups[cash];if(v.fresh(w.round)&&v.state==Lifecycle::Alive&&!v.camps.empty()){const auto&camp=v.camps.front();if(distance(w.self.pos,camp.pos)<=w.self.range&&w.me.can_attack()){auto h=w.camp(camp.id);if(!h)throw std::runtime_error("native visible cash handle");w.me.attack(*h);}else if(auto next=w.toward(target,w.self.range))w.me.move_absolute(sdk(*next));}else if(v.fresh(w.round)&&v.state==Lifecycle::Reward&&w.self.pos!=target){if(auto next=w.toward(target))w.me.move_absolute(sdk(*next));}else if(v.fresh(w.round)&&v.state==Lifecycle::Respawning&&w.self.pos==target&&w.me.can_move()){Pos at{target.x+(bc::detail::sdk_my_team()==0?-1:1),target.y};if(w.free(at))w.me.move_absolute(sdk(at));}else if(v.state==Lifecycle::Unknown){if(auto next=w.toward(target,w.self.range))w.me.move_absolute(sdk(*next));}}
}
if(phase==1){if(w.self.channel!=Channel::None){}else if(w.home_distance(w.self.pos)==0){phase=2;}else w.me.recall();}
if(phase==2){if(w.gold!=210||w.me.item_count()[shop_item(28)]!=0)throw std::runtime_error("actual untouched prelude wallet/inventory");w.me.buy(shop_item(28),4);w.me.buy(shop_item(10),3);auto counts=w.me.item_count();if(w.me.gold_count()!=0||counts[shop_item(28)]!=4||counts[shop_item(10)]!=3||counts[shop_item(29)]!=0||w.me.max_health()!=1900||w.me.strength()!=57)throw std::runtime_error("actual native4JungleHealth+3PowerHealth/emptywallet starting state");std::printf("PC20_PRELUDE %d %d wallet=%u jungleShards=%u powerShards=%u emblem=%u HP=%.0f STR=%.0f\n",w.self.id,int(bc::round_number()),w.me.gold_count(),counts[shop_item(28)],counts[shop_item(10)],counts[shop_item(29)],w.me.max_health(),w.me.strength());phase=25;}
}catch(const std::exception&e){std::printf("PC20_ERROR %s\n",e.what());phase=4;}
bc::end_turn();}}
