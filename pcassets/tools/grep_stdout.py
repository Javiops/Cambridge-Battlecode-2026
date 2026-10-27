r"""grep_stdout.py CHAIN TAG REGEX: per pinned game of a candidate, our stdout lines matching REGEX (group 1 = value);
prints how many games have each value. Usage: python -I grep_stdout.py c34 t10plan "\[t10plan\][^\n]*map=(\S+)" """
import collections, glob, os, re, sys, zipfile
H = os.path.dirname(os.path.abspath(__file__))
chain, tag, rx = sys.argv[1], sys.argv[2], re.compile(sys.argv[3])
per = collections.Counter(); games = 0; lines = collections.Counter(); maps_none = set()
for f in sorted(glob.glob(os.path.join(H, 'replays', chain, tag, 'cand_*.zip'))):
    z = zipfile.ZipFile(f); games += 1; vals = set()
    for n in z.namelist():
        if n.endswith('.stdout'):
            for m in rx.finditer(z.read(n).decode('utf-8', 'replace')):
                vals.add(m.group(1)); lines[m.group(1)] += 1
    for v in vals: per[v] += 1
    if 'none' in vals: maps_none.add(os.path.basename(f)[5:].rsplit('_', 2)[0])
print(f'{chain}/{tag}: {games} games; games per value {dict(per.most_common(12))}')
print('maps with none:', sorted(maps_none))
