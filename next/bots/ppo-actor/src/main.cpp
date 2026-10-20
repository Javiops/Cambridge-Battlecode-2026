// ppo-runtime-v1: port the frozen PPO policy and controller; expect exact native action parity and zero release fuel losses.
#include <cstdio>
#include "controller.h"
#include "sampling.h"
#include "weights.h"
namespace bc=cambc;
#include "actions.h"

// stdout attachments contain NUL timeline separators. Hex keeps those separators
// distinguishable even when libc flushes a record in several writes.
void record(const char* tag,const void* data,unsigned size) {
    const auto* bytes=static_cast<const unsigned char*>(data);constexpr char hex[]="0123456789abcdef";
    std::array<char,2005> line{};std::memcpy(line.data(),tag,4);
    for(unsigned i=0;i<size;i++){line[4+2*i]=hex[bytes[i]>>4];line[5+2*i]=hex[bytes[i]&15];}
    line[4+2*size]='\n';std::fwrite(line.data(),1,5+2*size,stdout);std::fflush(stdout);
}

int main() try {
    actor::Policy model;model.weights=trained::weights;bool first=true;
    const std::array picks{bc::champion_draft::ryth,bc::champion_draft::prism,bc::champion_draft::heart_of_ruin,
                          bc::champion_draft::tavi,bc::champion_draft::cassi_and_issac};
    while(true) {
        if(bc::is_draft())bc::draft::pick(picks.at(bc::draft::current_draft(bc::team::ally).size()));
        else {
            const unsigned budget=first?200000:100000;unsigned count=0;
            for(unsigned decision=0;decision<2;decision++) {
                auto start=bc::fuel_remaining();auto frame=observe();auto macro=banking(frame);
                unsigned controller=start-bc::fuel_remaining();actor::Result result;Sample choice{-1,0,0};Command command;
                if(macro)command=*macro;
                else {
                    result=model.evaluate(frame.input);choice=sample(result,frame.input);
                    const auto& c=frame.input.candidates[choice.index];
                    if(c[1])command={1,frame.info.x+int(c[4]*8),frame.info.y+int(c[5]*8)};
                    else if(c[2]) {
                        auto p=bc::vec2{frame.info.x+int(c[4]*8),frame.info.y+int(c[5]*8)};
                        if(c[8])for(auto t:frame.enemies)if(t.position()==p)command={2,1,int(unit_id(t))};
                        if(c[9])for(auto t:frame.camps)if(t.position()==p)command={2,2,int(unit_id(t))};
                    }else if(c[3])command={3,int(c[10]*2),0};
                }
                const unsigned kernel=start-bc::fuel_remaining();
                if(macro) {
                    if(command.kind==1)(void)bc::self().move_absolute({command.a,command.b});
                    if(command.kind==4)bc::self().submit_gems({command.a,command.b});
                }else (void)execute(frame,choice.index);
                const bool probe=!macro&&decision==0&&(bc::round_number()<=80||(bc::round_number()-1)%25==0);
                const std::array<std::uint32_t,14> header{bc::round_number(),unit_id(bc::self()),decision,command.kind,
                    std::uint32_t(choice.index),std::uint32_t(command.a),std::uint32_t(command.b),choice.before,choice.after,
                    controller,kernel,unsigned(budget-bc::fuel_remaining()),unsigned(probe),budget};
                std::array<unsigned char,1000> payload{};std::memcpy(payload.data(),header.data(),56);
                if(probe) {
                    std::memcpy(payload.data()+56,frame.input.features.data(),96);
                    std::memcpy(payload.data()+152,frame.input.candidates.data(),768);
                    std::memcpy(payload.data()+920,frame.input.mask.data(),16);
                    std::memcpy(payload.data()+936,result.scores.data(),64);
                }
                record("S6D!",payload.data(),probe?1000:56);
                count++;
                if(command.kind==0)break;
            }
            const std::array<std::uint32_t,5> footer{bc::round_number(),unit_id(bc::self()),budget,unsigned(budget-bc::fuel_remaining()),count};
            record("S6F!",footer.data(),20);
            first=false;
        }
        bc::end_turn();
    }
}catch(const bc::error& e) {
    std::printf("SDKERR round=%u id=%u %s ENDERR\n",bc::round_number(),unit_id(bc::self()),e.what());std::fflush(stdout);throw;
}
