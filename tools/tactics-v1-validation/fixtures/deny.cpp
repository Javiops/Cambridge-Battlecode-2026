#define TACTICS_COMBAT_MODEL_ONLY
#include "deny.h"
#include <cstdlib>
#include <iostream>
namespace tactics {
namespace bc {
inline unsigned fuel_remaining(){return 100000;}
namespace constants {
constexpr double submit_gem_duration_multiplier=.1;
constexpr int submit_gem_base_duration=0,submit_gem_minimum_duration=1,capture_time=5,winning_gems=1000;
}
}
struct Seen{Actor actor;int round=0;};
struct MockGeo {
    std::vector<Group>groups=std::vector<Group>(1);
    int index(Pos p)const{return p.y*32+p.x;}
};
struct World {
    Actor self;MockGeo geo;std::vector<Actor>allies,enemies;std::vector<Seen>sightings;
    std::vector<GroupView>groups=std::vector<GroupView>(1);
    std::array<Spell,2>spells{};std::vector<std::uint8_t>visible_bytes=std::vector<std::uint8_t>(128);
    int round=10,own_score=0,enemy_score=0,altar=2;bool warning=false;
    bool on_group(int gi,Pos p)const{
        if(gi<0||gi>=int(geo.groups.size()))return false;
        for(auto s:geo.groups[gi].spawns)if(s.pos==p)return true;
        return false;
    }
    int altar_distance(Pos)const{return altar;}
    bool warning_near(Pos,int)const{return warning;}
};
namespace combat_detail {
inline double spell_hp_damage(World&,const Spell&,const Actor&){return 0;}
}
// EXACT_DENIAL_PROPOSAL
}
using namespace tactics;
static int checks=0;
static void check(bool ok){++checks;if(!ok){std::cerr<<"FAIL deny "<<checks<<'\n';std::exit(1);}}
static Actor actor(int id,Pos p={5,5}){
    Actor a;a.id=id;a.pos=p;a.alive=true;a.hp=a.max_hp=100;a.strength=20;a.range=3;
    a.can_attack=a.can_cast=true;return a;
}
static Proposal proposed(Action action,double rate=1){Proposal p;p.action=action;p.valid=true;p.mission.rate=rate;return p;}
static void set(std::vector<std::uint8_t>&b,int i){b[i/8]|=1u<<(i%8);}
int main(){
    Actor self=actor(1),enemy=actor(2,{6,5});enemy.gems=40;enemy.channel=Channel::Tribute;enemy.channel_ticks=0;
    Action hit;hit.kind=Kind::BasicChampion;hit.target=2;
    auto e=denial_effect(self,enemy,hit);
    check(e.applicable&&!e.lethal&&!e.controls);
    check(denied_conversion_value(40,0,4,e)==0);
    enemy.hp=20;e=denial_effect(self,enemy,hit);check(e.lethal&&denied_conversion_value(40,0,4,e)==40);
    enemy.shield=10;e=denial_effect(self,enemy,hit);check(!e.lethal&&e.hp_damage==10);
    enemy.shield=0;enemy.mitigation=.5;check(!denial_effect(self,enemy,hit).lethal);enemy.mitigation=1;
    self.can_attack=false;check(!denial_effect(self,enemy,hit).applicable);self.can_attack=true;
    enemy.pos={20,20};check(!denial_effect(self,enemy,hit).applicable);enemy.pos={6,5};enemy.hp=100;
    self.type=7;self.enhanced=true;e=denial_effect(self,enemy,hit);check(e.controls);
    enemy.type=7;check(!denial_effect(self,enemy,hit).controls);enemy.type=2;
    self=actor(1);Spell cc;cc.kind=4;cc.ready=true;cc.enemies=true;cc.range=5;cc.duration=1;
    self.spells[0]=cc;Action cast;cast.kind=Kind::CastChampion;cast.target=2;cast.slot=0;
    e=denial_effect(self,enemy,cast);check(e.controls&&e.hp_damage==0);
    check(denied_conversion_value(40,4,4,e)==20); // Early reset earns delay, not a free full wallet.
    check(denied_conversion_value(40,-1,4,e)==0);
    self.can_cast=false;check(!denial_effect(self,enemy,cast).applicable);self.can_cast=true;
    self.type=0;self.spells[0].kind=3;self.spells[0].ground=true;self.spells[0].radius=1;
    Action area=cast;area.kind=Kind::CastGround;area.at=enemy.pos;
    check(denial_effect(self,enemy,area).controls);
    self.type=1;check(!denial_effect(self,enemy,area).controls);
    Action move;move.kind=Kind::Move;check(!denial_effect(self,enemy,move).applicable);
    self=actor(1);enemy.type=9;enemy.focus=100;self.hp=10;
    check(!denial_effect(self,enemy,hit).applicable);enemy.type=2;self=actor(1);
    check(!denial_beats_trade(40,1,false,1));check(!denial_beats_trade(40,1,true,40));
    check(denial_beats_trade(40,1,true,1));
    self.spells[0]=cc;self.spells[0].amount=200;
    check(!denial_effect(self,enemy,cast,5).lethal); // Actual selected native predictor overrides model.
    World w;w.self=self;w.spells=self.spells;w.enemies={enemy};Memory m;
    std::optional<Proposal> fight=proposed(cast),farm=proposed({},1),bank;
    auto p=denial_proposal(w,m,fight,bank,farm);check(p&&p->mission.intent==Intent::Deny);
    farm->mission.rate=100;check(!denial_proposal(w,m,fight,bank,farm));farm->mission.rate=1;
    w.enemies[0].channel=Channel::None;check(!denial_proposal(w,m,fight,bank,farm));
    w.enemies[0].channel=Channel::Tribute;bank=proposed({});bank->action.kind=Kind::Tribute;bank->priority=Priority::Deciding;
    check(!denial_proposal(w,m,fight,bank,farm));bank.reset();
    farm.reset();check(!denial_proposal(w,m,fight,bank,farm));
    w.enemy_score=970;check(denial_proposal(w,m,fight,bank,farm)->priority==Priority::Deciding);
    w.enemy_score=0;farm=proposed({},1);
    bank=proposed(move);bank->priority=Priority::Survival;
    check(!denial_proposal(w,m,fight,bank,farm));bank.reset();
    farm->priority=Priority::Survival;farm->action=move;
    check(!denial_proposal(w,m,fight,bank,farm));farm=proposed({},1);
    fight=proposed(move);check(!denial_proposal(w,m,fight,bank,farm));
    w=World{};w.self=actor(1);w.self.pos={5,5};w.allies={w.self};enemy=actor(2,{6,5});enemy.hp=10;w.enemies={enemy};
    Spawn s;s.pos={5,5};w.geo.groups[0].spawns={s};s.pos={6,5};w.geo.groups[0].spawns.push_back(s);
    w.geo.groups[0].gems=50;w.groups[0].state=Lifecycle::Reward;w.groups[0].seen=10;
    set(w.visible_bytes,w.geo.index({5,5}));set(w.visible_bytes,w.geo.index({6,5}));
    farm=proposed({},1);farm->mission.group=0;farm->mission.phase=Phase::Collect;farm->mission.target={5,5};fight=proposed(hit);
    p=denial_proposal(w,m,fight,bank,farm);check(p&&p->mission.phase==Phase::Collect);
    w.visible_bytes.assign(128,0);check(!denial_proposal(w,m,fight,bank,farm));
    set(w.visible_bytes,w.geo.index({5,5}));set(w.visible_bytes,w.geo.index({6,5}));
    w.allies.clear();check(!denial_proposal(w,m,fight,bank,farm));w.allies={w.self};
    Actor reinforcement=actor(3,{8,5});w.enemies.push_back(reinforcement);check(!denial_proposal(w,m,fight,bank,farm));w.enemies.pop_back();
    w.sightings.push_back({reinforcement,9});check(!denial_proposal(w,m,fight,bank,farm));w.sightings.clear();
    w.altar=unreachable;check(!denial_proposal(w,m,fight,bank,farm));w.altar=2;
    farm->mission.rate=10;check(!denial_proposal(w,m,fight,bank,farm));
    std::cout<<checks<<" deny checks passed\n";
}
