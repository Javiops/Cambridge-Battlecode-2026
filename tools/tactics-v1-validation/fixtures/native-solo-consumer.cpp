#include "coordinator.h"
#include "actions.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
using namespace tactics;
static void require(bool value,const char *why){if(!value){std::printf("NATIVE_SOLO_FAIL %s\n",why);std::fflush(stdout);throw std::runtime_error(why);}}
int main(){
    Geometry geo;Memory memory;std::unique_ptr<World> world;int gi=-1,stage=0;bool metadata=false,combo=false,lowhp=false;int first_round=-1,forecast_ticks=-1,forecast_hp=-1,total_resets=0,total_receipt_basics=0;
    while(true){
        if(bc::is_draft()){
            const auto old=bc::draft::current_draft(bc::team::ally);
            for(auto pick:{bc::champion_draft::cassi_and_issac,bc::champion_draft::varg,
                bc::champion_draft::ryth,bc::champion_draft::vendetta,bc::champion_draft::tavi})
                if(std::find(old.begin(),old.end(),pick)==old.end()){bc::draft::pick(pick);break;}
        }
        else if(stage<3){
            geo.initialize();if(!geo.initialized){bc::end_turn();continue;}
            if(gi<0){int best=unreachable;for(unsigned i=0;i<geo.groups.size();++i){const auto &g=geo.groups[i];
                if(g.spawns.size()==1&&g.initial_hp==1350&&g.initial_strength==20){int d=geo.at(geo.home,g.spawns[0].pos);if(d<best){best=d;gi=i;}}}
                require(gi>=0,"actual public map has a singleton wolf");}
            const Pos camp_at=geo.groups[gi].spawns[0].pos;
            if(!geo.goal_field(camp_at,0)){bc::end_turn();continue;}
            if(!world)world=std::make_unique<World>(geo,memory);
            auto &w=*world;w.refresh();
            if(!metadata){
                std::printf("NATIVE_SOLO_METADATA %d %d %d %d %d %d %d %d %d\n",w.self.id,w.self.type,
                    int(w.self.hp),int(w.self.strength),int(w.self.focus),w.self.range,
                    int(geo.groups[gi].initial_hp),int(geo.groups[gi].initial_strength),gi);
                metadata=true;
            }
            if(w.self.type!=4){stage=3;bc::end_turn();continue;}
            if(distance(w.self.pos,camp_at)>w.self.range){
                if(auto step=w.toward(camp_at,w.self.range)){
                    require(bc::fuel_remaining()>12000,"scripted actual walk has mutation reserve");
                    require(w.me.move_absolute(sdk(*step)),"scripted actual legal walk accepted");
                }
            }else {
                require(w.groups[gi].fresh(w.round),"target lifecycle remains personally observed");
                if(stage==0){
                    memory.mission.group=gi;memory.mission.phase=Phase::Travel;
                    memory.mission.start=memory.mission.last_progress=w.round;
                    memory.mission.expiry=w.round+100;
                    memory.mission.target=camp_at;memory.mission.rate=.1;
                    std::printf("NATIVE_SOLO_CONSUMER_BEGIN %d %d %d\n",w.self.id,w.round,int(w.self.hp));
                    first_round=w.round;stage=1;
                }
                if(w.groups[gi].state==Lifecycle::Reward){
                    require(combo&&lowhp,"actual basic-reset-basic sequence and lowHP continuation must occur");
                    require(total_resets>0&&total_resets==total_receipt_basics,"every actual reset must receive its certified same-owner extra basic");
                    require(w.round-first_round<=forecast_ticks&&w.self.hp>=forecast_hp,"observed timing and reserve must be no worse than the ideal certified schedule");
                    require(w.self.alive&&w.self.hp>225,"actual singleton clear preserves absolute survival floor");
                    auto capture=farming(w,memory);
                    require(capture.has_value(),"cleared singleton retains capture work");
                    std::printf("NATIVE_SOLO_CONSUMER_PASS %d %d %d\n",w.self.id,w.round,int(w.self.hp));
                    std::printf("NATIVE_SOLO_COMBO_PASS %d %d %d\n",w.self.id,int(combo),int(lowhp));
                    std::printf("NATIVE_SOLO_SCHEDULE_PASS %d %d %d %d %d %d %d\n",w.self.id,total_resets,total_receipt_basics,forecast_ticks,w.round-first_round,forecast_hp,int(w.self.hp));
                    stage=3;
                }else{
                    // The production consumer sees actual SDK kit, cooldowns,
                    // permissions and camp health after each accepted mutation.
                    int basics=0,resets=0;
                    SoloResetReceipt pending;
                    for(int sequence=0;sequence<5&&bc::fuel_remaining()>(pending.valid?16000u:24000u);++sequence){
                        std::optional<Proposal> proposal;
                        if(pending.valid){
                            proposal=solo_reset_basic_followup(w,memory,pending,true);
                            require(proposal&&proposal->action.kind==Kind::BasicCamp,"accepted certified reset must fund its immediate real basic");
                            require(!solo_reset_basic_followup(w,memory,pending,true),"reset receipt cannot be consumed twice");
                        }else if(sequence==0&&w.round==first_round){
                            const auto quote=quote_solo_farm(w,gi);
                            require(quote.known&&quote.feasible&&quote.ready_now,"actual first-hit forecast is known and immediately legal");
                            forecast_ticks=int(quote.clear_ticks);forecast_hp=int(quote.remaining_hp);
                            proposal=farming(w,memory,&quote);
                        }else if(sequence==0&&w.self.hp < Settings::ordinary_heal*w.self.max_hp){
                            proposal=choose_mission(w,memory);lowhp=true;
                        }else if(sequence>0){
                            proposal=solo_clear_followup(w,memory);
                            if(!proposal)break; // Same explicit production budget fallback.
                        }else{
                            proposal=farming(w,memory);
                        }
                        require(proposal.has_value()&&proposal->mission.group==gi,"production farming keeps certified singleton");
                        if(proposal->action.kind==Kind::None){
                            require(!w.self.can_attack&&proposal->mission.phase==Phase::Clear,"spent permissions keep next-owner Clear without fabricated attack");
                            std::printf("NATIVE_SOLO_CONSUMER_HOLD %d %d %d\n",w.self.id,w.round,int(w.self.hp));
                            break;
                        }
                        require(proposal->action.kind==Kind::BasicCamp||proposal->action.kind==Kind::CastSelf,
                            "certified actual contribution produces only real basic/reset");
                        auto stamped=make_solo_reset_receipt(w,proposal->mission,proposal->action);
                        if(proposal->action.kind==Kind::CastSelf){
                            require(stamped.valid,"actual selected reset has a certificate receipt before mutation");
                            auto rejected=stamped;
                            require(!solo_reset_basic_followup(w,memory,rejected,false),"unaccepted reset cannot grant a receipt basic");
                        }
                        const auto result=execute(w,proposal->action);
                        require(result.success,"actual native farming mutation accepted");
                        basics+=proposal->action.kind==Kind::BasicCamp;
                        resets+=proposal->action.kind==Kind::CastSelf;
                        total_resets+=proposal->action.kind==Kind::CastSelf;
                        total_receipt_basics+=proposal->action.reason&&std::string_view(proposal->action.reason)=="farm-certified-reset-receipt-basic";
                        pending=stamped;
                        combo|=basics>=2&&resets>=1;
                        memory.mission=proposal->mission;
                        bool refreshed=true;
                        if(proposal->action.kind==Kind::CastSelf)w.refresh(true);
                        else if(bc::fuel_remaining()>=30000)w.refresh_local_effects(proposal->action);
                        else refreshed=false; // Same production reserve: end after accepted hit.

                        std::printf("NATIVE_SOLO_ACTION_BUDGET %d %d %d %llu\n",w.self.id,w.round,int(proposal->action.kind),static_cast<unsigned long long>(bc::fuel_remaining()));
                        if(!refreshed || w.groups[gi].state==Lifecycle::Reward)break;
                    }
                }
            }
        }
        bc::end_turn();
    }
}
