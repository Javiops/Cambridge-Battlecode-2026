# Noncrew receipt cost microbenchmark

Run `run_native.py --cli PATH_TO_CAMBC --project PATH_TO_ARENA --source PATH_TO_BOT_SRC --output NEW_DIRECTORY` with the official Battlecode SDK and CLI 2.2.2. The supplied map contains three actual actors per team. Team B idles.

Each Team A actor reads a real SDK World, then passes an opaque synthetic runtime unflagged Proposal to the production `make_crew_turn_receipt`. A second sample applies the caller gate and clears only `valid` and `required` for this ordinary action. Both samples must leave these flags false. No production chooser, gameplay mutation, projected future HP or actual coalition action is tested. This is a helper cost and admission microbenchmark, not whole-main activation proof.

The retained development run measured 2,047 fuel for the unconditional helper call and 16 for the gate on all three actual actors, with zero fuel pauses and bot faults. Future compiler changes may change costs; correctness depends on flags, not a fixed performance threshold.

Output includes source, module, map, SDK, replay and statistics hashes and raw per-actor costs. The production main gate preserves paid coalition receipt construction; existing crew-sequence tests exercise that branch separately.
