#pragma once
// Camp planner v2: cheap, bounded basic-attack-only simulation.
// SDK-independent; receives *actual* positions, HP, Strength, attack ranges, item multipliers.
// This is a forecast, not an oracle: spells, hidden actors, path geometry, awake state and
// some shield effects are not fully represented. It must not veto a profitable camp until
// verified against replay observations. The main bot enables shadow logging by default.
#include <algorithm>
#include <cmath>
#include <cstdint>

namespace camp_forecast {
constexpr int MAX_ALLIES = 6;
constexpr int MAX_MONSTERS = 16;
struct Unit {
    int id=0, x=0, y=0, range=1;
    float health=0, max_health=0, basic=0, shield=0;
    float taken_mult=1, dealt_mult=1;
    bool varg=false, can_hit_now=true;
};
struct Monster {
    int x=0, y=0;
    float health=0, strength=0;
};
struct Result {
    int turns=0, first_death=-1, victim=-1, first_focus=-1;
    int attacker_count=0, moved_steps=0;
    float first_round_incoming=0, total_damage_taken=0, lowest_hp_frac=1;
    float own_health_after_four=-1, monsters_after_four=-1;
    bool cleared=false, confident=false;
};
inline int distance(int x,int y,int xx,int yy) { return std::max(std::abs(x-xx),std::abs(y-yy)); }

// Starts *before first attack* if awake=false. If true, monsters attack on the
// next global camp phase, even before our champion gets another action.
inline Result predict(const Unit* src, int n, const Monster* raw, int m,
                      bool awake, int max_rounds=40) {
    Result r;
    if (n<1 || n>MAX_ALLIES || m<1 || m>MAX_MONSTERS) return r;
    Unit a[MAX_ALLIES]; Monster mon[MAX_MONSTERS];
    for (int i=0;i<n;++i) a[i]=src[i];
    for (int i=0;i<m;++i) mon[i]=raw[i];
    bool attacked[MAX_ALLIES]{};
    bool simulated_move=false;
    for (int turn=0;turn<max_rounds;++turn) {
        bool alive_mon=false;
        for (int j=0;j<m;++j) if (mon[j].health>0) alive_mon=true;
        if (!alive_mon) {r.cleared=true;break;}
        // Attacks are resolved at round start, before champion turns.
        // The current global camp phase already ended before this champion acts.
        // The next camp hit is at NEXT round start, not before our first action.
        if (awake && turn>0) for (int j=0;j<m;++j) {
            if (mon[j].health<=0 || mon[j].strength<=0) continue;
            int best=-1, closest=9999;
            for (int i=0;i<n;++i) {
                if (a[i].health<=0) continue;
                int d=distance(mon[j].x,mon[j].y,a[i].x,a[i].y);
                if (d>3) continue;
                if (d<closest || (d==closest && best>=0 &&
                    a[i].health+a[i].shield < a[best].health+a[best].shield)) {closest=d;best=i;}
            }
            if (best<0) continue;
            if (r.first_focus<0) r.first_focus=a[best].id;
            float dmg=mon[j].strength*a[best].taken_mult;
            if (turn==1) r.first_round_incoming+=dmg;
            r.total_damage_taken+=dmg;
            float consumed=std::min(dmg,a[best].shield);
            a[best].shield-=consumed;dmg-=consumed;
            a[best].health-=dmg;
            if (a[best].health<=0 && r.first_death<0) {
                r.first_death=turn+1;r.victim=a[best].id;
            }
        }
        ++r.turns;
        if (r.first_death>=0) break;
        bool any_hit=false;
        for (int i=0;i<n;++i) {
            if (a[i].health<=0) continue;
            int target=-1; float score=-1;
            for (int j=0;j<m;++j) {
                if (mon[j].health<=0 || distance(a[i].x,a[i].y,mon[j].x,mon[j].y)>a[i].range) continue;
                float dmg=a[i].basic*a[i].dealt_mult;
                float s=(mon[j].strength+12.0f)/(mon[j].health+1.0f);
                if (dmg>=mon[j].health) s+=1.0f;
                if (s>score) {score=s;target=j;}
            }
            if (target>=0 && (turn>0 || a[i].can_hit_now)) {
                const float dmg=a[i].basic*a[i].dealt_mult;
                mon[target].health-=dmg;
                if (a[i].varg) for (int j=0;j<m;++j) if (j!=target && mon[j].health>0 &&
                    distance(mon[j].x,mon[j].y,mon[target].x,mon[target].y)<=1)
                    mon[j].health-=dmg;
                any_hit=true;attacked[i]=true;
                continue;
            }
            // Open-terrain arrival is an *optimistic* approximation. It is flagged
            // so a result depending on invented movement is never called confident.
            int closest=9999, t=-1;
            for (int j=0;j<m;++j) if(mon[j].health>0) {
                int d=distance(a[i].x,a[i].y,mon[j].x,mon[j].y);
                if (d<closest) {closest=d;t=j;}
            }
            if (t<0 || closest<=a[i].range) continue;
            simulated_move=true; ++r.moved_steps;
            int oldx=a[i].x, oldy=a[i].y;
            if (a[i].x<mon[t].x) ++a[i].x;
            else if (a[i].x>mon[t].x) --a[i].x;
            if (a[i].y<mon[t].y) ++a[i].y;
            else if (a[i].y>mon[t].y) --a[i].y;
            // Melee can move and attack, but never model illegal wall moves as proof.
            if (a[i].range<=1 && distance(a[i].x,a[i].y,mon[t].x,mon[t].y)<=1 &&
                (turn>0 || a[i].can_hit_now)) {
                float dmg=a[i].basic*a[i].dealt_mult;
                mon[t].health-=dmg;
                any_hit=true;attacked[i]=true;
            }
            (void)oldx; (void)oldy;
        }
        if (any_hit) awake=true;
        if (turn==3) {
            r.own_health_after_four=a[0].health;
            r.monsters_after_four=0;
            for(int j=0;j<m;++j) r.monsters_after_four+=std::max(0.0f,mon[j].health);
        }
        if (!any_hit && !simulated_move) break;
    }
    bool clear=true;
    for (int j=0;j<m;++j) if(mon[j].health>0) clear=false;
    r.cleared=clear;
    // Only a stationary, attack-range-complete forecast can be used as high-confidence
    // evidence. Even then unmodeled spells, shields and priority prevent a hard veto.
    r.confident=!simulated_move;
    for (int i=0;i<n;++i) {
        r.attacker_count+=attacked[i]?1:0;
        if (src[i].max_health>0)
            r.lowest_hp_frac=std::min(r.lowest_hp_frac,a[i].health/src[i].max_health);
    }
    return r;
}
}
