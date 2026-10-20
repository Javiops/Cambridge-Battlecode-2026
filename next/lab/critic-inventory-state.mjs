import {readWorld as readCurrentUnits} from './critic-state.mjs';
// SDK 3.0.1 enum_map<item_type>: 42 uint32 counts, alternating shard/emblem.
export function readWorld(game,roster) {
  const units=readCurrentUnits(game,roster),e=game.e;
  for(const u of units){
    e.view.setUint32(e.pov,u.team,true);e.view.setUint32(e.pov+4,u.id,true);
    e.call('Game_API_Champion_GetItems',game.g,e.pov,u.id,e.out,42);
    u.items=Array.from({length:42},(_,i)=>e.view.getUint32(e.out+4*i,true));
  }
  return units;
}
