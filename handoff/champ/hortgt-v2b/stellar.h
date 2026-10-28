#pragma once
// stellar.h - Stellar (legacy drafts; not in the V20 draft). Shop part 1 plan, hp share 0.20, capture rank 0,
// caster mode (champ::caster_mode).

namespace stellar {

CHAMP_HOOK bool is(const std::string& n) { return starts_with(n, "stellar"); }

}  // namespace stellar
