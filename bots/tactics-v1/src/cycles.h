#pragma once
#include "types.h"
namespace tactics {
struct ChainSchedule {
    double direct_bank = 0, self_to_job = 0, bank_to_job = 0, acquire = 0;
    double job_to_bank = 0, bank_new_bag = 0, bank_combined_bag = 0, recover = 0;
};
struct ChainComparison {
    double bank_then_job = 0, job_then_bank = 0;
    bool known = false, prefer_job = false;
};
inline ChainComparison compare_chain(const ChainSchedule &s, double margin) {
    for (double v : {s.direct_bank, s.self_to_job, s.bank_to_job, s.acquire, s.job_to_bank,
                     s.bank_new_bag, s.bank_combined_bag, s.recover})
        if (!std::isfinite(v) || v < 0)
            return {};
    ChainComparison out;
    // Equal rewards and the SAME final altar region. Never compare a completed
    // two-reward schedule with just the first leg's bag/time ratio.
    out.bank_then_job =
        s.direct_bank + s.bank_to_job + s.acquire + s.job_to_bank + s.bank_new_bag + s.recover;
    out.job_then_bank = s.self_to_job + s.acquire + s.job_to_bank + s.bank_combined_bag + s.recover;
    out.known = out.bank_then_job > 0 && out.job_then_bank > 0;
    out.prefer_job = out.known && out.job_then_bank * margin < out.bank_then_job;
    return out;
}
} // namespace tactics
