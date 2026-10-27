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

## Prism (2026-10-27, prism/)
Top-5 Prism in t5b (prismst.py, prisma.py): 150 games, but only two rivals draft her (willow best girl 75, prism best girl 75).
Per game: 307 gems, 1618 gold, 42k camp damage (their best farmer), 0.55 deaths. Build about half health (Bruiser-f 18.8,
Bruiser-h 10.2, Jungle-h 4.4, Durab-h 3.9, Home-h 3.4, Monster-h 2.9 shards). Spells: slot 0 targeted stun 1.5x focus range 4,
slot 1 ground area 1.0x range 4+1; both exclusive with movement; 78% of their casts with no enemy champion within 5 (camps).
Our generic Prism casts as often (pcast.py: 47/47 per 1000 alive rounds vs their 47/54), so spells are not the gap.
dB2 = dB + prism.h shop_plan/late_mix copying their build: 280/420 (dB 284, E1 298; vs dB +27/-31). Our Prism stays at
98 gems, 638 gold, 2.7 deaths (local), 6 gems in r1-150 (chact2). The gap is the generic farm loop, not her code.

## Ryth (2026-10-27)
rdeath.py on t5b e1 (125 games), deaths r1-400 per drafted game: Ryth 0.98, Vesper 1.02, Marcella 1.02, HoR 1.24,
Vendetta 1.17; top 5 0.06-0.34. Ryth is not our outlier. Common to all our deaths: 10 rounds before, nearest ally at
4-7 tiles (Vesper 7) and 0.4-0.9 allies within 4; theirs 2-3 tiles and 1.0-1.7 allies. No ryth.h piece.
Drafts without Ryth on E1 (298): Tavi 280, Willow 300; Ryth last (Vendetta 4th) 291.

## On e1foco (pcassets/zips/e1foco.zip sha 659ded19), base 304/420
| variant | wins | + / - | bar |
|---|---|---|---|
| efA e1focofarhor (P_FAR_SWAP "heart") | 309 | +29 / -24 | 14.6 |
| efW (Willow for Ryth) | 301 | +58 / -61 | 21.8 |
| efAW (both) | 298 | +52 / -58 | 21.0 |
zips/e1focofarhor.zip, marker "[init] efA".
