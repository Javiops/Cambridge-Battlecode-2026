# Brainstorm <date> (template)

On the table before starting:
- `scorecard.md` of the latest dissection (`online/data/dissect/<version>/scorecard.md`): the us/rival table and the **Proposals**.
- The `lfl.py` output of the last idea tested online (what changed and what did not).
- The "Closed" section of `harness/IDEAS.md`: what was already tried and the number that killed it. Nothing comes back without a new reason.
- The top-team studies that touch the topic (`/mnt/project-files/analysis/`).

## Gaps (from the scorecard: our number and the rival's)

| gap | us | rival | maps where it weighs |
|---|---|---|---|
| | | | |

## Ideas

One row per idea. Without a measurable hypothesis it does not go on the board.

| idea (one change) | kind | gap it attacks | hypothesis (which number, from what to what, on which maps) | risk (what could get worse) | who |
|---|---|---|---|---|---|
| | farm/fight/macro/bug | | | | |

## Order

1. ...   (reason: the biggest gap / the cheapest to test / unblocks others)
2. ...
3. ...

When done: `python3 tools/idea.py add "..." --kind ... --source "brainstorm <date>" --hypothesis "..." --owner ...` for each
idea on the list, in that order; at most 3 in development per person.
