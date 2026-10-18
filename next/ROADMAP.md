# Roadmap

Open questions and the next steps, in order. Settled conclusions move to DECISIONS.md.

## Foundation (before any real bot)

1. **Map generator.** The calibration shows 12 maps cannot see a 10% handicap. Build a generator of
   valid, symmetric `.map26a` maps (using the official map editor's format), then make `screen` ~100
   generated maps and `confirm` a separate sealed ~60, and keep the site maps as their own report line.
   Exit check: on the generated set, `calib-skip10-v1` ranks below `starter-v1` and the seed twin sits
   within the noise band.
2. **Noise floor as a number in every report.** Run the seed twin in every league and print its gap to
   starter next to the leaderboard, so every result is read against it.
3. **Farm benchmark.** Each version against `dummy-v1`: banked gems at rounds 500/1000/1500 and the round it
   reaches 1000. No opponent means no fight noise. It is a diagnostic for the economy, never the promotion judge
   (Carson, kaggriculture: outcome targets beat shaped proxies).
4. **Ladder replays as opponents' teacher.** Later: download top-team replays and measure their curves
   with the same snapshot fields, so our numbers have a target.

## The bot (after the foundation)

Layers: `sense -> plan -> act -> log`, strategy as data tables picked from map features.
Phases: economy, survival and fights, team play, freeze on 2 November.
