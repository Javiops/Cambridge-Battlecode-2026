#define TACTICS_SOLO_MODEL_ONLY
#define TACTICS_COORDINATION_MODEL_ONLY
#include "solo.h"
#include <cstdio>
#include <cstdlib>
namespace bc { static unsigned epoch=100,budget=100000;inline unsigned fuel_remaining(){return budget;}inline unsigned round_number(){return epoch;}}
namespace tactics { struct World {Memory&memory;Actor self;std::array<Spell,2>spells{};std::vector<GroupView>groups;int round=100,serial=3;};
// PRODUCTION_SOLO_BASIC

}
using namespace tactics;static int checks=0;static void yes(bool v,const char*why){++checks;if(!v){std::fprintf(stderr,"FAIL %s\n",why);std::exit(1);}}
struct Case {Memory memory;World w;Proposal paid;SoloBasicReceipt receipt;Case():w{memory}{bc::epoch=100;bc::budget=100000;memory.mission.phase=Phase::Clear;memory.mission.group=0;memory.mission.rate=1;
 auto&a=w.self;a.id=1;a.type=10;a.pos={0,0};a.hp=a.max_hp=1000;a.strength=50;a.focus=100;a.range=1;a.alive=a.can_attack=a.can_cast=true;
 auto&s=a.spells[0];s.kind=1;s.slot=0;s.self=s.ready=true;s.cooldown=0;s.recharge=8;w.spells=a.spells;
 Camp c;c.id=7;c.pos={1,0};c.hp=1350;c.strength=20;c.range=3;GroupView v;v.seen=100;v.state=Lifecycle::Alive;v.camps={c};w.groups={v};
 paid.mission=memory.mission;paid.action.kind=Kind::BasicCamp;paid.action.target=7;paid.valid=true;paid.solo_clear_certified=true;paid.solo_current_followup=Kind::CastSelf;paid.solo_current_slot=0;receipt=make_solo_basic_receipt(w,paid);
 }
 void hit(){w.self.can_attack=false;w.groups[0].camps[0].hp-=50;w.groups[0].camps[0].awake=true;++w.serial;}
 bool reject(){return !solo_basic_reset_followup(w,memory,receipt,true);}
};
int main(){
 {Case c;yes(c.receipt.valid,"paid real current certificate stamps basic proof");c.hit();auto p=solo_basic_reset_followup(c.w,c.memory,c.receipt,true);yes(p&&p->action.kind==Kind::CastSelf&&p->action.slot==0&&p->action.target==7,"actual ordinary basic grants only the already priced reset");yes(c.reject(),"basic receipt consumed once");}
 {Case c;c.paid.valid=false;yes(!make_solo_basic_receipt(c.w,c.paid).valid,"invalid proposal cannot grant paid proof");}
 {Case c;c.paid.solo_clear_certified=false;yes(!make_solo_basic_receipt(c.w,c.paid).valid,"unpaid generic basic never receives proof");}
 {Case c;c.paid.action.target=8;yes(!make_solo_basic_receipt(c.w,c.paid).valid,"other camp cannot borrow quote");}
 {Case c;bc::budget=59999;yes(!make_solo_basic_receipt(c.w,c.paid).valid,"pre-basic bundle admission preserves ordinary refresh budget");}
 {Case c;c.w.self.enhanced=true;yes(!make_solo_basic_receipt(c.w,c.paid).valid,"nonordinary enhanced basic not assumed");}
 {Case c;c.w.groups[0].camps[0].hp=40;yes(!make_solo_basic_receipt(c.w,c.paid).valid,"lethal first hit never wastes reset");}
 
 {Case c;c.hit();yes(!solo_basic_reset_followup(c.w,c.memory,c.receipt,false),"unaccepted first basic cannot grant reset");yes(c.reject(),"rejected proof consumed");}
 {Case c;c.hit();++bc::epoch;yes(c.reject(),"new owner epoch invalidates carried certificate");}
 {Case c;c.hit();++c.w.round;yes(c.reject(),"source snapshot round changed");}
 {Case c;c.hit();++c.w.serial;yes(c.reject(),"extra refresh is intervening state");}
 {Case c;c.hit();--c.w.serial;yes(c.reject(),"pre-refresh state rejected");}
 {Case c;c.hit();c.w.self.pos={0,1};yes(c.reject(),"moved body cannot use fixed-position proof");}
 {Case c;c.hit();--c.w.self.hp;yes(c.reject(),"new damage invalidates reserve");}
 {Case c;c.hit();++c.w.self.strength;yes(c.reject(),"changed equipment/stat invalidates damage proof");}
 {Case c;c.hit();++c.w.self.spells[1].cooldown;yes(c.reject(),"unrelated cast cannot intervene");}
 {Case c;c.hit();c.w.self.can_attack=true;yes(c.reject(),"basic was not actually spent");}
 {Case c;c.hit();c.w.self.can_cast=false;yes(c.reject(),"actual cast allowance required");}
 {Case c;c.hit();c.w.spells[0].ready=false;yes(c.reject(),"actual reset availability required");}
 {Case c;c.hit();--c.w.groups[0].camps[0].hp;yes(c.reject(),"different damage cannot satisfy exact basic effect");}
 {Case c;c.hit();c.w.groups[0].state=Lifecycle::Reward;yes(c.reject(),"dead target cannot spend reset");}
 {Case c;c.hit();c.w.self.alive=false;yes(c.reject(),"dead body cannot reset");}
 {Case c;c.hit();c.w.self.completed=true;yes(c.reject(),"completed body cannot reset");}
 {Case c;c.hit();c.w.self.stunned=true;yes(c.reject(),"stunned body cannot reset");}
 {Case c;c.hit();c.memory.mission.group=1;yes(c.reject(),"another mission cannot borrow proof");}
 {Case c;c.hit();bc::budget=33999;yes(c.reject(),"consumer does not lower funded34k continuation reserve");}

 {Case c;auto&s=c.w.self.spells[1];s.kind=2;s.slot=1;s.camps=s.ready=true;s.amount=200;s.range=3;s.cooldown=0;s.recharge=8;c.w.spells=c.w.self.spells;c.paid.solo_current_followup=Kind::CastCamp;c.paid.solo_current_slot=1;auto r=make_solo_basic_receipt(c.w,c.paid);yes(r.valid&&r.required&&r.continuation==SoloBasicContinuation::Damage&&r.continuations==1,"damage selected instead of reset after real basic");c.hit();auto p=solo_basic_reset_followup(c.w,c.memory,r,true);yes(p&&p->action.kind==Kind::CastCamp&&p->action.slot==1,"paid damage follows actual accepted basic");yes(!r.valid,"damage receipt consumed once");}
 {Case c;auto&s=c.w.self.spells[1];s.kind=3;s.slot=1;s.camps=s.ready=true;s.amount=200;s.range=3;s.cooldown=0;s.recharge=8;c.w.spells=c.w.self.spells;c.paid.solo_current_followup=Kind::CastCamp;c.paid.solo_current_slot=1;bc::budget=39999;auto r=make_solo_basic_receipt(c.w,c.paid);yes(r.required&&!r.valid,"unfunded required damage cannot degrade to basic-only");bc::budget=40000;r=make_solo_basic_receipt(c.w,c.paid);yes(r.required&&r.valid,"exact40k damage owner reserve admitted");c.hit();bc::budget=15999;yes(!solo_basic_reset_followup(c.w,c.memory,r,true),"damage consumer keeps ordinary16k mutation reserve");}
 {Case c;c.w.groups[0].camps[0].hp=40;auto r=make_solo_basic_receipt(c.w,c.paid);yes(!r.required&&!r.valid,"actually lethal basic has no continuation obligation");}
 {Case c;c.w.self.can_cast=false;auto r=make_solo_basic_receipt(c.w,c.paid);yes(r.required&&!r.valid,"lost credited cast permission cannot silently downgrade to BasicOnly");}
 {Case c;c.w.self.spells[0].ready=false;c.w.spells=c.w.self.spells;c.paid.solo_current_followup=Kind::CastCamp;c.paid.solo_current_slot=1;auto r=make_solo_basic_receipt(c.w,c.paid);yes(r.required&&!r.valid,"stale credited reset is rejected rather than silently dropping obligation");}
 {Case c;bc::budget=59999;auto r=make_solo_basic_receipt(c.w,c.paid);yes(r.required&&!r.valid,"unfunded existing reset reserve blocks first basic");}
 for(int negative=0;negative<13;++negative){Case c;auto&s=c.w.self.spells[1];s.kind=2;s.slot=1;s.camps=s.ready=true;s.amount=200;s.range=3;s.cooldown=0;s.recharge=8;c.w.spells=c.w.self.spells;c.paid.solo_current_followup=Kind::CastCamp;c.paid.solo_current_slot=1;auto r=make_solo_basic_receipt(c.w,c.paid);c.hit();switch(negative){case 0:++bc::epoch;break;case 1:++c.w.serial;break;case 2:++c.w.self.hp;break;case 3:++c.w.self.shield;break;case 4:++c.w.self.shield_ticks;break;case 5:++c.w.self.spells[0].duration;break;case 6:c.w.self.can_cast=false;break;case 7:c.w.spells[1].ready=false;break;case 8:c.w.memory.moved_round=c.w.round;c.w.spells[1].exclusive=true;break;case 9:c.w.groups[0].camps[0].pos={1,1};break;case 10:c.w.groups[0].camps[0].hp-=1;break;case 11:c.w.self.alive=false;break;case 12:c.memory.mission.group=1;break;}yes(!solo_basic_reset_followup(c.w,c.memory,r,true),"changed actual damage receipt dependency rejects");yes(!r.valid,"rejection never renews across owner");}

 {Case c;c.paid.solo_current_followup=Kind::None;c.paid.solo_current_slot=-1;auto&s=c.w.self.spells[1];s.kind=2;s.slot=1;s.camps=s.ready=true;s.amount=200;s.range=3;s.cooldown=0;c.w.spells=c.w.self.spells;bc::budget=31000;auto r=make_solo_basic_receipt(c.w,c.paid);yes(!r.required&&!r.valid,"paid BasicOnly provenance does not acquire optional ready kit obligations");}
 {Case c;c.w.self.enhanced=true;c.w.groups[0].camps[0].hp=20;auto r=make_solo_basic_receipt(c.w,c.paid);yes(!r.required,"enhanced lethal basic needs no continuation payload");}
 {Case c;c.w.self.enhanced=true;c.w.self.can_cast=false;auto r=make_solo_basic_receipt(c.w,c.paid);yes(r.required&&!r.valid,"enhanced lost credited permission remains invalid required proof");}
 {Case c;c.paid.solo_current_followup=Kind::None;c.w.self.enhanced=true;auto r=make_solo_basic_receipt(c.w,c.paid);yes(!r.required,"enhanced explicit BasicOnly proof not blocked by unrelated optional payload");}
 {Actor a;a.id=1;a.type=11;a.pos={0,0};a.alive=a.can_attack=a.can_cast=true;a.hp=a.max_hp=750;a.strength=35;a.range=3;a.camp_mitigation=1;Spell s;s.slot=0;s.kind=2;s.ready=s.camps=true;s.range=4;s.amount=220;s.cooldown=0;s.recharge=8;a.spells[0]=s;Camp c;c.id=7;c.pos={3,0};c.hp=1350;c.strength=20;c.range=3;
 auto full=certify_solo_clear(a,c,a.pos,0,true);yes(full.known&&full.feasible&&full.current_followup==Kind::CastCamp&&full.current_slot==0,"actual current scalar damage credit explicit");
 a.can_cast=false;auto alternate=certify_solo_clear(a,c,a.pos,0,true);yes(alternate.known&&alternate.feasible&&alternate.current_followup==Kind::None,"first-owner no-cast schedule independently certified");yes(alternate.clear_ticks<39,"future ready casts restored by future opportunities without resetting cooldown");
 a.can_cast=true;c.hp=20;auto lethal=certify_solo_clear(a,c,a.pos,0,true);yes(lethal.known&&lethal.feasible&&lethal.current_followup==Kind::None,"lethal actual basic does not credit unnecessary cast");
 c.hp=1350;auto future=certify_solo_clear(a,c,a.pos,1,false);yes(future.known&&future.feasible&&future.current_followup==Kind::None,"future arrival cannot grant current cast receipt");
 a.spells[1].kind=1;a.spells[1].slot=1;a.spells[1].ready=a.spells[1].self=true;a.spells[1].cooldown=0;a.spells[1].recharge=8;auto either=certify_solo_clear(a,c,a.pos,0,true);yes(either.current_followup==Kind::CastCamp&&either.current_slot==0,"one current cast chooses damage rather than double-crediting reset");
 }

 {Case c;auto&s=c.w.self.spells[1];s.kind=3;s.slot=1;s.ground=s.ready=true;s.camps=false;s.amount=200;s.range=3;s.cooldown=0;s.recharge=8;c.w.spells=c.w.self.spells;c.paid.solo_current_followup=Kind::CastGround;c.paid.solo_current_slot=1;auto r=make_solo_basic_receipt(c.w,c.paid);yes(r.valid&&r.required&&r.action_kind==Kind::CastGround,"ground-only credited cast retains exact native targeting kind");c.hit();auto p=solo_basic_reset_followup(c.w,c.memory,r,true);yes(p&&p->action.kind==Kind::CastGround&&p->action.at==c.w.groups[0].camps[0].pos&&p->action.target==7,"ground continuation uses actual bound targetpoint and id");}
 {Case c;auto&s=c.w.self.spells[1];s.kind=3;s.slot=1;s.ground=s.ready=true;s.camps=false;s.amount=200;s.range=3;s.cooldown=0;s.recharge=8;c.w.spells=c.w.self.spells;c.paid.solo_current_followup=Kind::CastCamp;c.paid.solo_current_slot=1;auto r=make_solo_basic_receipt(c.w,c.paid);yes(r.required&&!r.valid,"ground-only slot cannot borrow a Camp-target credited proof");}
 {Case c;c.paid.solo_current_followup=Kind::CastGround;c.paid.solo_current_slot=0;auto r=make_solo_basic_receipt(c.w,c.paid);yes(r.required&&!r.valid,"reset cannot borrow typed Ground damage proof");}
 {Actor a;a.id=1;a.type=6;a.pos={0,0};a.alive=a.can_attack=a.can_cast=true;a.hp=a.max_hp=1200;a.strength=50;a.range=1;a.camp_mitigation=1;auto&s=a.spells[0];s.slot=0;s.kind=3;s.ready=s.ground=true;s.camps=false;s.range=4;s.radius=1;s.amount=100;s.cooldown=0;s.recharge=8;Camp c;c.id=7;c.pos={1,0};c.hp=1350;c.strength=20;c.range=3;auto q=certify_solo_clear(a,c,a.pos,0,true);yes(q.known&&q.feasible&&q.current_followup==Kind::CastGround&&q.current_slot==0,"scalar credits ground-only actual native targeting kind");c.pos={5,0};auto far=certify_solo_clear(a,c,a.pos,0,true);yes(!far.known,"ground area radius cannot extend target range");}
#ifdef TACTICS_SOLO_LETHAL_BOUND
 {Actor a;a.id=2;a.alive=a.can_attack=true;a.range=3;a.pos={2,9};a.hp=180;a.max_hp=700;a.strength=30;Camp c;c.id=42;c.pos={5,12};c.hp=10;c.strength=20;c.range=3;
 yes(solo_guaranteed_current_basic_kill(a,c),"actual low-HP lethal finish removes selected monster reply");yes(a.hp<=.25*a.max_hp+20,"witness would fail hypothetical surviving next reply");
 for(int k=0;k<7;++k){Actor b=a;if(k==0)b.alive=false;if(k==1)b.can_attack=false;if(k==2)b.completed=true;if(k==3)b.stunned=true;if(k==4)b.channel=Channel::Recall;if(k==5)b.pos={1,9};if(k==6)b.strength=0;yes(!solo_guaranteed_current_basic_kill(b,c),"actual first-hit permission/range required");}
 for(double hp:{30.,30.000001,31.,100.}){Camp d=c;d.hp=hp;yes(!solo_guaranteed_current_basic_kill(a,d),"f32 lower-credit never invents exact-boundary lethality");}
 for(double hp:{0.,-1.,double(INFINITY),double(NAN)}){Camp d=c;d.hp=hp;yes(!solo_guaranteed_current_basic_kill(a,d),"invalid/unknown live HP gives no lethal credit");}
 for(double str:{-1.,0.,double(INFINITY),double(NAN)}){Actor b=a;b.strength=str;yes(!solo_guaranteed_current_basic_kill(b,c),"invalid damage gives no lethal credit");}
 Actor b=a;b.monster=true;Camp d=c;d.hp=32.9;yes(solo_guaranteed_current_basic_kill(b,d),"actual Monster multiplier once");d.hp=33;yes(!solo_guaranteed_current_basic_kill(b,d),"Monster ideal-double equality not credited");b=a;b.enhanced=true;yes(solo_guaranteed_current_basic_kill(b,c),"ordinary lower-hit bound remains sufficient when enhanced");}
#endif
 std::printf("%d pre-basic receipt checks passed\n",checks);
}
