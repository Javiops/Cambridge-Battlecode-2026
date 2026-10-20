// bc-actor-v1: replace random candidate scores with Stage 3 cloned scores; expect movement recall above the random control.
#include <cstdio>
#include <stdexcept>
#include <string>
#include "observe.h"
#include "weights.h"

namespace bc = cambc;
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

void trace(const Frame& frame,const actor::Result& result,const Action& action,unsigned budget,unsigned kernel) {
    auto json="[{\"action\":"+action.json+",\"code\":0,\"result\":"+(action.result?"true":"false")+"}]";
    const std::array<std::uint32_t,8> header{bc::round_number(),unit_id(bc::self()),budget,kernel,static_cast<std::uint32_t>(budget-bc::fuel_remaining()),
        static_cast<std::uint32_t>(result.chosen),static_cast<std::uint32_t>(frame.moves.size()),static_cast<std::uint32_t>(json.size())};
    std::fwrite("S1B!",1,4,stdout);std::fwrite(header.data(),4,header.size(),stdout);
    std::fwrite(frame.input.features.data(),4,actor::G,stdout);
    std::fwrite(frame.input.candidates.data(),4,actor::K*actor::C,stdout);
    std::fwrite(frame.input.mask.data(),1,actor::K,stdout);
    std::fwrite(result.scores.data(),4,actor::K,stdout);
    for(auto p:frame.moves){std::fwrite(&p.x,4,1,stdout);std::fwrite(&p.y,4,1,stdout);}
    std::fwrite(json.data(),1,json.size(),stdout);std::fflush(stdout);
}

int main() {
    actor::Policy model;model.weights=trained::weights;bool first=true;
    const std::array picks{bc::champion_draft::ryth,bc::champion_draft::prism,bc::champion_draft::heart_of_ruin,
                          bc::champion_draft::tavi,bc::champion_draft::cassi_and_issac};
    while(true) {
        if(bc::is_draft()) {
            bc::draft::pick(picks.at(bc::draft::current_draft(bc::team::ally).size()));
        } else {
            auto budget=first?200000u:100000u;unsigned kernels=0;
            for(int decision=0;decision<2;decision++) {
                auto start=bc::fuel_remaining();auto frame=observe();auto result=model.evaluate(frame.input);
                auto kernel=start-bc::fuel_remaining();kernels+=kernel;
                auto action=execute(frame,result.chosen);
                if(decision==0&&bc::round_number()<=80)trace(frame,result,action,budget,kernel);
                if(result.chosen==0)break;
            }
            if(bc::round_number()<=80) {
                const std::array<std::uint32_t,5> footer{bc::round_number(),unit_id(bc::self()),budget,kernels,static_cast<std::uint32_t>(budget-bc::fuel_remaining())};
                std::fwrite("S3F!",1,4,stdout);std::fwrite(footer.data(),4,footer.size(),stdout);std::fflush(stdout);
            }
            first=false;
        }
        bc::end_turn();
    }
}
