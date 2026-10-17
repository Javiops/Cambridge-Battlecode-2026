#define TACTICS_COORDINATION_MODEL_ONLY
#define TACTICS_SOLO_MODEL_ONLY
#include "solo.h"
#include "information.h"
#include <cstdio>
#include <cstdlib>
#include <string_view>
using namespace tactics;
namespace bc { static int now=100; inline int round_number(){return now;} inline unsigned fuel_remaining(){return 100000;} }
static bool safe=true;
inline bool fuel(int){return true;}
struct World {
 struct Geo { int index(Pos p)const{return p.y*20+p.x;} } geo;
 Memory&memory;Actor self;std::array<Spell,2>spells;std::vector<GroupView>groups;
 std::vector<std::uint8_t>visible_bytes=std::vector<std::uint8_t>(50,255);int round=100,serial=7;
 explicit World(Memory&m):memory(m){}
 bool free(Pos)const{return true;}
};
inline bool farm_safe(World&,int){return safe;}
inline double incoming_damage(World&,Pos){return 0;}
inline bool current_solo_quote(const World&w,const SoloFarmQuote&q,int gi){return q.group==gi&&q.owner==w.self.id&&q.round==w.round&&q.serial==w.serial&&q.origin==w.self.pos;}
inline Proposal economic(const Action&a,const Mission&m,Priority p,double v){Proposal x;x.action=a;x.mission=m;x.priority=p;x.value=v;x.valid=true;return x;}
inline Action moving(Pos p,const char*why){Action a;a.kind=Kind::Move;a.at=p;a.reason=why;return a;}
// EXACT_TYPED_SOLO_CONSUMER
static int checks=0;
static void yes(bool v,const char*why){++checks;if(!v){std::fprintf(stderr,"FAIL %s\n",why);std::exit(1);}}
int main(){Memory m;World w(m);w.self.id=6;w.self.alive=w.self.can_attack=w.self.can_cast=true;w.self.pos={9,6};w.self.range=3;w.self.hp=w.self.max_hp=700;
 Camp camp;camp.id=3;camp.pos={5,5};camp.hp=2400;camp.range=3;camp.strength=60;
 GroupView view;view.state=Lifecycle::Alive;view.seen=100;view.camps.push_back(camp);w.groups.push_back(view);
 auto&s=w.spells[0];s.kind=2;s.slot=0;s.camps=s.ready=true;s.cooldown=0;s.range=4;s.amount=140;
 w.spells[1]=s;w.spells[1].slot=1;w.spells[1].kind=3;w.spells[1].amount=1000;
 SoloFarmQuote q;q.group=0;q.owner=6;q.round=100;q.serial=7;q.origin=q.stage=w.self.pos;q.target=camp.pos;q.known=q.feasible=q.ready_now=true;q.rate=.2;q.mode=SoloFarmMode::DirectCastOnly;q.slot=0;
 auto p=solo_farm_proposal(w,m,q);yes(p&&p->action.kind==Kind::CastCamp&&p->action.slot==0,"typed direct slot cannot be replaced by larger ready area spell");
 yes(p&&!p->solo_clear_certified&&!p->crew_clear_certified,"outer cast cannot mint basic/reset or crew receipts");

 m.mission.group=0;m.mission.phase=Phase::Clear;m.mission.assembly_count=2;m.mission.assembly_ids={6,7};m.mission.assembly_anchor=6;m.mission.assembly_helper=7;m.mission.assembly_route_length=3;m.mission.assembly_exit_length=2;m.mission.assembly_signature=42;
 p=solo_farm_proposal(w,m,q);yes(p&&p->action.slot==0&&p->mission.assembly_count==0&&p->mission.assembly_anchor==-1&&p->mission.assembly_helper==-1&&p->mission.assembly_signature==0&&p->mission.assembly_route_length==0&&p->mission.assembly_exit_length==0,"same-group former crew cannot retain controller ownership over selected solo cast");
 q.ready_now=false;p=solo_farm_proposal(w,m,q);yes(p&&p->action.kind==Kind::None&&p->mission.assembly_count==0,"same-group coalition also cleared for stationary cooldown hold");m.mission={};
 q.ready_now=false;s.ready=false;s.cooldown=5;
 p=solo_farm_proposal(w,m,q);yes(p&&p->action.kind==Kind::None&&p->mission.phase==Phase::Clear,"new initialCD5 uses paid stationary Clear intention without phantom hit");
 yes(p&&p->mission.last_camp_hp==2400&&p->mission.last_progress==100,"new wait records observed HP and job start, no fabricated monster damage");
 m.mission=p->mission;m.mission.last_progress=90;
 for(int cd=8;cd>=1;--cd){s.cooldown=cd;p=solo_farm_proposal(w,m,q);yes(p&&p->action.kind==Kind::None&&p->mission.phase==Phase::Clear,"every knownCD8through1 remains no-action clear hold");yes(p&&p->mission.last_progress==90,"cooldown wait never counts as actual HP progress");}
 safe=false;p=solo_farm_proposal(w,m,q);yes(!p,"actual safety veto still applies to paid cooldown hold");safe=true;
 q.ready_now=true;s.ready=true;s.cooldown=0;w.self.can_cast=false;p=solo_farm_proposal(w,m,q);yes(!p,"spent actual cast permission cannot consume ready quote");w.self.can_cast=true;
 s.cooldown=1;p=solo_farm_proposal(w,m,q);yes(!p,"current native cooldown cannot consume forged readiness");s.cooldown=0;
 q.slot=1;p=solo_farm_proposal(w,m,q);yes(!p,"area slot never authorized by direct-only mode");q.slot=0;
 q.serial=6;p=solo_farm_proposal(w,m,q);yes(!p,"older serial rejected before action or hold");q.serial=7;
 w.visible_bytes.assign(50,0);p=solo_farm_proposal(w,m,q);yes(!p,"earlier-position group state is not current personal cast sight");q.ready_now=false;p=solo_farm_proposal(w,m,q);yes(!p,"unseen camp cannot retain a paid outer cooldown hold");
 std::printf("%d typed solo consumer checks passed\n",checks);
}
