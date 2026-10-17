// Read-only reconstruction of the pinned native replay. No guest instrumentation.
import fs from 'node:fs';
import crypto from 'node:crypto';
const a = {}; for (let i=2;i<process.argv.length;i+=2) a[process.argv[i].slice(2)]=process.argv[i+1];
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
const engine=fs.readFileSync(a.engine);
if(sha(engine)!=='e123b59d9dea198762ab7a04db9b3cb6d06dfa991088e41c24750fc4cb88b947') throw Error('Unverified replay engine');
let E; const view=()=>new DataView(E.memory.buffer), bytes=(p,n)=>new Uint8Array(E.memory.buffer,p,n);
const wasi={
  environ_get:()=>0,environ_sizes_get:(p,n)=>{view().setUint32(p,0,true);view().setUint32(n,0,true);return 0;},
  fd_close:fd=>fd<=2?0:8,fd_fdstat_get:(fd,p)=>{if(fd>2)return 8;bytes(p,24).fill(0);view().setUint8(p,2);return 0;},
  fd_prestat_get:()=>8,fd_prestat_dir_name:()=>8,
  fd_read:(fd,p,n,r)=>{if(fd!==0)return 8;view().setUint32(r,0,true);return 0;},fd_seek:fd=>fd<=2?70:8,
  fd_write:(fd,p,n,r)=>{if(fd!==1&&fd!==2)return 8;let total=0;for(let i=0;i<n;i++){const q=view().getUint32(p+i*8,true),z=view().getUint32(p+i*8+4,true);process.stderr.write(Buffer.from(bytes(q,z)));total+=z;}view().setUint32(r,total,true);return 0;},
  random_get:(p,n)=>{crypto.randomFillSync(bytes(p,n));return 0;},proc_exit:c=>{throw Error('Replay engine exit '+c);}
};
E=new WebAssembly.Instance(new WebAssembly.Module(engine),{wasi_snapshot_preview1:wasi}).exports;E._initialize();
if(E.Game_Visualiser_SnapshotSize()!==184696||E.Game_Visualiser_TimelineSnapshotSize()!==40152)throw Error('Unverified native snapshot ABI');
const out=E.Engine_Malloc(64),snap=E.Engine_Malloc(40152);
const checked=(name,...args)=>{const err=E[name](...args);if(err)throw Error(name+': '+err);};
const raw=fs.readFileSync(a.replay),p=E.Engine_Malloc(raw.length);bytes(p,raw.length).set(raw);
checked('Game_FromReplayFileBytes',p,raw.length,out);const game=view().getBigUint64(out,true);E.Engine_Free(p);
const turns=[],actions=[],seenTurns=new Set(),seenActions=new Set();let previous=null,finished=false,frames=0;
try{
  checked('Game_Visualiser_Timeline_GetMain',game,out);const timeline=view().getBigUint64(out,true);checked('Game_Visualiser_Timeline_Seek',game,timeline,0,0);
  for(let seq=0;seq<500000;seq++){
    checked('Game_Visualiser_ReadTimelineState',game,snap);frames++;
    const d=view(),u=n=>d.getUint32(snap+n,true),i=n=>d.getInt32(snap+n,true),f=n=>d.getFloat32(snap+n,true);
    const w={round:u(8),phase:u(24),input:u(56),owner:u(60),kind:u(68),actorKind:u(72),actor:u(76),sub:u(104),from:[i(80),i(84)],to:[i(88),i(92)],
      champions:Array.from({length:u(172)},(_,k)=>{const q=196+k*252;return{id:u(q+4),team:u(q+8),x:i(q+16),y:i(q+20),hp:f(q+24),max_hp:f(q+28),alive:!!u(q+32)};})};
    const turnKey=w.round+'/'+w.owner;
    if(w.phase===10&&!seenTurns.has(turnKey)){const c=w.champions.find(x=>x.id===w.owner);if(c){seenTurns.add(turnKey);turns.push({round:w.round,input:w.input,...c});}}
    if(previous&&w.actorKind===1&&w.sub===0&&!seenActions.has(w.input)){
      seenActions.add(w.input);const before=previous.champions.find(x=>x.id===w.actor),after=w.champions.find(x=>x.id===w.actor);
      if(before&&after&&[4,5,6].includes(w.kind))actions.push({round:w.round,input:w.input,owner:w.actor,kind:w.kind,from:w.from,to:w.to,before,after});
    }
    previous=w;if(w.phase===11){finished=true;break;}checked('Game_Visualiser_Timeline_ReplayNext',game,1);
  }
}finally{checked('Game_Destroy',game);}
if(!finished)throw Error('Incomplete replay reconstruction');
fs.writeFileSync(a.output,JSON.stringify({scope:'Read-only actual native timeline; owner HP is not a World projection.',engine_sha256:sha(engine),raw_replay_sha256:sha(raw),frames,turns,actions})+'\n');
console.log(JSON.stringify({frames,turns:turns.length,actions:actions.length}));
