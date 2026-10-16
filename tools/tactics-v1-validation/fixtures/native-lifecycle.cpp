#include "actions.h"
#include "shopping.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
using namespace tactics;
static void check(bool v,const char* label){if(!v)throw std::runtime_error(label);}
int main(){
 Geometry geometry;Memory memory;ShoppingState shopping;std::unique_ptr<World> world;
 bool met=false,gold_done=false,provoked=false,dead_checked=false,respawn_checked=false;
 int gold_group=-1,elk_group=-1;
 while(true){
  if(bc::is_draft()){bc::draft::pick(bc::champion_draft::ryth);bc::end_turn();continue;}
  geometry.initialize();
  if(!world){
   world=std::make_unique<World>(geometry,memory);
   check(world->kit_ready.size()==1,"fixture requires only self kit initially ready");
   for(const auto& enemy:world->enemy_handles)check(!enemy.is_visible(),"enemy must begin hidden");
  }
  World& w=*world;w.refresh();
  const bool left=w.geo.at(w.geo.home,{1,1})==0;
  if(gold_group<0){
   int best=unreachable;
   for(unsigned i=0;i<geometry.groups.size();++i)for(const auto&s:geometry.groups[i].spawns)
    if(s.type==3&&w.home_distance(s.pos)<best){best=w.home_distance(s.pos);gold_group=i;}
   best=unreachable;
   for(unsigned i=0;i<geometry.groups.size();++i)for(const auto&s:geometry.groups[i].spawns)
    if(s.type==1&&w.home_distance(s.pos)<best){best=w.home_distance(s.pos);elk_group=i;}
   check(gold_group>=0&&elk_group>=0,"fixture camp metadata");
  }
  if(!w.self.alive){
   if(!dead_checked){
    check(met&&gold_done&&provoked,"death must follow actual meeting, collection and elk wake");
    check(w.self.type==static_cast<int>(bc::champion_type::ryth),"own immutable type survives dead refresh");
    const int before=w.gold;check(before>=30,"dead body retains collected private gold");
    Mission job;auto purchase=shopping_proposal(w,job,shopping);
    check(purchase&&purchase->kind==Kind::Buy,"dead body may propose a legal component");
    const auto result=execute(w,*purchase);check(result.success,"actual dead component purchase accepted");
    w.refresh(true);shopping_after_action(w,*purchase,result.success,shopping);
    check(w.gold==before-30,"actual dead purchase wallet conserved");
    check(w.me.item_count()[static_cast<bc::item_type>(purchase->item)]==1,"dead purchase exact inventory increment");
    check(!w.me.is_alive(),"dead buying must not resurrect the body");
    std::printf("NATIVE_DEAD_SHOP_PASS %d %d\n",w.self.id,w.gold);dead_checked=true;
   }
   bc::end_turn();continue;
  }
  if(dead_checked){
   if(!respawn_checked){check(w.in_spawn(w.self.pos),"respawn returns to own spawn");check(w.self.type==0,"fresh living type after respawn");std::printf("NATIVE_RESPAWN_PASS %d\n",w.self.id);respawn_checked=true;}
   bc::end_turn();continue;
  }
  if(!met){
   if(!w.enemies.empty()){
    for(const auto&e:w.enemies){
     check(std::find(w.kit_ready.begin(),w.kit_ready.end(),e.id)!=w.kit_ready.end(),"newly visible enemy bound to fresh SDK kit");
     check(e.spells[0].kind!=0,"visible enemy kit metadata inspected");
     auto handle=w.champion(e.id);check(handle.has_value(),"visible handle exists");check(handle->abilities()[0].info().has_value(),"SDK cached hidden-error replaced with actual visible metadata");
    }
    std::printf("NATIVE_FIRST_VISIBLE_KIT_PASS %d\n",w.self.id);met=true;
   }else if(auto step=w.toward({left?14:17,14})){Action a;a.kind=Kind::Move;a.at=*step;a.reason="fixture-meet";execute(w,a);}
   bc::end_turn();continue;
  }
  if(!gold_done&&w.gold>=30)gold_done=true;
  const int group=gold_done?elk_group:gold_group;const auto target=geometry.groups[group].spawns[0].pos;
  if(!gold_done&&w.groups[group].fresh(w.round)&&w.groups[group].state==Lifecycle::Reward){
   if(!w.on_group(group,w.self.pos))if(auto step=w.toward(target)){Action a;a.kind=Kind::Move;a.at=*step;a.reason="fixture-collect";execute(w,a);}
  }else if(gold_done&&provoked){
   // Stand beside the awakened elk until it kills this actual native body.
  }else{
   std::optional<Camp> monster;
   for(const auto&c:w.groups[group].camps)if(c.hp>0)monster=c;
   if(monster&&distance(w.self.pos,monster->pos)<=w.self.range&&w.self.can_attack){
    Action a;a.kind=Kind::BasicCamp;a.target=monster->id;a.reason="fixture-wake-or-clear";auto r=execute(w,a);if(gold_done&&r.success)provoked=true;
   }else if(auto step=w.toward(target,1)){Action a;a.kind=Kind::Move;a.at=*step;a.reason="fixture-approach";execute(w,a);}
  }
  bc::end_turn();
 }
}
