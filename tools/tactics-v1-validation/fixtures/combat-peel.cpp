#define TACTICS_COMBAT_MODEL_ONLY
#include "combat.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
using namespace tactics::combat_detail;
static int checks=0;
static void check(bool value,const char*why){++checks;if(!value){std::fprintf(stderr,"FAIL %s\n",why);std::exit(1);}}
static unsigned state=0x763a91bdu;
static unsigned next(){state^=state<<13;state^=state>>17;state^=state<<5;return state;}
int main(){
 Actor caster,enemy;Spell spell;
 caster.can_cast=true;caster.hp=caster.max_hp=100;caster.mitigation=1;caster.pos={0,0};
 enemy.alive=true;enemy.type=4;enemy.hp=enemy.max_hp=900;enemy.pos={4,4};
 spell.kind=4;spell.ready=spell.enemies=true;spell.range=4;spell.duration=2;
 check(peel_target_eligible(caster,spell,enemy),"Chebyshev range boundary is a legal candidate");
 enemy.pos={5,4};check(!peel_target_eligible(caster,spell,enemy),"range five cannot peel with range four");enemy.pos={4,4};
 enemy.type=marcella_type;check(!peel_target_eligible(caster,spell,enemy),"control immune target cannot save ally");enemy.type=4;
 spell.ready=false;check(!peel_target_eligible(caster,spell,enemy),"cooldown spell cannot peel");spell.ready=true;
 caster.can_cast=false;check(!peel_target_eligible(caster,spell,enemy),"spent cast right cannot peel");caster.can_cast=true;
 spell.enemies=false;check(!peel_target_eligible(caster,spell,enemy),"allied-only cast not an enemy peel");spell.enemies=true;
 spell.duration=0;check(!peel_target_eligible(caster,spell,enemy),"zero control adds no windows");spell.duration=2;
 enemy.stunned=true;enemy.stun_ticks=2;check(!peel_target_eligible(caster,spell,enemy),"equal control duration adds no window");
 enemy.stun_ticks=1;check(peel_target_eligible(caster,spell,enemy),"strictly extending known control remains useful");
 enemy.stun_ticks=-1;check(!peel_target_eligible(caster,spell,enemy),"unknown active stun cannot certify extension");enemy.stunned=false;
 enemy.type=ren_type;enemy.focus=500;check(!peel_target_eligible(caster,spell,enemy),"exact self-lethal reflection is declined");
 caster.shield=1;check(peel_target_eligible(caster,spell,enemy),"one shield HP makes reflected cast survivable");
 caster.shield=0;caster.mitigation=.9;check(peel_target_eligible(caster,spell,enemy),"caster mitigation applies to reflection");
 int eligible_cases=0;
 for(int i=0;i<20000;++i){
  caster.can_cast=next()&1;caster.hp=1+next()%200;caster.shield=next()%100;caster.mitigation=(1+next()%10)/10.;caster.pos={int(next()%21)-10,int(next()%21)-10};
  enemy.type=next()%11;enemy.pos={int(next()%21)-10,int(next()%21)-10};enemy.focus=next()%1000;enemy.stunned=next()&1;enemy.stun_ticks=int(next()%7)-1;
  spell.ready=next()&1;spell.enemies=next()&1;spell.range=next()%9;spell.duration=int(next()%5)-1;
  const bool old_can_cast=caster.can_cast&&spell.ready&&spell.enemies&&distance(caster.pos,enemy.pos)<=spell.range;
  const bool old=old_can_cast&&added_control_windows(enemy,spell.duration)>0&&direct_hit_survives(caster,enemy);
  eligible_cases+=old;
  check(peel_target_eligible(caster,spell,enemy)==old,"eligibility equals the former per-ally predicate");
 }
 if(eligible_cases<20||eligible_cases>19980){std::fprintf(stderr,"FAIL degenerate randomized coverage %d\n",eligible_cases);return 1;}
 std::printf("%d peel eligibility checks passed (%d eligible randomized cases)\n",checks,eligible_cases);
}
