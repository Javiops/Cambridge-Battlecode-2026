#include "types.h"
#include <map>
#include <cstdio>
#include <cstdlib>
namespace tactics {
struct HintGeometry {std::vector<Group>groups{Group{},Group{}};std::map<std::pair<int,int>,int>goal_cache;std::map<int,int>route_cache;int index(Pos p)const{return p.y*32+p.x;}};
struct World {Actor self{};int gold=0,round=20;Memory memory{};std::vector<Actor>enemies;HintGeometry geo;};
struct ShoppingState {struct Receipt{int group=-1;Pos capture{};}cash;struct Installed{int group=-1,until=-1;Pos stage{};}installed_gem;int investment_item=-1;};
inline int cash_investment_group(const World&){return -1;}
inline std::optional<Pos> cash_contribution_stage(const World&,int,ShoppingState&){return std::nullopt;}
inline std::array<int,2>gem_investment_groups(const World&){return{-1,-1};}
inline std::optional<Pos>cached_gem_contribution_stage(const World&,int,ShoppingState&){return std::nullopt;}
// EXACT_CASH_HINT
}
using namespace tactics;
int main(){int checks=0;auto check=[&](bool b,const char*w){++checks;if(!b){std::fprintf(stderr,"FAIL %s\n",w);std::exit(1);}};World w;ShoppingState s;w.self.alive=true;w.self.type=3;s.cash.group=0;s.cash.capture={6,6};const int stage=w.geo.index({3,3}),target=w.geo.index(s.cash.capture);w.geo.goal_cache[{stage,0}]=1;
check(shopping_gem_route_hint(w,s)==std::optional<Pos>(s.cash.capture),"paid stage field does not substitute for actual cash target root");
w.geo.goal_cache[{target,0}]=1;check(!shopping_gem_route_hint(w,s),"completed actual goal field needs no repeated preparation");w.geo.goal_cache.erase({target,0});
w.geo.route_cache[target]=1;check(!shopping_gem_route_hint(w,s),"completed actual route field satisfies consumer contract");w.geo.route_cache.clear();
s.cash.group=-1;check(!shopping_gem_route_hint(w,s),"no finite receipt grants no gold target field");s.cash.group=2;check(!shopping_gem_route_hint(w,s),"invalid receipt group cannot index geometry");s.cash.group=0;
s.investment_item=28;check(!shopping_gem_route_hint(w,s),"already funded return needs no acquisition route");s.investment_item=-1;
w.self.alive=false;check(!shopping_gem_route_hint(w,s),"dead actor has no acquisition advisory");w.self.alive=true;
w.self.gems=1;check(!shopping_gem_route_hint(w,s),"real carried score does not enter acquisition advisory");w.self.gems=0;
w.enemies.push_back(Actor{});check(!shopping_gem_route_hint(w,s),"current hostile observation declines elective quote routing");w.enemies.clear();
w.self.type=11;check(!shopping_gem_route_hint(w,s),"field shop champion does not get spawn investment route");w.self.type=3;
w.gold=35;check(shopping_gem_route_hint(w,s)==std::optional<Pos>(s.cash.capture),"existing receipt root precedes generic wallet fallback");
w.geo.goal_cache.clear();check(shopping_gem_route_hint(w,s)==std::optional<Pos>(s.cash.capture),"empty unrelated caches still request exact consumer root");
s.installed_gem.group=1;s.installed_gem.stage={7,7};s.installed_gem.until=50;
check(shopping_gem_route_hint(w,s)==std::optional<Pos>(Pos{7,7}),"real installed named return gets its completed-field preparation before another gold hypothesis");
w.geo.goal_cache[{w.geo.index({7,7}),0}]=1;check(!shopping_gem_route_hint(w,s),"known installed-stage field is reused without a duplicate search");
w.geo.goal_cache.clear();w.round=50;check(!shopping_gem_route_hint(w,s),"expired installed travel window cannot request continuing field work");
std::printf("%d cash route-hint checks passed\n",checks);}
