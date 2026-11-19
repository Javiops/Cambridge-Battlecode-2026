#pragma once
// varg.h - Varg (legacy drafts; Vendetta took his slot). Splash damage in my_dps; shop part 1 plan, hp share 0.40.

namespace varg {

CHAMP_HOOK bool is(const std::string& n) { return starts_with(n, "varg"); }

// my_dps: splash damage counts 1.5x (varg::SPLASH, declared in champions.h)
CHAMP_HOOK bool splashes(const State& s) { return is(s.name); }

}  // namespace varg
