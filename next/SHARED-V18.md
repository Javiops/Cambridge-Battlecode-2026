# Shared rally release: topdraft v18

V91 completed140 native-verified field games. On Preyas elk A,five units release
at175–176 while Stellar0 still rallies200;the team collects no fresh gems and
banks0. A complete local ally scan does not make the per-unit release decision
shared. V18 propagates an existing successful quorum decision for that campaign.

The unchanged quorum authorizer sends byte7 tag(cycle+1)<<3. Empty,old-cycle and
legal danger packets cannot authorize this tag. Each instance remembers receipt
before banking,healing,dead/shop and other early turn returns. Only an eligible
objective_assemble call latches/logs phase=join;actual quorum authorization still
logs phase=assault. The65% entry health,50% counted-ally health,distance5,80%
authorization quorum,clock120/360/240 and survival/banking priorities remain.
Claims/cooldown bytes0–6,initialization reserve,draft,RNG,models and weights remain.
No new map/opponent-name cases.

The source audit finds update_danger as the active byte7 writer;legal altar
indices0..6 encode low3bits1..7. Fight help call sites are disabled and the
all-eight-byte map-seed sample helper has no call site;PPO sampling is per instance.
Direct local danger detection continues. A newly received release is protected
from danger broadcast writes for two rounds,then ordinary writes may resume.
This short protection refines the earlier whole-window reservation proposal.
Delivery remains best effort for late initialization/reset or same-cycle
republication. A healthy late joiner can enter an already lost fight;measure deaths.

## Release checks

The35 official plus140 generated development maps,both seats,finish69/70 starter
and172/350 parent v17,zero faults,four exhausted turns. These results do not
establish stronger play. All26 full-log canaries exactly reproduce the broad
outcomes,rounds,team and champion statistics:12/12 starter,7/14 parent,zero faults,
one repeated exhausted turn. Big-world starter banks868/773 with zero exhaustion.
There are494 new runs and468 unique fixtures. Independent rebuild of the frozen
source ZIP reproduces the release WASM exactly.

On24 predeclared sole-objective fixtures against frozen v6,all-unit first-cycle
logged release improves15/24→24/24. All512 shared joins have a preceding same-cycle
and same-group valid quorum authorization. Mean bank197.33→225.08,no-fresh6→4 and
fresh before3507/24→8/24;wins12/24→10/24 and deaths31.71→32.79. The targeted
coordination behavior improves while strength and safety remain mixed. Logged
release does not alone prove arrival,damage,capture or safe banking.

On24 split controls there are no release/join events. Wins9→10,mean bank211.5
→215.17,deaths44.58→44.38;20/24 match parent terminal/team/collection statistics
exactly. Extra code/budget effects are a possible explanation for the four
differences,not an established cause. All48 feature games have zero faults/fuel.
Parent17 feature captures are historical controls,not counted as new runs.

## Deployment boundary

Eligible for Fran's functional experimental upload authorization,not lab
promotion. Keep v91 as rollback;lower aggregate wins alone do not trigger one.
Compile failure,persistent faults or stalled play do. No confirmation maps were
played;70 fresh maps and original Stage1–7 models/certificates remain intact.
The runner correction was separately tested142/142 before this bot change.

All local runs use official1.0.1/buildc3e9ffc8. The1.0.2 announcement is separate:
at03:05UTC the Windows distribution still publishes the unchanged3.0.2 binary
SHA25604ff1ca0992379ab8e00d7a1aaf3f7f2b2b2b57777a423194b3b073fd5c5e456.
Verify actual server build per cohort;do not relabel old evidence. This offline
report alone makes no upload/server-binary claim. Read CURRENT and deployment JSON.

Source ZIP SHA256: `c1b3514b1702c7822e3fd1deeb20e846c510165a7c9902fc7a040aa34cc5c7e3`.
Local release WASM SHA256: `061aef4bf4c22e57578978c3742ab70adfa2a7839978281faa1770f9408f972f`.
