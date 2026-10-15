# Review notes

**Fresh confirmation failed:** direct 521–503, p = 0.603397; matched panel +2.23 pp, p = 0.139357. Keep this as experimental research. See [RESULTS.md](RESULTS.md) for the complete gate summary.

The review diff compares `productive_walk` with the cleaned PR11 control, whose origin `e72cec8` is explicitly abbreviated. Exact source and compiled-policy hashes are authoritative. Only `main.cpp` changes. The selected source files, submission ZIP, and injected WASM retain their frozen bytes; this documentation revision adds no bot-code changes.

The four retained features are walking-distance banking (`banking_walk`), camp basic-attack reach preference (`cf_camp_reach`), redundant-capturer evacuation (`cf_camp_evac`), and travel-aware optional capture recall (`cr_travel`). Their heuristics have limits: route costs can become stale, visible threats omit fog and future actions, and an ally present now may move later. Evacuation fails closed on camp-query failures and preserves capture when no safe purposeful step is found. Its guard does not interrupt an existing channel.

The parent experiment tested 13 packages. Its camp-focus forecast lost about **31.32 pp** against the matched five-reference screen panel; combinations containing it lost about 28 pp. Review identified a travel-stall failure mode involving hypothetical camp contact and a retained target. The parent full run was stopped before completing its planned cohort; surviving individual cache records do not make it a completed 253-map result. This mechanism does not explain every parent loss.

The adaptive second phase reused the same three frozen transformation modules and composed six packages without camp focus:

| Package | Features |
|---|---|
| productive_walk | walking banking + camp reach + capture evacuation + travel recall |
| productive_risk | risk-aware banking + camp reach + capture evacuation + travel recall |
| bank_walk | walking banking + travel recall |
| mobile_camps | camp reach + capture evacuation |
| productive_share85 | productive_walk + stacking-value exponent 0.85 |
| productive_share100 | productive_walk + stacking-value exponent 1.00 |

All six were screened on 53 development maps. The declared promotion rule advanced `productive_walk` and the best other package to the 253-map stage. The leading eligible package then received an exposed 128-map transfer check. One candidate was frozen before the separate 512-map confirmation; the failed final gates were retained without tuning or another candidate attempt.

The [review bundle](../../analysis/study27-economy/v2/README.md) preserves the exact baseline, selected and opponent sources, native maps, portable transformations, and compact evidence. The transformations reproduce all six package sources for review; their inclusion does not endorse every variant. Native endpoint/rate differences and geometry subgroups remain descriptive.

**Manifest provenance:** [source-manifest.json](source-manifest.json) is a byte-for-byte copy of the original export manifest. Its `exported_files_sha256` entries describe that original export, including its original prose. These repository documents are editorial revisions; they do not replace those historical document hashes. Source, WASM, and diff pins remain unchanged. The original root-layout ZIP was rejected by the platform and is superseded by the official `cambc bundle` archive with `src/` entries; [upload verification](upload-layout-verification.json) and the [independent audit](upload-layout-audit.json) record its new archive hash. The original exported evidence and frozen inputs were preserved.
