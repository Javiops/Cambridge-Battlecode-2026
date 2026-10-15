"""cmp_tables.py <out_dir_A> <out_dir_B> [labelA labelB]: parse the markdown tables of the q*.out files in two output directories and print them
side by side: every row of a table appears as us<A>, us<B>, opp<A>, opp<B> (tables keyed by split+who) or <A>/<B> (tables without a who column)."""
import sys, re, os, collections
A, B = sys.argv[1], sys.argv[2]; LA, LB = (sys.argv[3], sys.argv[4]) if len(sys.argv) > 4 else ('27', '26')
def parse(path):
    """returns list of (header_cells, rows) ; rows = list of cell lists"""
    tabs = []; cur = None
    for line in open(path):
        line = line.rstrip('\n')
        if line.startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if all(re.fullmatch(r'-+', c) for c in cells if c) and cur and len(cur[1]) == 0: continue
            if cur is None: cur = (cells, []); tabs.append(cur)
            else: cur[1].append(cells)
        else:
            cur = None
    return tabs
def find(tabs, first_cols):
    for h, rows in tabs:
        if [c.lower() for c in h[:len(first_cols)]] == [c.lower() for c in first_cols]: return h, rows
    return None
def merged(file, first_cols, who_col=1, keycols=None, rowfilter=None, whos=('us', 'opp'), order=None):
    ta = find(parse(os.path.join(A, file)), first_cols); tb = find(parse(os.path.join(B, file)), first_cols)
    if not ta or not tb: return '(table not found: %s %s)\n' % (file, first_cols)
    h = ta[0]; kc = keycols if keycols is not None else (who_col + 1)
    out = ['| ' + ' | '.join(h) + ' |', '|' + '---|' * len(h)]
    def key(r): return tuple(r[:kc])
    ra = collections.OrderedDict((key(r), r) for r in ta[1]); rb = {key(r): r for r in tb[1]}
    keys = list(ra.keys()) + [k for k in rb if k not in ra]
    if order: keys = sorted(keys, key=order)
    seen = set()
    for k in keys:
        base = k[:who_col] + k[who_col+1:] if who_col is not None else k
        if base in seen: continue
        seen.add(base)
        if rowfilter and not rowfilter(k): continue
        for who in whos:
            for lab, src in ((LA, ra), (LB, rb)):
                kk = k[:who_col] + (who,) + k[who_col+1:] if who_col is not None else k
                r = src.get(kk)
                if r is None: continue
                r = list(r)
                if who_col is not None: r[who_col] = who + lab
                else: r.insert(1, lab)
                out.append('| ' + ' | '.join(r) + ' |')
    return '\n'.join(out) + '\n'
def merged_nowho(file, first_cols, keycols=1, rowfilter=None):
    ta = find(parse(os.path.join(A, file)), first_cols); tb = find(parse(os.path.join(B, file)), first_cols)
    if not ta or not tb: return '(table not found: %s %s)\n' % (file, first_cols)
    h = list(ta[0]); h.insert(1, 'batch')
    out = ['| ' + ' | '.join(h) + ' |', '|' + '---|' * len(h)]
    ra = collections.OrderedDict((tuple(r[:keycols]), r) for r in ta[1]); rb = {tuple(r[:keycols]): r for r in tb[1]}
    for k in list(ra) + [k for k in rb if k not in ra]:
        if rowfilter and not rowfilter(k): continue
        for lab, src in ((LA, ra), (LB, rb)):
            r = src.get(k)
            if r is None: continue
            r = list(r); r.insert(1, lab); out.append('| ' + ' | '.join(r) + ' |')
    return '\n'.join(out) + '\n'
if __name__ == '__main__':
    MAPS = lambda k: k[0] == 'ALL' or k[0].startswith('map:')
    sections = [
        ('1a own/mid/enemy by bin', merged('q1_territory.out', ['split', 'who', 'games'], rowfilter=MAPS)),
        ('1b other locations', merged('q1_territory.out', ['split', 'who', '0-49'], rowfilter=MAPS)),
        ('1c enemy-half episodes', merged('q1_territory.out', ['split', 'who', 'games', 'episodes'], rowfilter=MAPS)),
        ('1d reaction to invaders', merged_nowho('q1_territory.out', ['split', 'rounds with invader'], rowfilter=MAPS)),
        ('2a spread', merged('q2_spread.out', ['split', 'who', 'rounds', 'mean pd'], rowfilter=MAPS)),
        ('2b formation', merged('q2_spread.out', ['split', 'who', 'melee d'], rowfilter=MAPS)),
        ('3a actions (type=ALL)', merged('q3_actions.out', ['split', 'who', 'type'], keycols=3, rowfilter=lambda k: k[2] == 'ALL')),
        ('3b idle where', merged('q3_actions.out', ['split', 'who', 'idle rounds'], rowfilter=MAPS)),
        ('3c idle streaks next to living camp (q14)', merged('q14_idlecamp.out', ['map', 'who', 'streaks'])),
        ('4a captures by territory', merged('q4_camps.out', ['split', 'who', '0-49'], rowfilter=MAPS)),
        ('4b own-half groups lost', merged_nowho('q4_camps.out', ['split', 'games', 'games with own-half group lost'], rowfilter=MAPS)),
        ('4c per-game means', merged_nowho('q4_camps.out', ['split', 'games', 'us mid caps'])),
        ('6a deaths', merged('q7_deaths.out', ['split', 'who', 'n', 'per game'], rowfilter=lambda k: MAPS(k) or k[0].startswith('res:'))),
        ('6b opening deaths', merged_nowho('q9_opening.out', ['map', 'games', 'our deaths <r100 (W / L)'])),
        ('6b local numbers', merged('q9_opening.out', ['split', 'who', 'champ-rounds'], rowfilter=MAPS)),
        ('7 determinism', merged_nowho('q10_determinism.out', ['map', 'games', 'us r10'])),
        ('cycle (q6)', merged('q6_cycle.out', ['map', 'who', 'captures'])),
        ('clearing (q11)', merged('q11_rows.out', ['map', 'who', 'clearings'])),
        ('lanes allocation (q8)', merged('q8_lanes.out', ['who', 'phase'], who_col=0, keycols=2)),
        ('lanes invaders (q8)', merged_nowho('q8_lanes.out', ['invaders in lane', 'rounds'])),
        ('stacking captures (q13)', merged('q13_stacking.out', ['map', 'who', 'class'], keycols=3)),
        ('stacking group-rounds (q13)', merged('q13_stacking.out', ['map', 'who', 'class', 'group-rounds'], keycols=3)),
    ]
    for name, t in sections: print('### ' + name + '\n'); print(t)
