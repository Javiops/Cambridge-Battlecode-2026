#define TACTICS_COORDINATION_MODEL_ONLY
#include "coordination.h"
#include <cstdlib>
#include <iostream>
using namespace tactics;
static int checks = 0;
static void check(bool ok) {
    ++checks;
    if (!ok) {
        std::cerr << "FAIL coordination " << checks << '\n';
        std::exit(1);
    }
}
static CampClearBody body(int id, double hp=100, double strength=10, Pos pos={0,0}) {
    CampClearBody b;
    auto &a=b.actor;
    a.id=id;a.alive=true;a.hp=hp;a.max_hp=hp;a.strength=strength;
    a.pos=pos;a.range=5;a.can_attack=true;a.can_cast=true;a.camp_mitigation=1;
    return b;
}
static CampClearMonster monster(int id, double hp, double strength, Pos pos={1,0}, int range=5) {
    CampClearMonster m;
    m.camp.id=id;m.camp.hp=hp;m.camp.strength=strength;m.camp.pos=pos;m.camp.range=range;
    return m;
}
static Spell spell(int kind, double amount, int recharge=6) {
    Spell s;s.kind=kind;s.amount=amount;s.range=5;s.camps=true;s.ready=true;
    s.cooldown=0;s.recharge=recharge;
    return s;
}
int main() {
    auto a=body(1,50);
    std::vector<CampClearMonster> two{monster(10,10,10),monster(11,100,1)};
    auto r=rollout_camp_clear(std::vector{a},two,1);
    check(r.ready && r.complete && r.ticks==11);
    check(r.damage_taken==std::vector<double>{21}); // Dead first member stops attacking.
    check(r.remaining_hp==std::vector<double>{29});
    auto b=body(2);
    r=rollout_camp_clear(std::vector{body(1),b},
                         std::vector{monster(10,10,0),monster(11,10,0),monster(12,10,0)},1);
    check(r.ready && r.ticks==2); // Several bodies can finish separate targets in one round.
    a=body(1,20);a.actor.shield=15;
    check(rollout_camp_clear(std::vector{a},std::vector{monster(10,10,10)},1).ready);
    check(!rollout_camp_clear(std::vector{a},std::vector{monster(10,40,10)},1).ready);
    a=body(1,30);a.actor.max_hp=50;a.actor.spells[0]=spell(5,50);a.actor.spells[0].self=true;
    r=rollout_camp_clear(std::vector{a},std::vector{monster(10,30,10)},1);
    check(r.ready && r.ticks==3 && r.remaining_hp[0]==40); // Actual missing HP cap.
    a=body(1);a.actor.spells={spell(2,60),spell(2,60)};
    r=rollout_camp_clear(std::vector{a},std::vector{monster(10,100,0)},1);
    check(r.ready && r.ticks==2); // Two ready spells share one cast budget.
    a=body(1);a.actor.spells[0]=spell(1,0);
    check(rollout_camp_clear(std::vector{a},std::vector{monster(10,30,0)},1).ticks==2);
    a.actor.can_attack=false;
    check(rollout_camp_clear(std::vector{a},std::vector{monster(10,10,0)},1).ticks==1);
    a.actor.spells[0]=spell(2,10);
    check(rollout_camp_clear(std::vector{a},std::vector{monster(10,10,0)},1).ready);
    a=body(1,30,10,{3,0});b=body(2,100,10,{1,0});
    r=rollout_camp_clear(std::vector{a,b},std::vector{monster(10,100,10,{0,0},3)},1);
    check(r.ready && r.ticks==5 && r.damage_taken[0]==0 && r.damage_taken[1]==50);
    a.actor.pos={-1,0};a.actor.hp=40;
    check(!rollout_camp_clear(std::vector{a,b},std::vector{monster(10,100,10,{0,0},3)},1).ready);
    a=body(1);a.enemy_reply=95;
    check(!rollout_camp_clear(std::vector{a},std::vector{monster(10,10,5)},1).ready);
    a=body(1);a.actor.pos={20,20};
    r=rollout_camp_clear(std::vector{a},std::vector{monster(10,10,0)},1);
    check(!r.ready && r.uncertain); // A remote claim supplies no free attack or movement.
    a=body(1);a.actor.can_attack=false;a.actor.can_cast=false;
    check(!coordination_detail::useful_now(a.actor,std::vector{monster(10,10,0)}));
    a.actor.can_attack=true;a.actor.completed=true;
    check(!coordination_detail::useful_now(a.actor,std::vector{monster(10,10,0)}));
    a=body(1);auto unknown=monster(10,10,0);unknown.observed=false;
    check(!rollout_camp_clear(std::vector{a},std::vector{unknown},1).ready);
    check(!rollout_camp_clear(std::vector{a,a},std::vector{monster(10,10,0)},1).ready);
    check(!rollout_camp_clear(std::vector{a},std::vector{monster(10,10,0)},2).ready);
    r=rollout_camp_clear(std::vector{a},std::vector{monster(10,10000,0)},1);
    check(!r.ready && r.uncertain && r.ticks<=128); // Work bound, no invented impossibility.
    check(rollout_camp_clear(std::vector{a},std::vector<CampClearMonster>{},1).ready);
    r=rollout_camp_clear(std::vector{body(1,100)},std::vector{monster(10,110,1)},1);
    check(r.ready && r.ticks==11); // Safe single-member clear must not be truncated at six rounds.
    auto bad=monster(10,-1,0);
    check(!rollout_camp_clear(std::vector{a},std::vector{bad},1).ready);
    a.actor.camp_mitigation=.1;
    check(rollout_camp_clear(std::vector{a},std::vector{monster(10,50,100)},1).ready);
    r=rollout_camp_clear(std::vector{body(1)},std::vector{monster(10,50,0)},1,0);
    check(!r.ready && r.uncertain); // Exhaustion is not a fabricated feasible crew.
    check(coordination_detail::essential_help_lost(true,false,true));
    check(!coordination_detail::essential_help_lost(false,false,true));
    check(!coordination_detail::essential_help_lost(true,true,true));
    check(!coordination_detail::essential_help_lost(true,false,false));
    CampRollout small,large;small.ready=true;small.selected_ids={1};
    large.ready=true;large.selected_ids={1,2};
    check(!prefer_local_crew(small,large,1,10,false));
    check(prefer_local_crew(small,large,1,10,true));
    small.ready=false;check(prefer_local_crew(small,large,1,10,false));
    check(stable_split_order(2,std::vector<int>{1,3}));
    check(!stable_split_order(1,std::vector<int>{2,3}));
    std::cout << checks << " coordination checks passed\n";
}



