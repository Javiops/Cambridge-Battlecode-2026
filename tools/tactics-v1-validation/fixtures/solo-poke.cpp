#include "solo_poke.h"
#include "solo_routes.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
static int checks=0;
static void yes(bool value,const char* name){++checks;if(!value){std::fprintf(stderr,"FAIL %s\n",name);std::exit(1);}}
static Actor cassi(){Actor a;a.id=6;a.type=3;a.pos={58,65};a.hp=a.max_hp=700;a.alive=a.can_cast=true;
 a.strength=30;a.focus=70;a.range=3;auto&s=a.spells[0];s.kind=2;s.slot=0;s.cooldown=0;s.recharge=8;
 s.range=4;s.amount=140;s.ready=s.camps=s.exclusive=true;return a;}
static Camp elk(){Camp c;c.id=3;c.pos={54,64};c.hp=c.max_hp=2400;c.strength=60;c.range=3;return c;}
int main(){auto a=cassi();auto c=elk();auto q=certify_cast_only_clear(a,c,a.pos,0);
 yes(q.known&&q.feasible&&q.ready_now&&q.slot==0&&q.shots==18&&q.clear_ticks==137,"actualCassi700/140/8 atdistance4 certifies18shots137owners");
 yes(q.remaining_hp==700&&q.first_delay==0,"fixed outside-range clear invents neither injury nor first cooldown wait");
 a.can_cast=false;q=certify_cast_only_clear(a,c,a.pos,0);
 yes(q.known&&q.feasible&&!q.ready_now&&q.first_delay==1&&q.clear_ticks==138,"spent actualcast waits one real owner before first shot");
 a=cassi();a.completed=true;q=certify_cast_only_clear(a,c,a.pos,0);
 yes(q.known&&!q.ready_now&&q.first_delay==1,"completedbody has no current cast promise");
 a=cassi();q=certify_cast_only_clear(a,c,a.pos,0,{},0,2000,false);
 yes(q.known&&!q.ready_now&&q.first_delay==1,"exclusivecast afterwalking waits for next owner");
 a.spells[0].ready=false;a.spells[0].cooldown=5;q=certify_cast_only_clear(a,c,a.pos,0);
 yes(q.known&&!q.ready_now&&q.first_delay==5&&q.clear_ticks==142,"known cooldown5 adds five real owner delays");
 q=certify_cast_only_clear(a,c,a.pos,3);
 yes(q.known&&!q.ready_now&&q.first_delay==2&&q.clear_ticks==139,"known elapsedownerends age cooldown without gift currentcast");
 a.spells[0].cooldown=-1;q=certify_cast_only_clear(a,c,a.pos,0);
 yes(!q.known,"unknown cooldown cannot invent recurring safe schedule");
 a=cassi();a.spells[0].recharge=0;q=certify_cast_only_clear(a,c,a.pos,0);
 yes(!q.known,"missing recharge cannot invent repeated sameownercasts");
 a=cassi();a.pos={59,65};q=certify_cast_only_clear(a,c,{58,65},0);
 yes(!q.known,"currentdisplacement cannot reuse old fixedstage without paid elapsedroute");
 a=cassi();q=certify_cast_only_clear(a,c,{57,64},1);
 yes(!q.known,"inside nativecamprange3 rejects evenan already awake lowrisk target");
 q=certify_cast_only_clear(a,c,{59,65},1);
 yes(!q.known,"outside actualspellrange4 rejects without AoEradiusborrow");
 a.spells[0].kind=3;a.spells[0].radius=2;q=certify_cast_only_clear(a,c,a.pos,0);
 yes(!q.known,"area spell needs separate collateral contract and is not silently borrowed");
 a=cassi();Camp neighbor=c;neighbor.id=8;neighbor.pos={58,62};neighbor.awake=true;neighbor.strength=20;
 q=certify_cast_only_clear(a,c,a.pos,0,std::span(&neighbor,1));
 yes(!q.known,"anotherawakecamp inrange invalidates unpriced zero-pressure promise");
 neighbor.pos={58,61};q=certify_cast_only_clear(a,c,a.pos,0,std::span(&neighbor,1));
 yes(q.feasible,"awakecamp outside actualreplyrange adds no invented pressure");
 neighbor.pos={58,62};neighbor.awake=false;q=certify_cast_only_clear(a,c,a.pos,0,std::span(&neighbor,1));
 yes(q.feasible,"directtargetcast does not wake another sleepinggroup");
 q=certify_cast_only_clear(a,c,a.pos,0,{},524);
 yes(!q.feasible,"existing75percent reserve andoneHPmargin still reject additional enemy reply atboundary");
 q=certify_cast_only_clear(a,c,a.pos,0,{},0,136);
 yes(q.known&&!q.feasible&&q.clear_ticks==137,"explicitdeadline cannot truncate incomplete clear into completion");
 c.hp=.5;a.spells[0].amount=.1;q=certify_cast_only_clear(a,c,a.pos,0);
 yes(q.feasible&&q.shots>=6,"f32subtractioncounterexample cannot optimistically credit fiveideal0.1hits");
 a=cassi();c=elk();a.monster=true;q=certify_cast_only_clear(a,c,a.pos,0);
 yes(q.feasible&&q.shots==16&&q.clear_ticks==121,"oneactualMonster family applies10percent once not percastcompound");
 a=cassi();a.spells[1]=a.spells[0];a.spells[1].slot=1;a.spells[1].amount=300;
 q=certify_cast_only_clear(a,c,a.pos,0);
 yes(q.feasible&&q.slot==1&&q.shots>=8&&q.clear_ticks<137,"single selected directslot chooses shorter honest schedule nottwo simultaneouscasts");
    c.pos={-1,-1};q=certify_cast_only_clear(a,c,a.pos,0);
    yes(!q.known,"missingcampcoordinate cannot certify hypothetical offboard target");

 constexpr int n=15;std::vector<std::uint8_t> blocked((n*n+7)/8),occupied=blocked,visible(blocked.size(),255);
 auto bit=[](auto&bytes,int x,int y,bool value){int i=y*n+x;if(value)bytes[i/8]|=1u<<(i%8);else bytes[i/8]&=~(1u<<(i%8));};
 bit(occupied,5,5,true);
 auto route=visible_solo_annulus_route(n,n,blocked,occupied,visible,{9,6},{5,5},4,4,1);
 yes(route.known&&route.stage==Pos{9,6}&&route.arrival_steps==0&&route.capture_steps==4,"already-safe distance4 needs separately funded four-step capture, not three-step approach cap");
 yes(route.capture_length==5&&route.capture_route[0]==route.stage&&route.capture_route[4]==Pos{5,5},"outer quote retains every capture waypoint for actual pressure checks");
 yes(route.visited<=128,"both annulus legs share a strict node work bound");
 route=visible_solo_annulus_route(n,n,blocked,occupied,visible,{11,6},{5,5},4,4,1);
 yes(route.known&&route.arrival_steps==2&&distance(route.stage,{5,5})==4,"future approach stops outside monster3 without marching into basic3");
 route=visible_solo_annulus_route(n,n,blocked,occupied,visible,{8,6},{5,5},4,4,1);
 yes(route.known&&route.arrival_steps==1&&distance(route.stage,{5,5})==4,"annulus respects strict lower bound even from sleeping monster range");
 route=visible_solo_annulus_route(n,n,blocked,occupied,visible,{13,6},{5,5},4,4,1);
 yes(!route.known,"approach longer than three owners is unknown");
 route=visible_solo_annulus_route(n,n,blocked,occupied,visible,{9,6},{5,5},4,4,1,2);
 yes(!route.known&&route.visited<=2,"annulus workcap never certifies incomplete capture");
 for(int y=0;y<n;++y)bit(blocked,7,y,true);
 route=visible_solo_annulus_route(n,n,blocked,occupied,visible,{9,6},{5,5},4,4,1);
 yes(!route.known,"visible current cast stage alone cannot invent a disconnected capture route");
 blocked.assign(blocked.size(),0);visible.assign(visible.size(),0);
 route=visible_solo_annulus_route(n,n,blocked,occupied,visible,{9,6},{5,5},4,4,1);
 yes(!route.known,"unseen capture/arrival tile is not a local path proof");
 visible.assign(visible.size(),255);for(int y=4;y<=6;++y)for(int x=4;x<=6;++x)if(x!=5||y!=5)bit(occupied,x,y,true);
 route=visible_solo_annulus_route(n,n,blocked,occupied,visible,{9,6},{5,5},4,4,1);
 yes(!route.known,"other bodies around dead camp cannot be forecast to vacate for capture");

 occupied.assign(occupied.size(),0);bit(occupied,5,5,true);int polls=0;
 route=visible_solo_annulus_route(n,n,blocked,occupied,visible,{9,6},{5,5},4,4,1,128,[&]{return ++polls<4;});
 yes(!route.known,"budget callback can stop between bounded search phases without certifying partial capture");
 std::printf("%d cast-only certificate checks passed\n",checks);
}
