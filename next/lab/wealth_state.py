"""Native current-inventory features. Net worth is a proxy, not terminal earned gold."""
from __future__ import annotations
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from threading import Timer
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from . import core,critic,central_critic as central,dataset,mapgen,replay

FEATURES=74
def root():return core.ROOT/'datasets'/core.config()['stage4']['dataset']


def make_state(o,units,terrain,backbone):
    base=central.make_state(o,units,terrain,backbone);totals=[]
    for side in (0,1):
        selected=[u for u in units if u['team']==side];assets=0;cash=0
        if not selected:raise ValueError('Missing wealth perspective')
        for u in selected:
            items=np.asarray(u['items'])
            if items.shape!=(42,) or not np.isfinite(items).all() or np.any(items<0) or not np.equal(items,np.floor(items)).all():raise ValueError('Invalid native inventory')
            assets+=float(items@np.asarray([30,150]*21));cash+=u['gold']
        totals.append(np.array([assets,assets+cash])/5000.)
    team=o['actor']['team'];margin=totals[team]-totals[1-team];elapsed=o['actor']['round']/2000
    return np.r_[base,margin,margin*elapsed,np.sign(margin)*np.log1p(np.abs(margin))].astype(np.float32)


def native_check():
    r=subprocess.run([mapgen.node(),'--no-warnings',str(core.ROOT/'lab/critic-inventory-check.mjs'),str(mapgen.engine_path()),str(core.map_path('00collision'))],
        capture_output=True,text=True,encoding='utf-8',cwd=core.ROOT,timeout=30)
    if r.returncode:raise ValueError(r.stderr[-2000:])
    return central.save('stage4-v5-native-proof.json',json.loads(r.stdout)|dict(engine_sha256=core.sha(mapgen.engine_path())))


def prepare():
    native_check();cfg=core.config()['stage4'];source=core.ROOT/'datasets'/cfg['inventory_source_dataset']
    manifest=json.loads((source/'training-manifest.json').read_text());episodes=[]
    def convert(e):return extract(e|dict(status='admitted'),core.ROOT/e['source_dir'])
    with ThreadPoolExecutor(cfg['jobs']) as pool:
        for e in pool.map(convert,manifest['episodes']):
            episodes.append(e);print(f"Inventory extraction {len(episodes)}/{len(manifest['episodes'])}",flush=True)
    value=dict(episodes=episodes,source_manifest_sha256=core.sha(source/'training-manifest.json'),
        rows=sum(e['rows'] for e in episodes),current_native_inventory=True)
    dataset.immutable(root()/'training-manifest.json',value)
    central.save('stage4-v5-dataset.json',value)
    return dict(games=len(episodes),rows=value['rows'])


def extract(e,source):
    if e['status']!='admitted':raise ValueError('Unsafe wealth training source')
    dest=root()/'episodes'/e['episode_id'];dest.mkdir(parents=True,exist_ok=True);meta=dest/'episode.json'
    if meta.exists():
        old=json.loads(meta.read_text())
        if old['extractor_sha256']!=central.normalized_sha(core.ROOT/'lab/critic-inventory.mjs') or old['reader_sha256']!=central.normalized_sha(core.ROOT/'lab/critic-inventory-state.mjs'):raise ValueError('Wealth reader changed')
        if core.sha(dest/'critic.npz')!=old['sha256'] or core.sha(dest/'states.jsonl.gz')!=old['states_sha256']:raise ValueError('Wealth cache changed')
        return old
    blob=dataset.raw_bytes(max(source.glob('*.repl26a'),key=lambda p:p.stat().st_mtime));actions=replay.decode(blob,core.map_path(e['map']).read_bytes())
    fields={k:[] for k in ('state','win','team','round','actor','input')};backbone=critic.parent();complete=False
    with tempfile.TemporaryDirectory(dir=dest) as tmp:
        tmp=Path(tmp);(tmp/'raw.repl26a').write_bytes(blob)
        request=dict(replay=str(tmp/'raw.repl26a'),map=str(core.map_path(e['map'])),actions=actions,round_stride=core.config()['stage4']['world_round_stride'])
        (tmp/'request.json').write_text(json.dumps(request))
        with (tmp/'error.txt').open('w',encoding='utf-8') as error,gzip.open(tmp/'states.jsonl.gz','wt',encoding='utf-8') as output:
            p=subprocess.Popen([mapgen.node(),'--no-warnings',str(core.ROOT/'lab/critic-inventory.mjs'),str(mapgen.engine_path()),str(tmp/'request.json')],
                cwd=core.ROOT,env=core.ENV,stdout=subprocess.PIPE,stderr=error,text=True,encoding='utf-8')
            timer=Timer(core.TIMEOUT,p.kill);timer.start()
            try:
                for line in p.stdout:
                    row=json.loads(line);output.write(line)
                    if row['type']=='metadata':
                        metadata=row
                        if row['terminal']!=e['terminal'] or row['engine_sha256']!=core.config()['stage1']['engine_wasm_sha256']:raise ValueError('Wealth native provenance mismatch')
                    elif row['type']=='decision':
                        o=row['observation'];a=o['actor'];state=make_state(o,row['units'],metadata['terrain'],backbone)
                        values=dict(state=state,win=(critic.terminal_value(metadata['terminal'],a['team'])+1)/2,team=a['team'],round=a['round'],actor=a['champion'],input=row['input'])
                        for k,v in values.items():fields[k].append(v)
                    elif row['type']=='complete':complete=True
                code=p.wait(timeout=30)
            except BaseException:p.kill();p.wait();raise
            finally:timer.cancel();p.stdout.close()
        if code or not complete:raise ValueError('Wealth extraction failed: '+(tmp/'error.txt').read_text()[-2000:])
        if set(fields['team'])!={0,1}:raise ValueError('Incomplete wealth perspectives')
        np.savez_compressed(tmp/'critic.npz',**{k:np.asarray(v,np.float32 if k=='state' else np.uint8 if k in ('win','team') else np.uint32) for k,v in fields.items()})
        shutil.copyfile(tmp/'critic.npz',dest/'critic.npz');shutil.copyfile(tmp/'states.jsonl.gz',dest/'states.jsonl.gz')
    result=dict(episode_id=e['episode_id'],split=e['split'],map=e['map'],family=e['family'],map_sha256=e['map_sha256'],lineages=e['lineages'],runtime=e['runtime'],terminal=e['terminal'],
        rows=len(fields['win']),path=(dest/'critic.npz').relative_to(root()).as_posix(),sha256=core.sha(dest/'critic.npz'),states_sha256=core.sha(dest/'states.jsonl.gz'),
        source_dir=source.relative_to(core.ROOT).as_posix(),source_replay_sha256=hashlib.sha256(blob).hexdigest(),
        extractor_sha256=central.normalized_sha(core.ROOT/'lab/critic-inventory.mjs'),reader_sha256=central.normalized_sha(core.ROOT/'lab/critic-inventory-state.mjs'))
    dataset.immutable(meta,result);return result
