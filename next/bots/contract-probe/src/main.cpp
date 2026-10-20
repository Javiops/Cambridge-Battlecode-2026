// contract-probe-v1: verify actor-only observations, action replay parity and two SIMD policy decisions within turn fuel.
#include <cambc.h>
#include <array>
#include <string>
#include <vector>
#include <cstdio>
#include "observe.h"

namespace bc=cambc;
struct Attempt {std::string action;int code=0;bool result=true;};
template<class Fn> void attempt(std::vector<Attempt>& a,std::string text,Fn fn) {
    if(a.size()>=2)return;
    Attempt r{std::move(text)};
    try{r.result=fn();}catch(const bc::error& e){r.code=static_cast<int>(e.code());r.result=false;}
    a.push_back(std::move(r));
}
std::string position(bc::vec2 p) {return "\"x\":"+std::to_string(p.x)+",\"y\":"+std::to_string(p.y);}

void script(const Frame& frame,std::vector<Attempt>& actions) {
    auto& me=bc::self();
    if(me.can_buy(bc::item_type::power_shard_of_strength,1))
        attempt(actions,"{\"kind\":\"buy\",\"item\":"+std::to_string(static_cast<int>(bc::item_type::power_shard_of_strength))+",\"count\":1}",[&]{me.buy(bc::item_type::power_shard_of_strength,1);return true;});
    if(!me.is_alive()||me.is_recalling()||me.is_submitting_gems()||me.is_teleporting())return;
    for(auto ability:me.abilities())if(ability.is_ready()&&((ability.is_attack_reset()&&!me.can_attack())||(ability.is_shield()&&ability.can_target_self()))) {
        auto text="{\"kind\":\"cast\",\"slot\":"+std::to_string(ability.slot());
        if(!ability.is_attack_reset()&&ability.can_target_self())text+=",\"target\":{\"kind\":1,\"id\":"+std::to_string(unit_id(me))+"}";
        text+="}";
        attempt(actions,text,[&]{return !ability.is_attack_reset()&&ability.can_target_self()?ability.use(me):ability.use();});
        break;
    }
    auto attack=[&](const auto& targets,int kind){
        if(!me.can_attack())return;
        for(const auto& t:targets)if(t.is_visible()&&t.health()>0&&me.attack_tiles().is_set(t.position())) {
            std::uint32_t handle=unit_id(t);
            attempt(actions,"{\"kind\":\"attack\",\"target\":{\"kind\":"+std::to_string(kind)+",\"id\":"+std::to_string(handle)+"}}",[&]{me.attack(t);return true;});
            return;
        }
    };
    attack(frame.enemies,1);attack(frame.camps,2);
    if(actions.size()>=2)return;
    auto p=me.position();
    if(me.gem_count()>0)for(auto altar:altars())if(p.chebyshev_distance(altar)<=bc::constants::submit_gems_range&&!bc::vision::has_altar_lock(altar)) {
        attempt(actions,"{\"kind\":\"submit\","+position(altar)+"}",[&]{me.submit_gems(altar);return true;});return;
    }
    if(!bc::map::spawn_region(bc::team::ally).is_set(p)&&me.health()<me.max_health()*.35f) {
        attempt(actions,"{\"kind\":\"recall\"}",[&]{me.recall();return true;});return;
    }
    if(!me.can_move())return;
    auto goals=altars();
    if(me.gem_count()==0) {
        static const auto spawns=[] {std::vector<bc::vec2> p;for(const auto& g:bc::map::camp_groups())for(auto tile:g.spawn_tiles().positions())p.push_back(tile);std::sort(p.begin(),p.end(),tile_order);return p;}();
        goals=spawns;
    }
    if(goals.empty())return;
    auto goal=*std::min_element(goals.begin(),goals.end(),[&](auto a,auto b){return a.chebyshev_distance(p)<b.chebyshev_distance(p);});
    auto best=p;
    for(auto tile:frame.moves)if(tile.chebyshev_distance(goal)<best.chebyshev_distance(goal))best=tile;
    if(best!=p)attempt(actions,"{\"kind\":\"move\","+position(best)+"}",[&]{return me.move_absolute(best);});
}

int main() {
    actor::Policy model;bool first=true;
    const std::array picks{bc::champion_draft::ryth,bc::champion_draft::prism,bc::champion_draft::heart_of_ruin,
                          bc::champion_draft::tavi,bc::champion_draft::cassi_and_issac};
    while(true) {
        if(bc::is_draft()) {
            auto chosen=bc::draft::current_draft(bc::team::ally);bc::draft::pick(picks.at(chosen.size()));
        } else if(bc::round_number()<=80) {
            const auto budget=first?200000u:100000u;
            const auto start=bc::fuel_remaining();
            auto frame=observe();auto result=model.evaluate(frame.input);
            // Re-encode each decision so the compiler cannot hoist host queries out of the loop.
            auto next=observe();result=model.evaluate(next.input);
            const auto kernel=start-bc::fuel_remaining();
            std::vector<Attempt> actions;script(frame,actions);
            const auto total=budget-bc::fuel_remaining();
            std::string json="[";
            for(std::size_t i=0;i<actions.size();i++){if(i)json+=',';json+="{\"action\":"+actions[i].action+",\"code\":"+std::to_string(actions[i].code)+",\"result\":"+(actions[i].result?"true":"false")+'}';}
            json+=']';
            // Binary floats avoid spending the bot's turn formatting a diagnostic JSON array.
            const std::array<std::uint32_t,8> header{bc::round_number(),unit_id(bc::self()),budget,static_cast<std::uint32_t>(kernel),static_cast<std::uint32_t>(total),
                static_cast<std::uint32_t>(result.chosen),static_cast<std::uint32_t>(frame.moves.size()),static_cast<std::uint32_t>(json.size())};
            std::fwrite("S1B!",1,4,stdout);std::fwrite(header.data(),4,header.size(),stdout);
            std::fwrite(frame.input.features.data(),4,actor::G,stdout);
            std::fwrite(frame.input.candidates.data(),4,actor::K*actor::C,stdout);
            std::fwrite(frame.input.mask.data(),1,actor::K,stdout);
            std::fwrite(result.scores.data(),4,actor::K,stdout);
            for(auto p:frame.moves){std::fwrite(&p.x,4,1,stdout);std::fwrite(&p.y,4,1,stdout);}
            std::fwrite(json.data(),1,json.size(),stdout);std::fflush(stdout);
            first=false;
        }
        bc::end_turn();
    }
}
