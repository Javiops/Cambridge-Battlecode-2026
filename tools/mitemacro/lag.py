# Per step: Mite's capture round vs the round our champion finished that step ([mm] logs, needs P_MM_LOG).
import re, sys, collections
lag = collections.defaultdict(list)
for line in open(sys.argv[1], errors='replace'):
    m = re.search(r'\[mm\] r(\d+) (\w+) step (\d+) (\w) \((\d+),(\d+)\) mite r(\d+)-(\d+) over', line)
    if m:
        r, name, i, k, x, y, r0, r1 = m.groups()
        lag[name].append((int(i), k, int(r) - int(r1), int(r)))
for n, v in lag.items():
    print(f'{n:8s}', ' '.join(f'{k}{i}:{d:+d}' for i, k, d, r in v[:30]))
