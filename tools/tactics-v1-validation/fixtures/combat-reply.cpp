#define TACTICS_COMBAT_MODEL_ONLY
#include "combat.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
using namespace tactics::combat_detail;
static int checks=0;
static void equal(double a,double b,const char *why){++checks;if(std::abs(a-b)>1e-8){std::fprintf(stderr,"FAIL %s %.3f != %.3f\n",why,a,b);std::exit(1);}}
static void yes(bool a,const char *why){equal(a?1:0,1,why);}
int main(){
    Actor self;self.alive=true;self.can_move=true;self.range=1;
    Action basic;basic.kind=Kind::BasicChampion;
    yes(preserves_ready_walk(self,basic),"melee basic preserves ready walk");
    equal(marginal_reply_cost(200,200,true),0,"unchanged holding reply cancels at common endpoint");
    yes(60-marginal_reply_cost(200,200,true)>0,"useful melee is not declined for unavoidable holding pressure");
    self.range=4;
    equal(preserves_ready_walk(self,basic)?1:0,0,"ranged basic consumes ready ordinary walk");
    equal(marginal_reply_cost(200,200,false,0,true),100,"ranged basic pays known safe-escape opportunity");
    equal(marginal_reply_cost(200,200,false,200,true),0,"no better escape means same endpoint risk");
    equal(marginal_reply_cost(200,200,false,80,true),60,"locking attack pays marginal lost escape");
    equal(marginal_reply_cost(200,200,false,200,false),100,"incomplete frontier gives no optimistic baseline credit");
    equal(marginal_reply_cost(200,200,false,400,true),0,"escape baseline cannot exceed holding alternative");
    self.can_move=false;
    yes(preserves_ready_walk(self,basic),"spent walk is not charged twice by ranged followup");
    self.can_move=true;
    Action cast;cast.kind=Kind::CastChampion;cast.slot=0;
    self.spells[0].exclusive=false;
    yes(preserves_ready_walk(self,cast),"compatible cast retains walk");
    self.spells[0].exclusive=true;
    equal(preserves_ready_walk(self,cast)?1:0,0,"exclusive cast loses ready walk");
    cast.slot=-1;
    equal(preserves_ready_walk(self,cast)?1:0,0,"unknown cast rights are conservative");
    self.range=1;
    equal(preserves_ready_walk(self,basic,true)?1:0,0,"movement first compares changed endpoint to escape alternative");
    equal(marginal_reply_cost(0,200,true),-100,"actual immediate removal earns reduced reply credit");
    equal(marginal_reply_cost(220,200,true),10,"extra retaliation is still priced over holding");
    equal(marginal_reply_cost(200,0,true),100,"new pressure is not waived as common holding damage");
    yes(marginal_reply_cost(unknown_reply_upper(),unknown_reply_upper(),true)>1e100,"unknown sentinels never cancel to zero");
    equal(marginal_reply_cost(200,unknown_reply_upper(),true),100,"unknown baseline grants no invented credit");
    equal(marginal_reply_cost(200,200,false,unknown_reply_upper(),true),100,"unknown escape is not a certified alternative");
    yes(!known_reply(unknown_reply_upper()),"finite unknown remains explicitly unknown");
    yes(known_reply(0),"known no damage remains exact");
    Actor target;target.alive=true;target.hp=target.max_hp=1000;target.pos={1,0};
    self.pos={0,0};self.strength=60;self.can_attack=self.can_cast=true;
    self.spells[0]=Spell{};self.spells[0].kind=1;self.spells[0].self=self.spells[0].ready=true;
    self.spells[1]=Spell{};self.spells[1].kind=2;self.spells[1].enemies=self.spells[1].ready=true;
    self.spells[1].amount=90;self.spells[1].range=1;
    bool reset=false,damage=false,illegal=false;
    for(const auto &sequence:stationary_sequences(self,target)){
        reset|=sequence.actions==3&&sequence.exchange.hits==2&&sequence.exchange.hp_damage==120;
        damage|=sequence.actions==2&&sequence.exchange.hits==2&&sequence.exchange.hp_damage==150;
        illegal|=sequence.exchange.hp_damage>150;
    }
    yes(reset&&damage&&!illegal,"marginal scoring does not add reset and damage casts to one sequence");
    std::printf("%d common-endpoint checks passed\n",checks);
}
