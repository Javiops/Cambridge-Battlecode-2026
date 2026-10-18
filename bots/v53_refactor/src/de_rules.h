#pragma once
#include <algorithm>
#include <string>
#include <vector>

#ifndef P_D34_FAMILY
#define P_D34_FAMILY 0
#endif
#ifndef P_D34_DRAFT_COLLISION
#define P_D34_DRAFT_COLLISION 0
#endif
#ifndef P_D34_DRAFT_CORNERS
#define P_D34_DRAFT_CORNERS 0
#endif
#ifndef P_D34_DRAFT_ELKRING
#define P_D34_DRAFT_ELKRING 0
#endif
#ifndef P_D34_DRAFT_EXPANSE
#define P_D34_DRAFT_EXPANSE 0
#endif
#ifndef P_D34_DRAFT_INTERLOCK
#define P_D34_DRAFT_INTERLOCK 0
#endif
#ifndef P_D34_DRAFT_LANES
#define P_D34_DRAFT_LANES 0
#endif
#ifndef P_D34_DRAFT_MONOLITH
#define P_D34_DRAFT_MONOLITH 0
#endif
#ifndef P_D34_DRAFT_PACKS
#define P_D34_DRAFT_PACKS 0
#endif
#ifndef P_D34_DRAFT_ROWS
#define P_D34_DRAFT_ROWS 0
#endif
#ifndef P_D34_OPENING
#define P_D34_OPENING 0
#endif
#ifndef P_D34_ROWS_BANK
#define P_D34_ROWS_BANK 0
#endif
#ifndef P_D34_SHOP_TRIP
#define P_D34_SHOP_TRIP 0
#endif

namespace v34de {
enum Family { Unknown=0, Collision=1, Corners=2, Elkring=3, Expanse=4,
              Interlock=5, Lanes=6, Monolith=7, Packs=8, Rows=9 };

// Public geometry only; independent of bushes, rotation, team side and results.
inline int classify(int width,int height,int altars,int walls) {
    int lo=std::min(width,height),hi=std::max(width,height);
    if(lo==41&&hi==41&&altars==2&&walls==84)return Collision;
    if(lo==71&&hi==71&&altars==5&&walls==44)return Corners;
    if(lo==30&&hi==30&&altars==2&&walls==0)return Elkring;
    if(lo==80&&hi==80&&altars==10&&walls==224)return Expanse;
    if(lo==40&&hi==40&&altars==4&&walls==76)return Interlock;
    if(lo==30&&hi==90&&altars==18&&walls==0)return Lanes;
    if(lo==50&&hi==50&&altars==6&&walls==98)return Monolith;
    if(lo==31&&hi==31&&altars==6&&walls==0)return Packs;
    if(lo==50&&hi==50&&altars==2&&walls==214)return Rows;
    return Unknown;
}

#ifndef V34_DE_PURE_TEST
inline int probe() {
    int family=Unknown;
    attempt([&]{family=classify(static_cast<int>(bc::map::width()),static_cast<int>(bc::map::height()),
        static_cast<int>(bc::map::altars().positions().size()),static_cast<int>(bc::map::walls().positions().size()));return true;});
    return family;
}
#endif

inline bool is_farm_family(int family) {
    return family==Rows||family==Expanse||family==Lanes||family==Monolith;
}
inline bool starts(const std::string& name,const char* prefix) {return name.rfind(prefix,0)==0;}

inline std::vector<const char*> recipe(int family) {
    switch(family) {
    case Collision:
        if(P_D34_DRAFT_COLLISION==1)return {"stellar","prism","ren"};
        if(P_D34_DRAFT_COLLISION==2)return {"stellar","ren","tavi"};
        break;
    case Corners:
        if(P_D34_DRAFT_CORNERS==1)return {"varg","stellar","cassi","tavi","ren"};
        if(P_D34_DRAFT_CORNERS==2)return {"stellar","tavi","cassi","willow","prism"};
        break;
    case Elkring:
        if(P_D34_DRAFT_ELKRING==1)return {"varg","stellar","cassi","tavi","ren"};
        if(P_D34_DRAFT_ELKRING==2)return {"stellar","prism","willow","ren","tavi"};
        break;
    case Expanse:
        if(P_D34_DRAFT_EXPANSE==1)return {"varg","cassi","vendetta"};
        if(P_D34_DRAFT_EXPANSE==2)return {"cassi","stellar","tavi"};
        break;
    case Interlock:
        if(P_D34_DRAFT_INTERLOCK==1)return {"ryth","cassi","stellar","ren"};
        break;
    case Lanes:
        if(P_D34_DRAFT_LANES==1)return {"varg","stellar","cassi","tavi","ren"};
        break;
    case Monolith:
        if(P_D34_DRAFT_MONOLITH==1)return {"ren","varg","vendetta","ryth","cassi"};
        break;
    case Packs:
        if(P_D34_DRAFT_PACKS==1)return {"varg","stellar","cassi"};
        if(P_D34_DRAFT_PACKS==2)return {"cassi","stellar","ren"};
        break;
    case Rows:
        if(P_D34_DRAFT_ROWS==1)return {"cassi","tavi","varg","stellar"};
        break;
    default:break;
    }
    return {};
}

struct Opening { const char* family=nullptr; char stat='s'; };
// A desired first emblem is prepended to the intact existing plan. A matching
// later target may already be satisfied; otherwise the extra150 gold delays it.
inline Opening opening(int map,const std::string& name,char original_stat,int mode) {
    if(!is_farm_family(map)||!mode)return {};
    if(mode==1)return {"jungle",original_stat};
    if(mode==2)return {"monster",original_stat};
    if(mode!=3)return {};
    if(map==Rows) {
        bool focus=starts(name,"cassi")||starts(name,"stellar");
        return {"jungle",focus?'f':'s'};
    }
    if(map==Monolith)return {"monster",'s'};
    if(map==Expanse) {
        if(starts(name,"varg"))return {"jungle",'s'};
        if(starts(name,"vendetta")||starts(name,"ryth")||starts(name,"issac"))return {"monster",'s'};
        return {};
    }
    if(map==Lanes) {
        if(starts(name,"varg")||starts(name,"ren"))return {"monster",'s'};
        if(starts(name,"stellar")||starts(name,"tavi")||starts(name,"cassi"))return {"monster",'f'};
    }
    return {};
}
} // namespace v34de
