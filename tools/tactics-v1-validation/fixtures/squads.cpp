#include "squads.h"
#include <cstdlib>
#include <iostream>

static int checks=0;
static void check(bool ok) {++checks;if(!ok){std::cerr<<"squad check "<<checks<<" failed\n";std::exit(1);}}
int main() {
    using namespace tactics;
    const std::vector<Contributor> crew{{1,10,1,true},{2,15,1,true},{3,30,1,true}};
    auto solo=minimum_ready_squad(crew,1,20,2);
    check(solo.ready && solo.ids==std::vector<int>{1} && solo.clear_ticks==2);
    auto pair=minimum_ready_squad(crew,1,60,2);
    check(pair.ready && pair.ids==std::vector<int>({1,3}) && pair.clear_ticks==2);
    auto triple=minimum_ready_squad(crew,1,100,2);
    check(triple.ready && triple.ids==std::vector<int>({1,2,3}));
    check(!minimum_ready_squad(crew,1,200,2).ready);
    const std::vector<Contributor> tie{{3,20,1,true},{1,10,1,true},{2,20,1,true}};
    check(minimum_ready_squad(tie,1,30,1).ids==std::vector<int>({1,2}));
    const std::vector<Contributor> cost{{1,10,1,true},{2,20,4,true},{3,20,1,true}};
    check(minimum_ready_squad(cost,1,30,1).ids==std::vector<int>({1,3}));
    auto unready=crew;unready[2].ready=false;
    check(!minimum_ready_squad(unready,1,60,2).ready);
    check(!minimum_ready_squad(crew,99,20,2).ready);
    auto duplicate=crew;duplicate.push_back(crew[1]);
    check(!minimum_ready_squad(duplicate,1,20,2).ready);
    std::vector<Contributor> too_many;
    for(int i=0;i<7;++i)too_many.push_back({i,10,1,true});
    check(!minimum_ready_squad(too_many,1,20,2).ready);
    check(minimum_ready_squad({{1,0,1,true}},1,0,0).ready);
    check(!minimum_ready_squad({{1,0,1,true}},1,10,2).ready);
    check(!minimum_ready_squad(crew,1,-1,2).ready);
    check(!minimum_ready_squad(crew,1,10,-1).ready);
    check(!minimum_ready_squad({{1,10,-1,true}},1,10,2).ready);
    auto fast=minimum_ready_squad({{1,10,1,true},{2,90,1,true},{3,15,1,true}},1,40,2);
    check(fast.ready && fast.ids==std::vector<int>({1,2}) && fast.person_turn_cost==2);
    std::cout<<"squad checks passed: "<<checks<<'\n';
    return 0;
}
