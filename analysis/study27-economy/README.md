# Study27 economy and farming policies

These implementations extend the cleaned combat bot from PR #11, commit
`e72cec84391cf0623d15c2eb3f2f864e2b0bddea`. They implement teammate feedback as
separate policies and coherent combinations. Development evaluation is in
progress; none is recommended for ladder activation from this document.

Implemented policies:

- `cr_tavi`: avoid a gold-only opportunistic capture recall for Tavi.
- `cr_travel`: include the Tavi fix and weigh optional capture recalls against
  the actual walking distance back from spawn. Ordinary/emergency recall rules
  remain active.
- `banking_walk`: choose a reachable altar approach using native walking fields,
  retaining lock, ownership and recent-danger penalties. Use that same cost in
  the surrounding bank/recall decisions.
- `banking_risk`: additionally prefer routes outside conservative visible enemy
  threat envelopes and carry the route constraint into movement. Missing
  information, low fuel and no-safe-route cases have explicit fallbacks; this
  does not guarantee safety against fog or future enemy movement.
- `cf_camp_reach`: prefer an attackable member of the current camp group on all
  maps, instead of restricting the existing policy to Packs.
- `cf_camp_focus`: estimate incoming damage on this champion from monsters that
  may focus it, including available nearby allies and approximate clear time.
  Unsafe new pulls can be deferred; an already engaged champion can still use
  legal stationary attacks rather than wait to die. This is a model, not an
  observation of the engine's hidden target state.
- `cf_camp_evac`: allow a redundant participant to leave a reward tile only when
  another available ally is physically capturing and a safe productive step
  toward an alternate camp exists. Incomplete monster queries abort evacuation.
- `share85` / `share100`: vary the camp participation heuristic exponent. Actual
  capture rewards retain the engine's even split.

`selection-plan.json` records all 13 packages and the evaluation plan before
new outcomes. Four coherent packages advance to the full development cohort
even if their isolated components lose. Opponents include the current baseline,
three fixed older sparring bots and two alternative local policy styles. These
styles are not claimed to represent current top teams.

The native SDK builds and helper fixtures check implementation correctness.
Match results will separately assess wins, submitted/collected gems, spending,
survival, monster damage and time-normalized productivity. Sampled counters are
lower bounds; a death after a camp action does not prove the camp caused it.

The final selected candidate, complete results and any submission recommendation
will be added after the recorded development and fresh-map checks. No changes
are merged or activated automatically.
