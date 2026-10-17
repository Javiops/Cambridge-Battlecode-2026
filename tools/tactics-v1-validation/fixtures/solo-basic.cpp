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
 paid.mission=memory.mission;paid.action.kind=Kind::BasicCamp;paid.action.target=7;paid.valid=true;paid.solo_clear_certified=true;receipt=make_solo_basic_receipt(w,paid);
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
 {Case c;auto&s=c.w.spells[1];s.kind=2;s.camps=s.ready=true;s.amount=200;s.range=3;yes(!make_solo_basic_receipt(c.w,c.paid).valid,"ready damage cast retains the schedule's one cast");}
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
 std::printf("%d pre-basic receipt checks passed\n",checks);
}
