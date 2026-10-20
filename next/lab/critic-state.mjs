// Training-only centralized state. Every value is read from the current native game.
export function readWorld(game,roster) {
  const engine=game.e;
  return roster.map(({id,team})=>{
    engine.view.setUint32(engine.pov,team,true);engine.view.setUint32(engine.pov+4,id,true);
    const unit=game.champion(id,engine.pov);
    unit.gold=game.scalar('Game_API_Champion_GetGold',engine.pov,id);
    unit.gems=game.scalar('Game_API_Champion_GetGems',engine.pov,id);
    return unit;
  });
}
