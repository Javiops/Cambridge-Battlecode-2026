# clus.py LIST.json: team size and number of clusters (allies chained within 3) by round bucket, plus camp sharing
import json,sys,collections
def ch(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
L=json.load(open(sys.argv[1])); B=[(30,90),(90,150),(150,300)]
A=collections.defaultdict(list); T=collections.Counter()
for fn,us in L:
    for l in open(fn):
        try: d=json.loads(l)
        except: continue
        r=d['round']; b=[i for i,(a,z) in enumerate(B) if a<=r<z]
        if not b: continue
        b=b[0]
        M=[c for c in d['champions'] if c['alive'] and c['x']>=0 and c['team']==us and c['typeName']!='Issac']
        if r==60:
            for c in M: T[c['typeName']]+=1
        n=len(M); par=list(range(n))
        def f(i):
            while par[i]!=i: i=par[i]
            return i
        for i in range(n):
            for j in range(i+1,n):
                if ch((M[i]['x'],M[i]['y']),(M[j]['x'],M[j]['y']))<=3: par[f(i)]=f(j)
        k=len({f(i) for i in range(n)})
        A[('n',b)].append(n); A[('cl',b)].append(k)
        sz=collections.Counter(f(i) for i in range(n))
        A[('big',b)].append(max(sz.values()) if sz else 0)
print(sys.argv[1], ' '.join(f"r{B[b][0]}: size {sum(A[('n',b)])/len(A[('n',b)]):.2f} clusters {sum(A[('cl',b)])/len(A[('cl',b)]):.2f} biggest {sum(A[('big',b)])/len(A[('big',b)]):.2f}" for b in range(3)))
print('  types@r60', T.most_common(8))
