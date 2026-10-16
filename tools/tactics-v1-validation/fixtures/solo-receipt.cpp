// Exact production reset-receipt guards over explicit local snapshots.
#define TACTICS_SOLO_MODEL_ONLY
#define TACTICS_COORDINATION_MODEL_ONLY
#include "solo.h"
#include <cstdio>
#include <cstdlib>
#include <string_view>
namespace bc { static unsigned epoch=100, budget=100000;
inline unsigned fuel_remaining(){return budget;}
inline unsigned round_number(){return epoch;}}
namespace tactics {
struct World {Memory &memory;Actor self;std::array<Spell,2> spells{};std::vector<GroupView> groups;int round=100,serial=3;};
// PRODUCTION_SOLO_RECEIPT
}
using namespace tactics;
static int checks=0;
static void yes(bool value,const char*why){++checks;if(!value){std::fprintf(stderr,"FAIL %s\n",why);std::exit(1);}}
struct Case {Memory memory;World w;SoloResetReceipt receipt;
 Case():w{memory}{bc::epoch=100;bc::budget=100000;memory.mission.phase=Phase::Clear;memory.mission.group=0;memory.mission.rate=1;
  auto &a=w.self;a.id=1;a.type=4;a.pos={0,0};a.hp=a.max_hp=900;a.strength=40;a.focus=100;a.range=1;a.alive=true;a.can_cast=true;
  auto &s=a.spells[0];s.kind=1;s.slot=0;s.self=s.ready=true;s.cooldown=0;s.recharge=8;w.spells=a.spells;
  GroupView view;view.seen=100;view.state=Lifecycle::Alive;Camp camp;camp.id=7;camp.pos={1,0};camp.hp=100;camp.strength=20;camp.range=3;view.camps={camp};w.groups={view};
  Action action;action.kind=Kind::CastSelf;action.slot=0;action.target=7;action.reason="farm-certified-solo-live-reset";
  receipt=make_solo_reset_receipt(w,memory.mission,action);
  a.can_attack=true;a.can_cast=false;a.spells[0].ready=false;a.spells[0].cooldown=8;w.spells=a.spells;++w.serial;
 }
 bool reject(){return !solo_reset_basic_followup(w,memory,receipt,true);}
};
int main(){
 {Case c;yes(c.receipt.valid,"selected certified reset stamps proof");auto p=solo_reset_basic_followup(c.w,c.memory,c.receipt,true);yes(p&&p->action.kind==Kind::BasicCamp&&p->action.target==7,"actual accepted reset grants exactly charged basic");yes(c.reject(),"receipt consumed once");}
 {Case c;yes(!solo_reset_basic_followup(c.w,c.memory,c.receipt,false),"rejected native reset cannot grant basic");yes(c.reject(),"rejected receipt is consumed");}
 {Case c;--c.w.serial;yes(c.reject(),"pre-refresh serial rejected");}
 {Case c;++c.w.serial;yes(c.reject(),"extra intervening snapshot rejected");}
 {Case c;++bc::epoch;yes(c.reject(),"native owner epoch changed");}
 {Case c;++c.w.round;yes(c.reject(),"stored source round changed");}
 {Case c;--c.w.self.hp;yes(c.reject(),"new damage invalidates old reserve proof");}
 {Case c;c.w.self.pos={0,1};yes(c.reject(),"movement invalidates fixed contribution proof");}
 {Case c;--c.w.groups[0].camps[0].hp;yes(c.reject(),"intervening camp mutation invalidates receipt");}
 {Case c;c.w.groups[0].camps[0].pos={2,0};yes(c.reject(),"camp movement invalidates receipt");}
 {Case c;++c.w.self.strength;yes(c.reject(),"kit stat mutation invalidates receipt");}
 {Case c;++c.w.self.spells[1].amount;yes(c.reject(),"other ability damage changed");}
 {Case c;++c.w.self.spells[1].cooldown;yes(c.reject(),"other ability cooldown changed");}
 {Case c;c.w.self.can_attack=false;yes(c.reject(),"reset did not restore actual allowance");}
 {Case c;c.w.self.alive=false;yes(c.reject(),"dead body cannot consume attack proof");}
 {Case c;c.w.self.stunned=true;yes(c.reject(),"stunned body cannot consume attack proof");}
 {Case c;c.memory.mission.group=1;yes(c.reject(),"different committed group rejected");}
 {Case c;bc::budget=15999;yes(c.reject(),"actual16k receipt admission enforced");}
 std::printf("%d solo receipt checks passed\n",checks);
}
