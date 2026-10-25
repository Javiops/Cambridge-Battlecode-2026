# form.py LIST.json : formation r30-300 for the studied side. LIST = [[dec_file, team], ...]
import json,sys,collections
def ch(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
L=json.load(open(sys.argv[1])); B=[(30,90),(90,150),(150,300)]
A=collections.defaultdict(lambda:[0,0]); EV=collections.Counter()
for fn,us in L:
    R={}
    for l in open(fn):
        try: d=json.loads(l)
        except: continue
        R[d['round']]=d
    prev_near={}
    for r in sorted(R):
        if r<30 or r>300: continue
        b=[i for i,(a,z) in enumerate(B) if a<=r<z]
        if not b: continue
        b=b[0]; d=R[r]
        C=[c for c in d['champions'] if c['alive'] and c['x']>=0]
        mine=[c for c in C if c['team']==us and c['typeName']!='Issac']
        foes=[c for c in C if c['team']!=us]
        pairs=0; g3=0
        for c in mine:
            o=[ch((c['x'],c['y']),(x['x'],x['y'])) for x in mine if x is not c]
            nn=min(o) if o else 99
            A[('paired',b)][0]+=nn<=3; A[('paired',b)][1]+=1
            A[('alone15',b)][0]+=nn>15; A[('alone15',b)][1]+=1
            A[('nn',b)][0]+=min(nn,30); A[('nn',b)][1]+=1
            if sum(1 for x in o if x<=3)>=2: g3=1
            pairs+=nn<=3
            fd=min([ch((c['x'],c['y']),(f['x'],f['y'])) for f in foes] or [99])
            key=(fn,c['index'])
            if fd<=6 and prev_near.get(key,99)>6:
                EV['contact']+=1; EV['contact_alone15']+=nn>15; EV['contact_ally8']+=nn<=8; EV['contact_ally3']+=nn<=3
            prev_near[key]=fd
            if fd<=4 and not (r<=300 and False):
                e=1+sum(1 for x in mine if x is not c and ch((c['x'],c['y']),(x['x'],x['y']))<=4)-sum(1 for f in foes if ch((c['x'],c['y']),(f['x'],f['y']))<=4)
                EV['fr']+=1; EV['fr2']+=e>=2; EV['fr1']+=e==1; EV['fr0']+=e==0; EV['frn']+=e<0
                if e<=0:
                    EV['bad']+=1; EV['bad_a8']+=nn<=8; EV['bad_a15']+=nn<=15
        A[('nopair',b)][0]+=pairs==0; A[('nopair',b)][1]+=1
        A[('g3',b)][0]+=g3; A[('g3',b)][1]+=1
print(sys.argv[1], 'games', len(L))
for k in ('paired','nopair','g3','alone15','nn'):
    print(f'{k:8s}', ' '.join(f'r{B[b][0]}-{B[b][1]}: {(A[(k,b)][0]/max(1,A[(k,b)][1])*(1 if k=="nn" else 100)):5.1f}{"" if k=="nn" else "%"}' for b in range(3)))
n=max(1,EV['contact']); f=max(1,EV['fr']); print('fight rounds',EV['fr'],'+2 %.1f%% +1 %.1f%% 0 %.1f%% <0 %.1f%%'%(100*EV['fr2']/f,100*EV['fr1']/f,100*EV['fr0']/f,100*EV['frn']/f), 'even/losing: ally<=8 %.0f%% ally<=15 %.0f%%'%(100*EV['bad_a8']/max(1,EV['bad']),100*EV['bad_a15']/max(1,EV['bad'])))
print('contacts (rival newly within 6)',EV['contact'],'alone15 %.0f%% ally<=8 %.0f%% ally<=3 %.0f%%'%(100*EV['contact_alone15']/n,100*EV['contact_ally8']/n,100*EV['contact_ally3']/n))
