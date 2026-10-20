#pragma once
#include "observe.h"
#include <cmath>
#include <span>

inline std::uint32_t map_seed() {
    namespace bc=cambc;
    std::uint32_t seed=2166136261u;
    auto mix=[&](std::uint32_t n){seed=(seed^n)*16777619u;};
    mix(bc::map::width());mix(bc::map::height());
    const std::array boards{bc::map::walls(),bc::map::holes(),bc::map::altars()};
    for(unsigned i=0;i<boards.size();i++) {
        mix(i+1);
        // Packed public terrain avoids sorting thousands of tiles on a large map.
        for(auto byte:boards[i].export_linear_buffer())mix(byte);
    }
    return seed;
}
struct Sample { int index;std::uint32_t before,after; };
inline Sample sample(const actor::Result& scores,const actor::Input& input) {
    namespace bc=cambc;
    std::array<std::uint32_t,2> memory{};bc::shared_memory.read(0,std::span{memory});
    if(memory[0]!=0x5336524eu)memory={0x5336524eu,map_seed()^(bc::detail::absolute_team(bc::team::ally)?0x9e3779b9u:0u)};
    const auto before=memory[1];memory[1]=1664525u*before+1013904223u;
    bc::shared_memory.write(0,std::span{memory});
    double maximum=-INFINITY;for(int k=0;k<actor::K;k++)if(input.mask[k])maximum=std::max(maximum,double(scores.scores[k]));
    std::array<double,actor::K> p{};double sum=0;
    for(int k=0;k<actor::K;k++)if(input.mask[k]){p[k]=std::exp(double(scores.scores[k])-maximum);sum+=p[k];}
    double u=(double(memory[1])+.5)/4294967296.*sum;int chosen=0;
    for(int k=0;k<actor::K;k++)if(input.mask[k]){chosen=k;u-=p[k];if(u<=0)break;}
    return {chosen,before,memory[1]};
}
