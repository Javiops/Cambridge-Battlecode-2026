#include "camp_basic.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
int main(){int checks=0;auto ck=[&](bool x,const char*n){++checks;if(!x){std::fprintf(stderr,"FAIL %s\n",n);std::exit(1);}};
Actor a;a.id=1;a.type=2;a.alive=a.can_attack=true;a.hp=a.max_hp=1000;a.strength=100;a.range=3;a.pos={0,0};
std::array<Actor,3> actors{a,a,a};actors[1].id=2;actors[2].id=3;
std::array<Camp,3> camps;for(int i=0;i<3;++i){camps[i].id=i;camps[i].pos={i,1};camps[i].hp=camps[i].max_hp=100;camps[i].strength=10;camps[i].range=3;}
std::array<BasicCampBody,3> bodies;std::array<BasicCampMonster,3> monsters;
for(int i=0;i<3;++i){bodies[i]={&actors[i],0};monsters[i]={&camps[i],true};}
auto run=[&](){return sufficient_basic_clear(bodies,monsters,1);};
auto r=run();ck(r.ready&&r.ticks==2,"conservative full-coverage sufficient clear");ck(r.damage_taken[0]>=30&&r.damage_taken[0]<30.01&&r.damage_taken[1]>=30&&r.damage_taken[1]<30.01,"full nearest ties each absorb full group response");
auto old=actors;
actors[0].can_attack=false;ck(run().ready&&run().ticks==3,"spent current permission is excluded from first volley");
for(auto&x:actors){x.can_attack=false;x.completed=true;}ck(run().ready&&run().ticks==3,"zero current volley waits one real camp response before future basics");actors=old;
actors[0].range=1;ck(!run().ready,"cast reach does not substitute basic reach to every member");actors=old;
actors[0].hp=200;ck(!run().ready,"actual health floor rejects fragile nearest tank");actors=old;
bodies[0].reserve=800;ck(!run().ready,"exit or enemy reserve is retained");bodies[0].reserve=0;
actors[1].pos={10,10};ck(!run().ready,"future walking is not a fixed clear certificate");actors=old;
monsters[2].observed=false;ck(!run().ready,"unseen living member cannot enter positive certificate");monsters[2].observed=true;
actors[0].stunned=true;ck(!run().ready,"current stun is unknown rather than future free actions");actors=old;
actors[0].channel=Channel::Recall;ck(!run().ready,"current channelled helper cannot promise basic sequence");actors=old;
actors[0].id=2;ck(!run().ready,"duplicate body cannot provide two volleys");actors=old;
actors[0].type=40;ck(!run().ready,"unknown passive family is unsupported");actors=old;
for(auto&x:actors){x.strength=1;x.spells[0].kind=2;x.spells[0].amount=1e9;x.spells[0].ready=true;}ck(!run().ready,"arbitrary free future spell cannot rescue failing basic bound");actors=old;
for(auto&x:actors)x.shield=1e9;actors[0].hp=200;ck(!run().ready,"unproven shield duration is not durable clear HP");actors=old;
actors[0].strength=100;for(auto&x:camps){x.hp=1;x.strength=0;}
auto solo=sufficient_basic_clear(std::span(bodies.data(),1),monsters,1);ck(solo.ready&&solo.ticks==3,"one huge attacker needs three opportunities for three tiny targets");
for(auto&x:camps)x.hp=100;actors[0].strength=10;actors[0].hp=actors[0].max_hp=100;for(auto&x:camps)x.strength=60;
ck(!sufficient_basic_clear(std::span(bodies.data(),1),monsters,1).ready,"long vulnerable basic-only clear remains Unknown");
actors=old;for(auto&x:camps){x.hp=150;x.strength=10;}
auto plain=run();actors[0].monster=true;auto emblem=run();ck(emblem.ready&&emblem.ticks<=plain.ticks,"actual Monster multiplier is credited once");
actors=old;for(auto&x:camps){x.hp=0;x.strength=10;}ck(!run().ready,"no living group uses capture policy rather than fabricated clear");
actors=old;for(auto&x:camps){x.hp=500;x.strength=0;}actors[0].strength=55.55555725097656;
auto boundary=sufficient_basic_clear(std::span(bodies.data(),1),std::span(monsters.data(),1),1);
ck(boundary.ready&&boundary.ticks==10,"native f32 nine-hit residual needs tenth basic rather than double ceil shortcut");
actors[0].id=-1;ck(!sufficient_basic_clear(std::span(bodies.data(),1),std::span(monsters.data(),1),-1).ready,"negative external self identity cannot certify a crew");actors=old;
camps[0].id=-1;ck(!run().ready,"negative native camp identity is not a legal target certificate");camps[0].id=0;
actors[0].strength=.000001;camps[0].hp=1e8;
ck(!sufficient_basic_clear(std::span(bodies.data(),1),std::span(monsters.data(),1),1).ready,"below-ULP hit with zero possible native HP progress is Unknown");
actors=old;for(auto&x:camps){x.hp=500;x.strength=0;}camps[0].hp=2400;camps[0].strength=60;camps[1].hp=1350;camps[1].strength=20;actors[0].type=0;actors[0].range=2;actors[1].type=10;actors[1].range=1;actors[2].type=8;actors[2].range=3;actors[2].spells[0].kind=5;actors[2].spells[0].amount=100;
ck(!run().ready,"hard seventeen-tick Ryth Varg Willow geometry remains detailed fallback, never a fake basic positive");
std::array<Camp,9> large;std::array<BasicCampMonster,9> lm;actors=old;for(int i=0;i<9;++i){large[i].id=i;large[i].pos={i%3,1+i/3};large[i].hp=10;large[i].strength=1;large[i].range=3;lm[i]={&large[i],true};}
for(auto&x:actors)x.range=4;
for(int count:{4,8}){auto many=sufficient_basic_clear(bodies,std::span(lm.data(),count),1);ck(many.ready&&many.count==3,"observed four/eight-member full-coverage group receives sufficient basic certificate");}
ck(!sufficient_basic_clear(bodies,lm,1).ready,"ninth living member is explicit bounded Unknown rather than truncation");
actors[0].range=1;ck(!sufficient_basic_clear(bodies,std::span(lm.data(),8),1).ready,"larger group still requires actual basic reach to every member");actors[0].range=4;
lm[7].observed=false;ck(!sufficient_basic_clear(bodies,std::span(lm.data(),8),1).ready,"eighth hidden member invalidates full larger-group certificate");
lm[7].observed=true;
for(int cap:{0,2,6,12}){int polls=0;auto capped=sufficient_basic_clear(bodies,std::span(lm.data(),8),1,[&]{return polls++<cap;});ck(!capped.ready,"budget interruption is Unknown without importing a cached positive");}
auto funded=sufficient_basic_clear(bodies,std::span(lm.data(),8),1,[]{return true;});ck(funded.ready&&funded.ticks==sufficient_basic_clear(bodies,std::span(lm.data(),8),1).ticks,"funded callback preserves the same sufficient certificate semantics");
std::printf("%d camp basic checks passed\n",checks);}
