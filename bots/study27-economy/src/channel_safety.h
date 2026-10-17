#pragma once
namespace channel_safety {
// Submission is not cancelled by ordinary damage: retain it unless the current
// observed volley is lethal. This is not a whole-channel survival guarantee.
inline bool local_allowed(bool recall,bool legacy_recall,bool awake_camp_near,
                          double current_damage,double health,bool ready_control,bool unknown_near) {
    if (ready_control || unknown_near) return false;
    return recall ? legacy_recall && !awake_camp_near && current_damage<=0
                  : health>current_damage;
}
}
