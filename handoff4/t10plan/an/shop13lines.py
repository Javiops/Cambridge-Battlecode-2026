"""shop13lines.py TAG: [v13-shop] lines per game from the bot side's stdout in rep/TAG (shards by champion and window, first purchase round)."""
import zipfile, glob, re, collections, sys, statistics as st
T = sys.argv[1]; n = 0; C = collections.Counter(); W = collections.Counter(); first = collections.defaultdict(list); fuel = 0
for f in sorted(glob.glob(f'/home/user/ws/rep/{T}/*.repl26a')):
    side = 'a' if f.endswith('_a.repl26a') else 'b'
    out = zipfile.ZipFile(f).read(f'team-{side}.stdout').decode(errors='replace'); n += 1
    seen = set()
    for m in re.finditer(r'\[v13-shop\] r=(\d+) ch=(\w+) item=([\w-]+) gold=(\d+)', out):
        r, ch, it = int(m.group(1)), m.group(2), m.group(3)
        C[(ch, it)] += 1; W[(ch, 'r30-150' if r <= 150 else 'r150-300' if r <= 300 else 'r300-600' if r <= 600 else 'r600+')] += 1
        if ch not in seen: seen.add(ch); first[ch].append(r)
    fuel += len(re.findall(r'low-fuel|fuel-wait', out))
print(f'{T}: {n} games, {sum(C.values())/n:.1f} [v13-shop] lines a game, low-fuel/fuel-wait markers {fuel}')
for ch in sorted({c for c, _ in C}):
    print(f'- {ch}: ' + ', '.join(f'{w} {W[(ch, w)]/n:.1f}' for w in ['r30-150', 'r150-300', 'r300-600', 'r600+']) + f'; first purchase round median {st.median(first[ch]):.0f}; items: ' + ', '.join(f'{it} {v/n:.1f}' for (c, it), v in C.most_common() if c == ch))
