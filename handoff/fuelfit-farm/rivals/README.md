# Local rival bots (engine 2.0.0 bench, cambc 4.0.0)

Source-only zips (`src/`) of the bots the farm thread's local panel plays against; unzip into a bot folder and `cambc build BOT --release`.
rTop1, rD, rF, rHunt, mV19, mV10d are our own replicas of rival behaviours (rHunt hunts in a group); kvvl is our ranked bot (k_vvl_mgwp, v164).
Protocol used by the farm thread (handoff/fuelfit-farm/NOTES.md): near = 40 old maps x 2 sides vs a rotating rival of the six,
far = 14 far maps vs rTop1 + rD both sides, h2h = kvvl on the 26 old near maps and on the 30 new maps, both sides.
