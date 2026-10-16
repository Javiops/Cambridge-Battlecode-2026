#define TACTICS_COORDINATION_MODEL_ONLY
#include "coordination.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
static int checks=0;
static void check(bool value,const char *why){++checks;if(!value){std::fprintf(stderr,"FAIL %s\n",why);std::exit(1);}}
static Actor actor(int type=0){Actor a;a.id=1;a.type=type;a.pos={0,0};a.range=1;a.hp=a.max_hp=1000;a.strength=50;a.focus=100;a.alive=a.can_attack=a.can_cast=true;return a;}
static Camp camp(int id,Pos pos,double hp=100,double strength=0){Camp c;c.id=id;c.pos=pos;c.hp=c.max_hp=hp;c.strength=strength;c.range=3;return c;}
static CampRollout run(Actor a,const std::vector<Camp>&camps){CampClearBody b;b.actor=a;std::vector<CampClearMonster> m;for(auto c:camps)m.push_back({c,true});return rollout_camp_clear(std::span(&b,1),m,a.id,4096);}
int main(){
 auto a=actor();std::vector<Camp> group{camp(10,{1,0},500,0),camp(11,{1,1},2400,60),camp(12,{2,1},2400,60)};
 auto action=stationary_camp_action(a,group);
 check(action.kind==Kind::BasicCamp&&action.target==11,"remove attacking elk pressure before harmless gem cluster");
 a.can_attack=false;auto &area=a.spells[0];area.kind=3;area.ready=true;area.ground=true;area.camps=false;area.range=4;area.radius=1;area.amount=100;area.duration=1;area.recharge=8;area.cooldown=0;
 action=stationary_camp_action(a,group);
 check(action.kind==Kind::CastGround&&action.slot==0,"native ground-only Ryth area is available against camps");
 for(auto &c:group){check(camp_action_damage(a,action,group,c)==100,"native Ryth area hits each of three members");check(camp_action_control(a,action,group,c)==1,"native Ryth control includes each damaged member");}
 area.range=0;area.radius=4;
 check(stationary_camp_action(a,group).kind==Kind::None,"radius does not turn an out-of-range camp into a legal center");
 area.range=4;area.exclusive=true;
 check(stationary_camp_action(a,group,false).kind==Kind::None,"spent walking excludes current exclusive cast");
 check(stationary_camp_action(a,group,true,[]{return false;}).kind==Kind::None,"budget stop does not produce partial area choice");
 a=actor(10);action=stationary_camp_action(a,group);
 for(auto &c:group)check(camp_action_damage(a,action,group,c)==50,"native Varg primary and secondary each hit once");
 a.monster=true;check(std::abs(camp_action_damage(a,action,group,group[1])-55)<1e-9,"existing verified Monster multiplier applies once");
 std::vector<Camp> pair{camp(20,{1,0}),camp(21,{1,1})};
 auto r=run(actor(10),pair);check(r.ready&&r.ticks==2,"Varg splash clears both members in two owner opportunities");
 auto ren=actor(9);ren.strength=40;pair={camp(20,{1,0},100,10),camp(21,{1,1},100,10)};
 r=run(ren,pair);check(r.ready&&r.ticks==4,"Ren actual camp-phase return can finish the last member");
 check(r.damage_taken[0]==40&&r.remaining_hp[0]==960,"Ren receives four full actual camp hits");
 auto ryth=actor(0);ryth.strength=1;ryth.can_attack=false;ryth.spells[0].kind=3;ryth.spells[0].ready=true;ryth.spells[0].ground=true;ryth.spells[0].range=4;ryth.spells[0].radius=1;ryth.spells[0].amount=50;ryth.spells[0].duration=1;ryth.spells[0].recharge=8;ryth.spells[0].cooldown=0;
 pair={camp(20,{2,0},100,20),camp(21,{3,0},100,20)};
 r=run(ryth,pair);check(r.ready&&r.ticks==9,"known eight-end cast cooldown waits are real elapsed opportunities");
 check(r.damage_taken[0]==280,"one-round native area stun suppresses exactly next camp phase");
 auto spent=actor();spent.can_attack=spent.can_cast=false;
 r=run(spent,{camp(30,{1,0},50,10)});check(r.ready&&r.ticks==2&&r.damage_taken[0]==10,"spent actual permissions do not become free current damage");
 auto healer=actor(8);healer.spells[0].kind=5;healer.spells[0].ready=true;healer.spells[0].allies=true;healer.spells[0].range=4;healer.spells[0].amount=100;
 auto tank=actor(2);tank.id=2;tank.hp=260;pair={camp(30,{1,0},100,20)};std::array<Actor,2> crew{healer,tank};
 action=stationary_camp_support(healer,crew,pair);check(action.kind==Kind::CastChampion&&action.target==2,"actual support protects an observed ally crossing reserve");
 healer.can_cast=false;check(stationary_camp_support(healer,crew,pair).kind==Kind::None,"spent cast cannot promise necessary heal");
 std::printf("%d camp action checks passed\n",checks);
}
