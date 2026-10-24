import json,glob,sys
man=sys.argv[1]
sub=set(l.split()[3].split('/')[-1].replace('.repl26a','')+l.split()[3].split('/')[-2] for l in open(man))
for d in sys.argv[2:]:
    w=n=0
    for f in glob.glob(d+'/*/*.json'):
        key=f.split('/')[-1][:-5]+f.split('/')[-2]
        if key not in sub: continue
        o=json.load(open(f))['match']['outcome']; side='teamA' if '/A_' in f else 'teamB'
        n+=1; w+= (json.dumps(o).find(side)>=0)
    print(d,n,w)
