# Next investigation: objective execution after a valid rally

Not implemented. V93's complete250-game window has79wins versus77,zero faults,
one unchanged exhausted turn,and all228 ordinary-map controls exact. On22
single-objective games,bank306.05→363.5,fresh322.55→383.64,deaths49.45→47.45.
The same four cases still collect no fresh gems and have no credited clear
targeting the public sole campGroup. Three have full first-cycle release;the
fourth intentionally rejects Ryth's33-round-old receipt. All have zero bot faults
and no own fuel loss. Do not diagnose these as another bank-route stall.

Read results/stage7-live-v93-objectives.json and the native-verified captures in
live/age-20261021-r1. The four cases are Preyas elk A,Slawomir Stampede A/B,and
Tozo Stampede A. Their case names are evidence,not proposed code exceptions.

Inspect actual post-release action priorities,positions,visible camp health,
target retention and available spell use. Establish whether the team damages
the objective,leaves it for PvP/kiting/recall,waits for an incorrectly estimated
squad,or loses the reward race. Separate approach,damage,credited clear,fresh
collection and depositing. Native beginning-round snapshots are not exact later
unit inputs;locate the actor's actual timeline state when the question requires it.

The existing campfoe branch interrupts farming near enemies,but source alone
does not prove it caused these four failures. Check its actual predicates and
world/action evidence before changing it. Do not disable survival safeguards
or lower quorum reflexively. Also inspect camp spell execution before assuming
that a focus-heavy draft can use all its purchased damage against camps.

Important evidence limits:the official summary's event kinds do not include
per-cast or per-hit damage records. Per-champion monsterDamage is global.
The current cf_focus_wait/exit/hit counters are declared/printed but never
incremented anywhere in the current source,so their zero values prove nothing
about casting. allies_near uses fresh vision::champions;do not assume it has the
old cached-roster abort bug. Tank-follow farming does read my_roster inside a
whole-loop handler;verify an actual failure before proposing a related fix.

Choose one general correction that improves sustained objective execution once
the trace supports it. Keep v93 frozen and live while investigating. Test broad
procedural sole/split maps,both seats,and ordinary-map controls;do not tune on
70 unused confirmation maps. No new map/opponent-name exceptions. Source20 is
not yet chosen. Already-latched release after death and delayed first receipt
remain known protocol limits,but another small timer change is not automatically
the right next step for the remaining zero-economy games.
