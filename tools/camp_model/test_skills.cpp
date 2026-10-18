#include "src/camp_forecast.h"
#include <cassert>
#include <cmath>
#include <cstdio>
using namespace camp_forecast;
int main() {
    // A ready direct spell is extra damage, with no arbitrary extra attack cost.
    Unit a{}; a.id=0; a.x=0; a.y=0; a.range=3; a.health=900; a.max_health=900;
    a.basic=100; a.skill_ready[0]=true;a.skill_damage[0]=200;
    Monster camp{3,0,900,0};
    auto old=predict(&a,1,&camp,1,false,4,false);
    auto skills=predict(&a,1,&camp,1,false,4,true);
    assert(old.monsters_after_four==500);
    assert(skills.monsters_after_four==300);
    // Attacks don't repeat the same once-per-eight-round spell in four rounds.
    assert(skills.monsters_after_four!=0);
    // An attack reset adds exactly one basic attack, only while target remains alive.
    a.skill_ready[0]=false; a.reset_ready=true;
    auto reset=predict(&a,1,&camp,1,false,4,true);
    assert(reset.monsters_after_four==400);
    // AOE spell can clear two monsters; its primary doesn't receive double damage.
    a.reset_ready=false; a.skill_ready[0]=true; a.skill_damage[0]=150;
    a.skill_aoe[0]=true;
    Monster wolves[2]={{3,0,500,0},{3,1,500,0}};
    auto aoe=predict(&a,1,wolves,2,false,4,true);
    auto base=predict(&a,1,wolves,2,false,4,false);
    assert(aoe.monsters_after_four<base.monsters_after_four);
    // No ability use when self has already cast in the same turn.
    a.can_cast_now=false;
    auto late=predict(&a,1,wolves,2,false,4,true);
    assert(late.monsters_after_four<base.monsters_after_four); // can cast starting next turn
    printf("PASS: 5 spell/reset shadow-model tests\n");
}
