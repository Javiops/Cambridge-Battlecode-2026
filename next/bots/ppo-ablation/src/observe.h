#pragma once
#include <cambc.h>
#include <algorithm>
#include <vector>
#include "policy.h"

struct Frame {
    actor::Input input;
    cambc::detail::champion_info info{};
    std::vector<cambc::vec2> moves;
    std::vector<cambc::champion> enemies;
    std::vector<cambc::camp> camps;
};
inline std::uint32_t unit_id(const cambc::champion& c) {return static_cast<std::uint32_t>(static_cast<cambc::handle_champion_t>(c));}
inline std::uint32_t unit_id(const cambc::camp& c) {return static_cast<std::uint32_t>(static_cast<cambc::handle_camp_t>(c));}

inline auto tile_order(cambc::vec2 a,cambc::vec2 b) {return a.y==b.y?a.x<b.x:a.y<b.y;}
inline std::vector<cambc::vec2> altars() {
    static auto result=[] {auto p=cambc::map::altars().positions();std::sort(p.begin(),p.end(),tile_order);return p;}();
    return result;
}

inline Frame observe(bool include_moves=true) {
    namespace bc=cambc;
    Frame f;auto& me=bc::self();auto& a=f.info;
    bc::detail::check(bc::detail::sdk_champion(unit_id(me),&a));
    auto allies=bc::vision::champions(bc::team::ally);
    f.enemies=bc::vision::champions(bc::team::enemy);f.camps=bc::vision::camps();
    std::sort(f.enemies.begin(),f.enemies.end(),[](const auto& a,const auto& b){return static_cast<bc::handle_champion_t>(a)<static_cast<bc::handle_champion_t>(b);});
    std::sort(f.camps.begin(),f.camps.end(),[](const auto& a,const auto& b){return static_cast<bc::handle_camp_t>(a)<static_cast<bc::handle_camp_t>(b);});
    if(include_moves&&(a.state&8)) {
        auto blocked=bc::map::walls()|bc::map::holes()|bc::map::altars()|bc::map::spawn_region(bc::team::enemy)|
            bc::vision::champion_tiles()|bc::vision::camp_tiles()|bc::vision::teleport_tiles();
        blocked.set({a.x,a.y},false);
        for(auto p:blocked.reachable_tiles({a.x,a.y},a.move_speed).positions())if(p!=bc::vec2{a.x,a.y})f.moves.push_back(p);
        std::sort(f.moves.begin(),f.moves.end(),tile_order);
    }
    auto altar=altars()[0];
    for(auto p:altars())if(p.chebyshev_distance({a.x,a.y})<altar.chebyshev_distance({a.x,a.y}))altar=p;
    const float w=bc::map::width(),h=bc::map::height();
    auto& g=f.input.features;
    g={a.health/std::max(1.f,a.max_health),a.strength/200,a.focus/200,me.gem_count()/100.f,me.gold_count()/1000.f,
       a.x/w,a.y/h,bc::round_number()/2000.f,float(bool(a.state&8)),float(bool(a.state&16)),float(bool(a.state&2048)),
       a.attack_range/8.f,a.move_speed/3.f,f.enemies.size()/10.f,allies.size()/10.f,f.camps.size()/20.f,a.type/12.f,
       float(bool(a.state&(2|4|4096))),float(bool(a.state&1)),bc::vision::visible_tiles().count()/512.f,
       (altar.x-a.x)/w,(altar.y-a.y)/h,bc::global_submitted_gems(bc::team::ally)/1000.f,
       bc::global_submitted_gems(bc::team::enemy)/1000.f};
    for(auto& v:g)v=std::clamp(v,-4.f,4.f);
    auto add=[&](actor::Candidate c){auto i=f.input.count++;f.input.candidates[i]=c;f.input.mask[i]=true;};
    add({1,0,0,0,0,0,0,0,0,0,0,1});
    for(auto ability:me.abilities())if(ability.is_ready()&&((ability.is_attack_reset()&&!me.can_attack())||(ability.is_shield()&&ability.can_target_self())))
        add({0,0,0,1,0,0,0,a.health/2000,0,0,ability.slot()/2.f,1});
    int attacked=0;
    auto target=[&](const auto& t,int kind){
        auto p=t.position();auto distance=p.chebyshev_distance({a.x,a.y});
        if(attacked<4 && distance<=a.attack_range && t.health()>0) {
            add({0,0,1,0,(p.x-a.x)/8.f,(p.y-a.y)/8.f,distance/8.f,t.health()/2000,
                 float(kind==1),float(kind==2),0,1});attacked++;
        }
    };
    if(a.state&16){for(const auto& t:f.enemies)target(t,1);for(const auto& t:f.camps)target(t,2);}
    for(auto p:f.moves)if(p.chebyshev_distance({a.x,a.y})==1 && f.input.count<actor::K)
        add({0,1,0,0,(p.x-a.x)/8.f,(p.y-a.y)/8.f,1/8.f,0,0,0,0,1});
    return f;
}
