#pragma once
#include "observe.h"
#include "weights.h"
#include "map-seed.h"
#include <cmath>
#include <type_traits>
#ifndef PPO_ENABLED
#define PPO_ENABLED 1
#endif
inline unsigned ppo_calls=0,ppo_changes=0,ppo_choices=0,ppo_last_round=0;
template<class U> U ppo_target(const U& original) {
    namespace bc=cambc;
    if(!PPO_ENABLED||bc::fuel_remaining()<50000||ppo_last_round==bc::round_number())return original;
    ppo_last_round=bc::round_number();
    // Most attacks have only one eligible target. Reject those before building
    // the full observation, preserving the strategic controller's fuel reserve.
    auto targets=bc::self().attack_tiles();
    if constexpr(std::is_same_v<U,bc::camp>)targets&=bc::vision::camp_tiles();
    else targets&=bc::vision::champion_tiles(bc::team::enemy);
    if(targets.count()<2)return original;
    auto frame=observe(false);std::array<bool,actor::K> allowed{};int count=0;
    for(int k=0;k<frame.input.count;k++) {
        const auto& c=frame.input.candidates[k];if(!c[2])continue;
        auto p=bc::vec2{frame.info.x+int(c[4]*8),frame.info.y+int(c[5]*8)};
        if constexpr(std::is_same_v<U,bc::camp>) {
            if(!c[9])continue;
            for(auto target:frame.camps)if(target.position()==p) {
                allowed[k]=target.kind()==original.kind()||target.is_gem_cluster()||target.is_gold_cluster();
            }
        }else {
            if(!c[8]||bc::map::spawn_region(bc::team::enemy).is_set(p))continue;
            // Preserve guaranteed finishing hits chosen by the strategic controller.
            allowed[k]=original.health()>bc::self().strength()*1.5f||p==original.position();
        }
        count+=allowed[k];
    }
    if(count<2||bc::fuel_remaining()<40000)return original;
    static const auto model=[] {actor::Policy p;p.weights=trained::weights;return p;}();
    const auto result=model.evaluate(frame.input);ppo_calls++;ppo_choices+=count;
    static unsigned state=map_seed()^(unit_id(bc::self())*0x9e3779b9u);
    state=1664525u*state+1013904223u;
    double maximum=-INFINITY;for(int k=0;k<actor::K;k++)if(allowed[k])maximum=std::max(maximum,double(result.scores[k]));
    std::array<double,actor::K> p{};double sum=0;for(int k=0;k<actor::K;k++)if(allowed[k]){p[k]=std::exp(double(result.scores[k])-maximum);sum+=p[k];}
    double u=(double(state)+.5)/4294967296.*sum;int selected=0;
    for(int k=0;k<actor::K;k++)if(allowed[k]){selected=k;u-=p[k];if(u<=0)break;}
    const auto& c=frame.input.candidates[selected];auto point=bc::vec2{frame.info.x+int(c[4]*8),frame.info.y+int(c[5]*8)};
    if constexpr(std::is_same_v<U,bc::camp>) {
        for(auto target:frame.camps)if(target.position()==point){ppo_changes+=unit_id(target)!=unit_id(original);return target;}
    }else {
        for(auto target:frame.enemies)if(target.position()==point){ppo_changes+=unit_id(target)!=unit_id(original);return target;}
    }
    return original;
}
