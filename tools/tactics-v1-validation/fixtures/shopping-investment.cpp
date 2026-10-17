#include "types.h"
#if __has_include("camp_actions.h")
#include "camp_actions.h"
#endif
#include <cstdlib>
#include <iostream>
#include <string_view>
using namespace tactics;
namespace bc {namespace constants {inline constexpr int max_rounds=2000;}}
namespace cambc {struct champion_stats{double health_growth=1,strength_growth=1,focus_growth=1;};}
// EXACT_SHOP_TYPES
struct ItemInfo;
struct Item {
    int raw=0;
    explicit operator int()const{return raw;}
    ItemInfo info() const;
    int cost() const{return 30;}
};
struct ItemInfo{double health_points=0,strength_points=0,focus_points=0;std::optional<Item>result;int cost=30;};
static std::array<ItemInfo,42>catalog;
inline ItemInfo Item::info()const{return catalog[raw];}
inline Item shop_item(int raw){return {raw};}
inline const ItemInfo &shop_info(int raw){return catalog[raw];}
inline ShopInventory shop_inventory(const ShopInventory&i){return i;}
struct MockMe {ShopInventory inventory;ShopInventory item_count()const{return inventory;}};
struct MockGeo {std::vector<Group>groups=std::vector<Group>(2);std::optional<int>path=6;std::optional<int>cached_steps(Pos,Pos)const{return path;}};
struct World {
    Actor self;MockMe me;MockGeo geo;Memory memory;int gold=0,round=20;
    std::vector<Actor> allies,enemies;
    std::array<Spell,2> spells{};
    double pressure=0;
    double exposure(Pos)const{return pressure;}
    bool in_spawn(Pos)const{return true;}
};
// EXACT_SHOP_FUNCTIONS
static int checks=0;
static void check(bool ok){++checks;if(!ok){std::cerr<<"FAIL shopping-investment "<<checks<<'\n';std::exit(1);}}
static ShoppingState plan(){
    ShoppingState s;s.investment_item=12;s.investment_count=1;s.investment_before=4;
    s.investment_buy_gold=30;s.investment_mission.group=0;s.investment_mission.phase=Phase::Clear;
    s.investment_mission.target={5,5};return s;
}
int main(){
    Actor a;a.type=2;a.alive=true;a.hp=a.max_hp=1000;a.strength=100;a.move_speed=1;
    Group g;g.gems=22;g.initial_hp=1000;g.respawn=20;
    UpgradeDelta str;str.strength=100;
    auto p=named_return_payoff(a,g,str,1000,1,5,1.25);
    check(p.known&&p.worthwhile&&p.saved_turns==40&&p.absence==7);
    UpgradeDelta health;health.health=100;
    check(!named_return_payoff(a,g,health,1000,1,5,1.25).worthwhile);
    check(!named_return_payoff(a,g,str,1000,unreachable,5,1.25).known);
    check(!named_return_payoff(a,g,str,6,1,5,1.25).known);
    check(!named_return_payoff(a,g,str,1000,1000,5,1.25).worthwhile);
    a.move_speed=2;check(named_return_payoff(a,g,str,1000,5,5,1.25).absence==9);
    auto gold=g;gold.gems=0;check(!named_return_payoff(a,gold,str,1000,1,5,1.25).known);
    g.initial_strength=100;a.hp=100;
    check(!named_return_payoff(a,g,str,1000,1,5,1.25).known); // Needed recovery is not an elective gain.
    a.hp=1000;g.initial_strength=0;a.strength=10;a.spells[0].kind=2;a.spells[0].camps=true;
    a.spells[0].amount=30;a.spells[0].recharge=3;a.spells[0].scale=2;
    UpgradeDelta focus;focus.focus=30;
    check(named_return_payoff(a,g,focus,1000,1,5,1.25).worthwhile);
    UpgradeDelta monster;monster.family=ShopFamily::Monster;
    check(!named_return_payoff(a,g,monster,1000,1,5,1.25).worthwhile);
    monster.first_passive=true;
    check(named_return_payoff(a,g,monster,1000,1,5,1.25).worthwhile);
    catalog[12]={1,0,0,Item{13}};catalog[13]={7,0,0,{}};
    ShopInventory inv;inv.count[12]=4;cambc::champion_stats growth;growth.health_growth=10;
    auto delta=upgrade_delta(12,inv,growth,1);
    check(delta.health==30&&delta.first_passive&&delta.strength==0);
    inv.active[2]=true;check(!upgrade_delta(12,inv,growth,1).first_passive);
    inv.count[12]=1;delta=upgrade_delta(12,inv,growth,2);
    check(delta.health==20&&!delta.first_passive);
    Action action;action.kind=Kind::Buy;action.item=12;action.count=1;action.reason="install-priced-return-bundle";
    World w;w.me.inventory.count[13]=1;auto state=plan();
    shopping_after_action(w,action,true,state);
    check(state.investment_item<0&&state.failed_round<0);
    check(w.memory.mission.group==0&&w.memory.mission.phase==Phase::Reenter&&w.memory.mission.expiry==26);
    w=World{};w.me.inventory.count[12]=1;state=plan();
    shopping_after_action(w,action,true,state);
    check(state.failed_round==20&&w.memory.mission.phase==Phase::Unassigned);
    w=World{};w.me.inventory.count[13]=1;w.gold=10;state=plan();
    shopping_after_action(w,action,true,state);check(state.failed_round==20);
    state=plan();shopping_after_action(w,action,false,state);
    check(state.investment_item<0&&state.failed_round==20);
    w=World{};state=plan();state.investment_before=2;state.investment_count=2;state.investment_buy_gold=60;
    w.me.inventory.count[12]=4;action.count=2;shopping_after_action(w,action,true,state);
    check(state.failed_round<0&&w.memory.mission.phase==Phase::Reenter);
    a=Actor{};a.type=2;a.strength=100;a.hp=a.max_hp=1000;a.move_speed=1;
    g.initial_strength=0;g.gems=22;g.initial_hp=1000;g.respawn=20;
    check(!named_return_payoff(a,g,str,100,1,5,1.25,100,3).worthwhile);
    check(!named_return_payoff(a,g,str,1000,1,5,1.25,unreachable,3).known);
    state=plan();state.investment_round=10;Memory memory;
    check(!investment_plan_invalid(state,memory,20,1,true,false,false));
    check(investment_plan_invalid(state,memory,20,1,true,true,false));
    check(investment_plan_invalid(state,memory,20,1,true,false,true));
    check(investment_plan_invalid(state,memory,20,1,false,false,false));
    memory.failed_group=0;memory.failed_until=21;
    check(investment_plan_invalid(state,memory,20,1,true,false,false));
    memory=Memory{};check(investment_plan_invalid(state,memory,51,1,true,false,false));
    action.count=1;w=World{};w.me.inventory.count[13]=1;state=plan();
    state.investment_mission.group=1;state.investment_origin.group=0;state.investment_origin.target={2,2};state.investment_gem_unlock=true;w.memory.upgrade_gem_unlock=true;
    shopping_after_action(w,action,true,state);
    check(w.memory.mission.group==1&&w.memory.mission.phase==Phase::Reenter&&!w.memory.upgrade_gem_unlock&&!state.investment_gem_unlock);
    w=World{};w.me.inventory.count[13]=1;w.gold=1;state=plan();state.investment_mission.group=1;state.investment_origin.group=0;w.memory.upgrade_gem_unlock=true;
    shopping_after_action(w,action,true,state);check(w.memory.mission.group==0&&state.failed_round==20&&!w.memory.upgrade_gem_unlock);
    w=World{};state=plan();state.investment_mission.group=1;state.investment_origin.group=0;w.memory.upgrade_gem_unlock=true;
    shopping_after_action(w,action,false,state);check(w.memory.mission.group==0&&state.investment_item<0&&!w.memory.upgrade_gem_unlock);
    auto named_plan=[&]{auto s=plan();s.investment_gem_unlock=true;s.investment_mission.group=1;s.investment_mission.latest=1900;s.investment_mission.rate=.3;s.gem_route_group[0]=1;s.gem_route_stage[0]={7,7};return s;};
    action.count=1;w=World{};w.me.inventory.count[13]=1;state=named_plan();
    shopping_after_action(w,action,true,state);
    check(state.installed_gem.group==1&&state.installed_gem.stage==Pos{7,7});
    check(state.installed_gem.installed==20&&state.installed_gem.until==38&&state.installed_gem.remaining_cycle==100);
    check(w.memory.mission.phase==Phase::Reenter&&w.memory.mission.group==1);
    w=World{};w.me.inventory.count[13]=1;w.gold=1;state=named_plan();shopping_after_action(w,action,true,state);
    check(state.installed_gem.group==-1&&state.failed_round==20);
    w=World{};state=named_plan();shopping_after_action(w,action,false,state);check(state.installed_gem.group==-1);
    w=World{};w.me.inventory.count[13]=1;w.geo.path=std::nullopt;state=named_plan();shopping_after_action(w,action,true,state);
    check(state.installed_gem.group==-1&&w.memory.mission.phase==Phase::Reenter);
    auto named=plan().investment_mission;named.latest=1900;named.rate=.3;
    check(make_installed_reentry(named,{7,7},6,1,20,2000).until==38);
    check(make_installed_reentry(named,{7,7},unreachable,1,20,2000).group==-1);
    check(make_installed_reentry(named,{7,7},6,1,1900,2000).group==-1);
    named.rate=0;check(make_installed_reentry(named,{7,7},6,1,20,2000).group==-1);
#if __has_include("camp_actions.h")
    a=Actor{};a.type=0;a.strength=10;a.hp=a.max_hp=1000;a.move_speed=1;
    a.spells[0].kind=3;a.spells[0].ground=true;a.spells[0].amount=80;
    a.spells[0].scale=1;a.spells[0].recharge=8;
    UpgradeDelta ground_focus{};ground_focus.focus=80;
    g.gems=24;g.initial_hp=1000;g.initial_strength=0;g.respawn=100;
    auto ground_return=named_return_payoff(a,g,ground_focus,2000,1,5,1.25);
    check(ground_return.known&&ground_return.worthwhile&&ground_return.saved_turns>0);
    a.spells[0].ground=false;a.spells[0].kind=2;
    check(!named_return_payoff(a,g,ground_focus,2000,1,5,1.25).worthwhile);
    a.spells={};a.type=2;a.strength=100;a.monster=true;g.initial_hp=1100;
    UpgradeDelta small_strength{};small_strength.strength=10;
    check(named_return_payoff(a,g,small_strength,2000,1,5,1.25).saved_turns==0);
    UpgradeDelta repeated_passive{};repeated_passive.family=ShopFamily::Monster;
    repeated_passive.first_passive=true;g.initial_hp=1000;
    check(named_return_payoff(a,g,repeated_passive,2000,1,5,1.25).saved_turns==0);
    w=World{};w.self.strength=10;w.self.hp=w.self.max_hp=1000;
    w.spells[0].kind=3;w.spells[0].ground=true;w.spells[0].amount=80;
    w.spells[0].scale=1;w.spells[0].recharge=8;
    w.geo.groups[0]=g;w.geo.groups[0].initial_hp=1000;
    Mission farm;farm.group=0;
    check(upgrade_mission_value(w,farm,ground_focus,ShoppingState{})>=384);
    w.spells[0].ground=false;w.spells[0].kind=2;
    check(upgrade_mission_value(w,farm,ground_focus,ShoppingState{})==0);
    w.self.strength=100;w.self.monster=true;w.spells={};
    w.geo.groups[0].initial_hp=1100;
    check(upgrade_mission_value(w,farm,small_strength,ShoppingState{})<10);
#endif
    std::cout<<checks<<" shopping-investment checks passed\n";
}
