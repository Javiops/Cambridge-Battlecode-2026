#include "farm_observation.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
static int checks=0;
static void need(bool v,const char*why){++checks;if(!v){std::fprintf(stderr,"FAIL %s\n",why);std::exit(1);}}
int main(){constexpr int n=16;std::vector<std::uint8_t> visible((n*n+7)/8,255);
Group g;g.spawns={{1,1,{6,6},2400,60,3},{2,1,{7,6},2400,60,3}};
GroupView live;live.seen=100;live.state=Lifecycle::Alive;
Camp a;a.id=1;a.pos={6,6};a.hp=2400;a.strength=60;a.range=3;Camp b=a;b.id=2;b.pos={7,6};live.camps={a,b};
auto seen=[&]{return fully_personally_observed_camp(g,live,visible,n,n,100);};
need(seen(),"fresh complete personal observation already resolves group information");
auto set=[&](Pos p,bool value){int i=p.y*n+p.x;if(value)visible[i/8]|=1u<<(i%8);else visible[i/8]&=~(1u<<(i%8));};
set({7,6},false);need(!seen(),"one visible original spawn grants lifecycle but not complete member coverage");set({7,6},true);
live.camps[1].pos={8,6};set({8,6},false);need(!seen(),"current hidden member cannot be replaced by seeing its empty original tile");set({8,6},true);need(seen(),"both actual current member and every original tile personally seen");
set({7,6},false);need(!seen(),"visible displaced member alone does not resolve hidden original capture region");set({7,6},true);
live.camps.pop_back();need(!seen(),"missing member is not assumed dead");live.known_dead={2};need(seen(),"fresh actual known-dead member does not require fictitious live target");
live.seen=99;need(!seen(),"earlier owner observation does not resolve current unknown state");live.seen=100;
for(auto state:{Lifecycle::Unknown,Lifecycle::Reward,Lifecycle::Respawning}){live.state=state;need(!seen(),"reward/unknown/respawn controllers retain their own contracts");}live.state=Lifecycle::Alive;
visible.clear();need(!seen(),"missing personal mask cannot erase observation job");visible.assign((n*n+7)/8,255);
g.spawns[1].pos={-1,6};need(!seen(),"malformed original coordinate cannot complete observation");g.spawns[1].pos={7,6};
live.known_dead.clear();live.camps.push_back(b);live.camps[1].hp=0;need(!seen(),"zero observed HP without declared death does not fabricate resolved lifecycle");
Group empty;need(!fully_personally_observed_camp(empty,live,visible,n,n,100),"empty static inventory is unknown");
need(!fully_personally_observed_camp(g,live,visible,0,n,100),"missing geometry is unknown");
std::printf("%d purposeful farm observation checks passed\n",checks);}
