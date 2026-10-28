"""shop13div.py TAGA TAGB: first round where the bot side's champion positions differ between dec37/TAGA and dec37/TAGB (same map/side)."""
import gzip, json, os, sys, collections
A, B = sys.argv[1:3]; out = []
for fn in sorted(os.listdir(f'/home/user/ws/dec37/{A}')):
    pb = f'/home/user/ws/dec37/{B}/{fn}'
    if not os.path.exists(pb): continue
    us = 1 if fn.endswith('_b.json.gz') else 0
    da = json.load(gzip.open(f'/home/user/ws/dec37/{A}/{fn}'))['rounds']; db = json.load(gzip.open(pb))['rounds']
    d = None
    for ra, rb in zip(da, db):
        pa = sorted((c[0], c[3], c[4]) for c in ra['c'] if c[1] == us); pb_ = sorted((c[0], c[3], c[4]) for c in rb['c'] if c[1] == us)
        if pa != pb_: d = ra['r']; break
    out.append((fn.replace('.json.gz', ''), d))
c = collections.Counter('same<=600' if d is None else '<30' if d < 30 else '30-79' if d < 80 else '80+' for _, d in out)
print(f'{A} vs {B}: {len(out)} games; first divergence of our positions: {dict(c)}; before r30: {[(f, d) for f, d in out if d is not None and d < 30]}')
