// Bounded acceptance fixtures call the actual bot policy, never copied formulas.
#include "types.h"
#include "draft.h"
#include <cassert>
#include <cstdlib>
#include <cstdio>
#include <set>
using namespace tactics;
static int checks=0;
static void check(bool condition,const char* name) {
    if(!condition)std::fprintf(stderr,"FAIL %s\n",name);
    if(!condition)std::exit(1);++checks;
}
int main() {
    check(distance({0,0},{3,4})==4,"movement metric diagonal distance");
    check(distance({5,8},{5,8})==0,"movement metric same position");
    check(tribute_ticks(5)==1,"small bag minimum tribute");
    check(tribute_ticks(31)==4,"tribute rounds up fractional duration");
    check(tribute_ticks(10,.1,2,1)==3,"actual settings base duration used");
    check(tribute_ticks(0,.1,0,3)==3,"actual settings minimum used");
    check(overlap_hold(5,5)==1,"normal recall requires prior held owner round");
    check(overlap_hold(5,3)==3,"Home short recall requires three held owner rounds");
    check(overlap_hold(5,8)==0,"long recall does not invent negative prior hold");
    check(deadline_allows(1997,0,1,2000),"completed before round limit feasible");
    check(!deadline_allows(1999,0,1,2000),"zero countdown still pending at deadline");
    check(!deadline_allows(1990,8,2,2000),"travel and channel both charged");
    check(deadline_allows(1990,7,2,2000),"travel and channel fit strictly before limit");

    Mission old,next;old.phase=Phase::Clear;old.group=0;old.target={8,8};old.expiry=20;old.rate=10;
    next=old;next.group=1;next.target={20,20};next.rate=100;
    check(!choose_new_job(old,next,19,false),"ordinary attractive job cannot break live lease");
    check(choose_new_job(old,next,19,true),"invalid unsafe incumbent releases immediately");
    next.rate=12.5;
    check(!choose_new_job(old,next,20,false),"equal switch margin does not oscillate");
    next.rate=12.6;
    check(choose_new_job(old,next,20,false),"expired lease permits materially better job");
    next=old;
    check(choose_new_job(old,next,15,false),"same mission can refresh without waiting lease");
    old.phase=Phase::Unassigned;
    check(choose_new_job(old,next,15,false),"initial mission needs no incumbent margin");

    check(retains_channel(Channel::Recall,false,false,true),"no observed danger retains recall");
    check(retains_channel(Channel::Recall,true,false,false),"no useful legal cancel alternative retains recall");
    check(!retains_channel(Channel::Recall,true,false,true),"useful escape may cancel lethal recall");
    check(!retains_channel(Channel::Tribute,false,true,true),"credible interrupt may justify useful tribute cancel");
    check(retains_channel(Channel::Teleport,true,true,true),"teleport has no manual cancel permission");

    Actor ally;ally.id=0;ally.alive=true;ally.hp=1000;ally.max_hp=1000;
    check(may_yield_holder(1,ally,true,true),"present lower-ID healthy matching holder accepts handoff");
    check(!may_yield_holder(1,ally,false,true),"remote claim alone cannot accept handoff");
    check(!may_yield_holder(1,ally,true,false),"physical presence without matching job cannot accept handoff");
    ally.channel=Channel::Recall;
    check(!may_yield_holder(1,ally,true,true),"departing channeler cannot accept handoff");
    ally.channel=Channel::None;ally.hp=349;
    check(!may_yield_holder(1,ally,true,true),"critically weak holder cannot accept normal handoff");
    ally.hp=350;
    check(may_yield_holder(1,ally,true,true),"health cutoff inclusive boundary");
    ally.hp=1000;
    for(int self=0;self<6;++self)for(int other=0;other<6;++other){
        ally.id=other;bool forward=may_yield_holder(self,ally,true,true);
        Actor counterpart=ally;counterpart.id=self;
        bool reverse=may_yield_holder(other,counterpart,true,true);
        check(!(forward&&reverse),"six-body collector handoff cannot be reciprocal");
        if(self==0)check(!forward,"lowest-ID real holder cannot voluntarily yield to higher ID");
    }
    ally.alive=false;
    check(!may_yield_holder(5,ally,true,true),"dead body not a physical replacement");

    auto close=draft_preferences(3,45,{});
    check(close.size()>=3&&close[0]==3&&close[1]==8&&close[2]==4,"compact geometry fallback draft");
    auto wide=draft_preferences(5,46,{});
    check(wide.size()==11&&wide[0]==2&&wide[1]==9,"long route general draft baseline");
    auto six=draft_preferences(5,20,{0,4});
    check(six[0]==5,"accepted picks excluded without confusing physical bodies");
    check(std::set<int>(six.begin(),six.end()).size()==six.size(),"draft candidates unique");
    check(draft_preferences(5,-1,{}).front()==2,"unknown geometry uses general draft");
    ClaimBytes packed{0x0f,0xa7,0x51,0x22,0xf8};
    for(int slot=0;slot<6;++slot)for(int group=-1;group<63;++group){
        auto before=packed;
        auto changed=encode_claim(packed,slot,6,63,group);
        check(changed.has_value(),"all six packed slots supported");
        check(decode_claim(*changed,slot,6,63)==group,"all packed group values roundtrip");
        for(int other=0;other<6;++other)if(other!=slot)
            check(decode_claim(*changed,other,6,63)==decode_claim(before,other,6,63),"packed update preserves other five body claims");
        check(((*changed)[4]&0xf0)==(before[4]&0xf0),"packed update preserves reserved high four bits");
        packed=*changed;
    }
    for(int slot=0;slot<5;++slot)for(int group=-1;group<255;++group){
        ClaimBytes prior{1,2,3,4,5};auto changed=encode_claim(prior,slot,5,255,group);
        check(changed.has_value()&&decode_claim(*changed,slot,5,255)==group,"legacy byte claims roundtrip");
        for(int other=0;other<5;++other)if(other!=slot)
            check((*changed)[other]==prior[other],"legacy byte update preserves all other slots");
    }
    check(!encode_claim(packed,5,6,64,10).has_value(),"unsupported sixth large-map claim never overwrites another slot");
    check(decode_claim(packed,5,6,64)==-1,"unsupported sixth large-map claim reads unknown");
    check(!encode_claim(packed,-1,6,63,1).has_value(),"negative body slot rejected");
    check(!encode_claim(packed,6,6,63,1).has_value(),"body slot outside roster rejected");
    check(decode_claim(packed,6,6,63)==-1,"outside roster reads unknown");
    auto cleared=encode_claim(packed,0,6,63,63);
    check(cleared&&decode_claim(*cleared,0,6,63)==-1,"group beyond packed capacity deliberately clears claim");
    std::printf("policy acceptance: %d checks passed\n",checks);
}
