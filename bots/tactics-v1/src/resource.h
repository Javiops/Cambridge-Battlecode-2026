#pragma once
#include "types.h"
namespace tactics {
// A gold-only capture is not a completed score cycle. Named investment must
// carry a separately priced upgrade -> useful gem job -> bank itinerary.
enum class ResourcePurpose {
    Ineligible,
    Score,
    CarryBank,
    HeldReward,
    MonolithFallback,
    Investment
};
inline bool priced_cash_investment(const Memory &memory, int group, int round) {
    return group >= 0 && memory.cash_investment_group == group &&
           round < memory.cash_investment_until && std::isfinite(memory.cash_investment_rate) &&
           memory.cash_investment_rate > 0;
}
inline ResourcePurpose resource_job_purpose(int new_gems, int current_bag, bool monolith_only,
                                            bool actual_holder = false,
                                            bool priced_investment = false) {
    if (new_gems > 0)
        return ResourcePurpose::Score;
    if (current_bag > 0)
        return ResourcePurpose::CarryBank;
    if (actual_holder)
        return ResourcePurpose::HeldReward;
    if (priced_investment)
        return ResourcePurpose::Investment;
    if (monolith_only)
        return ResourcePurpose::MonolithFallback;
    return ResourcePurpose::Ineligible;
}
inline bool resource_job_eligible(int new_gems, int current_bag, bool monolith_only,
                                  bool actual_holder = false, bool priced_investment = false) {
    return resource_job_purpose(new_gems, current_bag, monolith_only, actual_holder,
                                priced_investment) != ResourcePurpose::Ineligible;
}
// A new unpriced cash detour cannot improve the same completed bank: it
// adds no gems and incurs nonnegative clear/capture time. Existing commitments
// and real reward continuity remain revalidated separately.
inline bool resource_new_job_eligible(int new_gems, int current_bag, bool monolith_only,
                                      bool actual_holder = false, bool incumbent = false,
                                      bool priced_investment = false) {
    return resource_job_eligible(new_gems, current_bag, monolith_only, actual_holder,
                                 priced_investment) &&
           !(new_gems <= 0 && current_bag > 0 && !actual_holder && !incumbent &&
             !priced_investment);
}
inline bool resource_has_bank(int new_gems, int current_bag) {
    return new_gems > 0 || current_bag > 0;
}
// A cheap superset of every eligible NEW job. Pure cash cannot become a
// scoreable detour merely because a body already carries gems. Existing
// commitments, real holders and named investment receipts stay candidates.
inline bool farm_scan_relevant(int new_gems, bool monolith_only, bool incumbent, bool actual_holder,
                               bool priced_investment) {
    return new_gems > 0 || monolith_only || incumbent || actual_holder || priced_investment;
}
inline double score_resource_gold(int new_gems, double new_gold) {
    return new_gems > 0 ? new_gold : 0;
}
inline bool resource_candidate_before(bool eligible, bool fallback, double rate,
                                      bool other_eligible, bool other_fallback, double other_rate) {
    if (eligible != other_eligible)
        return eligible;
    if (fallback != other_fallback)
        return !fallback;
    return rate > other_rate;
}
} // namespace tactics
