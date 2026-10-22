#pragma once
// Independent geometry/policy primitives: no cambc calls, safe to unit-test natively.
namespace patch_v1 {
constexpr int cheb(int x1,int y1,int x2,int y2) {
    const int dx = x1 > x2 ? x1-x2 : x2-x1;
    const int dy = y1 > y2 ? y1-y2 : y2-y1;
    return dx > dy ? dx : dy;
}
constexpr bool dash_landing_geometry(int x,int y,int lx,int ly, int tx,int ty,
                                     int dash_range=2,int hit_radius=1) {
    const int travel = cheb(x,y,lx,ly);
    return travel >= 1 && travel <= dash_range &&
           cheb(lx,ly,tx,ty) <= hit_radius;
}
// An already-awake monster's next camp-action hit can kill us if it focuses us.
// Require a margin, and never veto a camp we expect to clear on this action.
constexpr double dash_score(int hits, double expected_enemy_damage, double our_health,
                            int travel_distance, bool versus_champions) {
    return hits*100.0 - (versus_champions ? 70.0*expected_enemy_damage/(our_health>100?our_health:100) : 0)
           - travel_distance;
}
constexpr bool lethal_camp_risk(double incoming, double hp_plus_shield,
                                double group_hp, double potential_finish) {
    return incoming > 0 && incoming >= hp_plus_shield * 1.04 && group_hp > potential_finish;
}
}
