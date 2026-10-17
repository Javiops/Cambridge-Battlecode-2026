#define TACTICS_COORDINATION_MODEL_ONLY
#define TACTICS_SOLO_MODEL_ONLY
#include "solo.h"
#include <cstdio>
#include <stdexcept>
using namespace tactics;
static int count=0;
static void check(bool value,const char* message){++count;if(!value)throw std::runtime_error(message);}
int main(){Actor actual;actual.id=0;actual.alive=true;actual.can_move=true;actual.pos={1,1};actual.hp=actual.max_hp=1000;actual.strength=100;actual.range=1;actual.move_speed=1;actual.camp_mitigation=actual.mitigation=1;actual.channel=Channel::None;Camp camp;camp.id=0;camp.awake=true;camp.pos={3,1};camp.hp=camp.max_hp=350;camp.strength=20;camp.range=1;const std::array<Pos,2> path{{{1,1},{2,1}}};
 auto q=forecast_one_owner_awake_entry(actual,camp,path);
 check(q.known&&q.feasible,"one-owner future schedule known");check(q.prefix_damage==20,"one whole possible response, despite origin outside camp range");check(q.clear.clear_ticks==4&&q.clear.damage_taken==80&&q.clear.remaining_hp==920,"prefix1 plus3 future phases, no free current hit");check(q.actual_origin==actual.pos&&q.projected_stage==path.back()&&actual.pos==Pos{1,1},"actual origin never rewritten by projection");check(!actual.can_attack&&!actual.can_cast,"actual current flags were not given future readiness");
 actual.hp=100;auto boundary=forecast_one_owner_awake_entry(actual,camp,path);check(boundary.known&&!boundary.feasible,"full prefix included in original HP reserve");Actor stationary=actual;stationary.pos=path.back();stationary.can_attack=true;const auto now=certify_solo_clear(stationary,camp,stationary.pos,0,true,0,64,true);check(now.known&&now.feasible&&now.damage_taken==60,"stationary counterfactual feasible but one-owner prefix is not");
 actual.hp=1000;actual.shield=10000;auto shielded=forecast_one_owner_awake_entry(actual,camp,path);check(shielded.clear.damage_taken==80&&shielded.clear.remaining_hp==920,"temporary shield gives no prefix or clear credit");
 actual.spells[0].kind=1;actual.spells[0].self=true;actual.spells[0].cooldown=1;actual.spells[0].recharge=5;auto reset=forecast_one_owner_awake_entry(actual,camp,path);check(reset.known&&reset.feasible&&reset.clear.clear_ticks==3&&reset.clear.damage_taken==60,"one elapsed owner matures known cooldown1 exactly once");
 actual.spells={};auto capped=forecast_one_owner_awake_entry(actual,camp,path,0,2);check(!capped.known&&!capped.feasible,"unfinished bounded clear stays Unknown");
 const std::array<Pos,3> two{{{1,1},{1,2},{2,1}}};check(!forecast_one_owner_awake_entry(actual,camp,two).known,"two movement steps cannot become a speed1 one-owner entry");
 for(int kind=0;kind<7;++kind){Actor a=actual;if(kind==0)a.can_move=false;if(kind==1)a.completed=true;if(kind==2)a.stunned=true;if(kind==3)a.alive=false;if(kind==4)a.channel=Channel::Recall;if(kind==5)a.move_speed=0;if(kind==6)a.move_speed=9;check(!forecast_one_owner_awake_entry(a,camp,path).known,"unavailable movement cannot forecast entry");}
 auto asleep=camp;asleep.awake=false;check(!forecast_one_owner_awake_entry(actual,asleep,path).known,"helper specifically models awake prefix");auto far=camp;far.pos={4,1};check(!forecast_one_owner_awake_entry(actual,far,path).known,"future endpoint must actually reach basic range");const std::array<Pos,2> jump{{{1,1},{3,1}}};check(!forecast_one_owner_awake_entry(actual,camp,jump).known,"nonadjacent path is not a proven walk");
 std::printf("%d awake arrival checks passed\n",count);}
