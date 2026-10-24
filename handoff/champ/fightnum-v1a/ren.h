#pragma once
// ren.h - Ren (takes Heart of Ruin's slot on far maps, P_FAR_SWAP; Marcella took his old slot).
// No hook of his own: shop part 1 (champions.h legacy_plan) gives him the casters' plan (power-f, durab-h, then
// bruiser-f after P_BRUISER_FILL), champ::hp_share a 0.50 bruiser health share, champ::cap_rank rank 2.

namespace ren {

CHAMP_HOOK bool is(const std::string& n) { return starts_with(n, "ren"); }

}  // namespace ren
