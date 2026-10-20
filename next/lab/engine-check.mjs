// Verification-only privileged mutation. This module is never loaded by the training worker.
import assert from 'node:assert/strict';
import {OfficialEngine,Episode} from './engine.mjs';
const engine=new OfficialEngine(process.argv[2]);
const game=new Episode(engine,process.argv[3],[[0,5,11,10,3],[0,5,11,10,3]]);
try {
  const before=game.observation(),pov=game.perspective();
  // The opposing team's first body is hidden at the opening spawn.
  const hidden=3;
  assert(!before.champions.some(c=>c.id===hidden));
  assert.equal(engine.x.Game_API_Champion_Get(game.g,pov,hidden,engine.out),97);
  assert.equal(engine.x.Game_API_Champion_GetGold(game.g,pov,hidden,engine.out),105);
  engine.view.setUint32(engine.entity,1,true);engine.view.setUint32(engine.entity+4,before.actor.champion,true);
  engine.view.setUint32(engine.entity+16,1,true);engine.view.setUint32(engine.entity+20,hidden,true);
  engine.call('Game_Sandbox_Damage',game.g,engine.entity,engine.entity+16,1);
  assert.deepEqual(game.observation(),before);
  assert.throws(()=>game.terminal(),/Unfinished/);
  console.log(JSON.stringify({passed:true,hidden_queries_denied:true,hidden_health_mutation_invariant:true,unfinished_unlabelled:true}));
} finally {game.close();}
