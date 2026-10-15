# Economy v2 — experimental review assets

**The selected `productive_walk` package failed its final fresh confirmation.** It scored 521–503 against the cleaned PR11 control (50.88%; paired-map p = 0.603397). Its matched five-reference improvement was +114 / 5,120 games (+2.23 pp), with map-direction p = 0.139357. Both required significance gates failed; this is not a validated stronger replacement.

The [bot overview](../../../bots/study27-economy/README.md) explains the four concrete changes. The candidate was chosen adaptively after exposed development results, then frozen before generating the 512-map cohort. All 11,264 fresh games completed, with zero reported faults or reinitializations. Caught SDK-error and logged low-fuel samples remained nonzero.

Download the [compressed review bundle](review-evidence-bundle-compressed.zip) and its [complete hash manifest](review-evidence-bundle-compressed-manifest.json). The archive is approximately 1.13 MiB and contains 582 entries:

- Exact cleaned PR11 baseline and selected experimental source trees.
- All six fixed reference source trees. The three older spars have their original three-file layouts; the other references have six files.
- All 512 native fresh maps and the generator manifest.
- Eight portable reproduction support files and an adjacent baseline source copy.
- The final independent audit, failed verdict, and source/runtime/generation manifests.

This is a **review/rerun archive, not a Battlecode bot upload**. It contains no raw game caches/statistics, stdout, replays, credentials, private configurations, SDK/CLI executables, or repository/worktree metadata. The compact evidence supports review without replacing the full raw evidence audit.

Archive SHA-256:

```text
c4c9e3c1c96e96d7a974071fb6abe381476f0ca5b2b0f98a4be197801ea39fd3
```

Extract and reproduce all six implemented package sources:

```sh
python -m zipfile -e review-evidence-bundle-compressed.zip review-assets
cd review-assets
python portable-tools/rebuild_candidates.py --baseline portable-tools/baseline-src --out reproduced
```

Use Python 3.10 or newer. The output parent must exist and `reproduced` must be new. Reproduction writes source and provenance only; it does not compile, simulate, or submit.

For a match rerun, copy the candidate and chosen reference source trees into an official C++ project as `bots/productive_walk/src` and `bots/original/src`, and copy `maps/confirmation512` into that project. Then build and run, for example:

```sh
cambc build bots/productive_walk
cambc build bots/original
cambc run bots/productive_walk bots/original --map maps/confirmation512/fresh-0000.map26a -o review-rerun --statistics review-rerun/statistics.json
```

Swap the bot order for the other side. Exact comparison requires matching the pinned runtime/source/WASM identities in `manifests/frozen-source-runtime.json`; the tested CLI was 2.1.6 and reported engine version 0.0.1. The generator engine hash does not mean that the CLI injected that engine binary.

The compressed wrapper uses DEFLATE level 9 with CPython 3.12.14 and zlib 1.3.2, pinned in the companion manifest. Its 582 uncompressed payloads are byte-identical to the original stored wrapper; the included historical README's ZIP_STORED sentence describes that original wrapper. Every file has a size and SHA-256 entry, including the internal manifest. CRC checks, registered source/map hashes, and deterministic same-host reencoding passed.
