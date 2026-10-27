import json,sys,os,glob
def res(d):
    o={}
    for f in glob.glob(d+'/*.json'):
        try: m=json.load(open(f))['match']['outcome']
        except Exception: continue
        o[os.path.basename(f)]=(m=='teamA')==(os.path.basename(f)[0]=='A')
    return o
for d in sys.argv[1:]:
    r=res(d); print(d,sum(r.values()),'/',len(r))
