#pragma once
// vesper.h - Vesper (draft slot 2, in Stellar's place: P_DRAFT_SWAP2).
// Today she has no hook of her own: her emblem plan is shop part 1's generic one (champions.h legacy_plan:
// durab-s, jungle-s, bruiser-h, then bruiser-s after P_BRUISER_FILL), no health rule (hp_pick), and she switches
// the team to the caster mode (champ::caster_mode, P_VESP_CASTER). Her damage work (build, spell use) goes here.

namespace vesper {

CHAMP_HOOK bool is(const std::string& n) { return starts_with(n, "vesper"); }

}  // namespace vesper
