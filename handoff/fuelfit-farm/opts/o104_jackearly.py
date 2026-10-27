#!/usr/bin/env python3
"""o104 jackearly: the jackpot group (most of the map's gems, as far from both spawns) is scored from round P_JACKPOT instead of 550, and
becomes the P_JACKN-champion team job from P_JACKGO. Real 2.0.0 games vs ranks 56-70 (c34, 67 clean e1foco games): in the 33 losses the
rival's r151-300 gems come from the MID of the map (878 of 1018 a game): 22 captures of groups holding a median 81% of the map's gems,
first taken at a median r121 with 2 champions while our nearest champion stands 5 tiles away; we leave the jackpot alone until r550
(I042, from 1.0.3 top teams). In wins nobody takes it before r300. Usage: o104_jackearly.py SRCDIR [JACKPOT=100] [JACKGO=550] [JACKN=3]"""
import sys, os, re
src = sys.argv[1]; args = sys.argv[2:] + ['100', '550', '3'][len(sys.argv) - 2:]
JP, JG, JN = args[:3]
p = os.path.join(src, 'params.h'); s = open(p).read()
for name, val in (('P_JACKPOT', JP), ('P_JACKGO', JG), ('P_JACKN', JN)):
    pat = re.compile(rf'^#define {name} .*$', re.M)
    assert len(pat.findall(s)) == 1, name
    s = pat.sub(f'#define {name} {val}  // o104 jackearly (was (P_E1 ? 550 : 350) / 3)', s)
open(p, 'w').write(s)
m = os.path.join(src, 'main.cpp'); t = open(m).read()
assert t.count('o129_goldopen45') == 1
t = t.replace('o129_goldopen45', 'o129_goldopen45 o104_jackearly', 1)
open(m, 'w').write(t)
print("o104 applied to", src, "P_JACKPOT", JP, "P_JACKGO", JG, "P_JACKN", JN)
