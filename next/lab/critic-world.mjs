// Critic-only current state. No team statistics are read after seeking to the future.
// Final replay inspection supplies only completion and immutable roster identity.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {OfficialEngine,Episode} from './engine.mjs';
import {readWorld} from './critic-state.mjs';

const emit=value=>fs.writeSync(1,JSON.stringify(value)+'\n');
const engine=new OfficialEngine(process.argv[2]);
const request=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const bytes=fs.readFileSync(request.replay);
const game=Object.create(Episode.prototype);
Object.assign(game,{e:engine,x:engine.x,closed:false,decisions:0,transitions:0,
  mapHash:crypto.createHash('sha256').update(fs.readFileSync(request.map)).digest('hex')});
game.g=engine.input(bytes,(p,n)=>{engine.call('Game_FromReplayFileBytes',p,n,engine.out);return engine.view.getBigUint64(engine.out,true)});
try {
  engine.call('Game_GetBitboardMetadata',game.g,engine.out);
  game.width=engine.view.getUint32(engine.out,true);game.height=engine.view.getUint32(engine.out+4,true);
  game.capacity=game.width*game.height;game.points=engine.x.Engine_Malloc(game.capacity*8);
  engine.call('Managed_Bitboard_Create',game.width,game.height,engine.out);game.board=engine.view.getBigUint64(engine.out,true);
  engine.call('Managed_Bitboard_GetBuffer',game.board,engine.out);game.raw=engine.view.getUint32(engine.out,true);
  engine.call('Game_Visualiser_Timeline_GetMain',game.g,engine.out);const timeline=engine.view.getBigUint64(engine.out,true);
  engine.call('Game_Visualiser_Timeline_Info',game.g,timeline,engine.out,engine.out+8,engine.out+16);
  const count=engine.view.getUint32(engine.out,true);
  if(count!==request.actions.length)throw Error('Decoded input count differs from official timeline');
  engine.call('Game_Visualiser_Timeline_Seek',game.g,timeline,count,0);
  const terminal=game.terminal();
  engine.call('Game_Statistics_GetSummary',game.g,engine.out);
  const champions=engine.view.getUint32(engine.out+12,true),roster=[];
  if(champions>16)throw Error('Unsupported roster');
  for(let i=0;i<champions;i++){
    engine.call('Game_Statistics_GetChampion',game.g,i,engine.out);
    roster.push({id:engine.view.getUint32(engine.out,true),team:engine.view.getUint32(engine.out+4,true)});
  }
  const terrain=game.terrain();
  emit({type:'metadata',terminal,terrain,roster,engine_sha256:engine.sha256,inputs:count});
  engine.call('Game_Visualiser_Timeline_Seek',game.g,timeline,0,0);
  const snap=engine.x.Engine_Malloc(engine.x.Game_Visualiser_TimelineSnapshotSize());
  function nextInput(input){
    for(let steps=0;steps<10000;steps++){
      engine.call('Game_Visualiser_Timeline_ReplayNext',game.g,1);
      engine.call('Game_Visualiser_ReadTimelineState',game.g,snap);
      const v=engine.view,position=v.getUint32(snap+56,true),waiting=v.getUint32(snap+20,true),outcome=v.getUint32(snap+28,true);
      if(outcome || (position===input+1&&waiting))return;
      if(position>input+1)throw Error('Replay skipped an input boundary');
    }
    throw Error('Replay failed to reach the next input boundary');
  }
  let key='',emitted=0;
  for(let input=0;input<count;input++){
    if(input)nextInput(input-1);
    if(request.actions[input].kind==='draft')continue;
    const actor=game.state();
    if(actor.phase!==1||actor.team>1)continue;
    const actorKey=`${actor.team}/${actor.champion}/${actor.round}`;
    const first=actorKey!==key;key=actorKey;
    if(!first||(actor.round-1)%request.round_stride!==0||actor.round>(request.max_round??2000))continue;
    const observation=game.observation();observation.shared_memory=null;
    const units=readWorld(game,roster),self=units.find(u=>u.id===actor.champion&&u.team===actor.team);
    for(const field of ['x','y','health','max_health','strength','focus','gold','gems','state'])
      if(self[field]!==observation.self[field])throw Error('Central snapshot differs from authenticated actor: '+field);
    emit({type:'decision',input,actor,observation,units});emitted++;
  }
  if(count){nextInput(count-1);if(JSON.stringify(game.terminal())!==JSON.stringify(terminal))throw Error('Sequential replay terminal mismatch');}
  emit({type:'complete',records:emitted,terminal});engine.x.Engine_Free(snap);
}finally{game.close();}
