#include "actions.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
using namespace tactics;
static void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
int main(){
    Geometry geometry;Memory memory;std::unique_ptr<World> world;bool done=false;
    while(true){
        if(bc::is_draft()){bc::draft::pick(bc::champion_draft::ren);bc::end_turn();continue;}
        geometry.initialize();if(!geometry.initialized){bc::end_turn();continue;}if(!world)world=std::make_unique<World>(geometry,memory);
        World& w=*world;w.refresh();
        if(done){bc::end_turn();continue;}
        check(w.self.alive && w.self.type==9,"fixture requires actual living Ren");
        const bool left=w.geo.at(w.geo.home,{1,1})==0;
        const Pos origin{left?10:21,10},target{left?12:19,10};
        if(w.self.pos!=origin){
            if(auto step=w.toward(origin)){Action move;move.kind=Kind::Move;move.at=*step;move.reason="fixture-dash-approach";check(execute(w,move).success,"fixture move");}
            bc::end_turn();continue;
        }
        const bool barrier=bc::map::walls().is_set({11,9});
        const auto ability=w.me.abilities()[1];
        check(ability.is_dash()&&ability.is_ready(),"native dash readiness");
        check(ability.valid_tiles().is_set(sdk(target)),"SDK range mask includes test target");
        Action dash;dash.kind=Kind::CastGround;dash.slot=1;dash.at=target;dash.reason="fixture-actual-dash-gateway";
        const auto result=execute(w,dash);
        if(barrier){
            check(!result.success && result.error==0 && result.outcome==Outcome::Rejected,"known unreachable dash rejected before SDK action");
            check(position(w.me.position())==origin&&ability.cooldown()==0,"rejected dash preserves position/cooldown");
            dash.at={origin.x,12};
            const auto legal=execute(w,dash);check(legal.success&&legal.error==0,"legal dash remains available after rejection");
            check(position(w.me.position())==dash.at,"legal dash actual relocation");
        }else{
            check(result.success&&result.error==0,"legal hole crossing or bending dash accepted");
            check(position(w.me.position())==target,"legal crossing actual relocation");
        }
        std::printf("NATIVE_DASH_GATEWAY_PASS %d %d\n",w.self.id,barrier?1:0);done=true;
        bc::end_turn();
    }
}
