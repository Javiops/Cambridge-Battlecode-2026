import json,glob,sys,collections,os
exec(open(os.path.dirname(os.path.abspath(__file__))+'/mbuy.py').read().split('J=jobs')[0])
J=jobs(sys.argv[1]); n=0; A=collections.defaultdict(float); first=collections.Counter()
for summ,tn in J:
    E=evs(summ,tn)
    if not E: continue
    n+=1
    for R in (100,150,200,300,400):
        st=collections.Counter()
        for r,name,v in E:
            if r>=R: continue
            fam,stat=name.split(' Shard of ')
            for s_ in ('Strength','Health','Focus'):
                w=1.0 if s_==stat else (0.2 if fam=='Bruiser' else 0)
                if fam=='Power' and s_==stat: w=1.2
                st[s_]+=w*v
            st['all']+=v
        for k,v in st.items(): A[k,R]+=v
    f=[nm for r,nm,v in E if 'Focus' in nm]
    if f: first[[nm for r,nm,v in E if 'Focus' in nm][0].split(' Shard')[0]]+=1
print(sys.argv[1],n)
for R in (100,150,200,300,400): print(R,' '.join(f"{k} {A[k,R]/n:.1f}" for k in ('all','Strength','Health','Focus')))
print('first focus family',first.most_common())
