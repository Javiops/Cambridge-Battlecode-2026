// Audit only: use the saved replay's terminal state as an outcome authority.
import fs from 'node:fs';
import {OfficialEngine,Episode} from './engine.mjs';
const e=new OfficialEngine(process.argv[2]),request=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const bytes=fs.readFileSync(request.replay),g=Object.create(Episode.prototype);
Object.assign(g,{e,x:e.x,closed:false});
g.g=e.input(bytes,(p,n)=>{e.call('Game_FromReplayFileBytes',p,n,e.out);return e.view.getBigUint64(e.out,true);});
try{
  e.call('Game_Visualiser_Timeline_GetMain',g.g,e.out);const timeline=e.view.getBigUint64(e.out,true);
  e.call('Game_Visualiser_Timeline_Info',g.g,timeline,e.out,e.out+8,e.out+16);const count=e.view.getUint32(e.out,true);
  e.call('Game_Visualiser_Timeline_Seek',g.g,timeline,count,0);
  console.log(JSON.stringify({terminal:g.terminal(),inputs:count,engine_sha256:e.sha256}));
}finally{g.close();}
