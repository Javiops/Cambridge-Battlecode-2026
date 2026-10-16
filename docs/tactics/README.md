# Cambridge Battlecode Tactics

The team's living specification for how our CAMBC 2026a bot makes decisions.
Each topic starts with a short description and grows into a concrete tactic: when it applies,
what the champion does, and how it interacts with the rest of the team.

> [!NOTE]
> All **96 topics across 12 chapters** now contain a concrete baseline or intended tactic. Chapters 04 (vision), 06 (coordination) and 11 (shopping) retain their detailed researched policies.
> **Planned** and **Implemented** distinguish intended improvements from behavior present in the pinned source. Complete documentation does not mean every tactic has been implemented or shown to improve results.
> The current code reference is `bots/study27-economy` at `a0c0fa2` (16 October 2026). Its identity with the supplied live-v43 screenshot remains unconfirmed. See the [reference snapshot, configuration and feedback mapping](reference-snapshot-2026-10-16.md).

## Chapters

| Chapter | Area | Covers |
| --- | --- | --- |
| 01 | [Overall strategy](01-overall-strategy.md) | The objectives and tradeoffs that guide every champion. |
| 02 | [Map understanding and adaptation](02-map-understanding.md) | The map features that shape routes, compositions, and objectives. |
| 03 | [Champion selection and draft](03-champion-selection.md) | Who we select, in which order, and how the team fits together. |
| 04 | [Vision and information](04-vision-and-information.md) | What each champion and ward reveals and how the team uses that knowledge. |
| 05 | [Pathfinding and individual movement](05-pathfinding-and-movement.md) | How each champion reaches a useful position safely and efficiently. |
| 06 | [Team coordination and group movement](06-team-coordination.md) | How champions divide work, support each other, and move as a team. |
| 07 | [Combat and survival](07-combat-and-survival.md) | When we fight, how we execute, and when we leave. |
| 08 | [Farming and camp capture](08-farming-and-capture.md) | How we turn camps into resources with useful timing and distribution. |
| 09 | [Gems and altar control](09-gems-and-objectives.md) | How we protect resources and convert them into a winning score. |
| 10 | [Recall and recovery](10-recall-and-recovery.md) | How we recall, teleport, recover, and rejoin productive play. |
| 11 | [Shopping and resource investment](11-shopping-and-investment.md) | How gold becomes useful power for each champion. |
| 12 | [Bot execution and validation](12-execution-and-validation.md) | How decisions run reliably and how we establish what the bot does. |

## Reading a tactic

Each chapter numbers its topics from **1 to 8**. Refer to a topic by chapter and number,
such as **04.1 Ward placement** or **07.6 Action sequencing**. Each topic also has a direct link
in its chapter's contents.

The opening sentence defines the topic's scope. The **Tactic** below it describes the desired behavior;
its **Status** shows how that description relates to the code.

| Status | Meaning |
| --- | --- |
| **Unspecified** | The detailed tactic has not been written. Existing implementation may already cover some or all of it. |
| **Planned** | The intended behavior is described; implementation is pending or differs from the specification. |
| **Implemented** | The documented behavior is present in a named code revision; validation is pending. |
| **Verified** | The documented behavior is linked to a code revision and supporting checks or replay evidence. |

Verification records the behavior checked and the limits of the evidence. Competitive improvement
requires comparative results; the status alone does not establish a stronger bot.


## Where to start

Read [01 Overall strategy](01-overall-strategy.md) for priorities, then the chapter governing the next decision. Each topic identifies its trigger, action, stop/yield condition, exceptions and fallback. Current behavior explains any material gap between the intended rule and the reference bot; unresolved thresholds are experiment parameters, not claimed optima.

The supplied team feedback makes **combat micro**, **secure farming under pressure**, and **completed capture/collection** the next implementation priorities. Those planned requirements are linked to their chapters in the [feedback mapping](reference-snapshot-2026-10-16.md#how-the-supplied-team-feedback-was-used). Keep the existing ward, coordination and investment research as the starting specification while implementing one coherent change at a time and testing useful combinations.

This completion is a **documentation and source audit**. It does not change the bot, upload a new version, run simulations, or prove a stronger strategy. [Chapter 12](12-execution-and-validation.md) defines the separate implementation and validation work.

## Keeping the specification current

Update the relevant tactic when a decision changes. Keep one authoritative description of each rule,
link related topics, and record implementation and validation beside the behavior they support.
Git history preserves superseded tactics.

Start with the [editing guide and tactic template](EDITING.md).

## Game rules and reference

The [official rules and champion specifications](https://2026a.battlecode.co.uk/game/docs/agents)
define legal game behavior. The handbook describes our choices within those rules.
Use the [official Bot API](https://2026a.battlecode.co.uk/game/api) for action preconditions and signatures.

Rules reference checked on **16 October 2026**. Check the official handbook again when mechanics change.
