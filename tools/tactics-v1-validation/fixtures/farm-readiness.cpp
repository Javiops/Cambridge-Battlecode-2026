#include "farm_readiness.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
static int checks=0;
static void yes(bool value,const char *why){++checks;if(!value){std::fprintf(stderr,"FAIL %s\n",why);std::exit(1);}}
static Actor hero(){Actor a;a.id=1;a.alive=true;a.can_move=a.can_attack=a.can_cast=true;a.hp=a.max_hp=900;a.strength=40;a.range=1;a.pos={0,0};return a;}
int main(){
 Actor a=hero(); Camp elk;elk.id=10;elk.pos={4,0};elk.hp=2400;elk.strength=60;elk.range=3;
 std::vector<Camp> camps{elk};
 auto current=[&](bool exclusive=true){return current_camp_contribution(a,camps,exclusive);};
 yes(!current().ready&&current().dps==0,"outside own range cannot supply nominal self DPS");
 auto false_crew=CampContributor{{a.id,40,1,true},a.pos.x,a.pos.y,a.hp,1,0};
 const std::vector<CampPressure> pressure{{elk.pos.x,elk.pos.y,elk.range,elk.strength,true}};
 yes(minimum_ready_camp_squad({false_crew},a.id,elk.hp,pressure).ready,"counterexample reproduces invalid old caller certificate");
 false_crew.contribution=current();
 yes(!minimum_ready_camp_squad({false_crew},a.id,elk.hp,pressure).ready,"actual readiness prevents outside-range free-pressure certificate");
 a.pos={3,0};yes(current().ready&&current().dps==40,"actual in-range available basic is useful");
 false_crew={current(),a.pos.x,a.pos.y,a.hp,1,0};
 yes(!minimum_ready_camp_squad({false_crew},a.id,elk.hp,pressure).ready,"actual melee clear cannot afford full elk reply");
 a.can_attack=false;yes(!current().ready&&current().dps==0,"spent basic cannot count as ready helper");
 a.spells[0]={};auto &s=a.spells[0];s.kind=2;s.camps=true;s.ready=true;s.range=1;s.amount=100;s.recharge=5;
 yes(current().ready&&current().dps==60,"actual legal damage cast can start useful work");
 a.can_cast=false;yes(!current().ready,"ready spell metadata does not restore spent cast allowance");
 a.can_cast=true;a.completed=true;yes(!current().ready,"completed helper contributes no present damage");
 a.completed=false;a.stunned=true;yes(!current().ready,"stunned helper contributes no present damage");
 a.stunned=false;a.channel=Channel::Recall;yes(!current().ready,"channeling helper is not ready");a.channel=Channel::None;
 s.exclusive=true;yes(!current(false).ready,"already moved body cannot promise exclusive cast");
 s.exclusive=false;s.range=0;s.radius=4;yes(!current().ready,"direct CastCamp cannot borrow ground AoE radius");
 s.kind=3;s.ground=true;s.camps=false;s.range=1;
 yes(current().ready&&current().dps==60,"native ground-only damage can hit an in-range camp center");
 s.range=0;yes(!current().ready,"ground area cannot borrow its radius for center reach");
 s.kind=1;s.ground=false;s.self=true;s.camps=false;s.range=0;s.recharge=8;s.radius=0;
 yes(current().ready&&current().dps==45,"actual ready reset in basic range restores useful basic");
 a.can_cast=false;yes(!current().ready,"spent cast cannot supply ready reset");
 a.can_cast=true;s.ready=false;yes(!current().ready,"cooldown reset is future potential only");
 a.can_attack=true;yes(current().ready,"actual available basic remains ready despite reset cooldown");
 a.monster=true;yes(std::abs(current().dps-49.5)<1e-9,"camp damage passive applied once to existing contribution");
 a.alive=false;yes(!current().ready,"dead body contributes no damage");
 a=hero();camps[0].hp=0;yes(!current().ready,"dead camp is not a legal useful target");
 camps.push_back(elk);a.pos={3,0};yes(current().ready,"different living group member qualifies as direct target");
 Group group;group.spawns.push_back({10,0,{4,0},2400,60,3});std::vector<Group> groups{group};std::vector<GroupView> views(1);
 yes(potential_camp_pressure({1,0},groups,views,8),"unseen sleeping monster potential range blocks unnamed staging");
 yes(!potential_camp_pressure({0,0},groups,views,8),"outside all potential camp range permits reversible staging");
 Group neighbor;neighbor.spawns.push_back({11,0,{-3,0},1350,20,3});groups.push_back(neighbor);views.resize(2);
 yes(potential_camp_pressure({0,0},groups,views,8),"other group's sleeping camp also blocks staging");
 views[1].seen=8;views[1].state=Lifecycle::Reward;
 yes(!potential_camp_pressure({0,0},groups,views,8),"fresh reward has no living monster reply");
 views[0].seen=8;views[0].state=Lifecycle::Alive;views[0].camps.push_back(elk);views[0].camps[0].pos={10,0};
 yes(!potential_camp_pressure({1,0},groups,views,8),"observed actual position replaces original stale spawn");
 yes(potential_camp_pressure({7,0},groups,views,8),"actual observed monster reply zone retained asleep");
 views[0].known_dead.push_back(10);yes(!potential_camp_pressure({7,0},groups,views,8),"fresh proven dead member no longer blocks stage");
 std::printf("%d farm readiness checks passed\n",checks);
}
