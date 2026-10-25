# fph_tot.py RESDIR... : per result dir, turns by total cost from the last [fph] 47 line of each champion stdout (2.5k buckets)
import zipfile,glob,sys
for d in sys.argv[1:]:
    tot=[0]*48; n=0; games=0
    for f in glob.glob(d+'/*/*.repl26a')+glob.glob(d+'/*.repl26a'):
        side='a' if '/A_' in f else 'b'
        try: t=zipfile.ZipFile(f).read(f'team-{side}.stdout').decode('latin1').splitlines()
        except KeyError: continue
        games+=1
        # one [fph] 47 line per champion program per print; take the last per champion: stdout is interleaved, so take the last 4 distinct? use max per block: simpler = last line per champion name unknown -> take all last occurrences by position of [fpn]
        last={}
        for l in t:
            if '[fph] 47 ' in l:
                p=l[l.index('[fph] 47 ')+9:].split()
                key=l[:l.index('[fph]')]  # indentation prefix differs per champion stream
                last[key]=[int(x) for x in p]
        for v in last.values():
            for i,x in enumerate(v): tot[i]+=x
    N=sum(tot)
    print(f"{d}: games {games} turns {N}  >=77.5k {sum(tot[31:])} ({100*sum(tot[31:])/max(N,1):.2f}%)  >=87.5k {sum(tot[35:])}  >=100k {sum(tot[40:])}  p99 bucket {[i for i in range(48) if sum(tot[:i+1])>=0.99*N][0]*2.5:.1f}k")
