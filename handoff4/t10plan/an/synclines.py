import zipfile,glob,re,collections,sys
T=sys.argv[1]
W=collections.Counter(); N=collections.Counter(); A=collections.Counter(); tot=0; cap=0; nexts=0; games=0; idle=collections.Counter()
for f in sorted(glob.glob(f'rep/{T}/*.repl26a')):
    side=f[-9]; games+=1
    out=zipfile.ZipFile(f).read(f'team-{side}.stdout').decode(errors='replace')
    for m in re.finditer(r'\[v12-sync\] r=(\d+) ch=(\w+) grp=(\d+) wait=(\d+) n=(\d+)/(\d+)',out):
        r,w,a,n=int(m.group(1)),int(m.group(4)),int(m.group(5)),int(m.group(6))
        if r>600: continue
        tot+=1; W[w]+=1; N[n]+=1; A[(a,n)]+=1
        if a<n: cap+=1
    nexts+=len(re.findall(r'\[v12-next\] r=([1-5]?\d\d) ',out))
    for m in re.finditer(r'\[v11-idle\] r=(\d+) who=\w+ grp=\S+ target=\S+ reason=(\S+)',out):
        if int(m.group(1))<=600: idle[m.group(2)]+=1
print('games',games,'sync lines<=600',tot,'per game %.1f'%(tot/games),'next lines/game %.1f'%(nexts/games))
print('want dist',sorted(N.items())); print('wait dist',sorted(W.items())); print('cap fired (arr<want)',cap, '%.0f%%'%(100*cap/max(1,tot)))
print('arr/want',sorted(A.items()))
print('idle reasons/game',{k:round(v/games,1) for k,v in idle.most_common()})
