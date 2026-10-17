#define TACTICS_COMBAT_MODEL_ONLY
#include "combat.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
using namespace tactics::combat_detail;
static std::uint32_t seed = 91021;
static unsigned rnd() { seed = seed * 1664525u + 1013904223u; return seed; }
static void require(bool value, const char *why) {
    if (!value) { std::fprintf(stderr, "FAIL %s\n", why); std::exit(1); }
}
static std::vector<Pos> sorted(std::vector<Pos> a) {
    std::sort(a.begin(), a.end(), [](Pos a,Pos b){return a.y != b.y ? a.y < b.y : a.x < b.x;});
    return a;
}
int main() {
    for (int test=0;test<4000;++test) {
        const int width=5+rnd()%32,height=5+rnd()%28,steps=rnd()%5;
        const Pos from{int(rnd()%width),int(rnd()%height)};
        std::vector<std::uint8_t> terrain((width*height+7)/8);
        for(int i=0;i<width*height;++i)if(rnd()%5==0)terrain[i/8]|=1u<<(i%8);
        const int origin=from.y*width+from.x;terrain[origin/8]&=~(1u<<(origin%8));
        const auto exact=sorted(expand_region(width,height,terrain,{from},steps));
        const auto local=sorted(ordinary_reachable_region(width,height,terrain,from,steps));
        require(exact==local,"local row flood equals independent queue BFS on packed terrain");
        std::vector<std::uint8_t> occupied(terrain.size()),combined=terrain;
        for(int i=0;i<width*height;++i)if(rnd()%9==0)occupied[i/8]|=1u<<(i%8);
        occupied[origin/8]&=~(1u<<(origin%8));
        for(unsigned i=0;i<combined.size();++i)combined[i]|=occupied[i];
        require(sorted(expand_region(width,height,combined,{from},steps))==
            sorted(ordinary_reachable_region(width,height,terrain,from,steps,&occupied)),
            "local walking counterfactual honors occupied intermediate tiles");
    }
    std::printf("8000 local reach checks passed\n");
}
