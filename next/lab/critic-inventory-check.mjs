import {OfficialEngine,Episode} from './engine.mjs';
import {readWorld} from './critic-inventory-state.mjs';
const e=new OfficialEngine(process.argv[2]),g=new Episode(e,process.argv[3],[[0,1,2],[0,1,2]]);
const roster=Array.from({length:6},(_,id)=>({id,team:id<3?0:1}));
const assets=u=>u.items.reduce((sum,n,i)=>sum+n*(i%2?150:30),0);
try{
  const before=g.observation(),world0=readWorld(g,roster);
  if(world0.some(u=>u.gold||u.gems||assets(u)))throw Error('Initial wealth is not zero');
  e.call('Game_Sandbox_GiveGold',g.g,3,700);
  if(JSON.stringify(g.observation())!==JSON.stringify(before))throw Error('Enemy wealth leaked into actor');
  e.call('Game_Sandbox_GiveGold',g.g,before.actor.champion,500);
  const beforeBuy=readWorld(g,roster).find(u=>u.id===before.actor.champion);
  e.call('Game_Action_BuyItem',g.g,0,5);
  const afterBuy=readWorld(g,roster).find(u=>u.id===before.actor.champion);
  if(afterBuy.items[0]!==0||afterBuy.items[1]!==1||afterBuy.gold!==350||assets(afterBuy)!==150)throw Error('Native shard/emblem accounting differs');
  if(beforeBuy.gold+assets(beforeBuy)!==afterBuy.gold+assets(afterBuy))throw Error('Purchasing faked an income change');
  if(world0.some(u=>assets(u)||u.gold))throw Error('Past wealth snapshot changed');
  console.log(JSON.stringify({passed:true,current_native_inventory:true,initial_wealth_zero:true,shard_emblem_fusion_verified:true,
    purchasing_preserves_wealth:true,hidden_enemy_gold_does_not_change_actor:true,past_snapshot_unchanged:true}));
}finally{g.close();}
