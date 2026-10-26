---
name: cambc-micro-v1b-design-1018
description: 2026-10-18 14:42 USER-APPROVED micro-v1b design: target first, bounded 2-step approach, cached reads
metadata:
  type: project
  modified: 2026-10-18T14:53:00.000Z
---
Split from [[cambc-micro-v1-profile-1018]] (result of micro-v1b recorded there: FAILS fuel 14:51).

14:35-14:42 UTC audit thread proposed and the USER APPROVED on a card ('Acercarse') micro-v1b = micro-v1 + three tweaks (STRATEGY.md 'Revision' under 'Result of micro-v1'): (a) target first: the low rival (<45% hp or killable this turn) is chosen before the cast-before-move step so the ready spell goes to it; no hitting a camp while a low rival is in range; (b) approach: if the low rival is out of reach and our ready damage kills it on arrival, up to 2 steps toward it, only through tiles no other visible rival can hit next round, never past the map centre, never if fight-or-leave says leave (a narrow MI4, an exception to the user's no-chase rule, approved explicitly); (c) fuel: each rival's max hp read once and cached, our abilities once per turn, target +0.00 lost turns vs parent. Expected into results\versions.md first; same measures as before (filter, fuel, classification of rounds with a low rival near) on both variants (bank-v1b-clean and base-v53-clean); if it passes, zips micro-v1b-bank.zip and micro-v1b-base.zip. Block to be pasted by the user into the bot thread at 14:42.
