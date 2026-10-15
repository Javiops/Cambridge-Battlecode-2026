import pickle, sys
S='/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad'
d=pickle.load(open(S+'/reports/scripts_mapcontrol/q4.pkl','rb'))
enc=d['enc']; grp=d['grp']; deaths=d['deaths']
print('## contact at hp<50%: Mite recalls, Uni walks')
for team in ('mite','uni'):
    L=[x for x in enc if x['team']==team and x['hp']<0.5 and (x['recall'] if team=='mite' else x['mv']=='retreat')][:4]
    for x in L: print(team,{k:x[k] for k in ('map','mid','r','ty','hp','gems','nal','nen','mv','recall','toSpawn')})
print('## contact while carrying >=50 gems')
for team in ('mite','uni'):
    L=[x for x in enc if x['team']==team and x['gems']>=50][:3]
    for x in L: print(team,{k:x[k] for k in ('map','mid','r','ty','hp','gems','nal','nen','mv','hitE','recall','toSpawn')})
print('## enemy group enters our half: episodes with >=2 of ours converging')
for team in ('mite','uni'):
    L=[x for x in grp if x['team']==team and x['toward']>=2][:4]
    for x in L: print(team,x)
print('## enemy group enters our half: ignored (nobody moves toward, farming continues)')
for team in ('mite','uni'):
    L=[x for x in grp if x['team']==team and x['toward']==0 and x['farm']>=2][:4]
    for x in L: print(team,x)
