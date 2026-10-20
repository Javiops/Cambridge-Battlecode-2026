import {OfficialEngine,Episode} from './engine.mjs';
import {readWorld} from './critic-state.mjs';
const e=new OfficialEngine(process.argv[2]),g=new Episode(e,process.argv[3],[[0,1,2],[0,1,2]]);
try {
  // Controlled 00collision fixture: three picks per side, no linked extra bodies.
  const count=6,roster=Array.from({length:count},(_,id)=>({id,team:id<3?0:1}));
  const before=g.observation(),world0=readWorld(g,roster);
  if(world0.some(u=>u.gold!==0||u.gems!==0))throw Error('Initial inventories are not zero');
  const enemy=roster.find(u=>u.team!==before.actor.team);
  e.call('Game_Sandbox_GiveGold',g.g,enemy.id,700);
  const world1=readWorld(g,roster),after=g.observation();
  if(world1.find(u=>u.id===enemy.id).gold!==700)throw Error('Central gold query is not current');
  if(JSON.stringify(before)!==JSON.stringify(after))throw Error('Privileged enemy wealth leaked into actor observation');
  e.call('Game_Sandbox_GiveGold',g.g,before.actor.champion,500);
  const current=g.observation(),world2=readWorld(g,roster);
  if(current.self.gold!==500||world2.find(u=>u.id===before.actor.champion).gold!==500)throw Error('Current actor inventory mismatch');
  if(world0.some(u=>u.gold!==0))throw Error('Previously recorded state changed with future actions');
  console.log(JSON.stringify({passed:true,roster:count,initial_inventories_zero:true,current_inventory_changes_verified:true,
    hidden_enemy_gold_does_not_change_actor:true,past_snapshot_unchanged:true,source:'live official native state; no terminal-statistic feature queries'}));
}finally{g.close();}
