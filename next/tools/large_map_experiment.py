"""Generate independent size-stratified maps with the official native builder.

Map generation uses the official 1.0.1 WASM builder. This does not
alter Stage 1-7 pins or consume any previous confirmation cohort.
"""
from pathlib import Path

import argparse,hashlib,json,os,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from lab import mapgen

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def expanded(layout,width,height):
    """Centre an already symmetric playable layout inside a larger open border."""
    m=dict(layout);dx=(width-m['width'])//2;dy=(height-m['height'])//2
    if width<m['width'] or height<m['height'] or (width-m['width'])%2 or (height-m['height'])%2:
        raise ValueError('Padding must preserve exact rotational symmetry')
    m.update(width=width,height=height,spawn=[1,1,4,4])
    for key in ('walls','holes','bushes','altars'):m[key]=[[x+dx,y+dy] for x,y in layout[key]]
    m['camps']=[[t,x+dx,y+dy] for t,x,y in layout['camps']]
    return m

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('mode',choices=['maps']);p.add_argument('--config',type=Path,required=True)
    p.add_argument('--engine-wasm',type=Path,required=True);p.add_argument('--bridge',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();plan=json.loads(a.config.read_text());out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    manifest=out/'map-plan.json'
    if a.mode=='maps':
        if manifest.exists():raise ValueError('Map plan is immutable; reuse it or start a new registered experiment')
        if sha(a.engine_wasm)!=plan['engine_wasm_sha256']:raise ValueError('Wrong native rules module')
        old_hashes={sha(x) for x in (ROOT/'maps').rglob('*.map26a')}
        entries=[];specs=[];sizes=[(72,80),(80,96),(96,96),(100,100)]
        prefix=plan.get('map_prefix',plan['candidate'].replace('ppo-',''))
        short=plan.get('map_id_prefix','td'+plan['candidate'].rsplit('-v',1)[1])
        for split,n,seed in [('screen-large',plan['development_large_maps'],plan['development_large_seed']),('confirm',plan['gate_maps'],plan['gate_seed'])]:
            for i in range(n):
                large=split=='screen-large' or i>=n//2
                value=mapgen.seed_for(prefix+'-'+split,seed,i);value=value-value%4+i%4
                layout=mapgen.layout(value)
                if large:layout=expanded(layout,*sizes[(i//4)%len(sizes)])
                name=f'{short}-{split}-{i:03}';rel=f'generated/{prefix}-{split}/{name}'
                layout.update(name=name,output=str(ROOT/'maps'/(rel+'.map26a')))
                if Path(layout['output']).exists():raise ValueError('Map path already exists; use the saved manifest or a new cohort prefix')
                specs.append(layout);entries.append(dict(name=rel,split=split,size='large' if large else 'standard',family=i%4,seed=value,width=layout['width'],height=layout['height']))
        request=out/'map-request.json';request.write_text(json.dumps(specs),encoding='utf-8')
        r=subprocess.run([os.environ['CAMBC_NODE'],'--no-warnings',str(a.bridge.resolve()),str(a.engine_wasm.resolve()),'maps',str(request)],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=300)
        if r.returncode:raise ValueError('Official map builder failed: '+r.stderr[-2000:])
        built=json.loads(r.stdout);assert len(entries)==len(built)
        for entry,made in zip(entries,built):entry.update(sha256=made['sha256'],bytes=made['bytes'])
        current={e['sha256'] for e in entries}
        if len(current)!=len(entries) or current&old_hashes:raise ValueError('Maps overlap old cohorts or each other')
        value=dict(schema=1,config_sha256=sha(a.config),engine_wasm_sha256=sha(a.engine_wasm),bridge_sha256=sha(a.bridge),maps=entries)
        manifest.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(generated=len(entries),development=plan['development_large_maps'],confirmation=plan['gate_maps'])),flush=True);return

if __name__=='__main__':main()

