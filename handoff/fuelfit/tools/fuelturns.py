import struct,zipfile,glob,sys,re,collections
# fuelturns.py RESDIR [R] [-v]: per game our turn-1 fuel per champion (total incl. engine overhead; cap 200000) and
# capped turns (overflow, 100000) in rounds 2..R (default 400), from team-x.fuel in the replay bundles; ts from stdout.
d=sys.argv[1]; R=int(([a for a in sys.argv[2:] if a.isdigit()]+["400"])[0])
V='-v' in sys.argv
tot_cap1=tot_capl=0; games=0; permap=collections.defaultdict(lambda:[0,0,0])
for f in sorted(glob.glob(d+'/*/*.repl26a')):
    side='a' if '/A_' in f else 'b'
    z=zipfile.ZipFile(f)
    try: b=z.read(f'team-{side}.fuel'); out=z.read(f'team-{side}.stdout').decode('utf8','replace')
    except Exception as e: print(f,'missing',e); continue
    m=re.search(r'\[mapplan\] ts=(\d+)',out); ts=int(m.group(1)) if m else 4
    vals=struct.unpack_from('<%dQ'%((len(b)-13)//8), b, 13)
    body=vals[8:]; turns=body[ts:]
    t1=turns[0:ts]; later=turns[ts:ts*R]
    cap1=sum(1 for v in t1 if v>=200000); capl=sum(1 for v in later if v>=100000)
    tot_cap1+=cap1; tot_capl+=capl; games+=1
    mp=f.split('/')[-1][4:-8]; permap[mp][0]+=1; permap[mp][1]+=cap1; permap[mp][2]+=capl
    if V: print(f.split('/',2)[-1].ljust(40),'ts',ts,'t1',t1,'cap t1',cap1,'cap r2-%d'%R,capl)
print(d,'games',games,'turn-1 capped champions',tot_cap1,'capped later turns',tot_capl)
print('  per map (games, t1 caps, later caps):',' '.join(f"{k}:{v[0]}/{v[1]}/{v[2]}" for k,v in sorted(permap.items()) if v[1] or v[2]))
