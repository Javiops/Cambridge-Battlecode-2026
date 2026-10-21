# V88 channel-cover field test, 21 October

All six requested unranked groups / 30 games are complete and native-verified
on 12 maps in both seats. Actual queued and completed version: 88. Final actual
allowance: zero. Own team observed #142 / 1,670 Elo; opponents Preyas #110/1,705,
Cozy #72/1,762 and BitShift #66/1,773. Preserve these observations rather than
assuming rank is linear strength. The three planned pairs are not pending.

**V88 wins 8/30, with zero faults and zero fuel losses.** The corresponding
v87 results have 12/30 wins. Opponents are pinned to previous submissions and
map/seat labels match, but engine seed equality is not certified. This is a
descriptive regression, not a controlled causal strength result. Keep v88 as
a functional experiment under Fran's iteration policy; no automatic rollback
solely for lower wins, no promotion or independent PPO gain.

| Opponent | V88 wins | V87 wins | V88 mean bank |
|---|---:|---:|---:|
| Preyas | 2/10 | 5/10 | 576.9 |
| Cozy Campfire | 4/10 | 2/10 | 708.6 |
| BitShift | 2/10 | 5/10 | 458.0 |

## What changed in the target behavior

- Cozy contest deposits are 200/0 versus v87 0/200: the pair still banks only
  200, while collection drops from 1,600 to 800. Deaths decline from 56/62 to
  53/56. One seat's improved delivery is not a successful paired channel fix.
- Preyas elk-arena banks 0/396 versus 72/72, with collection 72/564 versus
  144/72. Preyas big-world banks 327/386 versus 381/336, approximately unchanged
  as a pair. Acquisition, losses and deposits remain separate measurements.
- BitShift elk B collapses from 972 collected/900 banked to 72/72; deaths rise
  from 16 to 42. The A seat improves from zero to 72 collected/banked but still
  loses. This remains an acquisition/control concern, not a general banking stall.

Quiet cover appears in periodic logs in eight games. These samples prove that
the mode can activate, not its complete frequency or causal benefit. Inspect
optional scan costs and handling of hidden roster entries before broadening
combat commitments. In the current code, one outer exception wrapper can end
the whole ally scan on the first live hidden champion. The SDK also fetches
live champion state separately for channel and position queries. An isolated
visible-snapshot refinement is a hypothesis to test, not an established fix.

The first automatic ranked v88 group against Serious-Wyso is kept separately:
3/5, zero faults/fuel losses, all native-verified. **No ranked match was initiated
by this agent**, and these five games are not pooled into the 30-game benchmark.

Official reconstruction matches terminal winner/round/banks and each champion's
gold, collection, deposits, kills and deaths. Rules 1.0.1 and the pinned build
are verified. Source/WASM/model identities and original Stage 1–7 certificates
remain intact. No new map/opponent-name cases and no confirmation games. The
existing 15-minute heartbeat checks returning quota while development continues.
