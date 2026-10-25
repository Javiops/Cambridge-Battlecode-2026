import zipfile,glob,re,sys,statistics as st
T={};G=[];C=[]
for f in glob.glob(sys.argv[1]+'/*/*.repl26a'):
    side='team-a.stdout' if '/A_' in f else 'team-b.stdout'
    txt=zipfile.ZipFile(f).read(side).decode(errors='replace')
    for m in re.finditer(r'\[dbgI\] r(\d+) (\S+) (\d+)',txt): T.setdefault(m[2],[]).append(int(m[3]))
    for m in re.finditer(r'\[dbgG\] n (\d+) max (\d+) mean (\d+) raw (\d+)',txt): G.append((int(m[1]),int(m[2]),int(m[3])))
    for m in re.finditer(r'\[dbgC\] camp_groups (\d+)',txt): C.append(int(m[1]))
for k,v in T.items(): v.sort(); print(k,'n',len(v),'p50',v[len(v)//2],'p90',v[int(len(v)*.9)],'max',v[-1])
print('camp_groups p50',sorted(C)[len(C)//2],'max',max(C))
print('groups: maxn',max(g[0] for g in G),'pergroup max',max(g[1] for g in G),'mean of means',int(st.mean(g[2] for g in G)),'max mean',max(g[2] for g in G))
