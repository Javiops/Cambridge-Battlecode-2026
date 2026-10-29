import sys,os,json,gzip,zipfile,re,subprocess
NM={'Ryth':'ryth','Vesper':'vespervale','Vendetta':'vendetta','Marcella':'marcella','HoR':'heartofruin','Ren':'ren','Tavi':'tavi','Varg':'varg'}
dl,rep=sys.argv[1],sys.argv[2]
out=subprocess.run(['python3','an/camp17.py',dl],capture_output=True,text=True).stdout.splitlines()[:-1]
for l in out:
    f=l.split()[0]; r=int(l.split()[1]); t=l.split()[2]
    fn=[x for x in os.listdir(dl) if x.startswith(f)][0].replace('.json.gz','.repl26a')
    so=zipfile.ZipFile(os.path.join(rep,fn)).read('team-a.stdout').decode('latin1').replace('\0','')
    ev=[m for m in re.findall(r'\[(?:v17-race|v14-bail)\][^\n]*',so) if f"ch={NM.get(t,'?')}" in m and r-20<=int(re.search(r'r=(\d+)',m).group(1))<r]
    st=[m for m in re.findall(r'\[r\d+\] '+NM.get(t,'?')+r' [^\n]*',so) if r-25<=int(re.search(r'\[r(\d+)\]',m).group(1))<r]
    print(l[:80]); [print('   ',e) for e in ev]; [print('   ',e[:120]) for e in st]
