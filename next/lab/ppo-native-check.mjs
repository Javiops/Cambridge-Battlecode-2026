// Verification-only sandbox; never imported by the rollout worker.
import fs from 'node:fs';
import {OfficialEngine,Episode} from './engine.mjs';
import {encode,forward,banking} from './ppo-actor.mjs';
import {readWorld} from './critic-inventory-state.mjs';
const e=new OfficialEngine(process.argv[2]),g=new Episode(e,process.argv[3],[[0,5,11,10,3],[0,5,11,10,3]]);
try{
  const o=g.observation(),terrain=g.terrain(),before=encode(o,terrain);
  e.call('Game_Sandbox_GiveGold',g.g,3,700);
  if(JSON.stringify(encode(g.observation(),terrain))!==JSON.stringify(before))throw Error('Critic wealth leaked into actor');
  e.call('Game_Sandbox_GiveGems',g.g,o.actor.champion,80);const altar=terrain.altars[0];
  e.view.setInt32(e.out,altar[0]-1,true);e.view.setInt32(e.out+4,altar[1],true);
  e.view.setUint32(e.entity,1,true);e.view.setUint32(e.entity+4,o.actor.champion,true);e.call('Game_Sandbox_Teleport',g.g,e.entity,e.out);
  const action=banking(g.observation(),terrain,{bank_threshold:40,bank_late_round:1600});
  if(action.kind!=='submit'||!g.step(action,g.state(),false).accepted)throw Error('Banking cannot submit');
  if(banking(g.observation(),terrain,{bank_threshold:40,bank_late_round:1600}).kind!=='wait')throw Error('Controller cancels submission');
  g.finishWaiting(50000);if(g.terminal().banks[0]!==80)throw Error('Submission did not complete');
  console.log(JSON.stringify({passed:true,actor_privacy:true,native_submission_completed:true,channel_preserved:true,banks:g.terminal().banks}));
}finally{g.close();}
