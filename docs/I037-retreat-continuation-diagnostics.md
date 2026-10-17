# I037 Retreat continuation diagnostics

**Completed diagnostic follow-up. I035's `v60-camp-roster-bound` remains selected; no new bot is promoted or recommended for upload.** This work follows the observed failure of a successful first camp escape to continue: ordinary homeward fallback could immediately re-enter the same camp. We inspect concrete decisions before expanding tests.

The original I036 report and ZIP are preserved as historical artifacts with their original hashes. A [separate I036-r2 packaging correction](I036-r2-camp-lifecycle-diagnostics.md) restores14 exported CPP fixtures to their exact already-tested bytes; use its [corrected executable fixture evidence](I036-r2-camp-diagnostics-evidence.zip). The global backslash exporter error did not change the original source ZIPs, recorded tests, match outcomes or ledger. No tests, builds or games were rerun for that packaging correction. I037's copied CPP inputs are independently checked byte-for-byte. The historical and corrected packaging hashes are both retained under `provenance/`; this is not a claim that all packaging bytes are unchanged.

The [evidence ZIP](I037-retreat-continuation-evidence.zip) contains frozen sources, source patches, actual-header fixtures and their recorded SDK compilation, exact native record bindings, causal audits and resource accounting. Paths below refer to entries inside that archive. The completed v5 probe is listed below. Its native causal audit is included separately.

The optional [complete experimental patch](I037-camp-retreat-component.patch) is a full diff from current I035 `bots/team_baseline/src/` to `route-only-v5`, including the new header with `/dev/null` as its old path. It changes only `main.cpp`, `params.h` and the added `camp_escape.h`; it does not change the PR baseline or select a new bot. Ordinary `git apply --check` and application passed in isolated LF and CRLF/autocrlf Git fixtures, reconstructing all 17 target files after explicit LF normalization; the CRLF fixture also matches target raw bytes. This checks applicability, not competitive readiness. The patch is **experimental and not upload-ready**. The exact input/output source hashes and application evidence are in `mechanisms/patch-application/`.

## Three deliberately separate sources

**V3, home-only routing, was rejected before native play.** One field toward home can prolong the currently hitting camp. At the saved compact R186 state, Ryth has 50.25 HP at `(8,8)` inside a wolf's range. The home route can retain three further 18-damage hits, whereas a geometric exit retains two. V3 was compiled and fixture-tested, but has no native games or fuel measurements. Its source is retained as a rejected design checkpoint, not as a tested candidate.

**V4 leaves the current camp first, then heads home.** The unchanged v2 strict-exposure chooser runs first. Only when it has no admissible strict decrease and a legal visible neighboring tile could increase raw camp exposure does continuation run. Non-covering awake hazards form forbidden walls; the complement of the intersection of currently covering hazard squares forms nearest lower-exposure roots. At zero exposure the roots become home. One field supplies a strictly decreasing route; moving allies filter only the immediate step. Champion danger is ranked globally before the route filter. Known completed no-route states may hold only at the current champion minimum; failures, stale inputs or insufficient reserve preserve legacy fallback.

This gives a bounded SDK call pattern, not a hard fuel bound or complete tanking policy: at most eight hazard range draws, one field and nine distance getters. Only fresh visible hazards are modeled. A held champion may still take camp damage. Static-graph descent does not prove progress under changing visibility, hazards, occupancy or enemy decisions.

**V5 narrows continuation to a zero known champion-danger minimum.** Its sole source change from V4 is `if (!(poses.minimum_champion <= 1e-6)) return {};`, before any continuation SDK call, scratch mutation or deliberate hold. The original strict-improvement selector still runs first. Equal positive inflated threat envelopes cannot justify a route override; those states return to v2's combat fallback. NaN also declines. This changes admission rather than inventing a new champion risk model. Zero means zero under the current ready-threat model, not guaranteed safety against unseen enemies, future cooldowns or movement.

## Exact v4 decisions and interactions

- **Elkring B, Stellar R107:** candidate and parent share 2,559 global commands and an identical complete 184,696-byte native prestate. V4 moves `(28,19)→(27,19)` instead of re-entering `(28,20)`. Stellar completes a detour west of the elk, retains 225 HP, recalls R120 and reaches home R125. Parent v2 dies to the elk R113. This is a real local rescue. The still-wounded elk outside actual range also matches the inherited nearby-camp warning until allied Tavi kills it R119, consistent with a delayed recall; private read/fuel/`rsafe` values are not recorded, so an earlier successful recall is not claimed.
- **Compact A, Ryth R186:** candidate and parent share 3,954 commands and an identical complete native prestate. V4 moves `(8,8)→(8,7)→(8,6)→(8,5)`, avoiding further camp hits. Stationary Willow at `(5,4)` attacks for 40.5 at R187 and kills Ryth R188. Willow does not chase. The enlarged attack envelope assigns 80 to every legal neighboring pose, so V4 cannot distinguish the approach using that tie. This motivates V5's conservative zero-danger admission gate; it does not validate another multi-turn route.
- **The ally/resource cascade matters:** vacating `(9,9)` lets allied Tavi enter an 80-damage camp zone. V4 Tavi takes 80, 80, 20 and 20 damage, falls from 330 to 130 HP, recalls R193 and reaches home R199. Parent Tavi instead stays at 290 HP and interrupts Prism's group-0 capture R197; own Tavi receives 44 gems R213. In V4 he cannot make that denial, and full-health Prism receives 44 R200. Other trajectories also differ, so the linked sequence is not a sole-cause proof for the final loss.
- **The final compact race is not a neglected winning bag:** own Ren deposits 22 R828 to tie 992–992; own held gems are zero at every round start R829–843. Enemy Stellar deposits 44 R843 to end 992–1036. V4 has less own camp damage and fewer dropped gems than the winning parent, but receives 58 fewer camp-reward gems while the opponent gains 74. Reducing damage alone does not establish better resource ownership or throughput.

The exact hashes, actions, damage, channels, resource receipts and remaining attribution limits are under `causal/v4/`. The local camp rescue and the champion/ally regression are both retained.

## What the scoped v5 native audit establishes

The entire Elkring v5 gameplay stream equals v4: Stellar retains the safe detour and reaches home R125 with 225 HP. Compact preserves 7,319 parent-v2 actions before its first difference; the original R185/R186 focal worlds also match byte-for-byte. Ryth still takes the original camp re-entry and dies R187. Tavi therefore retains the original low-damage route, R197 Prism denial and R213 own 44-gem capture. This avoids the observed V4 combat/ally cascade, while explicitly leaving Ryth's combat retreat unresolved.

The saved return-to-service addendum also distinguishes the detour from simply delaying activity: parent Stellar dies R113, is first alive/full in spawn R173, exits R175 and attacks R179. Scoped v5 arrives R125, reaches full HP R126, exits R129 and attacks R136. Both preserve the observed 102 gold and buy the same three 30-gold HP upgrades, leaving 12; the old death carries zero gems. This is a 43-round earlier observed offensive return in this episode, not a general rule that death is always worse or that the detour/recall timing is optimal.

The later first compact change is Cassi R357 at `(12,9)`, with 160/700 HP and zero reconstructed champion danger. V5 chooses `(12,10)` at raw camp envelope 60, while parent v2 enters `(11,10)` at 80. Later continuation avoids re-entry, recalls R367 and reaches home R372 with 160 HP and no further retreat damage. Parent v2 oscillates between `(11,11)` and `(12,12)`, takes eight 20-damage hits and dies R377. The full native prestates match at the first changed action. This is another local rescue, not proof that it alone causes the final result. Compact v5 has 39 fuel events versus the parent's 33; it does not show uniformly lower runtime cost. The bound details are under `causal/v5/`.

## Source-bound native probes

| Candidate | Opponent | Maps | Slots | Wins–losses | Fuel candidate / opponent |
|---|---|---:|---:|---:|---:|
|postkill-route-escape-v4|spar11|2|4|3–1|27 / 0|
|postkill-route-escape-v5|diagnosis-v59|37|74|37–37|34 / 57|
|postkill-route-escape-v5|spar11|2|4|4–0|53 / 0|
|postkill-route-escape-v5|spar11|6|12|12–0|123 / 42|
|postkill-route-escape-v5|spar12|6|12|12–0|124 / 59|
|postkill-route-escape-v5|spar16|6|12|12–0|110 / 42|
|postkill-route-escape-v5|v60-camp-roster-bound|37|74|33–41|31 / 44|
|route-only-v5|diagnosis-v59|37|74|36–38|36 / 66|
|route-only-v5|spar11|6|12|12–0|121 / 41|
|route-only-v5|spar12|6|12|12–0|99 / 50|
|route-only-v5|spar16|6|12|12–0|110 / 43|
|route-only-v5|v60-camp-roster-bound|37|74|39–35|27 / 20|

V4's four-slot probe is 3–1 against spar11; the exact cached parent controls are kept separately. The four games are a causal diagnostic, not a strength estimate. Completed summaries contain 376 experimental slots, 372 distinct record keys, 372 distinct physical keys and 318 distinct replay streams; reused records and 4 cached matched controls are explicitly labeled. Different sources or later map panels are not pooled. All verified native faults are zero; caught SDK errors remain. Whole-trajectory fuel counts cannot establish per-call fuel improvement.

The saved predeclared validation plan requires the four-probe causal audit before any expansion. It specifies separate 37-map/74-slot panels against raw v59 and selected I035, plus six maps against each of three sparring bots (36 slots), reusing the four witness probe records inside the spar11 panel. Those are historical generated maps with earlier control/candidate results, not globally unseen tournament maps or a repository promotion gate. Planned slots are not counted as played; completed series enter the table separately. No parameter sweep, automatic selection, upload, activation or merge is performed here.

The completed postkill-plus-route V5 panels are 37–37 against raw v59, 33–41 against selected I035 and 36–0 across the three sparring bots. This fails to demonstrate superiority to I035, so it is not promoted. A separate component comparison removes the teammate's postkill-capture block without changing the frozen V5 escape policy: `route-only-v5` is exact `camp-escape-v2` plus the frozen V5 header and flag. It therefore contains **the complete strict escape and scoped continuation without postkill capture**. I035 has neither escape nor postkill capture, so the direct I035 comparison is not a pure route-flag ablation. Its finite comparison is included as a separate series above; it is never pooled with postkill-plus-route results. It uses the same historical outcome-known maps, explicitly post hoc rather than new independent confirmation. The composition distinguishes postkill presence, while scores against common opponents do not prove capture is universally harmful. No nonexistent 37-map bare strict-escape-v2 native control is inferred.

The completed component score is 36–38 versus raw v59 and 39–35 versus I035, with 36–0 on the three sparring bots. The direct I035 panel has three maps won on both sides versus one lost on both sides (paired sign p=0.3125): that small 39–35 edge does not demonstrate superiority. Component fuel is 36/66 against raw and 27/20 in the I035 head-to-head. Its matched sparring candidate total is 330, compared with selected I035's 302, so a blanket budget improvement is not established. No further sweep is included in this diagnostic; the component remains unpromoted.

For context, the exact source-bound selected-I035 controls use matching actual map bytes, seeds, runtime and opponent binaries. These cached controls are not additional new games and remain separate from every experimental head-to-head series:

| Cached source | Opponent | Maps | Slots | Wins–losses | Fuel candidate / opponent |
|---|---|---:|---:|---:|---:|
|camp-roster-bound|diagnosis-v59|37|74|31–43|28 / 68|
|camp-roster-bound|spar11|6|12|12–0|92 / 44|
|camp-roster-bound|spar12|6|12|12–0|112 / 58|
|camp-roster-bound|spar16|6|12|12–0|98 / 44|

## Validation boundary

V4 full-SDK off/on compilation and actual-header fixtures pass (7 off, 130 on). V5 passes full-SDK off/on compilation and 7 off / 135 on fixture checks, including exact Ryth admission rejection before route queries, positive/infinite/NaN minima, preserved positive-danger strict escape, zero-danger Stellar continuation, consistent no-route holding, lower-champion escape, and failure/owner/round/position/fuel guards. Fixtures use a mocked eight-neighbor field and controlled SDK callbacks; they are not native survival evidence. Independent audits bind exact sources and confirm that main, State, draft, capture and the shared protocol are unchanged from the parent composition.

The physical farming/tanking model, closest victim allocation, future camp wake, fog memory, multi-turn combat risk and ally route coordination remain open. No complete source gate, online A/B, activation or source promotion is claimed. The pending-input list in `summary.json` makes this snapshot explicit; rerunning the builder only incorporates completed saved artifacts and runs no games or tests.
