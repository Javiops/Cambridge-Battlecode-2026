"""Mechanism counter from local replays (before they are deleted): counts OUR team's stdout lines matching REGEX.
Round taken from 'r<N>' in the line. Writes DIR/counter.json {game.json: {n, ph:[r<100,100-400,400+]}}.
usage: python3 mechcount.py 'REGEX' DIR [DIR...]"""
import zipfile,re,json,glob,os,sys
rx=re.compile(sys.argv[1]); rr=re.compile(r'\br(\d+)\b')
for D in sys.argv[2:]:
    out={}
    for f in glob.glob(D+'/[AB]_*.repl26a'):
        side='team-a' if os.path.basename(f)[0]=='A' else 'team-b'
        try: z=zipfile.ZipFile(f)
        except Exception: continue
        names=[n for n in z.namelist() if side in n and n.endswith('stdout')]
        n=0; ph=[0,0,0]
        for nm in names:
            for line in z.read(nm).decode('utf8','replace').splitlines():
                if not rx.search(line): continue
                n+=1; m=rr.search(line); r=int(m.group(1)) if m else 0
                ph[0 if r<100 else 1 if r<400 else 2]+=1
        out[os.path.basename(f)[:-8]+'.json']={'n':n,'ph':ph}
    json.dump(out,open(D+'/counter.json','w')); print(D,len(out),'games',sum(v['n'] for v in out.values()),'fires')
