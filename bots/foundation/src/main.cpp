// PR1 runtime scaffold. Holds position; strategy migration follows in later PRs.
#include <cambc.h>
#include <cstdio>
#include "sdk_actions.h"
#include "policies/registry.h"

int main() {
    foundation::Executor executor;
    foundation::SdkPort port;
    for (;;) {
        try {
            if (cambc::is_draft()) {
                // Draft preferences are scaffolding, not a competitive composition.
                for (const auto pick : {cambc::champion_draft::varg,
                         cambc::champion_draft::ryth, cambc::champion_draft::vendetta,
                         cambc::champion_draft::stellar, cambc::champion_draft::tavi}) {
                    try { cambc::draft::pick(pick); break; }
                    catch (const cambc::error&) { /* Try the next available pick. */ }
                }
            } else {
                const auto snapshot = executor.observe(port);
                const auto decision = foundation::select(foundation::PlanningContext{snapshot},
                    foundation::policies::registry);
                if (decision.status == foundation::DecisionStatus::fault) {
                    std::puts("foundation: policy selection fault");
                    return 1;
                }
                if (decision.status == foundation::DecisionStatus::stale) {
                    cambc::end_turn();
                    continue;
                }
                const auto result = executor.execute(port,
                    decision.request);
                if (result.outcome == foundation::Outcome::fault) {
                    std::puts("foundation: observation/action fault");
                    return 1;
                }
            }
        } catch (...) { std::puts("foundation: turn fault"); return 1; }
        cambc::end_turn();
    }
}
