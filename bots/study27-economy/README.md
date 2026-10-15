# study27 economy — experimental

**The frozen `productive_walk` package failed its predeclared fresh confirmation.** It scored **521–503 against the control (50.88%; paired-map p = 0.603397)**. The matched five-reference panel improved by **2.23 percentage points**, but its map-direction test also failed (**p = 0.139357**). This remains draft research, without a validated-strength claim.

The candidate builds on the cleaned PR11 combat bot. Its four changes are:

- **Walking distance for banking:** rank reachable altar approaches and banking detours by estimated walking cost instead of straight-line distance, retaining existing lock and ownership penalties.
- **Reachable camp targets:** apply the existing Packs-only basic-attack target preference on every map, prioritizing a weak monster already within attack range.
- **Leave a redundant capture:** when another available ally already occupies a reward area, permit a legal, purposeful step toward the next camp if the safety checks pass. Preserve the capture when no such step exists.
- **Travel-aware optional recall:** require more healing value or shopping gold for a longer estimated return walk. Tavi does not take this optional trip for gold alone; normal recall decisions remain in the baseline path.

Only `main.cpp` differs from the control; the other five source files match its exact pins. The source is byte-identical to the frozen package tested in all 11,264 fresh games. The rejected camp-focus forecast is absent.

The experimental submission archive is `cambc-study27-economy-experimental-productive_walk-fbf835ee.zip`, containing exactly six source files at its root. Its SHA-256 is:

```text
d69b4385f7bbd3c05350b354f5cf5cb439c334e20e85acea65ac7b175895b6b9
```

See [results](RESULTS.md), [review notes](REVIEW-NOTES.md), and the unchanged [export manifest](source-manifest.json). The [review assets and reproduction guide](../../analysis/study27-economy/v2/README.md) include the exact maps and opponent sources. That review bundle is a separate artifact and is not a bot upload.
