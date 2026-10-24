"""Juez 2 standalone (see README.md). usage: judge2_local.py RESDIR   (RESDIR/<rival>/[AB]_<map>.json from run_judge2.sh)"""
import json,glob,os,sys,math
H=os.path.dirname(os.path.abspath(__file__))
MF=json.load(open(H+'/mapfeat40.json')); BASE=json.load(open(H+'/base_v6d_outcomes.json'))
cl=lambda m:(lambda d:'near' if d<35 else 'mid' if d<60 else 'far')(MF.get(m,{}).get('d_spawn',0))
HARD='rTop1 rD rF rHunt mV19 mV10d'.split(); PUN='rPun5 rPun5b rPun5c rPun5d'.split(); FARW=0.42
res=sys.argv[1]; C={}
for r in HARD+PUN:
    for f in glob.glob(f'{res}/{r}/[AB]_*.json'):
        k=f'{r}/{os.path.basename(f)[:-5]}'; us='teamA' if os.path.basename(f)[0]=='A' else 'teamB'
        if k in BASE: C[k]=(int(json.load(open(f))['match']['outcome']==us), int(BASE[k]==us), cl(os.path.basename(f)[2:-5]))
kh=[k for k in C if k.split('/')[0] in HARD]; kp=[k for k in C if k.split('/')[0] in PUN]
if not kh or not kp: sys.exit(f'missing games: hard {len(kh)} pun {len(kp)}')
wt=lambda k:FARW if C[k][2]=='far' else 1.0
jh=sum(wt(k)*(C[k][0]-C[k][1]) for k in kh)/len(kh)*100; jp=sum(C[k][0]-C[k][1] for k in kp)/len(kp)*100
bar=2*math.sqrt(sum(wt(k)**2*(C[k][0]!=C[k][1]) for k in kh)/len(kh)**2*1e4+sum(C[k][0]!=C[k][1] for k in kp)/len(kp)**2*1e4)
cls={q:sum(C[k][0]-C[k][1] for k in kh if C[k][2]==q) for q in ('near','mid','far')}
print(f"J2 {jh+jp:+.1f}/100 (bar {bar:.1f}) = hard {jh:+.1f} [near {cls['near']:+d} mid {cls['mid']:+d} far {cls['far']:+d}, far x{FARW}; {len(kh)} g] + pun {jp:+.1f} ({sum(C[k][0]-C[k][1] for k in kp):+d}/{len(kp)}) -> online est {0.8*(jh+jp):+.1f}/100 vs V20")
