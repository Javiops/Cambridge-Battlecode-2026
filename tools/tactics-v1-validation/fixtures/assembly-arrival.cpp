#define TACTICS_ASSEMBLY_MODEL_ONLY
#include "assembly.h"
#include <map>
#include <cstdio>
#include <cstdlib>
namespace tactics {
struct Geometry {
    int width=12,height=9;
    std::vector<std::uint8_t> terrain;
    std::map<int,std::vector<std::uint16_t>> route_cache;
    std::map<std::pair<int,int>,std::vector<std::uint16_t>> goal_cache;
    bool valid(Pos p)const{return p.x>=0&&p.y>=0&&p.x<width&&p.y<height;}
    int index(Pos p)const{return p.y*width+p.x;}
    bool blocked(Pos p)const{return !valid(p)||packed_bit(terrain,index(p));}
    int at(const std::vector<std::uint16_t>&f,Pos p)const{
        return valid(p)&&f.size()==unsigned(width*height)?f[index(p)]:unreachable;
    }
};
struct World {
    Geometry geo; std::vector<std::uint8_t> occupied_bytes,visible_bytes; Actor self;
    bool free(Pos p)const{return !geo.blocked(p)&&(p==self.pos||!packed_bit(occupied_bytes,geo.index(p)));}
};
namespace assembly_detail {
// EXACT_ASSEMBLY_ARRIVAL_TYPE
// EXACT_ASSEMBLY_ARRIVAL
// EXACT_ASSEMBLY_FINGERPRINT
}
// EXACT_ASSEMBLY_STEP
}
using namespace tactics;
int main(){
    int checks=0;
    auto check=[&](bool ok,const char*name){++checks;if(!ok){std::fprintf(stderr,"FAIL %s\n",name);std::exit(1);}};
    World w;
    const auto set=[&](std::vector<std::uint8_t>&v,Pos p,bool b){auto i=w.geo.index(p); if(b)v[i/8]|=1u<<(i%8);else v[i/8]&=~(1u<<(i%8));};
    const auto reset=[&](){
        w.geo.terrain.assign((w.geo.width*w.geo.height+7)/8,255);
        w.occupied_bytes.assign(w.geo.terrain.size(),0);
        w.visible_bytes.assign(w.geo.terrain.size(),255);
        for(int x=0;x<=8;++x)set(w.geo.terrain,{x,4},false);
        w.geo.goal_cache.clear();w.geo.route_cache.clear();
    };
    const auto field=[&](){
        std::vector<std::uint16_t> d(w.geo.width*w.geo.height,unreachable);
        for(int x=0;x<=8;++x)d[w.geo.index({x,4})]=8-x;
        return d;
    };
    reset();Pos camp{8,4};Actor a;a.pos={5,4};a.range=3;a.move_speed=1;
    auto arrival=assembly_detail::contribution_arrival(w,a,camp);
    check(arrival.known&&arrival.turns==0&&arrival.at==a.pos,"already useful actual tile needs no fabricated route");
    a.pos={2,4};
    check(!assembly_detail::contribution_arrival(w,a,camp).known,"missing field is unknown not geometric certificate");
    w.geo.goal_cache[{w.geo.index(camp),0}]=field();
    arrival=assembly_detail::contribution_arrival(w,a,camp);
    check(arrival.known&&arrival.turns==3&&arrival.at==Pos{5,4},"cached actual gradient reaches legal contribution tile");
    check(arrival.route_length==4&&arrival.route[0]==a.pos&&arrival.route[3]==arrival.at,
          "quoted exact useful landing retains its actual cached path");
    Mission job;job.assembly_pending=true;job.assembly_route=arrival.route;job.assembly_route_length=arrival.route_length;
    w.self=a;w.self.can_move=true;
    check(assembly_step(w,job)==std::optional<Pos>(Pos{3,4}),"stage execution follows quoted first path tile");
    w.self.move_speed=2;
    check(assembly_step(w,job)==std::optional<Pos>(Pos{4,4}),"actual speed advances along quoted path only");
    set(w.occupied_bytes,{3,4},true);
    check(!assembly_step(w,job),"cannot jump an occupied intermediate tile even with speed two");
    set(w.occupied_bytes,{3,4},false);w.self.can_move=false;
    check(!assembly_step(w,job),"spent movement retains job without a second move");
    w.self.can_move=true;w.self.pos={1,4};
    check(!assembly_step(w,job),"displaced body does not invent an unpriced route");
    w.self.pos=arrival.at;
    check(!assembly_step(w,job),"arrival at the quoted stage holds for real readiness");
    w.self=a;w.self.can_move=true;job.assembly_pending=false;
    check(!assembly_step(w,job),"nonpending mission cannot execute leftover assembly route");
    auto count=w.geo.goal_cache.size();assembly_detail::contribution_arrival(w,a,camp);
    check(w.geo.goal_cache.size()==count,"arrival search creates no new field");
    set(w.occupied_bytes,{3,4},true);
    check(!assembly_detail::contribution_arrival(w,a,camp).known,"occupied unique corridor is not certified");
    set(w.occupied_bytes,{3,4},false);set(w.visible_bytes,{3,4},false);
    check(!assembly_detail::contribution_arrival(w,a,camp).known,"hidden path is not assumed free");
    set(w.visible_bytes,{3,4},true);set(w.geo.terrain,{3,4},true);
    check(!assembly_detail::contribution_arrival(w,a,camp).known,"cached gradient never authorizes current blocked terrain");
    set(w.geo.terrain,{3,4},false);
    check(!assembly_detail::contribution_arrival(w,a,camp,{5,4}).known,"two prospective bodies cannot reserve same useful tile");
    a.pos={0,4};a.range=1;a.move_speed=2;
    check(!assembly_detail::contribution_arrival(w,a,camp).known,"over three movement opportunities declines");
    a.move_speed=3;arrival=assembly_detail::contribution_arrival(w,a,camp);
    check(arrival.known&&arrival.turns==3,"actual movement speed changes ETA");
    reset();w.geo.route_cache[w.geo.index(camp)]=field();a.pos={2,4};a.range=3;a.move_speed=1;
    check(assembly_detail::contribution_arrival(w,a,camp).known,"completed camp-rooted route cache accepted");
    w.geo.terrain.clear();
    check(!assembly_detail::contribution_arrival(w,a,camp).known,"missing exported terrain declines rather than host-loop work");
    Actor b=a;b.id=2;b.hp=b.max_hp=120;b.strength=26;b.focus=35;
    a.id=1;a.hp=a.max_hp=120;a.strength=26;a.focus=35;
    Camp monster;monster.id=7;monster.pos=camp;monster.hp=60;monster.strength=60;monster.range=1;
    const auto hash=assembly_detail::fingerprint(1,a,b,monster,true);
    const auto differs=[&](Actor changed,Camp changed_camp=Camp{}){
        return assembly_detail::fingerprint(1,changed,b,changed_camp.id<0?monster:changed_camp,true)!=hash;
    };
    Actor changed=a;changed.focus+=.01;check(differs(changed),"small Focus upgrade reopens exact failed opportunity");
    changed=a;changed.strength+=.01;check(differs(changed),"subinteger Strength breakpoint invalidates old failure");
    changed=a;changed.hp+=.01;check(differs(changed),"small real healing invalidates old HP failure");
    changed=a;changed.camp_mitigation=.9;check(differs(changed),"Jungle mitigation can reopen affordable crew");
    changed=a;++changed.range;check(differs(changed),"range change invalidates old contribution geometry");
    changed=a;++changed.move_speed;check(differs(changed),"speed change invalidates old arrival quote");
    changed=a;++changed.pos.x;check(differs(changed),"real local arrival is a changed forecast input");
    changed=a;changed.spells[0].amount=1;check(differs(changed),"actual spell power change invalidates old kill forecast");
    changed=a;changed.spells[0].cooldown=0;check(differs(changed),"actual cooldown readiness invalidates old forecast");
    Camp changed_camp=monster;changed_camp.hp-=.01;check(differs(a,changed_camp),"subinteger camp HP breakpoint invalidates old failure");
    changed_camp=monster;changed_camp.strength+=.01;check(differs(a,changed_camp),"camp pressure changes invalidate old certificate");
    check(assembly_detail::fingerprint(1,a,b,monster,true)==hash,"unchanged actual inputs keep stable identity");
    reset();a.pos={2,4};a.range=3;a.move_speed=1;Pos anchor{6,4};
    std::vector<std::uint16_t> ring(w.geo.width*w.geo.height,unreachable);
    for(int x=0;x<=8;++x)ring[w.geo.index({x,4})]=std::abs(x-6);
    w.geo.goal_cache[{w.geo.index(anchor),0}]=ring;
    std::array<Camp,2> covered;covered[0].pos=anchor;covered[1].pos={8,4};for(auto&c:covered)c.hp=100;
    auto ordinary=assembly_detail::contribution_arrival(w,a,anchor);
    auto coverage=assembly_detail::contribution_arrival(w,a,anchor,{},covered);
    check(ordinary.known&&ordinary.at==Pos{3,4}&&coverage.known&&coverage.at==Pos{5,4},"full basic coverage continues past anchor-only nearest ring to actual all-member tile");
    check(coverage.turns==3&&coverage.route_length==4,"all-target stage prices actual additional walking");
    set(w.occupied_bytes,{4,4},true);
    check(!assembly_detail::contribution_arrival(w,a,anchor,{},covered).known,"all-target stage never invents passage through occupied corridor");set(w.occupied_bytes,{4,4},false);
    covered[1].pos={8,0};check(!assembly_detail::contribution_arrival(w,a,anchor,{},covered).known,"unreachable basic intersection remains unknown rather than borrowing spell range");
    std::printf("%d assembly-arrival checks passed\n",checks);
}
