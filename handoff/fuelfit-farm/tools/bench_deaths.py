# bench_deaths.py BOT RESDIR... : our deaths per game by round window and cause (camp / champion), kills, from the bench statistics JSON
import sys,json,glob,os,collections
bot=sys.argv[1]
for d in sys.argv[2:]:
    files=glob.glob(f'/tmp/claude-0/ff/ws4/res/{d}/**/*.json',recursive=True); n=0
    D=collections.Counter(); K=0
    for f in files:
        side='teamA' if os.path.basename(f).startswith('A_') else 'teamB'
        try: j=json.load(open(f))
        except Exception: continue
        n+=1
        for ev in j['events']:
            if ev['owner'].get('team')!=side: continue
            if ev['kind']=='death':
                for e in ev['entries']:
                    r=e['timestamp']['round']; w='0-150' if r<=150 else ('151-300' if r<=300 else '301+')
                    D[(w,'camp' if e['context']=='camp' else 'champ')]+=1
            elif ev['kind']=='kill': K+=len(ev['entries'])
    if not n: print(d,'no files'); continue
    print(f"{d:22s} games {n:3d} deaths/game 0-150 camp {D[('0-150','camp')]/n:.2f} champ {D[('0-150','champ')]/n:.2f} | 151-300 camp {D[('151-300','camp')]/n:.2f} champ {D[('151-300','champ')]/n:.2f} | 301+ {sum(v for k,v in D.items() if k[0]=='301+')/n:.2f} | kills/game {K/n:.2f}")
