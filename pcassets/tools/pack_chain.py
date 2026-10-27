r"""pack_chain.py CHAIN OUTDIR TAG [TAG...]: copy only the .repl26a of each pinned game (fetch_replays --all) into
OUTDIR\<label>\ (label kvvl for the reference, taken from the first TAG) plus OUTDIR\index.json with bot, file, match, map,
rival, result and our side (from the bundle's team-<side> files). No stdout/debug files."""
import json, os, re, sys, zipfile
H = os.path.dirname(os.path.abspath(__file__))
chain, OUT, tags = sys.argv[1], sys.argv[2], sys.argv[3:]
plan = [(tags[0], 'ref', 'kvvl')] + [(t, 'cand', t) for t in tags]
index = []
for d, who, lab in plan:
    src = os.path.join(H, 'replays', chain, d)
    od = os.path.join(OUT, lab); os.makedirs(od, exist_ok=True)
    for f in json.load(open(os.path.join(src, 'index.json'), encoding='utf-8'))['files']:
        if f['who'] != who or not f.get('file') or not os.path.exists(os.path.join(src, f['file'])): continue
        with zipfile.ZipFile(os.path.join(src, f['file'])) as z:
            names = z.namelist(); rp = [n for n in names if n.endswith('.repl26a')]
            side = {m.group(1) for n in names for m in [re.match(r'team-([ab])\.', n)] if m}
            if len(rp) != 1: continue
            name = f['file'][len(who) + 1:-4] + '.repl26a'
            open(os.path.join(od, name), 'wb').write(z.read(rp[0]))
        index.append(dict(bot=lab, file=f'{lab}/{name}', match=f['match'], map=f['map'], rival=f['rival'],
                          result=f['result'], side=side.pop() if len(side) == 1 else None))
json.dump(index, open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8'), indent=1)
from collections import Counter
print(len(index), 'replays', dict(Counter(x['bot'] for x in index)), 'no side', sum(x['side'] is None for x in index))
