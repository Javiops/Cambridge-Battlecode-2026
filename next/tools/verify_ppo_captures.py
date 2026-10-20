"""Run the frozen PPO auditor with each immutable NPZ materialized once.

Usage from next/: python tools/verify_ppo_captures.py [--watch]
This changes array I/O only. The frozen lab.ppo.audit_episode performs every
native terminal, source, actor probability, value, and feature comparison.
"""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import hashlib
from pathlib import Path
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from lab import ppo,core


class Arrays(dict):
    @property
    def files(self):return list(self)
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def close(self):pass


@contextmanager
def materialized_reads():
    original=np.load
    def load(*args,**kwargs):
        archive=original(*args,**kwargs)
        if not hasattr(archive,'files'):return archive
        try:return Arrays({name:archive[name] for name in archive.files})
        finally:archive.close()
    np.load=load
    try:yield
    finally:np.load=original


@contextmanager
def fixed_audit_inputs():
    """Read verified immutable configuration/parent arrays once, then recheck.

    The numerical audit is read-only. Repeated TOML parsing and parent archive
    opening inside every probe do not add evidence about the same frozen bytes.
    """
    original_config=core.config;original_parents=ppo.parents
    configuration=original_config();parent=original_parents();config_sha=core.sha(core.ROOT/'lab.toml')
    core.config=lambda:configuration;ppo.parents=lambda:parent
    try:yield
    finally:
        core.config=original_config;ppo.parents=original_parents
        if core.sha(core.ROOT/'lab.toml')!=config_sha:raise ValueError('Configuration changed during audit')
        original_parents()


def run(watch=False):
    ppo.plan();source=ppo.source_hashes();cache=core.ROOT/'.cambc/ppo-audit-cache';cache.mkdir(parents=True,exist_ok=True)
    for i in range(ppo.cfg()['iterations']+1):
        if (ppo.checkpoint(i)/'checkpoint.json').exists():ppo.load_checkpoint(i)
    manifests=[ppo.root()/'warmup.json']+[ppo.root()/f'train-{i:03d}.json' for i in range(1,ppo.cfg()['iterations']+1)]+[ppo.root()/'evaluation.json']
    def one(e):
        dest=(ppo.root()/e['path']).parent
        expected={'rollout.npz':e['sha256'],'game.repl26a':e['native']['replay_sha256'],
            'frames.jsonl.gz':e['native']['frames_sha256'],'probes.json.gz':e['native']['probes_sha256']}
        for name,digest in expected.items():
            if core.sha(dest/name)!=digest:raise ValueError('Cached audit input changed')
        identity=ppo.digest(e);p=cache/(identity+'.json')
        if p.exists():
            old=ppo.read(p)
            if old['sources']==source and old['identity']==identity:return old['report']
        report=ppo.audit_episode(e)
        ppo.save(p,dict(identity=identity,sources=source,report=report));return report
    seen={}
    with materialized_reads(),fixed_audit_inputs():
        while True:
            if ppo.source_hashes()!=source:raise ValueError('PPO sources changed during audit')
            if not watch and any(not p.exists() for p in manifests):raise ValueError('Finish training/evaluation, or pass --watch')
            available=[e for p in manifests if p.exists() for e in ppo.read(p)['episodes']]
            with ThreadPoolExecutor(ppo.cfg()['jobs']) as pool:
                for report in pool.map(one,[e for e in available if e['episode_id'] not in seen]):
                    seen[report['episode']]=report;print(f'Audited {len(seen)} complete PPO games',flush=True)
            if all(p.exists() for p in manifests):break
            time.sleep(10)
    reports=[seen[e['episode_id']] for p in manifests for e in ppo.read(p)['episodes']]
    result=dict(passed=True,games=len(reports),states=sum(r['rows'] for r in reports),native_probes=sum(r['probes'] for r in reports),
        old_logp_max_error=max(r['old_logp_max_error'] for r in reports),critic_feature_max_error=max(r['critic_feature_max_error'] for r in reports),
        manifest_sha256={p.name:core.sha(p) for p in manifests},sources=source,all_native_terminals_checked=True,
        audit_driver_sha256=hashlib.sha256(Path(__file__).read_text(encoding='utf-8').encode()).hexdigest(),
        array_io='identical immutable arrays, materialized once per NPZ context')
    ppo.save(core.ROOT/'results/stage5-audit.json',result);return result


if __name__=='__main__':
    import json
    print(json.dumps(run('--watch' in sys.argv),indent=2))
