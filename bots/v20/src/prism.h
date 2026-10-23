#pragma once
// prism.h - Prism (legacy drafts; not in the V20 draft). Shop part 1 plan only.

namespace prism {

CHAMP_HOOK bool is(const std::string& n) { return starts_with(n, "prism"); }

}  // namespace prism
