#define TACTICS_COMBAT_MODEL_ONLY
#include "combat.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
using namespace tactics::combat_detail;
int checks=0;
void equal(double actual,double expected,const char* name) {
    ++checks;if(std::abs(actual-expected)>.00001){std::fprintf(stderr,"FAIL %s: %.4f != %.4f\n",name,actual,expected);std::exit(1);}
}
void yes(bool value,const char* name) {equal(value?1:0,1,name);}
Actor ranged() {Actor a;a.alive=true;a.hp=a.max_hp=1000;a.pos={0,0};a.range=5;a.strength=50;return a;}
Spell spell(int kind,double amount,int range,bool exclusive=false) {
    Spell s;s.kind=kind;s.amount=amount;s.range=range;s.cooldown=0;s.ready=true;s.enemies=true;s.exclusive=exclusive;return s;
}
int main() {
    Actor a=ranged();
    equal(reply_raw(a,{5,0},5),50,"stationary ranged basic");
    equal(reply_raw(a,{6,0},6),0,"ranged walk cannot add basic");
    a.spells[0]=spell(1,0,0);
    equal(reply_raw(a,{5,0},5),100,"stationary reset double basic");
    equal(reply_raw(a,{6,0},6),50,"ranged move reset gives one basic");
    a.spells[1]=spell(2,90,5);
    equal(reply_raw(a,{5,0},5),140,"one cast chooses damage+basic not reset+damage");
    equal(reply_raw(a,{6,0},6),90,"ranged walk damage competes with reset");
    a.spells[1].exclusive=true;
    equal(reply_raw(a,{6,0},6),50,"exclusive spell cannot extend with walk");
    a.spells[0]=Spell{};
    equal(reply_raw(a,{6,0},6),0,"exclusive-only ranged approach has no invented action");
    equal(reply_raw(a,{5,0},5),140,"exclusive stationary cast permits basic");
    a.spells[1]=spell(3,90,4,true);a.spells[1].radius=2;
    equal(reply_raw(a,{6,0},6),90,"area center reaches edge recipient");
    a.range=1;a.spells[0]=spell(1,0,0);a.spells[1]=spell(2,60,1,false);
    equal(reply_raw(a,{2,0},2),110,"melee move basic compatible spell beats reset");
    a.spells[1].exclusive=true;
    equal(reply_raw(a,{2,0},2),100,"melee move reset never adds exclusive spell");
    a.spells[0]=Spell{};a.spells[1]=Spell{};
    equal(reply_raw(a,{2,0},unreachable),0,"unreachable melee no approach basic");
    a.spells[0]=spell(6,0,2);
    equal(reply_raw(a,{3,0},unreachable),50,"dash treated as separate possible edge");
    a=ranged();a.completed=true;a.can_attack=false;a.can_cast=false;
    equal(reply_raw(a,{5,0},5),50,"completed turn does not erase next opportunity");
    a.alive=false;
    equal(reply_raw(a,{5,0},5),0,"dead body contributes no damage");
    Spell unknown=spell(2,90,5);unknown.ready=false;unknown.cooldown=-1;
    yes(plausible_ready(unknown),"unknown cooldown retains uncertainty");
    unknown.cooldown=4;
    equal(plausible_ready(unknown)?1:0,0,"known long cooldown unavailable next response");
    unknown.cooldown=1;
    yes(plausible_ready(unknown),"boundary cooldown conservatively available next response");
    Actor attacker=ranged(),ren=ranged();ren.type=ren_type;ren.focus=100;ren.shield=1000;ren.hp=10;
    equal(returned_damage(attacker,ren),20,"shielded lethal Ren still returns focus damage");
    equal(returned_damage(attacker,ren,false),0,"secondary Varg splash does not trigger direct Ren return");
    attacker.mitigation=.9;
    equal(returned_damage(attacker,ren),18,"attacker mitigation applies to retaliation");
    attacker.shield=25;
    equal(returned_damage(attacker,ren),0,"attacker shield absorbs current direct retaliation");
    attacker.shield=0;attacker.hp=18;
    equal(direct_hit_survives(attacker,ren)?1:0,0,"exact lethal return not survivable");
    attacker.hp=18.01;
    yes(direct_hit_survives(attacker,ren),"strictly greater health survives current return");
    ren.type=0;
    equal(returned_damage(attacker,ren),0,"ordinary target has no invented Ren return");
    Actor victim=ranged();victim.mitigation=.9;victim.shield=10;
    equal(basic_hp_damage(attacker,victim),35,"outgoing basic mitigation then shield");
    victim.hp=5;
    equal(basic_hp_damage(attacker,victim),5,"outgoing health loss capped at current HP");
    victim.hp=1000;victim.shield=100;
    equal(basic_hp_damage(attacker,victim),0,"fully absorbed basic not lethal health damage");
    // Unknown positions are a region of alternatives, not multiple enemies.
    a=ranged();a.spells[0]=spell(1,0,0);a.spells[1]=spell(2,90,5);
    equal(region_reply_raw(a,{{0,0},{1,0}},{{1,0},{2,0}},{6,0}),140,"missing enemy alternatives counted once with one cast");
    equal(region_reply_raw(a,{},{{1,0}},{6,0}),0,"empty possible current region contributes no ghost");
    a.spells[1].exclusive=true;
    equal(region_reply_raw(a,{{0,0}},{{1,0}},{6,0}),50,"missing enemy exclusive spell not combined with movement");
    a.spells[0]=Spell{};a.spells[1]=Spell{};
    equal(region_reply_raw(a,{{0,0}},{{2,0}},{7,0}),0,"missing ranged mover cannot ordinary basic");
    a.spells[0]=spell(1,0,0);
    equal(region_reply_raw(a,{{0,0}},{{2,0}},{7,0}),50,"missing ranged reset allows one basic after movement");
    a.range=1;a.spells[1]=spell(2,60,1);
    equal(region_reply_raw(a,{{0,0}},{{2,0}},{3,0}),110,"missing melee compatible cast and basic one sequence");
    a=ranged();a.spells[1]=spell(2,90,5,true);
    equal(long_window_reply_upper(a,{0,0},{6,0},2),140,"earlier walk precedes later stationary ranged cast/basic");
    equal(long_window_reply_upper(a,{0,0},{30,0},30),140,"long channel search cap cannot erase eventual contact");
    equal(long_window_reply_upper(a,{0,0},{30,0},2),0,"short temporal window cannot reach distant target");
    a.move_speed=3;
    equal(long_window_reply_upper(a,{0,0},{14,0},4),140,"speed-times-horizon cap uses conservative earlier movement before exclusive cast/basic");
    equal(long_window_reply_upper(a,{0,0},{15,0},4),0,"ranged exclusive cast cannot share the last-window normal movement");
    equal(recent_sighting(0)?1:0,0,"same round hidden state not fabricated as older observation");
    yes(recent_sighting(1),"one-round sighting retained");
    yes(recent_sighting(3),"three-round boundary retained");
    equal(recent_sighting(4)?1:0,0,"older sighting outside declared local horizon");
    a=ranged();a.pos={0,0};a.spells[1]=spell(2,90,5,true);
    equal(coarse_remembered_reply(a,1,{7,0},1),0,"low-budget missing ranged actor cannot attack beyond temporal reach");
    equal(coarse_remembered_reply(a,2,{7,0},1),140,"low-budget missing actor retains plausible prior movement threat");
    a.spells[1].ready=false;a.spells[1].cooldown=7;
    equal(coarse_remembered_reply(a,2,{7,0},1),50,"low-budget bound preserves known long spell cooldown");
    a.spells[0]=spell(6,0,3);a.spells[1]=spell(2,90,5,true);
    equal(coarse_remembered_reply(a,1,{9,0},1),140,"low-budget uncertainty retains a plausible prior dash");
    a.spells[0].ready=false;a.spells[0].cooldown=9;
    equal(coarse_remembered_reply(a,1,{9,0},1),0,"known unavailable past dash is not added to uncertainty");
    const int width=8,height=5;
    std::vector<std::uint8_t> terrain((width*height+7)/8);
    for(int y=0;y<height;++y){int i=y*width+3;terrain[i/8]|=1u<<(i%8);}
    const auto region=expand_region(width,height,terrain,{{1,2}},3);
    bool crosses=false;for(auto p:region)crosses|=p.x>=3;
    equal(crosses?1:0,0,"uncertainty walk cannot cross full wall");
    yes(std::find(region.begin(),region.end(),Pos{2,4})!=region.end(),"uncertainty follows reachable side of wall");
    const auto dash_region=expand_region(width,height,terrain,{{1,2}},0,3);
    yes(std::find(dash_region.begin(),dash_region.end(),Pos{4,2})!=dash_region.end(),"plausible dash has separate terrain extension");
    yes(std::find(dash_region.begin(),dash_region.end(),Pos{3,2})==dash_region.end(),"dash extension excludes blocked landing");
    equal(expand_region(width,height,terrain,{{1,2},{1,2}},0).size(),1,"duplicate origins deduplicated");
    equal(expand_region(width,height,terrain,{{3,2}},1).size(),0,"blocked origin does not invent reachable region");
    std::vector<std::uint8_t> sight((width*height+7)/8);int seen=2*width+1;sight[seen/8]|=1u<<(seen%8);
    equal(remove_visible_absence({{1,2},{2,2}},width,sight,{},44).size(),1,"currently visible absence removes only observed empty origin");
    Actor seen_enemy=ranged();seen_enemy.id=44;seen_enemy.pos={1,2};
    equal(remove_visible_absence({{1,2}},width,sight,{seen_enemy},44).size(),1,"matching visible actor not removed");
    seen_enemy.id=45;
    equal(remove_visible_absence({{1,2}},width,sight,{seen_enemy},44).size(),0,"different visible actor does not preserve stale identity");
    std::printf("%d combat checks passed\n",checks);
}
