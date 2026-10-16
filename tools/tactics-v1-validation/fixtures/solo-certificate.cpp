#define TACTICS_SOLO_MODEL_ONLY
#define TACTICS_COORDINATION_MODEL_ONLY
#include "solo.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
static int checks=0;
static void yes(bool a,const char*why){++checks;if(!a){std::fprintf(stderr,"FAIL %s\n",why);std::exit(1);}}
static Actor issac(){Actor a;a.id=3;a.type=4;a.alive=true;a.hp=a.max_hp=900;a.strength=40;a.range=1;a.pos={0,0};a.can_attack=a.can_cast=true;a.spells[0].slot=0;a.spells[0].kind=1;a.spells[0].ready=a.spells[0].self=true;a.spells[0].cooldown=0;a.spells[0].recharge=8;return a;}
int main(){
    Camp wolf;wolf.id=0;wolf.pos={1,0};wolf.hp=1350;wolf.strength=20;wolf.range=3;
    auto a=issac();auto q=certify_solo_clear(a,wolf,a.pos,0,true);
    yes(q.known&&q.feasible&&q.clear_ticks==30&&q.remaining_hp==320,"30owner reset clear pays29 future camp phases with unchanged25percent reserve");
    a.monster=true;q=certify_solo_clear(a,wolf,a.pos,0,true);
    yes(q.known&&q.feasible&&q.clear_ticks<30,"first Monster family applies10percent actual camp damage once");
    a.monster=false;
    a.hp=774;q=certify_solo_clear(a,wolf,a.pos,0,true);
    yes(q.known&&!q.feasible,"same75percent currentHP budget preserved at equality boundary");
    a=issac();q=certify_solo_clear(a,wolf,a.pos,0,true,95);
    yes(q.known&&!q.feasible,"enemy reply remains additional reserve");
    a=issac();a.spells[0].ready=false;a.spells[0].cooldown=2;
    auto later=certify_solo_clear(a,wolf,a.pos,2,false);
    auto ready=certify_solo_clear(issac(),wolf,a.pos,0,true);
    yes(later.known&&later.feasible&&later.clear_ticks==ready.clear_ticks,"only known elapsed owner ends restore reset");
    q=certify_solo_clear(a,wolf,a.pos,0,false);
    yes(!q.known,"no free prospective cast on current turn");
    a=issac();a.spells[0].ready=false;a.spells[0].cooldown=-1;
    q=certify_solo_clear(a,wolf,a.pos,3,false);
    yes(q.known&&q.feasible&&q.clear_ticks==34,"unknown reset timer uses34actual basics rather than invented ready reset");
    a=issac();a.hp=500;a.shield=10000;q=certify_solo_clear(a,wolf,a.pos,1,false);
    yes(!q.feasible,"current shield is discarded rather than invented durableHP");
    a=issac();a.can_attack=a.can_cast=false;q=certify_solo_clear(a,wolf,a.pos,0,true);
    yes(!q.known,"spent actual permissions cannot authorize first hit");
    a=issac();a.pos={-5,0};q=certify_solo_clear(a,wolf,a.pos,0,true);
    yes(!q.known,"outofrange body cannot certify stationary DPS");
    q=certify_solo_clear(a,wolf,{0,0},2,false);
    yes(q.known&&q.feasible,"explicit future legal stage uses actualkit not currentfaraway DPS");
    wolf.awake=true;
    a=issac();a.can_attack=a.can_cast=false;wolf.hp=200;
    q=certify_solo_clear(a,wolf,a.pos,1,false,0,64,true);
    yes(q.known&&q.feasible&&q.damage_taken==80,"spent incumbent pays awake idle reply plus three later responses");
    q=certify_solo_clear(a,wolf,{0,1},1,false,0,64,true);
    yes(!q.known,"awake incumbent cannot certify movement to a future tile");
    q=certify_solo_clear(a,wolf,a.pos,2,false,0,64,true);
    yes(!q.known,"awake incumbent may wait at most the next owner");
    wolf.hp=1350;q=certify_solo_clear(issac(),wolf,{0,0},0,true);
    yes(!q.known,"awake camp requires actual incumbent model rather than sleepingquote");wolf.awake=false;
    q=certify_solo_clear(issac(),wolf,{0,0},0,true,0,5);
    yes(!q.known,"workcap is unknown never unsafeorready by default");
    a=issac();a.id=2;a.type=3;a.hp=a.max_hp=700;a.strength=30;a.range=3;a.spells={};a.spells[0].kind=2;a.spells[0].ready=a.spells[0].camps=true;a.spells[0].amount=140;a.spells[0].range=4;a.spells[0].cooldown=0;a.spells[0].recharge=8;
    q=certify_solo_clear(a,wolf,{0,0},0,true);
    yes(q.known&&q.feasible&&q.clear_ticks==27&&q.damage_taken==520&&q.remaining_hp==180,
        "Cassi27owner Wolf clear pays26actual future phases and honestly preserves25percent reserve");
    a.hp=694;q=certify_solo_clear(a,wolf,{0,0},0,true);
    yes(q.known&&!q.feasible,"same Cassi Wolf clear still fails exact existing reserve below boundary");
    a.hp=700;wolf.awake=true;
    q=certify_solo_clear(a,wolf,{0,0},0,true,0,64,true);
    yes(q.known&&q.feasible&&q.damage_taken==520,"awake current snapshot does not repay already reflected camp upkeep");
    a.can_attack=a.can_cast=false;
    q=certify_solo_clear(a,wolf,{0,0},1,false,0,64,true);
    yes(q.known&&!q.feasible&&q.damage_taken==540,"awake next-owner wait still pays its extra real camp phase");
    wolf.hp=1;wolf.strength=1000;a=issac();
    q=certify_solo_clear(a,wolf,{0,0},0,true,0,64,true);
    yes(q.known&&q.feasible&&q.clear_ticks==1&&q.damage_taken==0,"current atomic camp kill precedes any future camp reply");
    a.can_attack=a.can_cast=false;
    q=certify_solo_clear(a,wolf,{0,0},1,false,0,64,true);
    yes(q.known&&!q.feasible,"awake delayed atomic kill cannot avoid a real intervening lethal response");
    std::printf("%d solo certificate checks passed\n",checks);
}
