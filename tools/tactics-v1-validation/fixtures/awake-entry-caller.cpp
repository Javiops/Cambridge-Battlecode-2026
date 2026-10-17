#define TACTICS_COORDINATION_MODEL_ONLY
#define TACTICS_SOLO_MODEL_ONLY
#include <solo.h>
#include <cstdio>
#include <stdexcept>
namespace bc {static std::uint64_t budget=65000;static int epoch=101;inline auto fuel_remaining(){return budget;}inline int round_number(){return epoch;}}
namespace tactics {
struct World {Actor self{};Memory&memory;int round=101,serial=1;};
static SoloFarmQuote offered;static int quote_calls=0,proposal_calls=0;static bool untagged=false,no_proposal=false,epoch_spill=false;
inline SoloFarmQuote quote_solo_basic_farm(World&,int){++quote_calls;if(epoch_spill)++bc::epoch;return offered;}
inline std::optional<Proposal> solo_farm_proposal(World&,Memory&,const SoloFarmQuote&q){++proposal_calls;if(no_proposal)return std::nullopt;Proposal p;p.valid=true;p.action.kind=Kind::BasicCamp;p.mission.group=q.group;p.mission.phase=Phase::Clear;p.awake_entry_current_certified=!untagged;return p;}
/*PRODUCTION_PENDING_CURRENT*/
}
using namespace tactics;static int checks=0;static void check(bool b,const char*why){++checks;if(!b){std::printf("PAID_CURRENT_FAIL %s\n",why);throw std::runtime_error(why);}}
int main(){Memory m;World w{{},m};auto reset=[&]{m={};m.awake_entry={0,2,7,100,{3,1},{4,1}};w.self={};w.self.id=0;w.self.alive=true;w.self.hp=730;w.self.max_hp=1000;w.self.pos={3,1};w.round=101;bc::epoch=101;bc::budget=65000;quote_calls=proposal_calls=0;untagged=no_proposal=epoch_spill=false;offered={};offered.group=2;offered.owner=0;offered.round=101;offered.serial=1;offered.origin={3,1};offered.stage={3,1};offered.known=offered.feasible=offered.ready_now=true;};
 reset();auto p=pending_awake_entry_proposal(w,m);check(p&&p->action.kind==Kind::BasicCamp&&p->awake_entry_current_certified,"funded fresh full current quote selected below ordinary .75 entry floor");check(quote_calls==1&&proposal_calls==1&&m.awake_entry.round==100,"one fresh quote, original pending deadline unchanged until actual acceptance");
 reset();bc::budget=43999;check(!pending_awake_entry_proposal(w,m)&&quote_calls==0,"44k floor unchanged");reset();bc::budget=44000;check(pending_awake_entry_proposal(w,m).has_value(),"exact44k admits real current full quote");
 reset();m.awake_entry={};check(!pending_awake_entry_proposal(w,m)&&quote_calls==0,"no accepted entry receipt, no privileged quote");
 reset();check(!pending_awake_entry_proposal(w,m,true)&&quote_calls==0&&m.awake_entry.round==100,"named cash, installed return or pending purchase keeps its own validated priority; no deadline renewal");
 reset();bc::epoch=102;check(!pending_awake_entry_proposal(w,m)&&quote_calls==0,"stale native epoch cannot spend promised consumer budget");
 reset();m.awake_entry.owner=1;check(!pending_awake_entry_proposal(w,m)&&quote_calls==0,"different owner cannot borrow entry");
 reset();w.self.pos={2,1};check(!pending_awake_entry_proposal(w,m)&&quote_calls==0,"changed actual stage cannot reuse entry");
 reset();w.round=bc::epoch=99;check(!pending_awake_entry_proposal(w,m)&&quote_calls==0,"pre-entry round invalid");reset();w.round=bc::epoch=102;check(!pending_awake_entry_proposal(w,m)&&quote_calls==0,"expired one-owner contract gets no paid revival");
 for(int kind=0;kind<5;++kind){reset();if(kind==0)offered.known=false;if(kind==1)offered.feasible=false;if(kind==2)offered.ready_now=false;if(kind==3)offered.current_only=true;if(kind==4)offered.entry=AwakeEntryTiming::FutureOneOwner;check(!pending_awake_entry_proposal(w,m)&&proposal_calls==0&&m.awake_entry.round==100,"unknown, infeasible, unready, inherited or future forecast cannot grant first hit");}
 reset();epoch_spill=true;check(!pending_awake_entry_proposal(w,m)&&proposal_calls==0,"quote budget spill cannot become stale action");
 reset();untagged=true;check(!pending_awake_entry_proposal(w,m),"actual proposal needs explicit current full-certificate tag");reset();no_proposal=true;check(!pending_awake_entry_proposal(w,m),"native producer decline stays decline");
 std::printf("%d pending awake caller checks passed\n",checks);}
