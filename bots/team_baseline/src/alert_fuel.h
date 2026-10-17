#pragma once
#ifndef P_FUEL_ALERT_MEMO
#define P_FUEL_ALERT_MEMO 1
#endif
#ifndef P_FUEL_ALERT_GATE
#define P_FUEL_ALERT_GATE 1
#endif
#ifndef P_FUEL_ALERT_SPAWN
#define P_FUEL_ALERT_SPAWN 1
#endif

// Only successful readings within one no-action update_danger call are reused.
// Native budget suspension can advance the round, so every lookup invalidates
// old entries after a round change. No state or packet layout is changed.
namespace alertfuel {
struct Entry { const Foe* foe=nullptr; double hp_pct=100.0,power=0.0; };
struct Frame { int round=-1; std::vector<Entry> entries; };
inline Frame* active=nullptr;
struct Scope {
    Frame frame;
    Frame* previous=active;
    explicit Scope(int round) { frame.round=round; active=&frame; }
    ~Scope() { active=previous; }
    Scope(const Scope&)=delete;
    Scope& operator=(const Scope&)=delete;
};
inline bool read(const Foe& foe,double& hp_pct,double& power) {
    if (!active) return false;
    const int round=static_cast<int>(bc::round_number());
    if (active->round!=round) { active->entries.clear();active->round=round; }
    for(const auto& e:active->entries)if(e.foe==&foe) { hp_pct=e.hp_pct;power=e.power;return true; }
    return false;
}
inline void remember(const Foe& foe,double hp_pct,double power) {
    if (!active || active->round!=static_cast<int>(bc::round_number())) return;
    active->entries.push_back({&foe,hp_pct,power});
}
} // namespace alertfuel
