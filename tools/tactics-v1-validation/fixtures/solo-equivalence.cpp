#define TACTICS_SOLO_MODEL_ONLY
#define TACTICS_COORDINATION_MODEL_ONLY
#include "solo.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
static unsigned seed=987122;static unsigned rnd(){seed=seed*1664525u+1013904223u;return seed;}
int main(){int certified=0;for(int test=0;test<4000;++test){
    Actor a;a.id=1;a.alive=true;a.hp=a.max_hp=500+rnd()%8000;a.strength=20+rnd()%150;
    a.range=1+rnd()%4;a.pos={0,0};a.can_attack=rnd()%2;a.can_cast=rnd()%2;
    a.camp_mitigation=.5+.1*(rnd()%6);
    for(int slot=0;slot<2;++slot){auto &s=a.spells[slot];s.slot=slot;s.kind=rnd()%5;
        s.camps=true;s.self=s.kind==1;s.range=1+rnd()%5;s.radius=rnd()%3;s.ground=s.kind==3;
        s.amount=s.kind>=2?30+rnd()%250:0;s.cooldown=rnd()%9;s.ready=s.cooldown==0;
        s.recharge=2+rnd()%9;}
    // Cassi/Issac offensive singleton kits have one damage/reset cast, with
    // a utility other slot. Mixed reset+damage kits use farm's different legal
    // basic-first cast preference and need not match general greedy rollout.
    a.spells[1]=Spell{};
    Camp c;c.id=10;c.pos={1,0};c.hp=100+rnd()%5000;c.strength=rnd()%61;c.range=rnd()%5;
    const double enemy=rnd()%50;
    const auto scalar=certify_solo_clear(a,c,a.pos,0,true,enemy,128);
    if(!scalar.feasible)continue;
    CampClearBody body;body.actor=a;body.enemy_reply=enemy;
    std::array<CampClearMonster,1> monster{{{c,true}}};
    const auto general=rollout_camp_clear(std::span(&body,1),monster,1,4096);
    if(!general.ready||general.ticks>scalar.clear_ticks+1e-8||
        scalar.damage_taken+enemy+1>=.75*a.hp){
        std::fprintf(stderr,"FAIL singleton equivalence %d generalready%d %.0f scalar%.0f\n",test,general.ready,general.ticks,scalar.clear_ticks);return 1;}
    ++certified;
    }
    if(certified<100){std::fprintf(stderr,"FAIL meaningful certified examples\n");return 1;}
    std::printf("4000 scalar singleton checks passed (%d certified schedules)\n",certified);
}
