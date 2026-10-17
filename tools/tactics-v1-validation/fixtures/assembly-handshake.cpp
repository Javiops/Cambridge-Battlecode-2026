#define TACTICS_ASSEMBLY_MODEL_ONLY
#include "assembly.h"
#include <cstdio>
#include <cstdlib>
namespace bc {inline unsigned budget=100000;inline int epoch=100;inline unsigned fuel_remaining(){return budget;}inline unsigned round_number(){return epoch;}}
namespace tactics {
struct World {Actor self;int round=100,group=0;bool nearby=true,affordable=true,alternative_known=true;double damage=0,quote_alternative=-1;int near_calls=0,quote_calls=0,alternative_calls=0;};
inline std::optional<int> nearby_assembly_group(World&w,Memory&){++w.near_calls;return w.nearby?std::optional(w.group):std::nullopt;}
namespace coordination_detail {inline double alternative(World&w,const Actor&,int,bool&known,int&,Pos&,bool&){++w.alternative_calls;known=w.alternative_known;return known?.1:0;}}
inline std::optional<AssemblyCandidate> local_assembly_candidate(World&w,Memory&,int gi,double value,bool known){++w.quote_calls;w.quote_alternative=value;if(!known||!w.affordable)return std::nullopt;AssemblyCandidate c;c.group=gi;c.anchor_id=w.self.id;c.helper_id=2;c.start=w.round;c.expiry=w.round+6;c.target={5,5};c.stage={3,3};c.rate=1;c.known=true;c.signature=19;c.selected_count=2;c.selected_ids={w.self.id,2};c.route={w.self.pos,c.stage};c.route_length=2;c.exit_route={c.stage,w.self.pos};c.exit_length=2;return c;}
inline std::optional<Pos> assembly_step(World&w,const Mission&m){return w.self.can_move&&m.assembly_route_length>1?std::optional(m.assembly_route[1]):std::nullopt;}
inline double incoming_damage(World&w,Pos){return w.damage;}
inline Action moving(Pos p,const char*reason){Action a;a.kind=Kind::Move;a.at=p;a.reason=reason;return a;}
inline Proposal economic(Action a,Mission m,Priority priority,double value){Proposal p;p.action=a;p.mission=m;p.priority=priority;p.value=value;p.valid=true;return p;}
// EXACT_HANDSHAKE
}
using namespace tactics;
struct Case {World w;Memory m;Case(){bc::budget=100000;bc::epoch=100;w.self.id=1;w.self.alive=w.self.can_move=true;w.self.hp=w.self.max_hp=1000;w.self.pos={2,3};m.mission.phase=Phase::Observe;m.mission.group=0;m.mission.expiry=106;}};
int main(){int checks=0;auto ck=[&](bool x,const char*n){++checks;if(!x){std::fprintf(stderr,"FAIL %s\n",n);std::exit(1);}};
{Case c;ck(early_assembly_eligible(c.w.self,c.m.mission,100,false,false,false),"healthy quiet bagless observer eligible before elective work");for(int k=0;k<16;++k){auto a=c.w.self;auto m=c.m.mission;bool held=false,hostile=false,transaction=false;if(k==0)a.alive=false;if(k==1)a.stunned=true;if(k==2)a.channel=Channel::Recall;if(k==3)a.gems=1;if(k==4)a.hp=749.99;if(k==5)held=true;if(k==6)hostile=true;if(k==7)transaction=true;if(k==8)m.phase=Phase::Clear;if(k==9)m.phase=Phase::Collect;if(k==10)m.sortie_length=1;if(k==11)m.assembly_pending=true;if(k==12)m.chain_used=true;if(k==13)m.bank_after_reward=true;if(k==14)m.group=-1;if(k==15)m.expiry=99;ck(!early_assembly_eligible(a,m,100,held,hostile,transaction),"early priority cannot bypass explicit survival/channel/conversion/holder/transaction contracts");}c.w.self.hp=750;ck(early_assembly_eligible(c.w.self,c.m.mission,100,false,false,false),"exact healthy boundary accepted");c.w.self.max_hp=0;ck(!early_assembly_eligible(c.w.self,c.m.mission,100,false,false,false),"invalid HP metadata cannot take early priority");}
{Case c;bc::budget=56000;auto p=assembly_handshake_proposal(c.w,c.m,std::nullopt,56000);ck(p&&p->action.kind==Kind::Move&&p->action.at==Pos{3,3},"56k preselected proposal carries only priced actual rendezvous move");ck(p->mission.phase==Phase::Assemble&&p->mission.assembly_pending&&p->mission.assembly_count==2&&p->mission.assembly_ids[1]==2,"typed crew route and helper identities preserved");ck(!p->crew_clear_certified&&p->crew_clear_proof==ClearProofKind::None&&!p->solo_clear_certified,"future quote never grants first-hit readiness");ck(c.m.mission.phase==Phase::Observe&&!c.m.mission.assembly_pending,"proposal does not commit mission before accepted mutation");ck(c.w.alternative_calls==1&&c.w.quote_calls==1,"unknown incumbent resolves actual opportunity once");}
{Case c;bc::budget=55999;ck(!assembly_handshake_proposal(c.w,c.m,std::nullopt,56000)&&c.w.quote_calls==0,"below existing56k producer entry declines before expensive quote");bc::budget=56000;ck(bool(assembly_handshake_proposal(c.w,c.m,std::nullopt,1)),"caller cannot lower internal56k entry even with smaller requested threshold");}
{Case c;bc::budget=64999;ck(!assembly_handshake_proposal(c.w,c.m)&&c.w.near_calls==0,"late default65k path preserves prior admission");}
{Case c;++bc::epoch;ck(!assembly_handshake_proposal(c.w,c.m,std::nullopt,56000)&&c.w.near_calls==0,"stale native epoch never starts early planning");}
{Case c;c.w.affordable=false;ck(!assembly_handshake_proposal(c.w,c.m,std::nullopt,56000)&&c.w.quote_calls==1,"unaffordable future quote is not a free first hit");for(int r:{101,102}){c.w.round=bc::epoch=r;ck(!assembly_handshake_proposal(c.w,c.m,std::nullopt,56000)&&c.w.quote_calls==1&&c.w.alternative_calls==1,"failed probe's next two owners skip expensive quote and leave ordinary alternatives available");}c.w.round=bc::epoch=103;c.w.affordable=true;ck(bool(assembly_handshake_proposal(c.w,c.m,std::nullopt,56000))&&c.w.quote_calls==2,"finite failed-probe throttle expires after three owners");}
{Case c;c.w.affordable=false;assembly_handshake_proposal(c.w,c.m,std::nullopt,56000);c.w.round=bc::epoch=101;c.w.group=1;c.w.affordable=true;ck(bool(assembly_handshake_proposal(c.w,c.m,std::nullopt,56000))&&c.w.quote_calls==2,"one failed group does not suppress a different observed alternative");}
{Case c;c.w.alternative_known=false;ck(!assembly_handshake_proposal(c.w,c.m,std::nullopt,56000),"unknown abandoned alternative is never replaced by fictitious free zero");}
{Case c;c.w.self.can_move=false;auto p=assembly_handshake_proposal(c.w,c.m,.1,56000);ck(p&&p->action.kind==Kind::None&&p->mission.assembly_pending,"spent move creates only intentional paid handshake wait");ck(c.w.alternative_calls==0,"known current bank alternative avoids redundant search");}
{Case c;c.m.mission.phase=Phase::Assemble;c.m.mission.rate=999;c.w.alternative_known=false;
ck(!assembly_handshake_proposal(c.w,c.m,std::nullopt,56000),"positive coarse unready mission rate cannot fabricate a known independent alternative");
ck(c.w.alternative_calls==1&&c.m.mission.rate==999,"raw score must be independently resolved without changing the existing proposal");}
{Case c;c.m.mission.rate=999;auto p=assembly_handshake_proposal(c.w,c.m,std::nullopt,56000);
ck(p&&c.w.alternative_calls==1&&std::abs(c.w.quote_alternative-.1)<1e-12,"fresh resolved task replaces same-target raw mission rate in price");}
{Case c;c.m.mission.rate=999;c.w.alternative_known=false;auto p=assembly_handshake_proposal(c.w,c.m,.2,56000);
ck(p&&c.w.alternative_calls==0&&std::abs(c.w.quote_alternative-.2)<1e-12,"actual positive external bank remains a valid opportunity without raw rate contamination");}
{Case c;c.w.alternative_known=false;ck(!assembly_handshake_proposal(c.w,c.m,std::numeric_limits<double>::infinity(),56000)&&c.w.alternative_calls==1,"nonfinite external price is unknown and requires independent resolution");}
std::printf("%d assembly handshake checks passed\n",checks);}
