#pragma once
#include "observe.h"
#include <optional>

struct Command { unsigned kind=0; int a=0,b=0; }; // wait, move, attack, cast, submit
inline std::optional<Command> banking(const Frame& f) {
    namespace bc=cambc;
    const auto& m=f.info;const bc::vec2 here{m.x,m.y};
    if(!(m.state&1)||(m.state&(2|4|4096)))return Command{};
    const auto gems=bc::self().gem_count();
    const bool returning=gems>=40||(bc::round_number()>=1600&&gems>0);
    struct Goal { bc::vec2 p; int radius; };std::vector<Goal> goals;
    if(returning) {
        for(auto p:altars())if(p.chebyshev_distance(here)<=1&&!(m.state&(64|128)))return Command{4,p.x,p.y};
        if(!(m.state&8))return Command{};
        for(auto p:altars())goals.push_back({p,1});
    } else {
        for(auto c:f.enemies)if(c.health()>0&&c.position().chebyshev_distance(here)<=6)return std::nullopt;
        for(auto c:f.camps)if(c.health()>0&&c.position().chebyshev_distance(here)<=m.attack_range)return std::nullopt;
        if(!(m.state&8))return std::nullopt;
        for(auto c:f.camps)if(c.health()>0)goals.push_back({c.position(),m.attack_range});
        if(goals.empty()) {
            const unsigned phase=(bc::round_number()/200+unit_id(bc::self()))%4;
            goals.push_back({{bc::map::width()*(phase&1?3:1)/4,bc::map::height()*(phase==1||phase==2?3:1)/4},2});
        }
    }
    static const auto terrain=bc::map::walls()|bc::map::holes()|bc::map::altars();
    auto blocked=terrain;
    for(auto c:bc::vision::champions())if(c.health()>0&&c.position()!=here)blocked.set(c.position());
    for(auto c:f.camps)if(c.health()>0&&c.position()!=here)blocked.set(c.position());
    bc::bitboard roots,destinations;
    for(auto goal:goals)roots.draw_chebyshev(goal.p,goal.radius);
    roots&=~blocked;
    for(auto p:f.moves)if(p.chebyshev_distance(here)==1)destinations.set(p);
    if(destinations.is_empty())return Command{};
    bc::distance_field distances;bc::bitboard visited;distances.compute_to(blocked,roots,destinations,visited);
    unsigned best=bc::distance_field::unreachable;Command command;
    for(auto p:f.moves)if(p.chebyshev_distance(here)==1) {
        auto d=distances.get(p);if(d<best){best=d;command={1,p.x,p.y};}
    }
    return command;
}
