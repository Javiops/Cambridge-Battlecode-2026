#pragma once

#include <algorithm>
#include <vector>

namespace tactics {

// Raw values are champion_draft, not physical champion_type. Cassi/Issac is
// one draft choice but produces two separately controlled physical bodies.
// This is the explicit Chapter 03 fallback, not an inferred matchup optimizer.
inline std::vector<int> draft_preferences(int pick_cap, int spawn_walk,
                                          const std::vector<int> &accepted) {
    const std::vector<int> baseline{2, 9, 3, 0, 10, 1, 6, 8, 4, 5, 7};
    std::vector<int> result;
    if (spawn_walk >= 0 && spawn_walk <= 45) {
        if (pick_cap <= 3)
            result = {3, 8, 4};
        else if (pick_cap == 4)
            result = {3, 8, 4, 10};
        else
            result = {0, 4, 5, 8, 10};
    }
    for (int choice : baseline)
        if (std::find(result.begin(), result.end(), choice) == result.end())
            result.push_back(choice);
    result.erase(std::remove_if(result.begin(), result.end(),
                                [&](int choice) {
                                    return std::find(accepted.begin(), accepted.end(), choice) !=
                                           accepted.end();
                                }),
                 result.end());
    return result;
}

} // namespace tactics
