---
name: cambc-patch-2-0-0-1026
description: Site switched to engine 2.0.0 / CLI 4.0.0 on 2026-10-26 ~00:15 Madrid; all 1.0.3 references void; patch content and impact on our bot
metadata:
  type: project
---
Site games switched from engine 1.0.3 to 2.0.0 (patchId "2.0.0:85aa7167…") at ~00:15 Madrid 2026-10-26; notes via GET /api/v1/patch-notes (posted 25-10 23:29 UTC), full text and summary in `lab\top10\patch\` (patch_2_0_0.md, RESUMEN_2_0_0.md). Map pool also grew 40 → 55 (25-10 evening) → 70 (02* maps active between 22:45 and 00:36); features in lab\j2\mapfeat55.json / dl70.

**Changes:** Vesper str 55→45; Marcella str/shard 5→4.5, focus/shard 15→14; HoR str/shard 3.5→3, focus/shard 12→10; Ryth str/shard 5→4.5; buffs Cassi focus 70→100, Issac and Varg str 40→45, Stellar focus/shard 7→8.5, Prism hp/shard 60→65, Willow focus 120→140, Ren stun 0.75→1.1×focus, Tavi stun 1.4→1.6×focus; Vendetta unchanged. Items: Treasure 20%→10% gold; Monster 10%→15% camp damage; new families Tribute (−33% tribute), Capture (capture 5→3 turns), Prospector (+25% cluster gold/gems), Hunter (+50 gold per kill), Skirmish (+5% champion damage), Greed (no passive, 25 shards = 35 stats), Collectors (+1% dmg per completed family); inventory 42→84 types. SDK: draft first-turn fuel ×10, CLI 4.0.0, new capture state API (timer/state), get_item_enum(family, stat), CLI can play vs old rival versions and activate versions.

**Impact:** our bot still runs (no botError since 00:15); first control replay 0/5 identical → every 1.0.3 reference (t5, t5a, c21-c29) is void; rebuild with new SDK; build_shop classifies unknown passive as power/bruiser (main.cpp:831) → Greed may slip in; our draft (Ryth, Vesper, Marcella, HoR) is nerfed. Local bench was cambc 3.0.5 (1.0.3); PyPI had no 4.0.0 at 00:38. Related [[cambc-plan-c97-1025]].
