#pragma once
// tavi.h - Tavi (legacy drafts; not in the V20 draft). She shops in the field, so gold alone is never a reason to
// walk home (capture recall, shop trips). Shop part 1 plan, hp share 0.06.

namespace tavi {

CHAMP_HOOK bool is(const std::string& n) { return starts_with(n, "tavi"); }

CHAMP_HOOK bool shops_in_field(const State& s) { return is(s.name); }

}  // namespace tavi
