#!/usr/bin/env python3
"""o99 shop2: 2.0.0 shop plans per champion, copied from what the top 5 hold at r300/r600 in 375 real 2.0.0 games
(pcassets/replays_t5b, gem/t5b_items.py). They use none of the 7 new families; they open with Bruiser-strength on the
carries and never with Treasure (nerfed to +10% gold). Our c95shop plans opened with Treasure on HoR, Marcella, Ryth and
Vendetta and our first emblem came 80-140 rounds later than theirs. Usage: o99_shop2.py SRCDIR"""
import sys, os
src = sys.argv[1]
def patch(fn, reps):
    p = os.path.join(src, fn); s = open(p).read()
    for a, b in reps:
        assert s.count(a) == 1, (fn, a[:70], s.count(a)); s = s.replace(a, b)
    open(p, 'w').write(s)
# Vesper (no own plan): the generic "Mite tank build" line is hers (Ren/Prism/Stellar/Tavi/Cassi/Issac/melee core override it later)
patch('champions.h', [(
    '        s.plan = {{"durab", \'s\', 1}, {"jungle", \'s\', 1}, {"bruiser", \'h\', 1}, {"power", \'s\', 99}};',
    '        s.plan = {{"bruiser", \'s\', 1}, {"jungle", \'s\', 1}, {"bruiser", \'h\', 1}, {"durab", \'h\', 1}, {"bruiser", \'s\', 99}};  // o99 shop2: top-5 Vesper r300 bruiser-s .56 jungle-s .50 durab-h .28 bruiser-h .24; r600 bruiser-s 2.98')])
patch('marcella.h', [(
    '    s.plan = {{"treasure", \'f\', 1}, {"bruiser", \'f\', 1}, {"jungle", \'s\', 1}, {"bruiser", \'h\', 2}, {"bruiser", \'f\', 99}};',
    '    s.plan = {{"bruiser", \'s\', 1}, {"jungle", \'s\', 1}, {"bruiser", \'h\', 1}, {"durab", \'h\', 1}, {"bruiser", \'s\', 99}};  // o99 shop2: top-5 Marcella r300 bruiser-s .39 jungle-s .29 bruiser-h .27 durab-h .20; r600 bruiser-s 2.28 bruiser-h .92 bruiser-f .64')])
patch('vendetta.h', [(
    '    s.plan = {{"treasure", \'s\', 1}, {"jungle", \'s\', 1}, {"bruiser", \'h\', 1}, {"bruiser", \'s\', 99}};',
    '    s.plan = {{"jungle", \'s\', 1}, {"bruiser", \'s\', 1}, {"bruiser", \'h\', 1}, {"monster", \'s\', 1}, {"bruiser", \'s\', 99}};  // o99 shop2: top-5 Vendetta r300 jungle-s .54 bruiser-s .19 monster-s .16; r600 bruiser-s 1.79 bruiser-h 1.09 jungle-s .89 monster-s .42')])
patch('heart_of_ruin.h', [(
    '    s.plan = {{"treasure", \'h\', 1}, {"jungle", \'f\', 1}, {"bruiser", \'h\', 1}, {"durab", \'h\', 1}, {"bruiser", \'h\', 2}, {"bruiser", \'f\', 99}};',
    '    s.plan = {{"jungle", \'f\', 1}, {"treasure", \'h\', 1}, {"bruiser", \'h\', 1}, {"bruiser", \'f\', 1}, {"durab", \'h\', 1}, {"bruiser", \'f\', 99}};  // o99 shop2: top-5 HoR r300 treasure-h .44 jungle-f .30; r600 bruiser-f .80 bruiser-h .75 jungle-f .73 treasure-h .67 durab-h .35')])
patch('ryth.h', [(
    '    s.plan = {{"treasure", \'h\', 1}, {"jungle", \'s\', 1}, {"bruiser", \'h\', 1}, {"durab", \'h\', 1}, {"bruiser", \'s\', 1}, {"bruiser", \'h\', 99}};',
    '    s.plan = {{"jungle", \'s\', 1}, {"bruiser", \'h\', 1}, {"treasure", \'h\', 1}, {"bruiser", \'s\', 1}, {"durab", \'h\', 1}, {"bruiser", \'h\', 99}};  // o99 shop2: top-5 Ryth r300 treasure-h .29 jungle-s .25; r600 jungle-s .75 bruiser-h .67 treasure-h .42')])
patch('main.cpp', [('o129_goldopen45', 'o129_goldopen45 o99_shop2')])  # stdout marker on the [fuelfit] line
print('o99 applied to', src)
