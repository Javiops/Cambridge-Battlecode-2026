import json,glob,os,sys
def res(d):
    o={}
    for f in glob.glob(d+'/*/*.json'):
        J=json.load(open(f)); us='teamA' if os.path.basename(f)[0]=='A' else 'teamB'; o[f[len(d):]]=J['match']['outcome']==us
    return o
B=res(sys.argv[1])
for d in sys.argv[2:]:
    C=res(d); k=[x for x in C if x in B]; ch=[x for x in k if C[x]!=B[x]]; net=sum(C[x]-B[x] for x in ch)
    print(d, 'net %+d changed %d bar %.1f'%(net,len(ch),2*len(ch)**.5))
