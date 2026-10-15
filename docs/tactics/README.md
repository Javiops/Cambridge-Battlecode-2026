# Cambridge Battlecode Tactics

The team's living specification for how our CAMBC 2026a bot makes decisions.
Each topic starts with a short description and grows into a concrete tactic: when it applies,
what the champion does, and how it interacts with the rest of the team.

> [!NOTE]
> This first edition contains 96 topics across 12 chapters. Tactical details are ready to be filled in.
> **Unspecified** means the behavior has not been documented here; it makes no claim about whether the bot already implements it.

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
