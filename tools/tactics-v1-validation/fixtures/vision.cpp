#include "types.h"
#include <cstdlib>
#include <iostream>
using namespace tactics;
struct Geo {
    int width=20,height=20;
    bool valid(Pos p) const {return p.x>=0&&p.y>=0&&p.x<width&&p.y<height;}
    int index(Pos p) const {return p.y*width+p.x;}
};
struct World {
    Geo geo;Actor self;std::vector<Actor> enemies;std::vector<std::uint8_t>visible_bytes;
    bool warning=false;
    bool warning_near(Pos,int)const{return warning;}
};
// EXACT_PRODUCTION_FUNCTIONS
static void set(std::vector<std::uint8_t>&b,int i,bool yes=true){
    if(yes)b[i/8]|=1u<<(i%8);else b[i/8]&=~(1u<<(i%8));
}
static int checks=0;
static void check(bool ok){++checks;if(!ok){std::cerr<<"FAIL vision "<<checks<<'\n';std::exit(1);}}
int main(){
    std::vector<std::uint8_t> one(8);set(one,14);
    check(ward_local_bit(one,14));check(!ward_local_bit(one,1));
    check(!ward_local_bit(one,-1));check(!ward_local_bit(one,64));
    World w;w.self.alive=true;w.self.hp=100;w.self.max_hp=100;w.self.pos={5,5};
    w.visible_bytes.resize(50);Mission m;m.phase=Phase::Travel;m.target={10,5};
    Action a;a.kind=Kind::Move;a.at={6,5};
    check(ward_opportunity(w,m,a));
    set(w.visible_bytes,w.geo.index(m.target));set(w.visible_bytes,w.geo.index(a.at));
    check(!ward_opportunity(w,m,a));
    w.warning=true;check(ward_opportunity(w,m,a));
    a.kind=Kind::BasicChampion;check(!ward_opportunity(w,m,a));
    a.kind=Kind::Tribute;check(!ward_opportunity(w,m,a));
    a.kind=Kind::Move;m.phase=Phase::Escape;check(!ward_opportunity(w,m,a));
    m.phase=Phase::Channel;check(!ward_opportunity(w,m,a));
    m.phase=Phase::Travel;w.self.channel=Channel::Recall;check(!ward_opportunity(w,m,a));
    w.self.channel=Channel::None;Actor enemy;enemy.pos={6,5};enemy.range=1;
    w.enemies.push_back(enemy);check(!ward_opportunity(w,m,a));w.enemies.clear();
    a.kind=Kind::Recall;w.self.hp=30;check(!ward_opportunity(w,m,a));
    w.self.hp=60;check(ward_opportunity(w,m,a));
    w.self.stunned=true;check(!ward_opportunity(w,m,a));w.self.stunned=false;
    w.self.alive=false;check(!ward_opportunity(w,m,a));
    std::vector<std::uint8_t>mask(50),now(50),future(50),blocked(50);
    const int tile=5*20+8;set(mask,tile);
    check(ward_buffer_score(mask,now,future,blocked,20,20,{5,5},{5,5})==7);
    set(now,tile);
    check(ward_buffer_score(mask,now,future,blocked,20,20,{5,5},{5,5})==3);
    set(future,tile);
    check(ward_buffer_score(mask,now,future,blocked,20,20,{5,5},{5,5})==0);
    set(blocked,tile);set(future,tile,false);set(now,tile,false);
    check(ward_buffer_score(mask,now,future,blocked,20,20,{5,5},{5,5})==0);
    mask.clear();check(ward_buffer_score(mask,now,future,blocked,20,20,{5,5},{5,5})==0);
    mask.resize(50);set(mask,0);
    check(ward_buffer_score(mask,now,future,blocked,20,20,{19,19},{19,19})==0);
    std::cout<<checks<<" vision checks passed\n";
}
