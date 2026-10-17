#include "channel_safety.h"
#include <vector>
#include <array>
#include <variant>
#include <optional>
#include <cassert>
#include <cmath>
#include <stdexcept>
#include <cstdio>
#include <type_traits>
#ifndef P_DP_CHANNEL_FIX
#define P_DP_CHANNEL_FIX 1
#endif
int X(vec2 p) { return p.x; } int Y(vec2 p) { return p.y; }
struct Mask { bool all=false;bool is_set(vec2 p) const { return all || (p.x==0 && p.y==0); } };
namespace bc {
inline int now=10;
int round_number() { return now; }
namespace constants { constexpr int recall_time=5,submit_gem_minimum_duration=1,submit_gem_base_duration=0;constexpr double submit_gem_duration_multiplier=.1; }
enum class ability_kind {attack_reset,damage,aoe_damage,cc,dash,heal,shield};
struct props { int max_cooldown=8;bool exclusive_with_movement=false; };
struct reset : props { static constexpr auto kind=ability_kind::attack_reset;bool enhanced_attack=false; };
struct damage : props { static constexpr auto kind=ability_kind::damage;float range=3,modifier=1; };
struct aoe : props { static constexpr auto kind=ability_kind::aoe_damage;float range=3,modifier=1,radius=0;int duration=1; };
struct cc : props { static constexpr auto kind=ability_kind::cc;float range=3,modifier=0;int duration=1; };
struct dash : props { static constexpr auto kind=ability_kind::dash;float range=3; };
struct heal : props { static constexpr auto kind=ability_kind::heal; };
using info_t=std::variant<reset,damage,aoe,cc,dash,heal>;
struct ability {
    std::optional<info_t> data;int cd=0;double raw=20;bool fails=false,cd_fails=false,damage_fails=false;
    const std::optional<info_t>& info() const { if(fails)throw std::runtime_error("info");return data; }
    int cooldown() const { if(fails||cd_fails)throw std::runtime_error("cd");return cd; }
    double damage_amount() const { if(fails||damage_fails)throw std::runtime_error("damage");return raw; }
};
struct camp {
    vec2 p{5,5};int range=1;bool awake=false,fails=false;double damage=20;
    static inline int positions=0,states=0;
    bool is_wolf() { return range>0; } bool is_elk() { return false; } bool is_monolith() { return false; }
    vec2 spawn_position() { return p; }
    int attack_range() { return range; }
    bool is_awake() { ++states;if(fails)throw std::runtime_error("state");return awake; }
    vec2 position() { ++positions;assert(awake);return p; }
    double strength() { return damage; }
};
struct champion {
    vec2 p{5,5};int gems=20;double hp=500,basic=10;int range=1;
    bool alive=true,recalling=false,submitting=false,no_op=false,fails=false,instant=false,strength_fails=false,advance_round=false;
    int calls=0;std::array<ability,2> slots{};
    static inline int strengths=0;
    vec2 position() { if(fails)throw std::runtime_error("position");return p; }
    bool is_alive() { return alive; }
    int attack_range() { return range; }
    double strength() { ++strengths;if(advance_round)++now;if(strength_fails)throw std::runtime_error("strength");return basic; }
    std::array<ability,2> abilities() { return slots; }
    int gem_count() { return gems; }
    double health() { return hp; }
    void recall() { ++calls;if(fails)throw std::runtime_error("denied");if(no_op)return;if(instant)p={0,0};else recalling=true; }
    void submit_gems(vec2) { ++calls;if(fails)throw std::runtime_error("denied");if(no_op)return;if(instant)gems=0;else submitting=true; }
    bool is_recalling() { return recalling; }
    bool is_submitting_gems() { return submitting; }
};
namespace vision {
inline std::vector<champion> enemies;
inline std::vector<camp> monsters;
inline bool foes_fail=false,camps_fail=false;
inline int reads=0;
std::vector<champion> champions(int) { ++reads;if(foes_fail)throw std::runtime_error("foes");return enemies; }
std::vector<camp> camps() { if(camps_fail)throw std::runtime_error("camps");return monsters; }
}
}
struct Group { int reward_seen=-1;Mask mask; };
inline int enemy=1;
constexpr int CAMP_RANGE=3;
// Exercise the existing optional distance gate; production TU uses its own settings.
#ifndef P_TRIBSAFE
#define P_TRIBSAFE 5
#endif
struct Threat {vec2 p;int ar=0;double damage=0;int sr=-9;};
double danger_at(const std::vector<Threat>& th,vec2 p) {double n=0;for(auto t:th)if(dist(t.p,p)<=t.ar)n+=t.damage;return n;}
struct State {
 int ch_round=10;vec2 ch_pos{5,5};bool ch_complete=true,ch_camps_complete=true;
 std::vector<vec2> ch_foes;std::vector<bc::camp> ch_camps;
 int* en=&enemy;std::vector<Group> groups;int target=-1,hit_round=-1000,rnear=7;Mask my_spawn;
 int thr_r=10;std::vector<Threat> thr;
};
std::vector<bc::camp> near_camps(State&,vec2,bool* complete) { *complete=!bc::vision::camps_fail;return bc::vision::monsters; }
