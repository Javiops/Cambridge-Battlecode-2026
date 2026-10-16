#define TACTICS_COORDINATION_MODEL_ONLY
#include "coordination.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;int main(){int checks=0;auto ck=[&](bool ok,const char*n){++checks;if(!ok){std::fprintf(stderr,"FAIL %s\n",n);std::exit(1);}};Actor willow;willow.id=1;willow.type=8;willow.pos={3,0};willow.hp=willow.max_hp=700;willow.strength=45;willow.focus=105;willow.range=3;willow.alive=willow.can_attack=willow.can_cast=true;willow.spells[0].slot=0;willow.spells[0].kind=5;willow.spells[0].amount=315;willow.spells[0].range=4;willow.spells[0].allies=willow.spells[0].ready=true;willow.spells[0].cooldown=0;willow.spells[0].recharge=8;Actor ryth=willow;ryth.id=0;ryth.type=0;ryth.pos={1,0};ryth.hp=330;ryth.max_hp=1200;ryth.strength=50;ryth.range=1;ryth.spells={};Camp c;c.id=2;c.pos={0,0};c.hp=100;c.max_hp=2400;c.strength=60;c.range=3;std::array<CampClearBody,2>b{};b[0].actor=willow;b[1].actor=ryth;for(auto&x:b)x.alternative_known=true;std::array<CampClearMonster,1>m{{{c,true}}};auto proof=rollout_camp_clear(b,m,1,48);auto action=stationary_camp_support(willow,std::array{willow,ryth},std::array{c});ck(proof.ready&&proof.ticks==2,"actual fixed current quote needs two turns with necessary support");
LocalAssignment assignment;assignment.ready=assignment.self_selected=assignment.locally_accepted=true;assignment.selected_ids=proof.selected_ids;assignment.rollout=proof;
Mission job;job.group=1;job.expiry=6;ck(job.assembly_count==0,"ordinary current job begins without prospective metadata");
ck(name_current_crew(job,assignment,1)&&job.assembly_count==2,"ordinary actual ready crew receives typed current IDs");
ck(job.assembly_anchor==0&&job.assembly_helper==0&&!job.assembly_pending,"current quote does not fabricate future assembly acceptance");
ck(action.kind==Kind::CastChampion&&action.target==0&&action.slot==0,"shared executor preserves necessary legal Willow heal before offense");
ck(45+50<100&&330-60<.25*1200+1,"legacy basic-first sequence would violate exact health reserve");
ck(job.expiry==6,"naming metadata alone does not extend a real clear lease");
{auto unknown=assignment;unknown.rollout.proof=ClearProofKind::None;Mission rejected;ck(!name_current_crew(rejected,unknown,1),"ready label without an explicit current proof cannot name a certified crew");}
for(int change=0;change<4;++change){auto bad=assignment;Mission rejected;
if(change==0)bad.ready=false;if(change==1)bad.locally_accepted=false;if(change==2)bad.selected_ids={0};if(change==3)bad.selected_ids={1,1};
ck(!name_current_crew(rejected,bad,1)&&rejected.assembly_count==0,"absent readiness actual permission self or unique identities cannot authorize a crew");}
willow.pos={4,0};auto actual=std::array{willow,ryth};auto live=std::array{c};
ck(!coordination_detail::useful_now(willow,m,true),"heal-only Willow outside basic range has no offensive allowance fiction");
ck(current_crew_support_actionable(willow,actual,live,true),"actual heal range four remains locally actionable with basic range three");
willow.spells[0].exclusive=true;actual[0]=willow;
ck(!current_crew_support_actionable(willow,actual,live,false),"spent movement cannot promise an exclusive heal");
willow.completed=true;actual[0]=willow;
ck(!current_crew_support_actionable(willow,actual,live,true),"completed owner cannot promise current ally heal");
std::printf("%d current crew checks passed\n",checks);}
