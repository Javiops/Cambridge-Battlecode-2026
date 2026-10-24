import zipfile,glob,sys,hashlib
A,B=sys.argv[1:3]; n=d=0
for f in glob.glob(A+'/*/*.repl26a'):
    g=B+f[len(A):]
    try: x=zipfile.ZipFile(f).read('replay.repl26a'); y=zipfile.ZipFile(g).read('replay.repl26a')
    except Exception as e: continue
    n+=1; d+= x!=y
print(B,'replays',n,'differ',d)
