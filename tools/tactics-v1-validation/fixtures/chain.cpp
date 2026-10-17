#define TACTICS_CHAIN_MODEL_ONLY
#include "chain.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
int main(){int checks=0;auto ck=[&](bool x,const char*n){++checks;if(!x){std::fprintf(stderr,"FAIL %s\n",n);std::exit(1);}};
ChainSchedule positive{18,2,13,16,12,3,5,0};
auto c=compare_chain_conservatively(positive,0,0,Settings::switch_margin);
ck(c.known&&c.prefer_job&&c.job_then_bank==35&&c.bank_then_job==46,"conservative full same-endpoint route35 beats even instant-acquisition bank-first46");
ck(compare_chain(positive,Settings::switch_margin).bank_then_job==62,"upper acquisition is explicitly removed only from bank-first lowerbound");
{auto s=positive;s.direct_bank=8;s.bank_to_job=5;s.job_to_bank=5;auto q=compare_chain_conservatively(s,0,0,Settings::switch_margin);ck(q.known&&!q.prefer_job,"open short-bank control declines expensive extra reward");}
{auto s=positive;s.recover=40;auto q=compare_chain_conservatively(s,0,0,Settings::switch_margin);ck(q.known&&!q.prefer_job&&q.job_then_bank==75&&q.bank_then_job==46,"actual required return is not canceled out of optimistic bank-first comparison");}
ck(!compare_chain_conservatively(positive,17,0,1.25).known,"cannot invent acquisition lowerbound exceeding paid upper");
ck(!compare_chain_conservatively(positive,0,1,1.25).known,"cannot invent recovery lowerbound");
ck(!compare_chain_conservatively(positive,-1,0,1.25).known,"negative lower bound invalid");
ck(!compare_chain_conservatively(positive,0,0,.99).known,"margin cannot weaken below equal completion cost");
{auto s=positive;s.direct_bank=std::numeric_limits<double>::quiet_NaN();ck(!compare_chain_conservatively(s,0,0,1.25).known,"unknown route never becomes free direct bank");}
Actor a;a.id=0;a.type=2;a.alive=a.can_attack=a.can_cast=a.can_move=true;a.hp=a.max_hp=800;a.strength=70;a.range=1;a.pos={4,10};a.camp_mitigation=1;a.gems=24;
Mission job;job.phase=Phase::Unassigned;
ck(chain_entry_eligible(a,job,20,0,1000,false,false,false,false),"healthy quiet carried bag can receive early cycle comparison");
for(int k=0;k<12;++k){auto b=a;auto j=job;bool holder=false,hostile=false,transaction=false;if(k==0)b.alive=false;if(k==1)b.completed=true;if(k==2)b.stunned=true;if(k==3)b.channel=Channel::Recall;if(k==4)b.gems=0;if(k==5)b.hp=439;if(k==6)holder=true;if(k==7)hostile=true;if(k==8)transaction=true;if(k==9)j.phase=Phase::Recover;if(k==10)j.assembly_pending=true;if(k==11)j.phase=Phase::Deliver;ck(!chain_entry_eligible(b,j,20,0,1000,holder,hostile,transaction,false),"channel survival actual holder committed bank or installation precedes discretionary chain");}
ck(!chain_entry_eligible(a,job,20,976,1000,false,false,false,false),"already deciding bag converts before new expenditure");
{auto j=job;j.chain_used=true;ck(!chain_entry_eligible(a,j,20,0,1000,false,false,false,false),"one accepted extra reward cannot start a second extra itinerary");j.chain_used=false;j.bank_after_reward=true;ck(!chain_entry_eligible(a,j,20,0,1000,false,false,false,false),"actual new-receipt bank obligation precedes any new extra");}
{auto b=a;b.can_attack=b.can_cast=b.can_move=false;ck(chain_entry_eligible(b,job,20,0,1000,false,false,false,false),"spent permissions may authorize only a paid future intention, not present readiness");}
Camp camp;camp.id=8;camp.hp=camp.max_hp=500;camp.strength=0;camp.range=0;camp.pos={5,9};
auto ready=chain_basic_certificate(a,camp,a.pos,0);ck(ready.ready&&ready.ticks==8&&ready.remaining_hp[0]==800,"complete basic-only upper needs no optional reset or cast budget");
{auto b=a;b.can_attack=false;auto spent=chain_basic_certificate(b,camp,b.pos,0);ck(spent.ready&&spent.ticks==9,"spent current basic includes one real future permission wait");ck(!b.can_attack,"certificate does not mutate actual spent permission");}
{auto b=a;b.pos={5,12};b.can_attack=false;auto future=chain_basic_certificate(b,camp,{4,10},2);ck(future.ready&&future.ticks==8&&!b.can_attack&&b.pos==Pos{5,12},"future endpoint bound changes only a copy; it never grants actual attack or movement");}
{auto b=camp;b.awake=true;ck(!chain_basic_certificate(a,b,{5,10},1).ready,"future awake approach cannot invent unpaid incoming phases");}
ck(!chain_basic_certificate(a,camp,a.pos,0,[]{return false;}).ready,"work budget failure is Unknown, never an affordable clear");
ChainState state;state.owner=0;state.group=2;state.altar=0;state.initial_bag=24;state.latest=55;state.probe_round=20;
Proposal p;p.valid=true;p.mission.phase=Phase::Travel;p.mission.group=2;p.action.kind=Kind::Move;p.action.at={4,10};
ck(bind_chain_contract(p,state)&&p.mission.chain_used&&!p.mission.bank_after_reward&&p.mission.latest==55,"finite contract is stamped after common builder's group reset");
ck(!p.solo_clear_certified&&!p.crew_clear_certified&&p.action.kind==Kind::Move,"future-stage binding never mints current camp-hit proof");
{auto q=p;q.mission.group=3;ck(!bind_chain_contract(q,state),"wrong objective cannot borrow selected completed-cycle contract");}
{auto q=p;q.valid=false;ck(!bind_chain_contract(q,state),"rejected proposal cannot commit chain intent");}
Memory m;m.mission=p.mission;m.mission.phase=Phase::Clear;m.mission.latest=20;
ck(!chain_entry_eligible(a,m.mission,20,0,1000,false,false,false,true),"absolute chain deadline cannot be refreshed by current-only clear");
ck(abort_declined_chain(a,m,state,{11,12},false)&&m.mission.phase==Phase::Deliver&&m.mission.group==-1&&m.mission.target==Pos{11,12},"expired or hard-declined clear cannot fall through ordinary current-clear fastlane");
ck(m.mission.chain_used&&!m.mission.bank_after_reward&&!state.active()&&state.probe_round==20,"abort preserves no-second-reward commitment without fabricating receipt or resetting throttle");
{auto s=state;s.owner=0;s.group=2;s.altar=0;Memory h;h.mission.phase=Phase::Collect;h.mission.group=2;h.mission.chain_used=true;ck(!abort_declined_chain(a,h,s,{11,12},true)&&h.mission.phase==Phase::Collect,"real holder continuity retains its separate priority");}
{auto s=state;s.owner=0;s.group=2;s.altar=0;Memory h;h.mission.phase=Phase::Clear;h.mission.group=2;h.mission.chain_used=true;auto channel=a;channel.channel=Channel::Tribute;ck(!abort_declined_chain(channel,h,s,{11,12},false),"active native channel cannot be replaced by abort intent");}
{ChainState s;s.latest=100;Memory h;h.hold_since=100;ck(chain_capture_window(s,h,106,true,6,10,2000),"expired planned bank clock cannot displace actual holder one phase before supported payout");ck(!chain_capture_window(s,h,107,true,6,10,2000),"holder exception cannot become renewed indefinite capture wait");ck(!chain_capture_window(s,h,106,false,6,10,2000),"expired unoccupied future reward cannot borrow actual holder exception");ck(!chain_capture_window(s,h,1990,true,6,10,2000),"actual holder cannot extend reward past known conversion deadline");}
std::printf("%d bounded chain checks passed\n",checks);}
