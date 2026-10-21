// Standalone, strictly pinned native reconstruction for official 1.0.2 replays.
// Historical Stage 1-7 decoders and their pins remain unchanged.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {WASI} from 'node:wasi';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const engineBytes=fs.readFileSync(process.argv[2]);
if(sha(engineBytes)!=='742919b4454b427912eece99e5675752791fe5d83167b2fee1766c908e9cccee')throw Error('Wrong 1.0.2 engine bytes');
const request=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const bytes=fs.readFileSync(request.replay),map=fs.readFileSync(request.map);
if(bytes.subarray(0,8).toString('hex')!=='6136327065720000'||bytes.readUInt32LE(8)!==131073||!bytes.subarray(14,14+map.length).equals(map))throw Error('Wrong replay format or embedded map');
const wasi=new WASI({version:'preview1',args:[],env:{},preopens:{}});
const instance=new WebAssembly.Instance(new WebAssembly.Module(engineBytes),wasi.getImportObject());wasi.initialize(instance);
const x=instance.exports;if(x.Version()!==131073n)throw Error('Wrong engine version export');
const out=x.Engine_Malloc(4096),pov=x.Engine_Malloc(8);
const view=()=>new DataView(x.memory.buffer);
const call=(name,...args)=>{const code=x[name](...args);if(code!==0)throw Error(name+': official engine error '+code);};
let game;
try{
 const p=x.Engine_Malloc(bytes.length);
 try{new Uint8Array(x.memory.buffer,p,bytes.length).set(bytes);call('Game_FromReplayFileBytes',p,bytes.length,out);game=view().getBigUint64(out,true);}finally{x.Engine_Free(p);}
 call('Game_Visualiser_Timeline_GetMain',game,out);const timeline=view().getBigUint64(out,true);
 call('Game_Visualiser_Timeline_Info',game,timeline,out,out+8,out+16);const count=view().getUint32(out,true);
 call('Game_Visualiser_Timeline_Seek',game,timeline,count,0);
 call('Game_Runner_GetState',game,out);if(view().getUint32(out,true)!==2)throw Error('Replay has no terminal outcome');
 const n=x.Game_Visualiser_SnapshotSize(),snapshot=x.Engine_Malloc(n);let terminal;
 try{
  view().setUint32(pov,2,true);view().setUint32(pov+4,0xffffffff,true);
  call('Game_Visualiser_ReadState',game,pov,snapshot);const v=view(),outcome=v.getUint32(snapshot+28,true);
  if(![1,2].includes(outcome))throw Error('No completed team outcome');
  terminal={outcome:outcome===1?'teamA':'teamB',round:v.getUint32(snapshot+8,true),banks:[Number(v.getBigUint64(snapshot+32,true)),Number(v.getBigUint64(snapshot+40,true))]};
 }finally{x.Engine_Free(snapshot);}
 call('Game_Statistics_GetSummary',game,out);const num=view().getUint32(out+12,true),statistics=[];
 if(num>16)throw Error('Unsupported physical roster');
 for(let i=0;i<num;i++){
  call('Game_Statistics_GetChampion',game,i,out);const v=view();statistics.push({id:v.getUint32(out,true),team:v.getUint32(out+4,true),type:v.getUint32(out+8,true),kills:v.getUint32(out+12,true),deaths:v.getUint32(out+16,true),gold:Number(v.getBigUint64(out+24,true)),collected_gems:Number(v.getBigUint64(out+32,true)),submitted_gems:Number(v.getBigUint64(out+40,true))});
 }
 console.log(JSON.stringify({type:'metadata',terminal,statistics,inputs:count,engine_sha256:sha(engineBytes),replay_format:131073}));
 console.log(JSON.stringify({type:'complete',terminal}));
}finally{if(game!==undefined)call('Game_Destroy',game);x.Engine_Free(out);x.Engine_Free(pov);}
