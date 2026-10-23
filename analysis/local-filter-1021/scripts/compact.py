import json,os,glob,sys
# keeps what pair6/gold400j/mechgate need: match, champions, timelines (earnedGold) and the events of the mechanism gauges
KEEP={'death','kill','fuelExhausted','campClear','gemCollection','botFault'}
for pat in sys.argv[1:]:
  for f in glob.glob(pat+'/[AB]_*.json'):
    if os.path.getsize(f)<60000: continue
    try: d=json.load(open(f))
    except Exception: continue
    k={x:d[x] for x in ('match','champions','roster','teams','teamTimelines','formatVersion','jsonFormatVersion','diagnostics') if x in d}
    k['championTimelines']=[t for t in d.get('championTimelines',[]) if t.get('metric')=='earnedGold']
    k['nkinds']=len({e['kind'] for e in d.get('events',[])})
    sl=lambda x: {'timestamp':{'round':x.get('timestamp',{}).get('round')},'context':x.get('context'),'value':x.get('value'),
                  'target':{q:x['target'][q] for q in ('id','kind','name','team') if q in x['target']} if isinstance(x.get('target'),dict) else x.get('target')}
    k['events']=[{'kind':e['kind'],'owner':e.get('owner'),'entries':[sl(x) for x in e['entries']]} for e in d.get('events',[]) if e.get('kind') in KEEP]
    json.dump(k,open(f,'w'),separators=(',',':'))
