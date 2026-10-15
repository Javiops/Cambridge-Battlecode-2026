# Editing the tactics handbook

[← Tactics index](README.md)

Describe decisions precisely enough that a teammate or an AI can implement them and compare the result
with the specification. Write in English and keep the established chapter structure.

## Updating a topic

1. Open its chapter and keep the topic's existing number and heading.
2. Replace **To be defined** with the intended behavior and set the appropriate status.
3. State the trigger, chosen action, stopping condition, exceptions, and fallback wherever they matter.
4. Include exact thresholds with units and map or champion conditions. Mark unresolved values explicitly.
5. Link related topics when they share a decision. Put the authoritative rule in one place.
6. Link the implementation revision and relevant validation when available. Distinguish code present from behavior observed.

When a planned tactic differs from existing behavior, add a **Current behavior** paragraph describing
the difference and its code revision. Keep **Tactic** as the intended behavior and **Status** as Planned
until the implementation matches it. If a later change makes verified evidence obsolete, update the status
and references in the same edit.

## Tactic template

Keep simple tactics short. Add the following fields only when they help explain a populated entry.
Replace bracketed instructions with actual content; remove unused fields.

```markdown
## 1. Existing topic title

[One sentence defining the topic's scope.]

**Status:** Planned

**Tactic**

[Describe the intended behavior in direct, present-tense language.]

**Conditions**

- [When the tactic starts, including relevant map, champion, health, score, or timing conditions.]
- [When it stops or yields to a more important action.]

**Exceptions and fallback**

[Describe champion exceptions, missing information, unavailable actions, and fallback behavior.]

**Related decisions:** [Topic title](chapter-file.md#topic-anchor)

**Implementation:** [Permanent source link at the relevant commit, plus active configuration if applicable.]

**Validation:** [Evidence link, the behavior checked, and any material limitation.]
```

## References and numbering

Chapter numbers follow the index. Topic numbers restart at 1 within each chapter.
Use references such as **04.1 Ward placement** and relative Markdown links.
For example: [Ward placement](04-vision-and-information.md#1-ward-placement).

Preserve existing filenames, headings, and numbers during ordinary tactic edits so links remain useful.
Append new topics within the relevant chapter instead of renumbering existing ones. If the structure changes,
update the contents, index, counts, and incoming links together.

## Writing behavior clearly

- Describe actions and decision order, including what happens when two policies compete.
- Separate game mechanics from our chosen thresholds and preferences.
- Use named conditions rather than vague instructions such as "when safe" without a definition.
- Identify which code branch or configuration actually enables the behavior.
- Preserve the distinction between a hypothesis, implemented code, observed behavior, and measured improvement.
- Keep old tactics in Git history; the main text should describe the latest intended policy.

## Adding this package to the team repository

Copy the package's `docs/tactics/` directory into the repository. It contains only documentation.
The handbook uses relative links and GitHub Markdown, so it needs no build step, dependency, or hosted service.

Add this link to the repository's existing README where appropriate:

```markdown
[Tactics handbook](docs/tactics/README.md)
```
