#include "information.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
int main() {
    int checks=0;
    auto check=[&](bool ok){++checks;if(!ok){std::fprintf(stderr,"FAIL information %d\n",checks);std::exit(1);}};
    for(int round:{0,1,63,64,255,256,1023,1999,2000})
        for(int writer=0;writer<6;++writer)
            for(int x:{0,7,15}) {
                Warning a{x,15-x,round,3,writer};
                auto b=decode_warning(encode_warning(a));
                check(a.x==b.x&&a.y==b.y&&a.round==b.round&&a.writer==b.writer&&b.severity==3);
                check(b.fresh(round)&&b.fresh(round+2)&&!b.fresh(round+3)&&!b.fresh(round-1));
            }
    check(!decode_warning({}).fresh(0));
    check(!decode_warning(encode_warning({1,1,64,1,0})).fresh(128));
    check(!decode_warning(encode_warning({1,1,2001,1,6})).fresh(2001));
    Memory m;m.mission.phase=Phase::Travel;
    check(!update_route_progress(m,{0,0},{9,0},9,1));
    check(!update_route_progress(m,{1,0},{9,0},8,2));
    check(!update_route_progress(m,{0,0},{9,0},9,3));
    check(update_route_progress(m,{1,0},{9,0},8,4));
    check(!update_route_progress(m,{1,0},{9,0},8,4));
    check(!update_route_progress(m,{2,0},{9,0},7,5));
    check(!update_route_progress(m,{2,0},{0,9},9,6));
    m.mission.phase=Phase::Collect;
    for(int r=7;r<14;++r)check(!update_route_progress(m,{2,0},{0,9},9,r));
    std::printf("%d information checks passed\n",checks);
}
