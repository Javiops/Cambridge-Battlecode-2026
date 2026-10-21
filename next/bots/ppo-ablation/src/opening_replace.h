#pragma once
#include <algorithm>
#include <cstring>
#include <string>
#include <vector>


namespace opening36 {
inline bool same(const Step& a, const Step& b) {
    return a.stat == b.stat && std::strcmp(a.family, b.family) == 0;
}

// No host calls. build_shop starts from the original plan every time it runs,
// so a partial catalogue retry never stacks another opening or rebasing pass.
inline void replace(std::vector<Step>& plan, int family, const std::string& name, int mode) {
    if (mode < 1 || mode > 4 || !v34de::is_farm_family(family) || plan.empty()) return;
    // An all-game target is not an opening. Baseline front quotas are 1 or 2.
    if (plan.front().want < 1 || plan.front().want > 3) return;
    const auto original = plan;
    const bool roles = mode >= 3;
    const bool focus = name.rfind("cassi", 0) == 0 || name.rfind("stellar", 0) == 0 ||
                       name.rfind("tavi", 0) == 0;
    plan.front().family = (mode == 1 || mode == 4) ? "jungle" : "monster";
    if (roles) plan.front().stat = focus ? 'f' : 's';
    // Preserve the original first-Step quota (including Issac's two emblems).
    // For every later step, preserve family/stat and its incremental quantity.
    for (std::size_t i = 1; i < plan.size(); ++i) { stage7_budget_checkpoint(); 
        int before_old = 0, before_new = 0;
        for (std::size_t j = 0; j < i; ++j) { stage7_budget_checkpoint(); 
            if (same(original[j], original[i])) before_old = std::max(before_old, original[j].want);
            if (same(plan[j], plan[i])) before_new = std::max(before_new, plan[j].want);
        }
        const int additional = std::max(0, original[i].want - before_old);
        plan[i].want = before_new + additional;
    }
}
} // namespace opening36
