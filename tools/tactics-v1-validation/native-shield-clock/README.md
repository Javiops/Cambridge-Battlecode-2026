# Native shield clock regression

Run `run_native.py --cli PATH_TO_CAMBC --project PATH_TO_ARENA --source PATH_TO_BOT_SRC --output NEW_DIRECTORY`. The official SDK and CLI 2.2.2 and its engine are required. The runner compiles a test guest from the supplied production headers and this fixture; it never modifies the bot or game installation.

The test moves actual Varg to an actual Wolf with 20 Strength, casts its 250 point shield lasting five turns and attacks once. Subsequent real SDK snapshots must retain full HP through five future monster phases. The shield expires with unused value before the sixth phase, which deals 20 HP. Production Actor shield value/duration must equal native buffs at all seven observations. Team B and the other actors idle. No World projections or custom camp stats are used. This establishes carry/expiry timing, not coalition strength or other-body shielding.

The output records exact source, module, map, SDK, replay and statistics hashes. It requires the full ledger, zero native fuel pauses and zero bot faults.
