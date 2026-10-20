// Actor-scoped replay observations; all simulation and timeline reconstruction are official WASM.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {encode,forward,sample,banking} from './ppo-actor.mjs';
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
  const terrain=game.terrain(),wb=fs.readFileSync(request.weights),weights=Array.from({length:305},(_,i)=>wb.readFloatLE(i*4));
  if(wb.length!==1220)throw Error('Wrong model size');
  let seed=2166136261;const mix=v=>seed=Math.imul(seed^v,16777619)>>>0;
  mix(game.width);mix(game.height);
  ['walls','holes','altars'].forEach((kind,i)=>{
    mix(i+1);const packed=new Uint8Array(Math.ceil(game.width*game.height/8));
    for(const [x,y] of terrain[kind]){const k=y*game.width+x;packed[Math.floor(k/8)]|=1<<(k%8);}
    for(const byte of packed)mix(byte);
  });
  let state=(seed^(request.seat?0x9e3779b9:0))>>>0;
  const random=()=>{state=(Math.imul(1664525,state)+1013904223)>>>0;return (state+.5)/4294967296;};
  const canonical=a=>Object.fromEntries(Object.entries(a).filter(([k])=>k!=='reason').sort(([a],[b])=>a.localeCompare(b)));
  const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
  const kinds={},types=new Set(),seen=new Set(),turns=new Set();let probes=0,logits=0,featureError=0,policy=0,macros=0,channels=0,drafts=0;
  engine.call('Game_Visualiser_Timeline_Seek',game.g,timeline,0,0);
  const timelineSnapshot=engine.x.Engine_Malloc(engine.x.Game_Visualiser_TimelineSnapshotSize());
  function nextInput(input){
    for(let steps=0;steps<10000;steps++){
      engine.call('Game_Visualiser_Timeline_ReplayNext',game.g,1);
      engine.call('Game_Visualiser_ReadTimelineState',game.g,timelineSnapshot);
      const v=engine.view,position=v.getUint32(timelineSnapshot+56,true),waiting=v.getUint32(timelineSnapshot+20,true),outcome=v.getUint32(timelineSnapshot+28,true);
      if(outcome||(position===input+1&&waiting))return;
      if(position>input+1)throw Error('Replay skipped input');
    }
    throw Error('Replay input timeout');
  }
  let previous='',decision=0;
  for(let i=0;i<count;i++){
    if(i)nextInput(i-1);
    const actual=request.actions[i];
    if(actual.kind==='draft'){
      if(game.state().team===request.seat){
        const expected=request.picks[drafts++];
        // Explicit user draft choices carry the official 255 (no forced reason) tag.
        if(actual.reason!==255||actual.pick!==expected)throw Error('Deployment draft differs from training '+JSON.stringify({actual,expected,drafts,state:game.state()}));
      }
      continue;
    }
    const actor=game.state();if(actor.phase!==1||actor.team!==request.seat)continue;
    const turn=`${actor.round}/${actor.champion}`;if(turn!==previous){previous=turn;decision=0;}
    const key=`${turn}/${decision}`,trace=request.traces[key],footer=request.footers[turn];
    if(!trace){
      if(!footer||decision!==2||footer.count!==2||actual.kind!=='wait'||actual.reason!==0)throw Error('Missing deployed command '+key);
      decision++;continue;
    }
    if(actual.reason)throw Error('Faulted SDK input '+key);
    const o=game.observation(),input=encode(o,terrain),macro=banking(o,terrain,request.controller);let action,pick=-1;
    types.add(o.self.type);if(o.self.state&(2|4|4096))channels++;
    if(macro){macros++;action=macro;if(trace.before||trace.after)throw Error('Controller consumed random state '+key);}
    else {
      const scores=forward(weights,input).scores,before=state;pick=sample(scores,input.mask,random,1).index;
      if(trace.before!==before||trace.after!==state)throw Error('Shared RNG parity '+key);
      action=input.actions[pick];policy++;
      if(trace.features){
        probes++;for(const field of ['features','candidates']){
          const x=input[field].flat(),y=trace[field].flat();
          if(x.length!==y.length)throw Error('Feature shape');
          x.forEach((v,j)=>featureError=Math.max(featureError,Math.abs(v-y[j])));
        }
        if(featureError>0.000002||!same(input.mask,trace.mask))throw Error('SDK observation parity '+key+' error '+featureError);
        if(!same(scores,trace.scores))throw Error('Nonidentical float32 logits '+key);
        logits+=scores.length;
      }
    }
    const kind={wait:0,move:1,attack:2,cast:3,submit:4}[action.kind];
    if(pick!==trace.pick||kind!==trace.kind)throw Error('Controller/sample parity '+key+' '+JSON.stringify({action,trace}));
    if(!same(canonical(actual),canonical(action)))throw Error('SDK/native action parity '+key+' '+JSON.stringify({actual,expected:action,macro,trace,self:o.self,moves:o.moves,camps:o.camps,champions:o.champions}));
    if((kind===1||kind===4)&&(trace.a!==action.x||trace.b!==action.y))throw Error('Command position parity '+key);
    if(kind===2&&(trace.a!==action.target.kind||trace.b!==action.target.id))throw Error('Command target parity '+key);
    if(kind===3&&trace.a!==action.slot)throw Error('Command ability parity '+key);
    seen.add(key);turns.add(turn);kinds[action.kind]=(kinds[action.kind]??0)+1;decision++;
  }
  nextInput(count-1);if(!same(game.terminal(),terminal))throw Error('Sequential terminal mismatch');
  if(seen.size!==Object.keys(request.traces).length||turns.size!==Object.keys(request.footers).length)throw Error('Incomplete decision/turn coverage');
  if(!probes||!policy||!macros)throw Error('Missing runtime paths');
  emit({passed:true,terminal,turns:turns.size,decisions:seen.size,policy_decisions:policy,controller_decisions:macros,
    probes,bit_identical_logits:logits,feature_max_error:featureError,actions:kinds,actor_types:[...types].sort((a,b)=>a-b),
    preserved_channel_decisions:channels,draft_picks:drafts,map_seed:seed,final_rng:state,engine_sha256:engine.sha256});
  engine.x.Engine_Free(timelineSnapshot);
}finally{game.close();}
