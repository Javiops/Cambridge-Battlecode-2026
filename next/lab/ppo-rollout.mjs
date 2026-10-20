// Complete on-policy native games. No sandbox calls or terminal statistics during play.
import fs from 'node:fs';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
import {OfficialEngine,Episode} from './engine.mjs';
import {encode,forward,sample,banking} from './ppo-actor.mjs';
import {criticState} from './ppo-state.mjs';
import {readWorld} from './critic-inventory-state.mjs';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const request=JSON.parse(fs.readFileSync(process.argv[3],'utf8')),e=new OfficialEngine(process.argv[2]);
if(e.sha256!==request.engine_sha256||hash(request.map)!==request.map_sha256)throw Error('Wrong PPO rules/map bytes');
const load=p=>{const b=fs.readFileSync(p);if(b.length!==1220)throw Error('Wrong actor bytes');return Array.from({length:305},(_,i)=>b.readFloatLE(i*4));};
const weights=request.weights.map(load),backbone=load(request.backbone);
const rng=seed=>()=>{seed=(Math.imul(1664525,seed)+1013904223)>>>0;return (seed+.5)/4294967296;};
// Separate streams: changing critic sampling/proof capture cannot change play.
const random=[rng(request.seed),rng(request.seed^0x9e3779b9)],game=new Episode(e,request.map,request.picks);
const records=[],probes=[],counts=[{},{}],forced=[{},{}];let transitions=0,failedMoves=0;
try{
  const terrain=game.terrain();e.call('Game_GetNumChampsPerTeam',game.g,e.out);const count=e.view.getUint32(e.out,true);
  const sizes=request.picks.map(p=>count+(p.slice(0,count).includes(3)?1:0));
  const roster=Array.from({length:sizes[0]+sizes[1]},(_,id)=>({id,team:id<sizes[0]?0:1}));
  for(const u of readWorld(game,roster))if(u.team!==(u.id<sizes[0]?0:1))throw Error('Unexpected physical roster');
  while(game.state().phase!==2){
    if(transitions>=request.maximum_decisions)throw Error('PPO game truncated; no outcome admitted');
    const o=game.observation(),team=o.actor.team,input=encode(o,terrain),scores=forward(weights[team],input).scores;
    const macro=request.controller?banking(o,terrain,request.controller):null;
    const chosen=macro?{index:-1,logp:0,logits:scores.map(v=>v/request.temperature)}:sample(scores,input.mask,random[team],request.temperature);
    const action=macro??input.actions[chosen.index];
    const sampled=(o.actor.round-1+(request.seed%request.round_stride))%request.round_stride===0;
    if(sampled){
      const units=readWorld(game,roster),state=criticState(o,units,terrain,input,backbone);
      const row={features:input.features,candidates:input.candidates,mask:input.mask,state,team,actor:o.actor.champion,round:o.actor.round,
        action:chosen.index,old_logp:chosen.logp,old_logits:chosen.logits,learner:team===request.learner_team,
        policy_action:!macro&&input.mask.filter(Boolean).length>1};
      records.push(row);
      if(probes.length<64&&(records.length<9||records.length%67===0))probes.push({row:records.length-1,observation:o,units,action});
    }
    const bucket=macro?forced[team]:counts[team];bucket[action.kind]=(bucket[action.kind]??0)+1;
    const result=game.step(action,o.actor,false);transitions++;
    if(!result.accepted)throw Error('Illegal native PPO action '+JSON.stringify({actor:o.actor,action,code:result.error_code}));
    if(action.kind==='move'&&!result.result)failedMoves++;
  }
  const terminal=game.terminal();
  if(!records.length||new Set(records.map(r=>r.team)).size!==2)throw Error('Missing rollout perspectives');
  e.call('Game_SaveReplay',game.g);e.call('Game_FileBuffer',game.g,e.out,e.out+4);
  const replay=Buffer.from(new Uint8Array(e.x.memory.buffer,e.view.getUint32(e.out,true),e.view.getUint32(e.out+4,true)));
  fs.mkdirSync(request.output,{recursive:true});fs.writeFileSync(request.output+'/game.repl26a',replay);
  fs.writeFileSync(request.output+'/frames.jsonl.gz',zlib.gzipSync(records.map(r=>JSON.stringify(r)).join('\n')+'\n'));
  fs.writeFileSync(request.output+'/probes.json.gz',zlib.gzipSync(JSON.stringify({terrain,probes})));
  const report={completed:true,terminal,engine_sha256:e.sha256,map_sha256:request.map_sha256,actor_sha256:request.weights.map(hash),
    backbone_sha256:hash(request.backbone),seed:request.seed,learner_team:request.learner_team,temperature:request.temperature,
    round_stride:request.round_stride,rows:records.length,transitions,model_actions:counts,controller_actions:forced,
    rejected_actions:0,failed_moves:failedMoves,physical_roster:roster,
    replay_sha256:hash(request.output+'/game.repl26a'),frames_sha256:hash(request.output+'/frames.jsonl.gz'),probes_sha256:hash(request.output+'/probes.json.gz')};
  fs.writeFileSync(request.output+'/native.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
}finally{game.close();}
