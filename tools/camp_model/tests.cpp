#include "src/camp_forecast.h"
#include <cassert>
#include <cstdio>
using namespace camp_forecast;
int main(){
    // A sole champion against an elk should not be declared survivable.
    Unit solo{}; solo.id=1; solo.x=0;solo.y=0;solo.range=1;solo.health=200;solo.max_health=200;solo.basic=100;
    Monster elk{1,0,2400,60};
    auto a=predict(&solo,1,&elk,1,false,40);
    assert(a.first_death>0 && a.victim==1 && !a.cleared);
    // No incoming strength: clears safely.
    elk={1,0,400,0};
    auto b=predict(&solo,1,&elk,1,false,40);
    assert(b.cleared && b.first_death<0);
    // Jungle reduces received damage, monster emblem boosts attack.
    elk={1,0,600,50}; solo.health=350;solo.max_health=350;solo.basic=120;
    solo.taken_mult=0.7f;solo.dealt_mult=1.1f;
    auto c=predict(&solo,1,&elk,1,false,40);
    assert(c.cleared && c.first_death<0);
    // Varg hits adjacent monsters exactly once each.
    Monster wolves[2]={{1,0,200,0},{1,1,200,0}};
    solo.basic=100;solo.health=800;solo.max_health=800; solo.varg=true;solo.taken_mult=1;solo.dealt_mult=1;
    auto d=predict(&solo,1,wolves,2,false,40);
    assert(d.cleared && d.turns==2);
    // Ranged attack already in range should not require movement.
    solo={};solo.id=7;solo.x=0;solo.y=0;solo.health=2000;solo.max_health=2000;solo.basic=120;solo.range=3;
    elk={3,0,200,40};
    auto e=predict(&solo,1,&elk,1,false,40);
    assert(e.cleared && e.moved_steps==0 && e.confident);
    // Out-of-range ally: simulated path MUST be marked uncertain.
    solo.x=8;elk={0,0,600,0};
    auto f=predict(&solo,1,&elk,1,false,40);
    assert(f.moved_steps>0 && !f.confident);
    // Target-focused damage: nearest low-HP unit dies while far ally survives.
    Unit pair[2]={{1,0,0,1,100,100,50,0,1,1,false,true},
                  {2,3,2,3,1000,1000,200,0,1,1,false,true}};
    elk={1,0,500,100};
    auto g=predict(pair,2,&elk,1,false,40);
    assert(g.first_death>0 && g.victim==1);
    std::printf("PASS: 7 bounded camp forecast test cases\n");
}
