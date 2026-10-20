// Thin bridge to the pinned official engine. Game rules and map encoding stay in vendor WASM.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {WASI} from 'node:wasi';
import {pathToFileURL} from 'node:url';
import readline from 'node:readline';

export class OfficialEngine {
  constructor(file) {
    if (Number(process.versions.node.split('.')[0]) < 22) throw Error('Node.js 22+ required');
    const bytes = fs.readFileSync(file);
    this.sha256 = crypto.createHash('sha256').update(bytes).digest('hex');
    const wasi = new WASI({version: 'preview1', args: [], env: {}, preopens: {}});
    const instance = new WebAssembly.Instance(new WebAssembly.Module(bytes), wasi.getImportObject());
    wasi.initialize(instance);
    this.x = instance.exports;
    this.out = this.x.Engine_Malloc(4096);
    this.pov = this.x.Engine_Malloc(8);
    this.entity = this.x.Engine_Malloc(8);
    if (this.x.Version() !== 1n) throw Error('Unexpected official engine ABI version');
  }
  get view() { return new DataView(this.x.memory.buffer); }
  check(code, operation) { if (code !== 0) throw Error(`${operation}: official engine error ${code}`); }
  call(name, ...args) { this.check(this.x[name](...args), name); }
  input(bytes, fn) {
    const p = this.x.Engine_Malloc(bytes.length);
    try { new Uint8Array(this.x.memory.buffer, p, bytes.length).set(bytes); return fn(p, bytes.length); }
    finally { this.x.Engine_Free(p); }
  }
  load(bytes) {
    return this.input(bytes, (p, n) => {
      this.call('Game_FromMapFileBytes', p, n, this.out, 0);
      return this.view.getBigUint64(this.out, true);
    });
  }
  encode(m) {
    this.call('MapBuilder_Create', m.width, m.height, 2, this.out);
    const handle = this.view.getBigUint64(this.out, true);
    try {
      m.spawn.forEach((v, i) => this.view.setInt32(this.out + i * 4, v, true));
      this.call('MapBuilder_SetTeamASpawnArea', handle, this.out);
      this.call('MapBuilder_SetNumChampsPerTeam', handle, m.champions);
      for (const [key, kind] of [['walls','Wall'],['holes','Hole'],['bushes','Bush'],['altars','Altar']]) {
        for (const [x, y] of m[key]) {
          if (y * m.width + x <= (m.height - 1 - y) * m.width + (m.width - 1 - x))
            this.call('MapBuilder_Add' + kind, handle, x, y);
        }
        // The official builder mirrors terrain; check its physical result before serializing.
        for (const [x, y] of m[key]) {
          this.call('MapBuilder_Get' + kind, handle, x, y, this.out);
          if (!this.view.getUint8(this.out)) throw Error(`Terrain was not mirrored: ${kind}`);
        }
      }
      // Camp entries represent a symmetric pair; adding both would duplicate physical camps.
      for (const [type, x, y] of m.camps) {
        if (y * m.width + x <= (m.height - 1 - y) * m.width + (m.width - 1 - x))
          this.call('MapBuilder_AddCamp', handle, type, x, y, this.out);
      }
      this.call('MapBuilder_VerifyIntegrity', handle);
      this.call('MapBuilder_Encode', handle, this.out, this.out + 4);
      const p = this.view.getUint32(this.out, true), n = this.view.getUint32(this.out + 4, true);
      const encoded = Buffer.from(new Uint8Array(this.x.memory.buffer, p, n));
      // Verify playability as well as MapBuilder integrity (e.g. a 2x2 spawn is too small).
      const game = this.load(encoded);
      this.call('Game_Destroy', game);
      return encoded;
    } finally { this.call('MapBuilder_Destroy', handle); }
  }
}

export class Episode {
  constructor(engine, file, picks = [[0, 1, 2, 3, 4], [0, 1, 2, 3, 4]]) {
    this.e = engine; this.x = engine.x;
    const bytes=fs.readFileSync(file);this.g = engine.load(bytes);
    this.mapHash = crypto.createHash('sha256').update(bytes).digest('hex');
    this.closed = false; this.decisions = 0; this.transitions = 0;
    try {
    engine.call('Game_GetBitboardMetadata', this.g, engine.out);
    this.width = engine.view.getInt32(engine.out, true); this.height = engine.view.getInt32(engine.out + 4, true);
    this.capacity = this.width * this.height;
    this.points = this.x.Engine_Malloc(this.capacity * 8);
    engine.call('Managed_Bitboard_Create', this.width, this.height, engine.out);
    this.board = engine.view.getBigUint64(engine.out, true);
    engine.call('Managed_Bitboard_GetBuffer', this.board, engine.out);
    this.raw = engine.view.getUint32(engine.out, true);
    engine.call('Game_Runner_SetCheckpointsEnabled', this.g, 0);
    engine.call('Game_Runner_Init', this.g);
    engine.call('Game_API_Draft_GetNumRounds', this.g, engine.out);
    const count = engine.view.getUint8(engine.out);
    if(!Array.isArray(picks)||picks.length!==2)throw Error('Draft requires two lineups');
    for (const lineup of picks) {
      if (!Array.isArray(lineup)||lineup.length < count || new Set(lineup.slice(0, count)).size !== count ||
          lineup.slice(0, count).some(p => !Number.isInteger(p) || p < 0 || p > 11)) {
        this.close(); throw Error('Draft requires distinct valid picks for each team');
      }
    }
    while (this.state().phase === 0) {
      const s = this.state();
      engine.call('Game_Action_Draft', this.g, picks[s.team][s.round]);
      engine.call('Game_Runner_EndTurn', this.g, 0);
      engine.call('Game_Runner_Advance', this.g);
    }
    }catch(error){this.close();throw error;}
  }
  state() {
    if (this.closed) throw Error('Episode is closed');
    this.e.call('Game_Runner_GetState', this.g, this.e.out);
    const v = this.e.view, p = this.e.out;
    return {phase: v.getUint32(p, true), team: v.getUint32(p + 4, true),
            round: v.getUint32(p + 8, true), champion: v.getUint32(p + 12, true)};
  }
  perspective(s = this.state()) {
    if (s.phase !== 1 || s.team > 1 || s.champion === 0xffffffff) throw Error('No authenticated actor');
    this.e.view.setUint32(this.e.pov, s.team, true);
    this.e.view.setUint32(this.e.pov + 4, s.champion, true);
    return this.e.pov;
  }
  scalar(name, ...args) {
    this.e.call(name, this.g, ...args, this.e.out);
    return this.e.view.getUint32(this.e.out, true);
  }
  tiles(name, ...args) {
    this.e.call(name, this.g, ...args, this.raw);
    this.e.call('Managed_Bitboard_GetSetBits', this.board, this.points, this.capacity, this.e.out);
    const count = this.e.view.getUint32(this.e.out, true), v = this.e.view;
    return Array.from({length: count}, (_, i) => [v.getInt32(this.points + 8*i, true), v.getInt32(this.points + 8*i + 4, true)]);
  }
  champion(id, pov) {
    this.e.call('Game_API_Champion_Get', this.g, pov, id, this.e.out);
    const v = this.e.view, p = this.e.out;
    const ints = [0,4,8,12].map(i => v.getInt32(p+i, true));
    const floats = [16,20,24,28].map(i => v.getFloat32(p+i, true));
    return {id, team: ints[0], type: ints[1], x: ints[2], y: ints[3],
            health: floats[0], max_health: floats[1], strength: floats[2], focus: floats[3],
            move_speed: v.getInt32(p+32, true), attack_range: v.getInt32(p+36, true), state: v.getUint32(p+40, true)};
  }
  observation() {
    const s = this.state();
    if (s.phase === 2) return {done: true, terminal: this.terminal()};
    const pov = this.perspective(s), self = this.champion(s.champion, pov);
    const vision = this.tiles('Game_API_GetVision', pov);
    const moves = self.state & 8 ? this.tiles('Game_API_Champion_GetMovementMask', pov, s.champion) : [];
    const champions = [];
    for (const name of ['Game_API_GetAllyOccupancy', 'Game_API_GetEnemyOccupancy']) {
      for (const [x, y] of this.tiles(name, pov)) {
        const id = this.scalar('Game_API_GetChampion', pov, x, y);
        champions.push(this.champion(id, pov));
      }
    }
    champions.sort((a,b) => a.id-b.id);
    const camps = this.tiles('Game_API_GetCampOccupancy', pov).map(([x,y]) => {
      const id = this.scalar('Game_API_GetCamp', pov, x, y);
      this.e.call('Game_API_Camp_Get', this.g, pov, id, this.e.out);
      const v = this.e.view, p = this.e.out;
      return {id, x: v.getInt32(p,true), y: v.getInt32(p+4,true), health: v.getFloat32(p+8,true),
              max_health: v.getFloat32(p+12,true), strength: v.getFloat32(p+16,true), focus: v.getFloat32(p+20,true)};
    }).sort((a,b) => a.id-b.id);
    // Gold/gems are self-only queries. Never obtain an enemy inventory or hidden health.
    self.gold = this.scalar('Game_API_Champion_GetGold', pov, s.champion);
    self.gems = this.scalar('Game_API_Champion_GetGems', pov, s.champion);
    const banks = [0,1].map(team => this.scalar('Game_API_GetSubmittedGemCount', team));
    const abilities=[0,1].map(slot=>{
      this.e.call('Game_API_Champion_GetAbilityProps',this.g,pov,s.champion,slot,this.e.out);
      const kind=this.e.view.getUint32(this.e.out,true), targets=this.e.view.getUint32(this.e.out+12,true);
      const cooldown=this.scalar('Game_API_Champion_GetCooldown',pov,s.champion,slot);
      return {slot,kind,targets,cooldown};
    });
    this.e.call('Game_API_ReadSharedMemory',this.g,s.team,0,this.e.out+256,8);
    const shared_memory=Array.from(new Uint8Array(this.x.memory.buffer,this.e.out+256,8));
    return {schema: 1, done: false, actor: s, map_hash: this.mapHash, width: this.width, height: this.height,
            self, vision, moves, champions, camps, banks, abilities, shared_memory, decisions_left: 2-this.decisions};
  }
  terrain() {
    const result = {width: this.width, height: this.height, map_hash: this.mapHash};
    for (const [key, kind] of [['walls','Wall'],['holes','Hole'],['bushes','Bush'],['altars','Altar']]) {
      result[key] = [];
      for (let y=0;y<this.height;y++) for (let x=0;x<this.width;x++) {
        this.e.call('Game_Get'+kind, this.g, x, y, this.e.out);
        if (this.e.view.getUint8(this.e.out)) result[key].push([x,y]);
      }
    }
    return result;
  }
  target(action) {
    if (!action.target || ![1,2,6].includes(action.target.kind) || !Number.isInteger(action.target.id) || action.target.id<0 || action.target.id>0xffffffff)
      throw Error('Action requires a typed target');
    this.e.view.setUint32(this.e.entity, action.target.kind, true);
    this.e.view.setUint32(this.e.entity+4, action.target.id, true);
    return this.e.entity;
  }
  position(action) {
    if (![action.x,action.y].every(v=>Number.isInteger(v)&&v>=-2147483648&&v<=2147483647)) throw Error('Action requires int32 coordinates');
    this.e.view.setInt32(this.e.out+128, action.x, true);
    this.e.view.setInt32(this.e.out+132, action.y, true);
    return this.e.out+128;
  }
  step(action, expected, observe=true) {
    const s = this.state();
    if (s.phase === 2) throw Error('Episode already finished');
    if (!expected || ['team','round','champion'].some(k => expected[k] !== s[k])) throw Error('Stale or wrong actor');
    if(!action||typeof action!=='object')throw Error('Action must be an object');
    for(const field of ['slot','item','count','priority'])if(action[field]!==undefined &&
      (!Number.isInteger(action[field])||action[field]<0||action[field]>0xffffffff))throw Error('Action requires uint32 '+field);
    if(action.kind==='cast'&&![0,1].includes(action.slot))throw Error('Cast slot must be 0 or 1');
    this.perspective(s);
    let code=0, result=true, ended=false;
    const x=this.x, g=this.g, out=this.e.out;
    switch (action.kind) {
      case 'wait': ended=true; break;
      case 'move': this.position(action); code=x.Game_Action_Move(g,action.x,action.y,out); result=this.e.view.getInt32(out,true)!==0; break;
      case 'attack': code=x.Game_Action_Attack(g,this.target(action)); break;
      case 'cast': code=x.Game_Action_Cast(g,action.slot,action.target?this.target(action):0,
                                         action.x===undefined?0:this.position(action),out); result=this.e.view.getInt32(out,true)!==0; break;
      case 'recall': code=x.Game_Action_Recall(g); break;
      case 'submit': code=x.Game_Action_SubmitGems(g,this.position(action)); break;
      case 'cancel': code=x.Game_Action_CancelChannel(g); break;
      case 'buy': code=x.Game_Action_BuyItem(g,action.item,action.count??1); break;
      case 'sell': code=x.Game_Action_Sell(g,action.item); break;
      case 'buy_consumable': code=x.Game_Action_BuyConsumable(g,action.item); break;
      case 'use_consumable': code=x.Game_Action_UseConsumable(g,action.item,this.position(action),out); result=this.e.view.getInt32(out,true)!==0; break;
      case 'ward': code=x.Game_Action_PlaceWard(g,this.position(action),out); result=this.e.view.getInt32(out,true)!==0; break;
      case 'priority': code=x.Game_Action_SetPriority(g,action.priority); break;
      default: throw Error('Unsupported action kind');
    }
    this.decisions++; this.transitions++;
    ended ||= this.decisions>=2;
    if (ended && this.state().phase!==2) {
      this.e.call('Game_Runner_EndTurn',g,0); this.e.call('Game_Runner_Advance',g); this.decisions=0;
    }
    return {accepted: code===0, error_code: code, result: code===0&&result, turn_ended: ended,
            ...(observe?{observation:this.observation()}:{})};
  }
  terminal() {
    if (this.state().phase!==2) throw Error('Unfinished episodes have no outcome label');
    const n=this.x.Game_Visualiser_SnapshotSize(), p=this.x.Engine_Malloc(n);
    // Authoritative terminal outcome only. This snapshot never enters actor observations.
    this.e.view.setUint32(this.e.pov,2,true); this.e.view.setUint32(this.e.pov+4,0xffffffff,true);
    try {
      this.e.call('Game_Visualiser_ReadState',this.g,this.e.pov,p);
      const outcome=this.e.view.getUint32(p+28,true);
      if (![1,2].includes(outcome)) throw Error('Official engine has no completed team outcome');
      return {outcome:outcome===1?'teamA':'teamB',round:this.e.view.getUint32(p+8,true),
              banks:[Number(this.e.view.getBigUint64(p+32,true)),Number(this.e.view.getBigUint64(p+40,true))]};
    } finally { this.x.Engine_Free(p); }
  }
  finishWaiting(limit) {
    if(!Number.isInteger(limit)||limit<1||limit>50000)throw Error('Wait limit must be 1..50000');
    let turns=0;
    while(this.state().phase!==2&&turns<limit){
      this.e.call('Game_Runner_EndTurn',this.g,0);this.e.call('Game_Runner_Advance',this.g);turns++;
    }
    this.decisions=0;
    return {turns,observation:this.observation()};
  }
  close() {
    if (!this.closed) {
      if(this.board!==undefined)this.e.call('Managed_Bitboard_Destroy',this.board);
      if(this.points!==undefined)this.x.Engine_Free(this.points);
      this.e.call('Game_Destroy',this.g);this.closed=true;
    }
  }
}

async function serve(engine) {
  const games=new Map();let next=1;
  const dispatch=cmd=>{
    if(cmd.op==='reset') {
      if(games.size>=64)throw Error('Close episodes before opening more than 64');
      const game=new Episode(engine,cmd.map,cmd.picks);const id=String(next++);games.set(id,game);
      return {env_id:id,engine_sha256:engine.sha256,terrain:game.terrain(),observation:game.observation()};
    }
    if(cmd.op==='batch'){
      if(!Array.isArray(cmd.commands)||cmd.commands.length>64||cmd.commands.some(c=>c?.op==='batch'))throw Error('Batch requires at most 64 non-batch commands');
      return cmd.commands.map(command=>{
      try{return {ok:true,result:dispatch(command)};}catch(e){return {ok:false,error:e.message};}
      });
    }
    const game=games.get(cmd.env_id);if(!game)throw Error('Unknown episode');
    if(cmd.op==='step')return game.step(cmd.action,cmd.actor,cmd.observe!==false);
    if(cmd.op==='observe')return game.observation();
    if(cmd.op==='finish_wait')return game.finishWaiting(cmd.limit);
    if(cmd.op==='close'){game.close();games.delete(cmd.env_id);return {closed:true};}
    throw Error('Unsupported operation');
  };
  for await(const line of readline.createInterface({input:process.stdin,crlfDelay:Infinity})) {
    let request;try{request=JSON.parse(line);console.log(JSON.stringify({id:request.id,ok:true,result:dispatch(request)}));}
    catch(e){console.log(JSON.stringify({id:request?.id,ok:false,error:e.message}));}
  }
  for(const game of games.values())game.close();
}

function buildMaps(engine, request) {
  const allowed = path.resolve('maps/generated') + path.sep;
  return JSON.parse(fs.readFileSync(request, 'utf8')).map(m => {
    const output = path.resolve(m.output);
    if (!output.startsWith(allowed)) throw Error('Generated map output must stay inside maps/generated');
    const bytes = engine.encode(m);
    const sha256 = crypto.createHash('sha256').update(bytes).digest('hex');
    if (fs.existsSync(output) && !fs.readFileSync(output).equals(bytes))
      throw Error(`Refusing to overwrite different generated map: ${output}`);
    fs.mkdirSync(path.dirname(output), {recursive: true});
    if (!fs.existsSync(output)) fs.writeFileSync(output, bytes, {flag: 'wx'});
    return {name: m.name, path: path.relative(process.cwd(), output).split(path.sep).join('/'),
            sha256, bytes: bytes.length};
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const engine = new OfficialEngine(process.argv[2]);
    if (process.argv[3] === 'maps') console.log(JSON.stringify(buildMaps(engine, process.argv[4])));
    else if (process.argv[3] === 'serve') await serve(engine);
    else throw Error('Expected command: maps REQUEST.json | serve');
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
