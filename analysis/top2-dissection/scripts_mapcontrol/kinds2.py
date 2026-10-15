import sys, json, glob, collections
S='/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad'
f=sys.argv[1]; who=int(sys.argv[2])
evs=[json.loads(l) for l in open(f)]
tl=[]
for e in evs:
    if e['t']!='ev': continue
    if e['ak']==1 and e['a']==who and e['k'] in (11,12,14,18,20,23,26,13,1):
        tl.append((e['r'],e['ph'],'k%d'%e['k'],tuple(e['apos']) if e['apos'] else None, e['eff'][:1]))
    if e['ak']==1 and e['a']==who and e['k']==4 and e['ph']==14:
        tl.append((e['r'],e['ph'],'JUMP',tuple(e['apos']),e['eff'][:1]))
for t in tl[:120]: print(t)
