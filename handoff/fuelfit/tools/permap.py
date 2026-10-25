import json,collections,sys
man=sys.argv[1]; bots=sys.argv[2:]
keys=[]
for l in open(man):
    p=l.split()[3]; keys.append((p.split('/')[-1][:-8],p.split('/')[-2]))
def win(d,g,r):
    try: o=json.load(open(f'{d}/{r}/{g}.json'))['match']['outcome']
    except Exception: return None
    side='teamA' if g.startswith('A_') else 'teamB'
    return int(json.dumps(o).find(side)>=0)
per=collections.defaultdict(lambda: collections.defaultdict(int))
for g,r in keys:
    m=g[4:]
    for b in bots:
        w=win(b,g,r)
        if w is not None: per[m][b]+=w; per[m]['n_'+b]+=1
print('map'.ljust(22),*[b.split('/')[-1].rjust(5) for b in bots])
for m in sorted(per):
    row=[f"{per[m][b]}/{per[m]['n_'+b]}" for b in bots]
    print(m.ljust(22),*[x.rjust(5) for x in row])
