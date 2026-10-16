// Optional regeneration of the committed controlled map. No accounts/network.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {WASI} from 'node:wasi';

if (!process.argv[2]) throw Error('Usage: node generate_native_cycle_map.mjs OFFICIAL_ENGINE_WASM [OUTPUT_DIRECTORY]');
const enginePath=path.resolve(process.argv[2]);
const root=process.argv[3]?path.resolve(process.argv[3]):path.join(path.dirname(fileURLToPath(import.meta.url)),'fixtures');
const bytes=fs.readFileSync(enginePath);
const engineHash=crypto.createHash('sha256').update(bytes).digest('hex');
assert.equal(engineHash,'e123b59d9dea198762ab7a04db9b3cb6d06dfa991088e41c24750fc4cb88b947','Unreviewed engine');
const wasi=new WASI({version:'preview1',args:[],env:{},preopens:{}});
const {instance}=await WebAssembly.instantiate(bytes,{wasi_snapshot_preview1:wasi.wasiImport});
wasi.initialize(instance);
const E=instance.exports,out=E.Engine_Malloc(64),scratch=E.Engine_Malloc(256);
const v=()=>new DataView(E.memory.buffer);
function errorString(pointer){const b=new Uint8Array(E.memory.buffer);let end=pointer;while(b[end])end++;return new TextDecoder().decode(b.subarray(pointer,end));}
function checked(name,...args){const code=E[name](...args);if(code)throw Error(name+': '+code+' '+errorString(E.GetLastErrorMsg()));}
checked('MapBuilder_Create',32,32,0,out);const map=v().getBigUint64(out,true);
checked('MapBuilder_SetNumChampsPerTeam',map,1);
[1,1,4,4].forEach((n,k)=>v().setInt32(scratch+4*k,n,true));checked('MapBuilder_SetTeamASpawnArea',map,scratch);
checked('MapBuilder_AddAltar',map,8,7);checked('MapBuilder_AddCamp',map,0,7,7,out);
checked('MapBuilder_VerifyIntegrity',map);checked('MapBuilder_Encode',map,out,out+4);
const p=v().getUint32(out,true),n=v().getUint32(out+4,true),encoded=Buffer.from(new Uint8Array(E.memory.buffer,p,n));
checked('Game_FromMapFileBytes',p,n,out,0);checked('Game_Destroy',v().getBigUint64(out,true));checked('MapBuilder_Destroy',map);
fs.mkdirSync(root,{recursive:true});
fs.writeFileSync(path.join(root,'native-cycle.map26a'),encoded);
fs.writeFileSync(path.join(root,'native-cycle-map.json'),JSON.stringify({
 scope:'Scripted actual SDK/native capture-recall and bank-completion regression; no strength claim.',
 engine_sha256:engineHash,map_sha256:crypto.createHash('sha256').update(encoded).digest('hex')},null,2)+'\n');
