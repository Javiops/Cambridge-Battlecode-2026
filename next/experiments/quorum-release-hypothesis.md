# Candidate next hypothesis, not implemented

V91 Preyas elk A (game0c360477-4e50-492c-b786-70f42a534577) releases units
4 at175 and1/2/3/5 at176,while unit0 Stellar still rallies at200. Team banks0.
V90 previously released only1/3/4 at176. V17 fixes a real partial scan,but the
per-instance `objective_release_cycle` still leaves the sixth member waiting.
Finish the140-game v91 audit before choosing the next change.

A general next experiment could broadcast the existing successful quorum decision
for the current sole-objective campaign cycle. Keep entry health,quorum,clock,
survival and banking priorities. A receiver joins the already-authorized phase;
it does not manufacture a fresh local quorum. Log a distinct shared-join event.
Measure all-unit release,fresh collection,deposits,deaths and runtime.

Verified byte layout in current frozen v17:

- Claims occupy0–4,including six packed6-bit claims when roster6/groups<=63.
  Cooldown/reward cache uses5/6. Their writes preserve7.
- Active byte7 writer is `update_danger`,encoding altar index+1 in low3bits.
  Its loop limits indices0..6,so legal danger tags always have low bits1..7.
- `fight.h` help sender/receiver exists,but its call sites are `if(false)`.
- `map-seed.h::sample()` writes all8bytes,but has no call site. PPO adapter
  uses an independent per-instance static RNG,not that shared-memory helper.

Possible cycle tag:`(cycle+1)<<3` has low3bits0 and nonzero value8..48 for the
six current120/360 cycles through round2000. No legal danger packet equals it;
old cycle tags do not match the next cycle and empty0 cannot authorize release.
Reserve byte7 from danger *broadcast writes* only during `objective_window`;
retain direct local enemy-pack detection and all combat/survival guards. Outside
those windows normal danger sharing returns. Record this communication tradeoff.
Add a forward declaration if update_danger calls objective_window before its
definition. Verify all memory writers again before implementing; do not assume
these conclusions survive later source changes.

The current per-unit latch already lasts the campaign window. A shared phase tag
would extend that same phase to late joiners,including a healthy respawned unit;
that can feed a lost fight. Test deaths and objective reward capture; do not claim
the protocol is proven safe or competitive from encoding alone. No new map-name
or opponent-name cases. Broad procedural sole/split controls and both seats.
