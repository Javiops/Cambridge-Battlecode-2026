#include "types.h"
#define TACTICS_COORDINATION_MODEL_ONLY
#include "coordination.h"
namespace bc { inline unsigned epoch=100,budget=100000;inline unsigned fuel_remaining(){return budget;}inline unsigned round_number(){return epoch;} }
namespace tactics { struct World {Memory &memory;Actor self;std::array<Spell,2>spells{};std::vector<Actor>allies;std::vector<GroupView>groups;int round=100,serial=3;}; }
#define TACTICS_CREW_SEQUENCE_MODEL_ONLY
#include "crew_sequence.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;static int checks=0;static void yes(bool v,const char*why){++checks;if(!v){std::fprintf(stderr,"FAIL %s\n",why);std::exit(1);}}
struct Case {Memory memory;World w;Proposal paid;CrewTurnReceipt receipt;Case():w{memory}{bc::epoch=100;bc::budget=100000;memory.mission.phase=Phase::Clear;memory.mission.group=0;memory.mission.rate=1;memory.mission.assembly_count=2;memory.mission.assembly_ids[0]=0;memory.mission.assembly_ids[1]=1;
 auto&a=w.self;a.id=0;a.type=10;a.pos={0,0};a.hp=a.max_hp=1000;a.strength=50;a.focus=100;a.range=1;a.alive=a.can_attack=a.can_cast=true;
 auto&s=a.spells[0];s.kind=1;s.slot=0;s.self=s.ready=true;s.cooldown=0;s.recharge=8;w.spells=a.spells;
 Actor helper=a;helper.id=1;helper.type=0;helper.pos={0,1};helper.hp=helper.max_hp=1200;w.allies={a,helper};
 Camp c;c.id=8;c.pos={1,0};c.hp=c.max_hp=500;c.range=3;Camp e=c;e.id=9;e.pos={1,1};e.hp=e.max_hp=2400;e.strength=60;Camp f=e;f.id=10;f.pos={2,0};GroupView v;v.seen=100;v.state=Lifecycle::Alive;v.camps={c,e,f};w.groups={v};
 paid.mission=memory.mission;paid.action=crew_stationary_choice(a,w.allies,v.camps,true);paid.valid=paid.crew_clear_certified=true;paid.crew_clear_proof=ClearProofKind::DetailedBundle;paid.crew_proof_owner=a.id;paid.crew_proof_round=w.round;paid.crew_proof_serial=w.serial;receipt=make_crew_turn_receipt(w,paid);
 }
 void apply(){crew_project_effect(w.self,w.groups[0].camps,paid.action);w.spells=w.self.spells;++w.serial;}
 bool reject(){return !crew_turn_followup(w,memory,receipt,true);}
};
static Proposal basic_only(Case &c) {
 c.w.self.range=3;c.w.self.strength=100;c.w.allies[0]=c.w.self;c.w.allies[1].range=3;c.w.allies[1].strength=100;
 for(auto &m:c.w.groups[0].camps){m.hp=m.max_hp=500;m.strength=1;}
 std::array<CampClearBody,2>b; b[0].actor=c.w.self;b[1].actor=c.w.allies[1];
 std::vector<CampClearMonster> monsters;for(auto &m:c.w.groups[0].camps)monsters.push_back({m,true});
 auto proof=basic_clear_rollout(b,monsters,c.w.self.id);yes(proof&&proof->ready&&proof->proof==ClearProofKind::BasicOnly,"actual basic adapter retains its dependency kind");
 LocalAssignment assignment;assignment.ready=assignment.self_selected=assignment.locally_accepted=true;assignment.rollout=*proof;assignment.selected_ids=proof->selected_ids;
 Proposal p;p.valid=true;p.mission=c.memory.mission;yes(name_current_crew(p.mission,assignment,c.w.self.id),"basic certificate retains actual selected named IDs");p.crew_clear_certified=true;p.crew_clear_proof=proof->proof;p.crew_proof_owner=c.w.self.id;p.crew_proof_round=c.w.round;p.crew_proof_serial=c.w.serial;
 p.action=certified_camp_first_action(c.w.self,c.w.allies,c.w.groups[0].camps,p.crew_clear_proof,true);
 return p;
}
int main(){
 {Case c;yes(c.receipt.valid&&c.receipt.required,"paid actual selected coalition stamps required continuation");yes(c.paid.action.kind==Kind::BasicCamp&&c.paid.action.target==9,"shared pressure-removing target");c.apply();auto p=crew_turn_followup(c.w,c.memory,c.receipt,true);yes(p&&p->action.kind==Kind::CastSelf&&p->action.slot==0&&p->crew_clear_certified,"actual Varg splash basic carries only legal reset");yes(c.reject(),"receipt consumed once");c.paid=*p;c.receipt=make_crew_turn_receipt(c.w,c.paid);yes(c.receipt.valid,"accepted legal reset requires funded next basic");c.apply();p=crew_turn_followup(c.w,c.memory,c.receipt,true);yes(p&&p->action.kind==Kind::BasicCamp,"actual reset restores exactly actual next basic");c.paid=*p;c.receipt=make_crew_turn_receipt(c.w,c.paid);yes(!c.receipt.required,"one-cast allowance stops sequence after extra basic");}
 {Case c;c.paid.crew_clear_certified=false;yes(!make_crew_turn_receipt(c.w,c.paid).valid,"generic unpaid hit cannot borrow coalition proof");}
 {Case c;c.paid.mission.assembly_count=0;yes(!make_crew_turn_receipt(c.w,c.paid).valid,"unnamed job rejected");}
 {Case c;c.paid.mission.assembly_ids[1]=0;yes(!make_crew_turn_receipt(c.w,c.paid).valid,"duplicate physical IDs rejected");}
 {Case c;c.paid.mission.assembly_ids[0]=4;yes(!make_crew_turn_receipt(c.w,c.paid).valid,"unobserved participant rejected");}
 {Case c;c.paid.action.target=8;yes(!make_crew_turn_receipt(c.w,c.paid).valid,"cannot replace model-selected target");}
 {Case c;bc::budget=61999;auto r=make_crew_turn_receipt(c.w,c.paid);yes(r.required&&!r.valid,"required pre-basic bundle retains funding admission");}
 {Case c;c.apply();yes(!crew_turn_followup(c.w,c.memory,c.receipt,false),"rejected SDK mutation cannot authorize continuation");}
 {Case c;c.apply();++bc::epoch;yes(c.reject(),"native epoch changed");}
 {Case c;c.apply();++c.w.serial;yes(c.reject(),"two refreshes cannot borrow proof");}
 {Case c;c.apply();--c.w.serial;yes(c.reject(),"pre-refresh stale data rejected");}
 {Case c;c.apply();c.w.self.pos={0,1};yes(c.reject(),"owner moved");}
 {Case c;c.apply();c.w.allies[1].pos={0,2};yes(c.reject(),"helper moved");}
 {Case c;c.apply();c.w.allies.pop_back();yes(c.reject(),"helper hidden or missing");}
 {Case c;c.apply();--c.w.self.hp;yes(c.reject(),"new owner injury invalidates reserve");}
 {Case c;c.apply();--c.w.allies[1].hp;yes(c.reject(),"new helper injury invalidates crew reserve");}
 {Case c;c.apply();++c.w.self.strength;yes(c.reject(),"equipment changed");}
 {Case c;c.apply();++c.w.allies[1].focus;yes(c.reject(),"helper equipment changed");}
 {Case c;c.apply();++c.w.self.spells[0].range;yes(c.reject(),"kit changed");}
 {Case c;c.apply();++c.w.self.spells[1].cooldown;yes(c.reject(),"unrelated cast intervened");}
 {Case c;c.apply();c.w.self.can_attack=true;yes(c.reject(),"first actual basic was not spent");}
 {Case c;c.apply();c.w.self.can_cast=false;yes(c.reject(),"actual cast permission absent");}
 {Case c;c.apply();c.w.self.stunned=true;yes(c.reject(),"stunned body rejected");}
 {Case c;c.apply();c.w.self.completed=true;yes(c.reject(),"completed body rejected");}
 {Case c;c.apply();c.memory.mission.assembly_ids[1]=3;yes(c.reject(),"crew claim changed");}
 {Case c;c.apply();c.memory.mission.group=1;yes(c.reject(),"another group cannot reuse proof");}
 {Case c;c.apply();++c.w.groups[0].camps[0].hp;yes(c.reject(),"splash damage was not actually applied");}
 {Case c;c.apply();c.w.groups[0].camps[0].pos={1,-1};yes(c.reject(),"camp moved");}
 {Case c;c.apply();c.w.groups[0].seen=99;yes(c.reject(),"personal observation stale");}
 {Case c;c.apply();bc::budget=15999;yes(c.reject(),"consumer preserves actual16k admission");}
 {Case c;c.apply();c.w.self.hp+=1;yes(c.reject(),"unrelated positive HP gain is not the accepted basic effect");}
 {Case c;c.apply();c.w.allies[1].hp+=1;yes(c.reject(),"unrelated helper healing cannot forge accepted basic effect");}
 {Case c;c.apply();c.w.self.shield=250;yes(c.reject(),"unrelated shield gain cannot forge accepted basic effect");}
 {Case c;auto&a=c.w.self;a.type=0;auto&s=a.spells[0];s.kind=3;s.self=false;s.ground=true;s.amount=100;s.range=4;s.radius=1;s.duration=1;c.w.spells=a.spells;c.w.allies[0]=a;c.paid.action=crew_stationary_choice(a,c.w.allies,c.w.groups[0].camps,true);c.receipt=make_crew_turn_receipt(c.w,c.paid);yes(c.receipt.valid,"Ryth actual basic carries funded ground AoE");c.apply();auto p=crew_turn_followup(c.w,c.memory,c.receipt,true);yes(p&&p->action.kind==Kind::CastGround&&p->action.slot==0,"ground-only camp damage retained without camp-target flag");c.paid=*p;c.receipt=make_crew_turn_receipt(c.w,c.paid);yes(!c.receipt.required,"damage cast cannot invent another cast/basic allowance");}
 {Case c;auto&a=c.w.self;a.type=8;a.range=3;auto&s=a.spells[0];s.kind=5;s.self=false;s.allies=true;s.amount=200;s.range=4;c.w.spells=a.spells;c.w.allies[0]=a;c.w.allies[1].hp=300;c.paid.action=crew_stationary_choice(a,c.w.allies,c.w.groups[0].camps,true);yes(c.paid.action.kind==Kind::CastChampion&&c.paid.action.target==1,"necessary actual ally heal precedes offense");c.receipt=make_crew_turn_receipt(c.w,c.paid);yes(c.receipt.valid,"paid support can carry its still-available basic");c.apply();c.w.allies[1].hp+=200;auto p=crew_turn_followup(c.w,c.memory,c.receipt,true);yes(p&&p->action.kind==Kind::BasicCamp,"actual ally healing preserves the priced remaining offense");}
 {Case c;c.apply();c.w.self.shield_ticks=1;yes(c.reject(),"unrelated owner shield duration change invalidates receipt");}
 {Case c;c.apply();c.w.allies[1].shield_ticks=1;yes(c.reject(),"unrelated helper shield duration change invalidates receipt");}
 {Case c;Actor before=c.w.self,after=before,caster=before;Action shield;shield.kind=Kind::CastSelf;shield.target=before.id;shield.slot=1;caster.spells[1].kind=7;caster.spells[1].amount=250;caster.spells[1].duration=5;after.shield=250;after.shield_ticks=5;yes(crew_body_effect_matches(before,after,caster,shield),"accepted actual shield includes exact known remaining duration");after.shield_ticks=4;yes(!crew_body_effect_matches(before,after,caster,shield),"shorter observed shield cannot forge accepted support effect");after.shield_ticks=-1;yes(!crew_body_effect_matches(before,after,caster,shield),"unknown observed shield expiry cannot forge accepted support effect");}
 for(unsigned budget:{40000u,50000u,61000u})for(int kind:{1,2})for(bool ready:{false,true}){
  Case c;auto &s=c.w.self.spells[0];s.kind=kind;s.ready=ready;s.self=kind==1;s.camps=kind==2;s.amount=200;s.range=3;c.w.spells=c.w.self.spells;
  auto p=basic_only(c);bc::budget=budget;yes(p.action.kind==Kind::BasicCamp&&crew_basic_first_action_valid(c.w,p),"40-61k ordinary first Basic independent of optional reset/damage availability");
  auto r=make_crew_turn_receipt(c.w,p);yes(!r.required&&!r.valid,"basic-only proof has no required optional continuation");
 }
 for(int change=0;change<12;++change){Case c;auto p=basic_only(c);if(change==0)++bc::epoch;if(change==1)++c.w.serial;if(change==2)++p.crew_proof_serial;if(change==3)p.crew_proof_owner=7;if(change==4)c.w.self.can_attack=false;if(change==5)c.w.self.completed=true;if(change==6)c.w.groups[0].seen=99;if(change==7)c.w.groups[0].camps.clear();if(change==8)c.w.allies.pop_back();if(change==9)p.mission.assembly_ids[1]=p.mission.assembly_ids[0];if(change==10)p.action.kind=Kind::CastSelf;if(change==11)p.crew_clear_proof=ClearProofKind::None;
  yes(!crew_basic_first_action_valid(c.w,p),"stale/changed/malformed Basic-only proof cannot authorize a hit");auto r=make_crew_turn_receipt(c.w,p);yes(r.required&&!r.valid,"invalid current proof fails closed instead of clearing admission");
 }
 {Case c;auto p=basic_only(c);p.crew_clear_proof=ClearProofKind::DetailedBundle;bc::budget=50000;auto r=make_crew_turn_receipt(c.w,p);yes(r.required&&!r.valid,"same optional-ready state remains prepaid when detailed proof could depend on reset");}
 {Case c;++c.paid.crew_proof_serial;auto r=make_crew_turn_receipt(c.w,c.paid);yes(r.required&&!r.valid,"detailed proof also rejects another snapshot before first action");}
 {Case c;auto&a=c.w.self;a.type=8;a.range=3;auto&s=a.spells[0];s.kind=5;s.self=false;s.allies=true;s.amount=315;s.range=4;c.w.spells=a.spells;c.w.allies[0]=a;c.w.allies[1].hp=300;c.paid.action=crew_stationary_choice(a,c.w.allies,c.w.groups[0].camps,true);bc::budget=40000;auto r=make_crew_turn_receipt(c.w,c.paid);yes(c.paid.action.kind==Kind::CastChampion&&r.required&&!r.valid,"necessary detailed heal cannot enter without its44k remaining offense budget");}
 {Case c;auto p=basic_only(c);c.w.self.can_attack=false;auto a=certified_camp_first_action(c.w.self,c.w.allies,c.w.groups[0].camps,ClearProofKind::BasicOnly);yes(a.kind==Kind::None,"spent Basic-only permission never falls through into an uncertified reset");}
 std::printf("%d crew sequence checks passed\n",checks);
}
