#define TACTICS_SOLO_MODEL_ONLY
#define TACTICS_COORDINATION_MODEL_ONLY
#include "solo.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
// EXACT_CASH_POLICY
static int checks=0;
static void check(bool value,const char*why){++checks;if(!value){std::fprintf(stderr,"FAIL %s\n",why);std::exit(1);}}
int main(){
 Actor a;a.type=3;a.alive=true;a.hp=a.max_hp=700;a.strength=30;a.focus=70;a.range=3;a.move_speed=1;a.camp_mitigation=a.mitigation=1;a.can_attack=a.can_cast=a.can_move=true;a.pos={0,0};
 a.spells[0].kind=2;a.spells[0].camps=true;a.spells[0].ready=true;a.spells[0].range=4;a.spells[0].amount=140;a.spells[0].scale=2;a.spells[0].cooldown=0;a.spells[0].recharge=8;
 Camp cash;cash.id=0;cash.pos={3,0};cash.hp=500;cash.strength=0;cash.range=0;
 //21STR is an explicit synthetic policy boundary, not a native Wolf stat.
 // The old native20STR Wolf is now affordable without a Health purchase.
 Camp gem;gem.id=1;gem.pos={13,0};gem.hp=1350;gem.strength=21;gem.range=3;
 const Pos cs{0,0},capture{3,0},gs{10,0};CashGemLegs cl{0,3,6};GemReturnLegs gl{10,6,3,5,5,6,3};
 UpgradeDelta delta;delta.health=71.25;delta.family=ShopFamily::Jungle;
 auto native_wolf=gem;native_wolf.strength=20;
 check(certify_solo_clear(a,native_wolf,gs,1,false).feasible,"correct native Wolf clock does not require a Health unlock");
 check(!completed_cash_gem(a,cash,cs,capture,cl,0,35,30,delta,native_wolf,gs,gl,2000,1.25).known,"obsolete native cash detour is not forced to buy");
 auto price=[&](const Actor&b,const Camp&c,const CashGemLegs&legs,int wallet=0,int gold=35,int cost=30,int horizon=2000){return completed_cash_gem(b,c,cs,capture,legs,wallet,gold,cost,delta,gem,gs,gl,horizon,1.25);};
 const auto q=price(a,cash,cl);
 check(q.known&&q.worthwhile,"one35gold payout buys exact30gold shard and unlocks real gem trip");
 check(q.cash_ticks>cl.hold&&q.total_ticks>q.cash_ticks+q.absence,"cash clear capture and entire returned gem cycle are priced");
 check(!price(a,cash,cl,0,17,30).known,"shared payout cannot finance promised bundle");
 check(!price(a,cash,cl,0,29,30).known,"insufficient sole reward declines");
 check(price(a,cash,cl,5,25,30).known,"exact future wallet amount funds named bundle");
 check(!price(a,cash,cl,30,35,30).known,"already affordable wallet is handled by actual return planner");
 check(!price(a,cash,cl,-1,35,30).known,"invalid wallet declines");
 check(!price(a,cash,cl,0,35,0).known,"zero item cost does not fabricate investment");
 check(!price(a,cash,cl,0,35,60).known,"one payout cannot silently become repeated cash cycles");
 auto bad=cl;bad.walk=unreachable;check(!price(a,cash,bad).known,"missing cash approach field declines");
 bad=cl;bad.capture_walk=unreachable;check(!price(a,cash,bad).known,"missing actual capture walk declines");
 bad=cl;bad.hold=0;check(!price(a,cash,bad).known,"unpriced capture hold declines");
 auto awake=cash;awake.awake=true;check(!price(a,awake,cl).known,"new chain does not start through awake cash camp");
 auto dead=a;dead.alive=false;check(!price(dead,cash,cl).known,"dead actor cannot acquire promised future gold");
 auto bag=a;bag.gems=1;check(!price(bag,cash,cl).known,"carried gems need their real conversion before cash detour");
 auto attacked=cash;attacked.strength=100;attacked.range=3;check(!price(a,attacked,cl).known,"unsafe cash clear cannot finance continuation");
 const int deadline=static_cast<int>(q.total_ticks);
 check(!price(a,cash,cl,0,35,30,deadline).known,"exact horizon cannot fit completed finite itinerary");
 check(price(a,cash,cl,0,35,30,deadline+1).known,"one more owner admits a completed priced endpoint");
 auto upgraded=a;upgraded.hp=upgraded.max_hp=1000;check(!price(upgraded,cash,cl).known,"already feasible same gem route receives no fictional unlock");
 CashInvestment receipt;receipt.group=0;receipt.item=28;receipt.count=1;receipt.gold_before=0;receipt.expected_gold=35;receipt.holding=true;
 check(cash_reward_paid(receipt,35,30,true,Lifecycle::Respawning,true),"observed completed solo payout authorizes actual wallet");
 check(!cash_reward_paid(receipt,0,30,true,Lifecycle::Respawning,true),"projected35 never substitutes for actual zero wallet");
 check(!cash_reward_paid(receipt,17,30,true,Lifecycle::Respawning,true),"actual shared payout cannot install promised item");
 check(!cash_reward_paid(receipt,35,60,true,Lifecycle::Respawning,true),"actual payout still must afford exact bundle");
 check(!cash_reward_paid(receipt,35,30,true,Lifecycle::Reward,true),"capture hold is not completed native payout");
 check(!cash_reward_paid(receipt,35,30,true,Lifecycle::Alive,true),"successful hit is not capture completion");
 check(!cash_reward_paid(receipt,35,30,false,Lifecycle::Respawning,true),"stale public lifecycle cannot authorize transition");
 check(!cash_reward_paid(receipt,35,30,true,Lifecycle::Respawning,false),"unrelated remote payout is not this holder receipt");
 receipt.holding=false;check(!cash_reward_paid(receipt,35,30,true,Lifecycle::Respawning,true),"unobserved capture prefix cannot create receipt");receipt.holding=true;
 receipt.gold_before=5;check(!cash_reward_paid(receipt,35,30,true,Lifecycle::Respawning,true),"partial unexpected wallet delta invalidates expected payout");
 check(cash_reward_paid(receipt,40,30,true,Lifecycle::Respawning,true),"actual prior wallet plus sole payout funds exact purchase");
 receipt.expected_gold=0;check(!cash_reward_paid(receipt,40,30,true,Lifecycle::Respawning,true),"zero-income receipt cannot manufacture investment");
 std::printf("%d finite cash investment checks passed\n",checks);
}
