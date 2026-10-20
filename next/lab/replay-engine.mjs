// Actor-scoped replay observations; all simulation and timeline reconstruction are official WASM.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {OfficialEngine,Episode} from './engine.mjs';

const emit=value=>fs.writeSync(1,JSON.stringify(value)+'\n');
const engine=new OfficialEngine(process.argv[2]);
const request=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const bytes=fs.readFileSync(request.replay);
const game=Object.create(Episode.prototype);
Object.assign(game,{e:engine,x:engine.x,closed:false,decisions:0,transitions:0,
  mapHash:crypto.createHash('sha256').update(fs.readFileSync(request.map)).digest('hex')});
game.g=engine.input(bytes,(p,n)=>{engine.call('Game_FromReplayFileBytes',p,n,engine.out);return engine.view.getBigUint64(engine.out,true)});
try{
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
  const terminal=game.terminal(); // Fails before emitting any demonstration if the replay is incomplete.
  const statistics=[];
  engine.call('Game_Statistics_GetSummary',game.g,engine.out);
  const champions=engine.view.getUint32(engine.out+12,true);
  if(champions>16)throw Error('Unsupported statistics roster');
  for(let i=0;i<champions;i++){
    engine.call('Game_Statistics_GetChampion',game.g,i,engine.out);
    const v=engine.view,p=engine.out;
    statistics.push({id:v.getUint32(p,true),team:v.getUint32(p+4,true),type:v.getUint32(p+8,true),
      kills:v.getUint32(p+12,true),deaths:v.getUint32(p+16,true),gold:Number(v.getBigUint64(p+24,true)),
      collected_gems:Number(v.getBigUint64(p+32,true)),submitted_gems:Number(v.getBigUint64(p+40,true))});
  }
  emit({type:'metadata',terminal,terrain:game.terrain(),statistics,engine_sha256:engine.sha256,inputs:count});
  engine.call('Game_Visualiser_Timeline_Seek',game.g,timeline,0,0);
  const timelineSnapshot=engine.x.Engine_Malloc(engine.x.Game_Visualiser_TimelineSnapshotSize());
  function nextInput(input){
    for(let steps=0;steps<10000;steps++){
      engine.call('Game_Visualiser_Timeline_ReplayNext',game.g,1);
      engine.call('Game_Visualiser_ReadTimelineState',game.g,timelineSnapshot);
      const v=engine.view,position=v.getUint32(timelineSnapshot+56,true),waiting=v.getUint32(timelineSnapshot+20,true),outcome=v.getUint32(timelineSnapshot+28,true);
      if(outcome || (position===input+1&&waiting))return;
      if(position>input+1)throw Error('Replay skipped an input boundary');
    }
    throw Error('Replay failed to reach the next input boundary');
  }
  let key='',decision=0,micro=0,emitted=0;
  for(let input=0;input<count&&!request.metadata_only;input++){
    if(input)nextInput(input-1);
    const action=request.actions[input];
    if(action.kind==='draft')continue;
    const actor=game.state();
    if(actor.phase!==1||actor.team>1)continue;
    const actorKey=`${actor.team}/${actor.champion}/${actor.round}`;
    if(actorKey!==key){key=actorKey;decision=0;micro=0;}
    const isMicro=['move','attack','cast','wait'].includes(action.kind);
    if(request.metadata_only)continue;
    // A deterministic cadence samples whole turns, before outcomes are inspected.
    if(actor.round<=(request.max_round??2000)&&(actor.round-1)%request.round_stride===0 && decision<request.max_actions_per_turn){
      const observation=game.observation();
      // Guest RAM and memory writes are not serialized by the official replay format.
      // They are unavailable, not zero. v1 features intentionally do not consume them.
      observation.shared_memory=null;
      observation.decisions_left=Math.max(0,2-micro);
      emit({type:'decision',input,decision_index:decision,micro_decision_index:micro,
            action,observation,memory_source:'not_recorded',micro_action:isMicro});
      emitted++;
    }
    decision++;if(isMicro)micro++;
  }
  if(count&&!request.metadata_only){
    nextInput(count-1);
    if(JSON.stringify(game.terminal())!==JSON.stringify(terminal))throw Error('Sequential replay terminal mismatch');
  }
  emit({type:'complete',records:emitted,terminal});
  engine.x.Engine_Free(timelineSnapshot);
}finally{game.close();}
