#include "observation_detour.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
int main(){int checks=0;auto ck=[&](bool value,const char*why){++checks;if(!value){std::fprintf(stderr,"FAIL %s\n",why);std::exit(1);}};
 Actor actor;actor.id=5;actor.alive=true;actor.can_move=true;actor.hp=actor.max_hp=750;actor.move_speed=1;actor.pos={2,2};
 auto valid=[](Pos p){return p.x>=0&&p.y>=0&&p.x<8&&p.y<8;};
 auto field=[](Pos p){return distance(p,Pos{6,2});};
 auto legal=[](Pos){return true;};auto safe=[](Pos){return false;};auto funded=[](){return true;};
 auto quote=[&](Actor a){return observation_detour_step(a,valid,field,legal,safe,funded);};
 auto r=quote(actor);ck(r.known&&r.feasible&&r.after<r.before&&distance(actor.pos,r.at)==1,"complete adjacent strict field progress");
 r=observation_detour_step(actor,valid,field,legal,[](Pos p){return p==Pos{3,1};},funded);ck(r.known&&r.feasible&&r.at==Pos{3,2},"unsafe first geometric tie does not hide safe equal-rank adjacent step");
 r=observation_detour_step(actor,valid,field,legal,[](Pos){return true;},funded);ck(r.known&&!r.feasible,"sealed by potential pressure never invents a path");
 r=observation_detour_step(actor,valid,[](Pos){return -1;},legal,safe,funded);ck(!r.known&&!r.feasible,"missing completed field stays Unknown");
 r=observation_detour_step(actor,valid,[](Pos){return unreachable;},legal,safe,funded);ck(!r.known&&!r.feasible,"disconnected field does not fabricate progress");
 r=observation_detour_step(actor,valid,field,[](Pos){return false;},safe,funded);ck(r.known&&!r.feasible,"unseen occupied or failed tiles cannot be crossed");
 for(int state=0;state<5;++state){Actor a=actor;if(state==0)a.alive=false;if(state==1)a.completed=true;if(state==2)a.stunned=true;if(state==3)a.channel=Channel::Recall;if(state==4)a.can_move=false;r=quote(a);ck(!r.known&&!r.feasible,"actual movement permission required before any route");}
 int calls=0;r=observation_detour_step(actor,valid,field,legal,safe,[&]{return ++calls<7;});ck(!r.known&&!r.feasible,"budget or epoch interruption cannot publish partial best");
 r=observation_detour_step(actor,valid,field,legal,safe,funded,8);ck(!r.known&&!r.feasible,"node bound cutoff remains Unknown");
 r=observation_detour_step(actor,valid,field,[](Pos p){return p==Pos{3,3};},safe,funded);ck(r.known&&r.feasible&&r.at==Pos{3,3},"single legal diagonal has no hidden intermediate endpoint");
 r=observation_detour_step(actor,valid,[](Pos){return 4;},legal,safe,funded);ck(r.known&&!r.feasible,"equal or worsening endpoint cannot renew observation progress");
 actor.move_speed=2;r=quote(actor);ck(r.known&&r.feasible&&distance(actor.pos,r.at)==1,"boosted body still receives only entire adjacent safe leg");
 actor.pos={7,13};actor.move_speed=1;
 auto real_valid=[](Pos p){return p.x>=0&&p.y>=0&&p.x<72&&p.y<36;};
 auto real_field=[](Pos p){return distance(p,Pos{18,9});};
 auto real_legal=[](Pos p){for(Pos occupied:{Pos{5,11},Pos{5,12},Pos{5,13},Pos{6,13},Pos{5,10},Pos{9,8},Pos{9,9}})if(p==occupied)return false;return true;};
 auto real_pressure=[](Pos p){return distance(p,{9,8})<=3||distance(p,{9,9})<=3;};
 r=observation_detour_step(actor,real_valid,real_field,real_legal,real_pressure,funded);ck(r.known&&r.feasible&&r.at==Pos{8,13}&&r.before==11&&r.after==10,"retained Tavi snapshot has real safe progress around sleeping wolf rings");
 actor.pos={5,11};r=observation_detour_step(actor,real_valid,real_field,real_legal,real_pressure,funded);ck(r.known&&!r.feasible,"retained blocked Vendetta does not borrow another body's future vacancy");
 std::printf("%d observation detour checks passed\n",checks);
}
