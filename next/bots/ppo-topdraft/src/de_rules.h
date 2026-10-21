#pragma once
#include <algorithm>
#include <string>
#include <vector>


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

inline int probe() {
    int family=Unknown;
    attempt([&]{family=classify(static_cast<int>(bc::map::width()),static_cast<int>(bc::map::height()),
        static_cast<int>(bc::map::altars().positions().size()),static_cast<int>(bc::map::walls().positions().size()));return true;});
    return family;
}

inline bool is_farm_family(int family) {
    return family==Rows||family==Expanse||family==Lanes||family==Monolith;
}
inline bool starts(const std::string& name,const char* prefix) {return name.rfind(prefix,0)==0;}

inline std::vector<const char*> recipe(int family) {
    switch(family) {
    case Collision:
        break;
    case Corners:
        break;
    case Elkring:
        break;
    case Expanse:
        break;
    case Interlock:
        break;
    case Lanes:
        break;
    case Monolith:
        break;
    case Packs:
        break;
    case Rows:
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
