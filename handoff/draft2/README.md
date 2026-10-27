# draft2 (2026-10-27): draft vs the top 5 on engine 2.0.0

Measured on the real t5b replays (branch claude/pc-e1-assets dcfe4d3, pcassets/replays_t5b, 125 games per bot):
- fep3.py / fep3p.py: contact episodes r21-100, both sides, per champion. e1 85 games, kvvl 100, e1foco 85 decoded.
  Top 5 gets 4.0-4.9 outnumbering contacts per game, we get 2.1-2.5. We die 1.0-1.1 per game, they die 0.4-0.5.
- draftc.py: champions per side. Ours: Vesper 125, Marcella 125, Ryth 106, HoR 91, Vendetta 78, Ren 34 (far swap).
  Top 5: Vesper 123, HoR 117, Marcella 92, Vendetta 80, Prism 50, Tavi 29, Ryth 24, Cassi&Issac 22, Willow 19, Ren 1.

Local filter on E1 (420 games: p17_rTop1, p17_rD, p17_mV19, 70 maps, both sides; cmpw.py), E1 = 298:
| variant | change | wins | + / - | bar |
|---|---|---|---|---|
| dA e1farhor | P_FAR_SWAP "heart" (HoR on far maps too, no Ren) | 302 | +27 / -23 | 14.1 |
| dB | prefs heart, vesper, marcella, vendetta, prism (Ryth out) | 284 | +50 / -64 | 21.4 |
| dC | dA + dB | 274 | +56 / -80 | 23.3 |

dA passes the gate (neutral locally). zips/e1farhor.zip, stdout marker "[init] drdA". dB/dC fail: Prism has no
champion code (prism.h is a stub), so taking Ryth out for Prism loses locally.
