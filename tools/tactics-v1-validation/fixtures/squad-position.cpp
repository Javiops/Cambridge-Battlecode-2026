#define TACTICS_COORDINATION_MODEL_ONLY
#define TACTICS_COMBAT_MODEL_ONLY
#include "coordination.h"
#include "combat.h"
#include <cstdlib>
#include <iostream>
namespace tactics {
struct Geometry {
    int width=12,height=12;
    std::vector<Group>groups;
    std::vector<std::uint8_t>terrain=std::vector<std::uint8_t>(18);
    std::vector<std::uint16_t>home=std::vector<std::uint16_t>(144,5);
    bool valid(Pos p)const{return p.x>=0&&p.y>=0&&p.x<width&&p.y<height;}
    int index(Pos p)const{return p.y*width+p.x;}
    int at(const std::vector<std::uint16_t>&f,Pos p)const{return valid(p)?f[index(p)]:unreachable;}
};
struct World {
    Geometry geo;Actor self;std::vector<Actor>allies,enemies;
    std::vector<GroupView>groups;
    std::vector<std::uint8_t>occupied_bytes=std::vector<std::uint8_t>(18);
    Memory memory;int round=1,self_index=0;
    bool on_group(int g,Pos p)const{
        for(auto s:geo.groups[g].spawns)if(s.pos==p)return true;
        return false;
    }
};
// EXACT_SQUAD_POSITION
}
using namespace tactics;
static int checks=0;
static void check(bool ok){++checks;if(!ok){std::cerr<<"FAIL squad-position "<<checks<<'\n';std::exit(1);}}
static void set(std::vector<std::uint8_t>&b,int i){b[i/8]|=1u<<(i%8);}
int main(){
    World w;w.self.id=1;w.self.pos={5,5};w.self.alive=true;w.self.hp=w.self.max_hp=100;
    w.self.can_move=true;w.self.range=1;
    Group g;Spawn s;s.pos={9,5};g.spawns.push_back(s);w.geo.groups.push_back(g);w.groups.resize(1);
    LocalAssignment a;a.selected_ids={1};a.self_role=LocalRole::Clear;
    auto p=squad_position(w,a,0);
    check(p && distance(*p,w.self.pos)==1 && p->x==6);
    set(w.occupied_bytes,w.geo.index(*p));auto q=squad_position(w,a,0);
    check(q && *q!=*p && !packed_bit(w.occupied_bytes,w.geo.index(*q)));
    set(w.geo.terrain,w.geo.index(*q));p=squad_position(w,a,0);
    check(!p || !packed_bit(w.geo.terrain,w.geo.index(*p)));
    w.self.can_move=false;check(!squad_position(w,a,0));w.self.can_move=true;
    w.self.channel=Channel::Recall;check(!squad_position(w,a,0));w.self.channel=Channel::None;
    w.occupied_bytes.clear();check(!squad_position(w,a,0));w.occupied_bytes.resize(18);
    check(!squad_position(w,a,1));
    w.geo.terrain.assign(18,0);w.self.range=8;Camp c;c.pos={9,5};c.hp=10;w.groups[0].camps={c};
    Actor ally;ally.id=2;ally.pos={5,4};ally.alive=true;w.allies={w.self,ally};
    Actor enemy;enemy.id=3;enemy.pos={10,5};enemy.alive=true;enemy.strength=0;
    Spell aoe;aoe.kind=3;aoe.ready=true;aoe.cooldown=0;aoe.range=10;aoe.radius=2;enemy.spells[0]=aoe;
    w.enemies={enemy};p=squad_position(w,a,0);
    check(p && distance(*p,ally.pos)>distance(w.self.pos,ally.pos));
    w.enemies.clear();a.self_role=LocalRole::Collector;w.geo.groups[0].spawns[0].pos={6,5};
    p=squad_position(w,a,0);check(p && *p==Pos{6,5});
    std::cout<<checks<<" squad-position checks passed\n";
}
