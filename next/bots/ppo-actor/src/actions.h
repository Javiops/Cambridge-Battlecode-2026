#pragma once
#include <string>
struct Action { std::string json="{\"kind\":\"wait\"}"; bool result=true; };

// Execute exactly the proposal represented by the selected encoded candidate.
// No hidden macro heuristics, shopping, submission, or unsupported abilities.
Action execute(const Frame& frame, int selected) {
    auto& me=bc::self();const auto& c=frame.input.candidates.at(selected);
    if(c[0])return {};
    if(c[1]) {
        auto p=me.position()+bc::vec2{static_cast<int>(c[4]*8),static_cast<int>(c[5]*8)};
        return {"{\"kind\":\"move\",\"x\":"+std::to_string(p.x)+",\"y\":"+std::to_string(p.y)+"}",me.move_absolute(p)};
    }
    if(c[2]) {
        auto p=me.position()+bc::vec2{static_cast<int>(c[4]*8),static_cast<int>(c[5]*8)};
        if(c[8])for(const auto& t:frame.enemies)if(t.position()==p) {
            me.attack(t);return {"{\"kind\":\"attack\",\"target\":{\"kind\":1,\"id\":"+std::to_string(unit_id(t))+"}}",true};
        }
        if(c[9])for(const auto& t:frame.camps)if(t.position()==p) {
            me.attack(t);return {"{\"kind\":\"attack\",\"target\":{\"kind\":2,\"id\":"+std::to_string(unit_id(t))+"}}",true};
        }
    }
    if(c[3])for(auto ability:me.abilities())if(ability.slot()==static_cast<unsigned>(c[10]*2)) {
        auto text="{\"kind\":\"cast\",\"slot\":"+std::to_string(ability.slot());
        if(ability.is_attack_reset())return {text+"}",ability.use()};
        return {text+",\"target\":{\"kind\":1,\"id\":"+std::to_string(unit_id(me))+"}}",ability.use(me)};
    }
    throw std::runtime_error("Encoded candidate could not be mapped to an SDK action");
}

