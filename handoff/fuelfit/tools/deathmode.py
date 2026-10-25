import json,glob,sys,zipfile,re,collections
# deathmode.py RES... : our deaths <=300 by last logged mode (status lines every 25 rounds) + killer context, local panel
for d in sys.argv[1:]:
    modes=collections.Counter(); n=0; tot=0
    for f in sorted(glob.glob(d+'/*/*.json')):
        j=json.load(open(f)); us='teamA' if '/A_' in f else 'teamB'; side='a' if us=='teamA' else 'b'; n+=1
        try: out=zipfile.ZipFile(f[:-5]+'.repl26a').read(f'team-{side}.stdout').decode('utf8','replace')
        except Exception: continue
        st=collections.defaultdict(dict)  # name -> round -> (mode,farm)
        for r,name,mode,farm in re.findall(r'\[r(\d+)\] (\w+) pos=\S+ hp=\S+ gems=\d+ gold=\d+ mode=(\S+) farm=(\S+)',out):
            st[name[:5]][int(r)]=(mode,farm)
        for e in j['events']:
            if e.get('kind')!='death' or e['owner'].get('team')!=us: continue
            who=e['owner'].get('name','?').replace(' ','').lower()[:5]
            for en in e['entries']:
                r=en['timestamp']['round']
                if r>300 or r<20: continue
                tot+=1
                rs=[k for k in st.get(who,{}) if k<=r]
                m=st[who][max(rs)] if rs else ('?','?')
                modes[m[0]+('/'+m[1] if m[1]!='-' else '')]+=1
    print(d,'games',n,'deaths r20-300',tot, modes.most_common(10))
