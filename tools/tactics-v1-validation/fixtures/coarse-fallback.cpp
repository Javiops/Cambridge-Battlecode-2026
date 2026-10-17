#define TACTICS_COORDINATION_MODEL_ONLY
#define TACTICS_COMBAT_MODEL_ONLY
#include "coordination.h"
#include "combat.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
namespace bc {
inline unsigned remaining=100000;
inline int now=100;
inline unsigned fuel_remaining(){return remaining;}
inline int round_number(){return now;}
}
namespace tactics {
struct World {
 int round=100;Actor self;
 struct Geo {std::vector<Group>groups;int index(Pos p)const{return p.y*32+p.x;}}geo;
 struct Sighting {Actor actor;int round=100;};
 std::vector<GroupView>groups;
 std::vector<Actor>allies,enemies;
 std::vector<Sighting>sightings;
 std::vector<std::uint8_t>visible_bytes=std::vector<std::uint8_t>(128,255);
 bool warning=false;
 bool warning_near(Pos,int)const{return warning;}
 bool matching_claim(int,int)const{return true;}
};
// EXACT_FALLBACK
}
static int checks=0;
static void need(bool v,const char*why){++checks;if(!v){std::fprintf(stderr,"FAIL %s\n",why);std::exit(1);}}
static World setup(double hp=900,double campHP=500){
 bc::remaining=100000;bc::now=100;World w;
 auto&a=w.self;a.id=3;a.type=4;a.pos={1,1};a.alive=true;a.hp=hp;a.max_hp=900;
 a.strength=40;a.focus=100;a.range=1;a.camp_mitigation=1;a.can_attack=a.can_cast=true;
 a.spells[0].slot=0;a.spells[0].kind=1;a.spells[0].self=a.spells[0].ready=true;
 a.spells[0].cooldown=0;a.spells[0].recharge=8;
 Camp c;c.id=0;c.pos={2,1};c.hp=c.max_hp=campHP;c.strength=20;c.range=3;
 Group g;g.spawns.push_back({0,0,c.pos,c.hp,c.strength,c.range});w.geo.groups.push_back(g);
 GroupView v;v.seen=100;v.state=Lifecycle::Alive;v.camps.push_back(c);w.groups.push_back(v);return w;
}
int main(){
 const std::array self{3};
 {auto w=setup();auto r=current_basic_farm_fallback(w,0,self);
  need(r.ready&&r.complete&&r.proof==ClearProofKind::BasicOnly,"safe actual ordinary basics retain typed complete proof");
  need(r.selected_ids==std::vector<int>({3})&&r.remaining_hp[0]>.25*w.self.max_hp,"proof carries actual IDs and reserve");
  LocalAssignment a;use_basic_farm_fallback(a,r);Mission m;
  need(a.ready&&a.self_selected&&a.locally_accepted&&name_current_crew(m,a,3),"low-budget skipped assignment can name only certified IDs");
  need(m.assembly_count==1&&m.assembly_ids[0]==3&&a.rollout.proof==ClearProofKind::BasicOnly,"existing one-basic gateway receives BasicOnly provenance");
  a.uncertain=true;a.ready=false;use_basic_farm_fallback(a,r);
  need(a.ready&&!a.uncertain&&a.rollout.proof==ClearProofKind::BasicOnly,"Unknown detailed assignment restored only by independent sufficient proof");}
 {auto w=setup(850,1350);auto r=current_basic_farm_fallback(w,0,self);
  need(!r.ready,"unsupported30tick reset heuristic cannot authorize34owner ordinary basic execution");}
 {auto w=setup();auto c=w.groups[0].camps[0];c.id=1;c.pos={8,1};c.hp=2400;c.strength=60;
  w.groups[0].camps.push_back(c);w.geo.groups[0].spawns.push_back({1,0,c.pos,c.hp,c.strength,c.range});
  need(!current_basic_farm_fallback(w,0,self).ready,"one reachable member never certifies far surviving group member");
  w.groups[0].known_dead.push_back(1);w.groups[0].camps.pop_back();
  need(current_basic_farm_fallback(w,0,self).ready,"fresh known dead member does not block real remaining singleton");}
 {auto w=setup();w.groups[0].camps.clear();need(!current_basic_farm_fallback(w,0,self).ready,"hidden wandering member not dead");}
 {auto w=setup();w.visible_bytes[4]=0;need(!current_basic_farm_fallback(w,0,self).ready,"missing actual personal camp visibility cannot certify hit");}
 {auto w=setup();w.self.can_attack=false;need(!current_basic_farm_fallback(w,0,self).ready,"ready reset alone is not a currently funded basic");}
 {auto w=setup();w.self.completed=true;need(!current_basic_farm_fallback(w,0,self).ready,"completed owner never becomes ready");}
 {auto w=setup();w.self.stunned=true;need(!current_basic_farm_fallback(w,0,self).ready,"stunned actor cannot carry future basic promise");}
 {auto w=setup();w.groups[0].seen=99;need(!current_basic_farm_fallback(w,0,self).ready,"stale group excluded");}
 {auto w=setup();bc::now=101;need(!current_basic_farm_fallback(w,0,self).ready,"stale native epoch excluded");}
 {auto w=setup();bc::remaining=35999;need(!current_basic_farm_fallback(w,0,self).ready,"unfunded independent proof is Unknown");}
 {auto w=setup();w.warning=true;need(!current_basic_farm_fallback(w,0,self).ready,"remote danger not silently omitted");}
 {auto w=setup();w.geo.groups.clear();need(!current_basic_farm_fallback(w,0,self).ready,"geometry group bound is checked independently");}
 {auto w=setup();Group other;w.geo.groups.push_back(other);GroupView view;view.seen=100;view.state=Lifecycle::Alive;
  Camp external;external.id=1;external.pos={1,2};external.hp=1000;external.strength=20;external.range=3;external.awake=true;
  view.camps.push_back(external);w.groups.push_back(view);
  need(!current_basic_farm_fallback(w,0,self).ready,"external awake overlapping camp is not paid by selected-group reserve");
  w.groups[1].camps[0].pos={20,20};need(current_basic_farm_fallback(w,0,self).ready,"external awake camp outside actual response range preserves safe work");}
 {auto w=setup();auto e=w.self;e.id=8;e.pos={15,1};e.move_speed=1;w.enemies.push_back(e);
  need(!current_basic_farm_fallback(w,0,self).ready,"full-clear possible enemy contact vetoes one-reply reserve shortcut");}
 {auto w=setup();auto e=w.self;e.id=8;e.pos={15,1};e.move_speed=1;w.sightings.push_back({e,99});
  need(!current_basic_farm_fallback(w,0,self).ready,"recent unseen contact retains full-window veto");}
 {auto w=setup();w.self.type=10;Group other;other.spawns.push_back({1,0,{3,1},500,20,3});
  w.geo.groups.push_back(other);w.groups.push_back({});need(!current_basic_farm_fallback(w,0,self).ready,"unavoidable Varg basic splash cannot wake outside forecast group");
  w.self.type=4;need(current_basic_farm_fallback(w,0,self).ready,"ordinary nonarea basic does not borrow optional AoE veto");}
 {auto w=setup();auto helper=w.self;helper.id=4;helper.pos={1,2};w.allies.push_back(helper);
  const std::array ids{3,4};auto r=current_basic_farm_fallback(w,0,ids);
  need(r.ready&&r.selected_ids==std::vector<int>({3,4}),"actual fixed ready pair carries exact selected IDs");
  w.allies[0].can_attack=false;need(!current_basic_farm_fallback(w,0,ids).ready,"spent helper cast-ready DPS is never ordinary basic readiness");}
 std::printf("%d exact ordinary fallback checks passed\n",checks);
}
