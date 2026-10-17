#include "observation_detour.h"
#include "farm_readiness.h"
#include <cstdio>
#include <cstdlib>
#include <map>
namespace bc {
inline unsigned budget=65000,queries=0,cutoff=0,epoch_at=0;
inline int epoch=100;
inline unsigned fuel_remaining(){++queries;if(epoch_at&&queries>=epoch_at)epoch=101;return cutoff&&queries>=cutoff?19000:budget;}
inline int round_number(){return epoch;}
}
namespace tactics {
struct TestGeometry {
 int width=8,height=8;std::vector<Group>groups;
 std::map<std::pair<int,int>,std::vector<std::uint16_t>>goal_cache;
 std::map<int,std::vector<std::uint16_t>>route_cache;
 bool valid(Pos p)const{return p.x>=0&&p.y>=0&&p.x<width&&p.y<height;}
 int index(Pos p)const{return p.y*width+p.x;}
 int at(const std::vector<std::uint16_t>&f,Pos p)const{return valid(p)?f[index(p)]:unreachable;}
};
struct World {
 Actor self{};TestGeometry geo;std::vector<GroupView>groups;std::vector<std::uint8_t>visible_bytes;
 int round=100,free_calls=0,incoming_calls=0;std::vector<Pos>occupied,reserved;
 Pos failed{};bool failed_active=false,incoming_epoch=false,incoming_cutoff=false;double incoming=0;
 bool free(Pos p){++free_calls;return geo.valid(p)&&std::find(occupied.begin(),occupied.end(),p)==occupied.end()&&std::find(reserved.begin(),reserved.end(),p)==reserved.end()&&!(failed_active&&p==failed);}
};
inline bool packed_bit(std::span<const std::uint8_t>b,int i){return (b[std::size_t(i)>>3]&(1u<<(i&7)))!=0;}
inline double incoming_damage(World&w,Pos){++w.incoming_calls;if(w.incoming_epoch)bc::epoch=101;if(w.incoming_cutoff)bc::budget=19000;return w.incoming;}
/*EXACT_OBSERVATION_DETOUR*/
}
using namespace tactics;
int main(){int checks=0;auto ck=[&](bool b,const char*why){++checks;if(!b){std::fprintf(stderr,"FAIL %s\n",why);std::exit(1);}};
 World w;Pos target{6,2};auto reset=[&]{w={};bc::budget=65000;bc::queries=bc::cutoff=bc::epoch_at=0;bc::epoch=100;w.self.id=5;w.self.alive=w.self.can_move=true;w.self.hp=w.self.max_hp=750;w.self.move_speed=1;w.self.pos={2,2};w.visible_bytes.assign(8,255);std::vector<std::uint16_t>field(64);for(int y=0;y<8;++y)for(int x=0;x<8;++x)field[y*8+x]=distance({x,y},target);w.geo.goal_cache[{w.geo.index(target),0}]=field;};
 reset();auto q=safe_observation_detour(w,target);ck(q&&*q==Pos{3,1}&&w.incoming_calls==1,"exact production wrapper obtains whole fresh adjacent progress and checks enemy risk");
 reset();ck(!safe_observation_detour(w,{-2,3})&&w.free_calls==0,"invalid target rejected before a linear-index alias borrows another field");
 reset();w.geo.goal_cache.clear();ck(!safe_observation_detour(w,target)&&w.free_calls==0,"missing cached route stays Unknown without inline field construction");
 reset();auto field=w.geo.goal_cache.begin()->second;w.geo.goal_cache.clear();w.geo.route_cache[w.geo.index(target)]=field;ck(safe_observation_detour(w,target).has_value(),"existing completed target route cache is supported");
 reset();bc::budget=27999;ck(!safe_observation_detour(w,target)&&w.free_calls==0,"28k admission decline preserves action reserve");
 reset();bc::budget=28000;ck(safe_observation_detour(w,target).has_value(),"exact28k entry remains admitted with explicit funded callback");
 reset();bc::epoch=101;ck(!safe_observation_detour(w,target)&&w.free_calls==0,"stale snapshot rejected before path reads");
 reset();bc::cutoff=5;ck(!safe_observation_detour(w,target)&&w.incoming_calls==0,"budget cutoff cannot publish partial winner");
 reset();bc::epoch_at=6;ck(!safe_observation_detour(w,target)&&w.incoming_calls==0,"native epoch change during bounded scan remains Unknown");
 reset();w.occupied={{3,1}};q=safe_observation_detour(w,target);ck(q&&*q==Pos{3,2},"fresh actual occupation cannot be wished away");
 reset();w.reserved={{3,1},{3,2},{3,3}};ck(!safe_observation_detour(w,target),"all useful cells reserved means no claimed path");
 reset();w.failed_active=true;w.failed={3,1};q=safe_observation_detour(w,target);ck(q&&*q!=w.failed,"fresh failed-step veto survives optional routing");
 reset();int i=w.geo.index({3,1});w.visible_bytes[i>>3]&=std::uint8_t(~(1u<<(i&7)));q=safe_observation_detour(w,target);ck(q&&*q==Pos{3,2},"unseen candidate cell cannot authorize movement");
 reset();Group g;Spawn spawn;spawn.id=7;spawn.pos={4,1};spawn.hp=100;spawn.strength=20;spawn.range=1;g.spawns={spawn};w.geo.groups={g};GroupView v;v.seen=100;v.state=Lifecycle::Alive;Camp c;c.id=7;c.pos=spawn.pos;c.hp=100;c.strength=20;c.range=1;c.awake=false;v.camps={c};w.groups={v};q=safe_observation_detour(w,target);ck(q&&*q==Pos{3,3},"same production pressure predicate conservatively vetoes sleeping-camp ring");
 reset();w.incoming=.65*w.self.hp;ck(!safe_observation_detour(w,target),"lethal-risk threshold remains vetoed");
 reset();w.incoming=.65*w.self.hp-1;ck(safe_observation_detour(w,target).has_value(),"bounded known nonlethal landing can proceed");
 reset();w.incoming_epoch=true;ck(!safe_observation_detour(w,target),"enemy query epoch change cannot become stale Move");
 reset();w.incoming_cutoff=true;ck(!safe_observation_detour(w,target),"enemy query reserve cutoff cannot become unfunded Move");
 std::printf("%d observation detour caller checks passed\n",checks);
}
