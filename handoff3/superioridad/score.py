import sys,re,collections
A,B,f=sys.argv[1:4]
w=l=d=0; per=collections.Counter()
for line in open(f):
  m=re.search(r'\[\+\] (?:TEAM [AB] WIN \((\S+)\)|DRAW)\s+(\S+) vs (\S+)\s+(\S+)',line)
  if not m: continue
  if m.group(1) is None: d+=1; continue
  if m.group(1)==A: w+=1; per[m.group(4)]+=1
  else: l+=1
print(f"{A} vs {B}: {w}-{l} (draw {d})")
