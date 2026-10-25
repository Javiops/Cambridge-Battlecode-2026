# restarts.py RES... : champion restarts = [init] lines beyond one per champion (a turn over the fuel restarts the program)
import zipfile,glob,sys,re,collections
for d in sys.argv[1:]:
    tot=0; games=0; per=collections.Counter(); ex=[]
    for f in glob.glob(d+'/*/*.repl26a'):
        side='team-a.stdout' if '/A_' in f else 'team-b.stdout'
        try: t=zipfile.ZipFile(f).read(side).decode(errors='replace')
        except KeyError: continue
        c=collections.Counter(m.group(1) for m in re.finditer(r'\[init\] (\w+) ',t))
        r=sum(v-1 for v in c.values() if v>1)
        if r: games+=1; tot+=r; ex.append((f.split('/')[-2]+'/'+f.split('/')[-1][:-8],r))
    print(d,'games with restarts',games,'restarts',tot,ex[:6])
