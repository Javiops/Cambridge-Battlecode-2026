import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-cambridge-battlecode-2026/7dd169fd-a130-5bbc-a998-7ca88e70fea6/scratchpad/reports/scripts_recall')
from loader import *
import collections, json
sel=load_sel()
TEAM={'mite':'Mite','uni':'Univardisty'}
def analyze(g):
    m=load_map(g['map']); al=altars(m)
    rounds,order,events,types,camps=load_game(g['match'])
    side=0 if g['side']=='a' else 1
    sa=m['spawnA']
    sp={0:set((x,y) for x in range(sa[0],sa[2]+1) for y in range(sa[1],sa[3]+1))}
    sp[1]=set(mirror(m,x,y) for x,y in sp[0])
    dsp={t:bfs(m,sp[t]) for t in (0,1)}
    dal=bfs(m,al) if al else {}
    out=[]
    # per champion pending recall
    pend={}
    def foes(r,i):
        c=rounds[r][i]
        return [f for f in rounds[r].values() if f['team']!=c['team'] and f['alive'] and f['i']!=i]
    def state(r,i,p):
        c=rounds[r][i]
        fs=foes(r,i)
        dn=min((cheb(p,(f['x'],f['y'])) for f in fs),default=99)
        return dict(hp=c['hp'],mhp=c['mhp'],hpp=round(100*c['hp']/c['mhp']),gems=c['gems'],gold=c['gold'],dfoe=dn,
                    nfoe3=sum(1 for f in fs if cheb(p,(f['x'],f['y']))<=3),nfoe8=sum(1 for f in fs if cheb(p,(f['x'],f['y']))<=8),
                    dspawn=dsp[c['team']].get(p,99),dalt=dal.get(p,99))
    # damage taken per champion per round (by foes or camps), and last damage round
    lasthit={}  # idx -> (round, src)
    for r in order:
        if r==0: continue
        for e in events[r]:
            if e['ak']==1 and e['k']==11:
                a=e['a']; t=types[a][0]
                if t!=side: continue
                p=tuple(e['apos'])
                st=state(r-1,a,p)
                st.update(match=g['match'],team=g['team'],map=g['map'],ty=types[a][1],idx=a,r=r,pos=p,last_hit=r-lasthit.get(a,(-999,))[0])
                if a in pend and pend[a]['result'] is None:
                    pend[a]['result']='restarted'; pend[a]['end']=r
                pend[a]=dict(st,result=None,end=None,ev=[])
                out.append(pend[a])
                continue
            # track damage to champions of our side
            for x in e['eff']:
                i=x['i']
                if x.get('hp',0)<0 and types[i][0]==side:
                    src='camp' if e['ak']==2 else ('foe' if e['ak']==1 and types[e['a']][0]!=side else 'self')
                    lasthit[i]=(r,src)
                    if i in pend and pend[i]['result'] is None:
                        pend[i]['result']='hit_'+src; pend[i]['end']=r; pend[i]['hit_by']=types[e['a']][1] if e['ak']==1 else 'camp'; pend[i]['hp_at_hit']=x['hpnow']
                        if x.get('alive')==0: pend[i]['result']='died'
                if x.get('alive')==0 and types[i][0]==side and i in pend and pend[i]['result'] is None:
                    pend[i]['result']='died'; pend[i]['end']=r
            if e['ak']==1 and types[e['a']][0]==side and e['a'] in pend and pend[e['a']]['result'] is None:
                a=e['a']
                if e['ph']==14 and e['k']==4 and cheb(tuple(e['eff'][0]['pos'][:2]),tuple(e['eff'][0]['pos'][2:]))>1:
                    pend[a]['result']='arrived'; pend[a]['end']=r
                elif e['ph']==10 and e['k']==4:
                    pend[a]['result']='moved'; pend[a]['end']=r
                elif e['ph']==10 and e['k'] in (5,6) and (e['eff'] or e['keff']):
                    pend[a]['result']='attacked_k%d'%e['k']; pend[a]['end']=r
                elif e['ph']==10 and e['k'] in (12,14,20,23,26,13):
                    pend[a]['ev'].append((r,e['k']))
    for p in pend.values():
        if p['result'] is None: p['result']='game_end'
    return out,rounds,order,events,types,dsp,dal,sp
if __name__=='__main__':
    allr=[]
    for g in sel:
        o,*_=analyze(g); allr+=o
    json.dump(allr,open(S+'/reports/scripts_recall/recalls.json','w'))
    for team in ('mite','uni'):
        rs=[x for x in allr if x['team']==team]
        print(team,len(rs),collections.Counter(x['result'] for x in rs))
        print('  pending-ev kinds among non-arrived:',collections.Counter(k for x in rs if x['result']!='arrived' for _,k in x['ev']))
        print('  pending-ev kinds among arrived:',collections.Counter(k for x in rs if x['result']=='arrived' for _,k in x['ev']))
        print('  duration arrived:',collections.Counter(x['end']-x['r'] for x in rs if x['result']=='arrived'))
