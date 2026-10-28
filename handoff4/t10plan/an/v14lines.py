"""v14lines.py TAG: [v14-leave] / [v14-bail] / [v14-camp] lines per game from the bot side's stdout in rep/TAG (by champion, round window, ratio)."""
import zipfile, glob, re, collections, sys, statistics as st
T = sys.argv[1]; n = 0; C = collections.Counter(); W = collections.Counter(); ratios = []; hps = []; fuel = 0; per_game = []
for f in sorted(glob.glob(f'/home/user/ws/rep/{T}/*.repl26a')):
    side = 'a' if f.endswith('_a.repl26a') else 'b'
    out = zipfile.ZipFile(f).read(f'team-{side}.stdout').decode(errors='replace'); n += 1; g = 0
    for m in re.finditer(r'\[v14-(leave|bail|camp)\] r=(\d+) ch=(\w+)(.*)', out):
        kind, r, ch, rest = m.group(1), int(m.group(2)), m.group(3), m.group(4); g += 1
        C[(kind, ch)] += 1; W[(kind, 'r30-150' if r <= 150 else 'r150-300' if r <= 300 else 'r300-600' if r <= 600 else 'r600+')] += 1
        if kind == 'leave':
            mm = re.search(r'foes=(\d+) allies=(\d+) ratio=(-?\d+) hp=(\d+)', rest)
            if mm: ratios.append(int(mm.group(3))); hps.append(int(mm.group(4))); C[('foes', mm.group(1))] += 1; C[('allies', mm.group(2))] += 1
    per_game.append(g)
    fuel += len(re.findall(r'low-fuel|fuel-wait', out))
print(f'{T}: {n} games, {sum(per_game)/max(n,1):.1f} v14 lines a game (games with 0: {sum(1 for x in per_game if x == 0)}), low-fuel/fuel-wait markers {fuel}')
for kind in ('leave', 'bail', 'camp'):
    tot = sum(v for (k, c), v in C.items() if k == kind)
    print(f'- {kind}: {tot/max(n,1):.2f}/game; ' + ', '.join(f'{w} {W[(kind, w)]/max(n,1):.2f}' for w in ['r30-150', 'r150-300', 'r300-600', 'r600+']) + '; by champion: ' + ', '.join(f'{c} {v/max(n,1):.2f}' for (k, c), v in C.most_common() if k == kind))
if ratios: print(f'- leave: ratio median {st.median(ratios)}, hp median {st.median(hps)}; foes ' + ', '.join(f'{c}:{v}' for (k, c), v in sorted(C.items()) if k == 'foes') + '; allies ' + ', '.join(f'{c}:{v}' for (k, c), v in sorted(C.items()) if k == 'allies'))
