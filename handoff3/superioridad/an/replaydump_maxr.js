#!/usr/bin/env node
// replaydump.js - decode a CAMBC replay (.repl26a, raw or inside a zip bundle) with the
// game engine's wasm module and print one JSON line per round plus a final summary line.
//
// usage: node replaydump.js <replay.repl26a | bundle.zip> [--draft] [--every-step] [--camps]
//
// --camps adds a "camps" array to every line (see readCamps for the entry layout). Camp entity index e
// maps to map camp floor(e/2); odd e is the mirrored copy (as the visualiser's campSpawn does).
//
// Per-round line: the last engine state observed while header.round == N, i.e. the state after the
// last end-of-turn step of round N, just before the "Round N+1 start" step (its header phase is 0 =
// Initial for that reason). Round 0 is the pre-game state (champions at spawn, right after the draft).
// The final state of the game (phase 11 = Finished) is always emitted as the last round line.
// Draft phase (phase 12) counts its own "rounds" 0..4 (two picks each) before game round 0; those
// lines are skipped unless --draft is given (they carry "draft":true and have no champions).
// With --every-step every timeline step is printed instead (large output; adds a "step" object).
//
// Call conventions (verified against the visualiser JS and a known game):
//   Game_FromReplayFileBytes(ptr, len, out)            -> code; u64 game handle at out
//   Game_Visualiser_SnapshotSize()                    -> 184696 (wasms v0_0_*, engine 2.x) or 184760 (v0_1_0 and
//                                                     v1_0_0; v1_0_0 = engine 3.0): ABI 1 both; 3.0 appends f32 passiveDamageBonus[16] at 184696
//                                                     (per champion index; Heart of Ruin missing-health bonus). Other offsets unchanged.
//   Game_Visualiser_Timeline_GetMain(h, out)          -> u64 timeline handle at out
//   Game_Visualiser_Timeline_Info(h, tl, pSize, pParent, pParentPos) -> u32 size (number of input positions)
//   Game_Visualiser_Timeline_Seek(h, tl, position, substep)
//   Game_Visualiser_Timeline_ReplayNext(h, 1)         -> code 18 "Replay cannot advance." at the end
//   Game_Visualiser_ReadState(h, perspectivePtr, snapshotPtr)  perspective = {u32 team, u32 champion};
//                                                     omniscient perspective = {2, 0xffffffff}
//   Game_API_GetRoundNumber(h, out)                   -> u32 round at out
//   Game_API_GetSubmittedGemCount(h, team, out)       -> u64 gems at out (team 0/1)
//   Game_Statistics_GetSummary(h, buf)                -> 80-byte struct (see readSummary)
//   Game_Statistics_GetChampion(h, index, buf)        -> 664-byte struct in 2.x and 3.0; 1168 bytes with engine 2.0.0 (84 item types:
//                                                     itemsBought u64[84] @64, consumablesBought u64[4] @736, items u32[84] @768, consumables u32[4] @1104, f64 x6 @1120)
//   Game_GetBitboardMetadata(h, out) -> i32 width, i32 height, ...; Game_GetSymmetry(h, out) -> i32
//   Game_GetNumCamps(h, out) -> u32; Game_GetCampHandle(h, i, out) -> u64; Game_GetCamp(h, campHandle, out) -> i32 type, i32 x, i32 y
//   Game_GetNumCampGroups(h, out) -> u32; Game_GetCampGroupHandle(h, i, out) -> u64;
//   Game_GetCampGroup(h, groupHandle, out) -> u32 gemValue, goldValue, cooldown, numCamps; Game_GetCampGroupCamp(h, groupHandle, j, out) -> u64 camp handle
'use strict';
const fs = require('fs');
const zlib = require('zlib');
const path = require('path');
// Synchronous stdout: with a pipe reader (| python3 compact.py) the async process.stdout.write buffers the whole
// dump in memory and dies with ENOBUFS; writeSync blocks on backpressure instead.
function emitLine(s) {
  const b = Buffer.from(s); let off = 0;
  while (off < b.length) {
    try { off += fs.writeSync(1, b, off, b.length - off); }
    catch (e) {
      if (e.code === 'EAGAIN') { Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 2); continue; }
      if (e.code === 'EPIPE') process.exit(0);
      throw e;
    }
  }
}

// The engine wasms ship with the cambc visualiser assets, one per engine version (v<maj>_<min>_<patch>-<hash>.wasm;
// engine 3.0 replays need v1_0_0). The wasm matching the replay's engine version (inner replay header bytes 8..10) is
// preferred; otherwise the newest wasm is used. CAMBC_VIS_WASM overrides.
const findWasm = (want) => process.env.CAMBC_VIS_WASM || (() => {
  const roots = [path.join(require('os').homedir(), '.cache', 'cambc', 'assets'),
                 path.join(process.env.LOCALAPPDATA || '', 'cambc', 'assets')];
  let best = null;
  for (const r of roots) {
    let dirs = []; try { dirs = fs.readdirSync(r); } catch (e) { continue; }
    for (const d of dirs) {
      const a = path.join(r, d, 'visualiser', 'assets'); let fl = [];
      try { fl = fs.readdirSync(a); } catch (e) { continue; }
      for (const f of fl) if (f.endsWith('.wasm')) {
        const fp = path.join(a, f), t = fs.statSync(fp).mtimeMs, m = want && f.startsWith(want + '-') ? 1 : 0;
        if (!best || m > best.m || (m === best.m && (t > best.t || (t === best.t && f > best.f)))) best = { fp, t, m, f };
      }
    }
  }
  if (best && want && !best.m) process.stderr.write(`replaydump: no wasm for engine ${want} found; using ${best.f}\n`);
  if (!best) { process.stderr.write('replaydump: engine wasm not found; run `cambc view` once or set CAMBC_VIS_WASM\n'); process.exit(2); }
  return best.fp;
})();
const SNAPSHOT_SIZES = [184696, 184760, 189768]; // 2.x, 3.0 (= engine 1.0.x), engine 2.0.0 (+5008 at the end; champion/camp/group/header offsets unchanged)
const SNAPSHOT_ABI = 1;
const OMNISCIENT = { team: 2, champion: 0xffffffff };
const CHAMP = { countOffset: 120, dataOffset: 140, stride: 456, capacity: 16 };
const CAMPS = { countOffset: 124, dataOffset: 7436, stride: 232, capacity: 500 };
const GROUPS = { countOffset: 128, dataOffset: 123436, stride: 20, capacity: 500 };
const CAMP_TYPES = ['wolf', 'elk', 'gem_cluster', 'gold_cluster', 'monolith', 'golem']; // golem: engine 3.0
const GROUP_STATES = ['unknown', 'alive', 'reward_available', 'respawning']; // engine: Unknown, HasCamps, WaitingForRewardClaim, WaitingToRespawn
const SYMMETRY = ['HORIZONTAL', 'VERTICAL', 'ROTATIONAL180'];
const CHAMPION_TYPES = ['Ryth', 'VesperVale', 'Vendetta', 'Cassi', 'Issac', 'Stellar', 'Prism', 'Marcella', 'Willow', 'Ren', 'Varg', 'Tavi', 'HeartOfRuin'];
const PHASES = { 0: 'Initial', 1: 'CampRespawns', 4: 'Spells', 7: 'CampCaptures', 9: 'Camps', 10: 'Champions', 11: 'Finished', 12: 'Draft', 13: 'ChampionEndTurn', 14: 'ChampionStartTurn' };
const OUTCOMES = { 0: 'none', 1: 'teamA', 2: 'teamB' };

// --- minimal zip reader (central directory based; stored + deflate only) ---------------------------
function unzipEntry(buf, wantName) {
  const eocdMin = buf.length - 22;
  let eocd = -1;
  for (let i = eocdMin; i >= Math.max(0, eocdMin - 65557); i--) if (buf.readUInt32LE(i) === 0x06054b50) { eocd = i; break; }
  if (eocd < 0) throw new Error('zip: no end-of-central-directory record');
  const count = buf.readUInt16LE(eocd + 10), cdOff = buf.readUInt32LE(eocd + 16);
  let p = cdOff; const names = [];
  for (let i = 0; i < count; i++) {
    if (p + 46 > buf.length || buf.readUInt32LE(p) !== 0x02014b50) throw new Error('zip: bad central directory');
    const method = buf.readUInt16LE(p + 10), csize = buf.readUInt32LE(p + 20), usize = buf.readUInt32LE(p + 24);
    const nlen = buf.readUInt16LE(p + 28), xlen = buf.readUInt16LE(p + 30), clen = buf.readUInt16LE(p + 32), lho = buf.readUInt32LE(p + 42);
    const name = buf.subarray(p + 46, p + 46 + nlen).toString('utf8');
    names.push(name);
    if (!wantName || name === wantName || name.endsWith('/' + wantName)) {
      if (lho + 30 > buf.length || buf.readUInt32LE(lho) !== 0x04034b50) throw new Error('zip: bad local header');
      const lnlen = buf.readUInt16LE(lho + 26), lxlen = buf.readUInt16LE(lho + 28);
      const start = lho + 30 + lnlen + lxlen;
      if (start + csize > buf.length) throw new Error('zip: truncated entry');
      const raw = buf.subarray(start, start + csize);
      if (method === 0) return { name, data: raw };
      if (method === 8) { const d = zlib.inflateRawSync(raw); if (usize && d.length !== usize) throw new Error('zip: size mismatch'); return { name, data: d }; }
      throw new Error('zip: unsupported compression method ' + method);
    }
    p += 46 + nlen + xlen + clen;
  }
  throw new Error('zip: entry not found; entries: ' + names.join(', '));
}

function loadReplayBytes(file) {
  const buf = fs.readFileSync(file);
  if (buf.length >= 4 && buf.readUInt32LE(0) === 0x04034b50) {
    const e = unzipEntry(buf, 'replay.repl26a');
    process.stderr.write(`[replaydump] extracted ${e.name} (${e.data.length} bytes) from zip bundle\n`);
    return e.data;
  }
  return buf;
}

// --- wasm engine ---------------------------------------------------------------------------------
function replayEngineVersion(replay) { // 'v1_0_0' for engine 3.0; null if not a replay header
  if (replay.length < 14 || replay.readBigUInt64LE(0) !== 125779999602273n) return null;
  return `v${replay[8]}_${replay[9]}_${replay[10]}`;
}
async function createEngine(WASM) {
  const bytes = fs.readFileSync(WASM);
  let mem = null; const td = new TextDecoder();
  const rd = (p) => { const u = new Uint8Array(mem.buffer); let e = p; while (u[e]) e++; return td.decode(u.subarray(p, e)); };
  const dv = () => new DataView(mem.buffer);
  const z = () => 0;
  const wasi = {
    random_get(p, n) { require('crypto').randomFillSync(new Uint8Array(mem.buffer, p, n)); return 0; },
    clock_time_get(i, pr, o) { dv().setBigUint64(o, BigInt(Date.now()) * 1000000n, true); return 0; },
    environ_sizes_get(a, b) { dv().setUint32(a, 0, true); dv().setUint32(b, 0, true); return 0; }, environ_get: z,
    args_sizes_get(a, b) { dv().setUint32(a, 0, true); dv().setUint32(b, 0, true); return 0; }, args_get: z,
    fd_close: z,
    fd_fdstat_get(fd, p) { const d = dv(); d.setUint8(p, 2); d.setUint16(p + 2, 0, true); d.setBigUint64(p + 8, 0n, true); d.setBigUint64(p + 16, 0n, true); return 0; },
    fd_prestat_get() { return 8; }, fd_prestat_dir_name() { return 8; },
    fd_read(fd, i, n, o) { dv().setUint32(o, 0, true); return 0; }, fd_seek() { return 70; },
    fd_write(fd, iovs, n, out) {
      const d = dv(); let c = 0, s = '';
      for (let i = 0; i < n; i++) { const p = d.getUint32(iovs + i * 8, true), l = d.getUint32(iovs + i * 8 + 4, true); s += td.decode(new Uint8Array(mem.buffer, p, l)); c += l; }
      process.stderr.write('[wasm fd' + fd + '] ' + s); d.setUint32(out, c, true); return 0;
    },
    proc_exit(c) { throw new Error('WASM exited with code ' + c); },
  };
  const imports = { wasi_snapshot_preview1: wasi, deep_wasm: { on_assert_fail_impl(a, b, c, d) { process.stderr.write(`${rd(b)}:${c}: assertion failed: ${rd(a)} ${rd(d)}\n`); return 1; } } };
  const { instance } = await WebAssembly.instantiate(bytes, imports);
  const X = instance.exports; mem = X.memory; X._initialize();
  const check = (code, what) => { if (code !== 0) throw new Error(`${what}: engine error ${code}: ${rd(X.GetLastErrorMsg())}`); };
  return { X, rd, dv, check, get memory() { return mem; } };
}

// --- snapshot parsing (layout from the visualiser's PanelChrome chunk) ----------------------------
function readHeader(d, p) {
  const u = (o) => d.getUint32(p + o, true);
  if (u(0) !== SNAPSHOT_ABI || !SNAPSHOT_SIZES.includes(u(4))) throw new Error('Unsupported game snapshot ABI');
  return {
    round: u(8), turn: u(12), team: u(16), awaitingInput: !!u(20), phase: u(24), outcome: u(28),
    submittedGems: [Number(d.getBigUint64(p + 32, true)), Number(d.getBigUint64(p + 40, true))],
    timeline: d.getBigUint64(p + 48, true), inputPosition: u(56), currentChampion: u(60),
    step: { phase: u(64), kind: u(68), actorKind: u(72), actorIndex: u(76), round: u(96), inputPosition: u(100), substep: u(104) },
  };
}
const r2 = (x) => Math.round(x * 100) / 100;
function readChampions(d, p) {
  const n = d.getUint32(p + CHAMP.countOffset, true);
  if (n > CHAMP.capacity) throw new Error('Invalid snapshot champion count');
  const out = [];
  for (let i = 0; i < n; i++) {
    const b = p + CHAMP.dataOffset + i * CHAMP.stride;
    const u = (o) => d.getUint32(b + o, true);
    const x = d.getInt32(b + 20, true), y = d.getInt32(b + 24, true), type = u(12);
    out.push({
      team: u(8), index: u(4), type, typeName: CHAMPION_TYPES[type] ?? String(type),
      x, y, // -1,-1 while dead / not on the board
      health: r2(d.getFloat32(b + 28, true)), maxHealth: r2(d.getFloat32(b + 32, true)),
      gems: u(236), gold: u(232), alive: !!u(224), cd: [u(92), u(96)], respawn: u(228),
    });
  }
  return out;
}

// Camp entries (stride 232): +0 entity.kind(2) +4 index +8 team +12 type +16 known +20 x +24 y (i32) +28 health +32 maxHealth (f32)
// +224 group index (into the groups table) +228 awake. Group entries (stride 20): +0 state +4 rewardAvailable +8 captureTeam
// +12 captureTimer (i32) +16 respawnRounds (i32). Spawn/reward come from the static map tables (see readMapCamps).
function readGroups(d, p) {
  const n = d.getUint32(p + GROUPS.countOffset, true);
  if (n > GROUPS.capacity) throw new Error('Invalid snapshot group count');
  const out = [];
  for (let i = 0; i < n; i++) {
    const b = p + GROUPS.dataOffset + i * GROUPS.stride;
    out.push({ state: d.getUint32(b, true), rewardAvailable: !!d.getUint32(b + 4, true), captureTeam: d.getUint32(b + 8, true), captureTimer: d.getInt32(b + 12, true), respawnRounds: d.getInt32(b + 16, true) });
  }
  return out;
}
function readCamps(d, p, map) {
  const n = d.getUint32(p + CAMPS.countOffset, true);
  if (n > CAMPS.capacity) throw new Error('Invalid snapshot camp count');
  const groups = readGroups(d, p);
  const out = [];
  for (let i = 0; i < n; i++) {
    const b = p + CAMPS.dataOffset + i * CAMPS.stride;
    const u = (o) => d.getUint32(b + o, true);
    const index = u(4), type = u(12), x = d.getInt32(b + 20, true), y = d.getInt32(b + 24, true), health = r2(d.getFloat32(b + 28, true));
    const group = u(224), g = groups[group], spawn = map.spawn(index), reward = map.reward(index);
    const e = { index, team: u(8), type, typeName: CAMP_TYPES[type] ?? String(type), spawnX: spawn ? spawn.x : null, spawnY: spawn ? spawn.y : null, x, y,
      health, maxHealth: r2(d.getFloat32(b + 32, true)), alive: health > 0 && x >= 0 && y >= 0, awake: !!u(228), group,
      groupState: g ? g.state : null, groupStateName: g ? (GROUP_STATES[g.state] ?? String(g.state)) : null,
      rewardAvailable: g ? g.rewardAvailable : null, captureTeam: g ? g.captureTeam : null, captureTimer: g ? g.captureTimer : null, respawnRounds: g ? g.respawnRounds : null };
    if (reward) { e.rewardGems = reward.gems; e.rewardGold = reward.gold; e.respawnDelay = reward.respawnDelay; }
    out.push(e);
  }
  return out;
}
// Static map data: camp spawns (mirrored for odd entity indices) and per-camp group rewards, read via the Game_Get* map API.
function readMapCamps(E, H) {
  const { X, dv, check } = E; const out = X.Engine_Malloc(64);
  const u64 = () => dv().getBigUint64(out, true);
  check(X.Game_GetBitboardMetadata(H, out), 'Game_GetBitboardMetadata'); const width = dv().getInt32(out, true), height = dv().getInt32(out + 4, true);
  check(X.Game_GetSymmetry(H, out), 'Game_GetSymmetry'); const symmetry = SYMMETRY[dv().getInt32(out, true)] ?? 'UNKNOWN';
  check(X.Game_GetNumCamps(H, out), 'Game_GetNumCamps'); const numCamps = dv().getUint32(out, true);
  const camps = [], handleToIndex = new Map();
  for (let i = 0; i < numCamps; i++) {
    check(X.Game_GetCampHandle(H, i, out), 'Game_GetCampHandle'); const h = u64(); handleToIndex.set(h, i);
    check(X.Game_GetCamp(H, h, out), 'Game_GetCamp'); camps.push({ type: dv().getInt32(out, true), x: dv().getInt32(out + 4, true), y: dv().getInt32(out + 8, true) });
  }
  check(X.Game_GetNumCampGroups(H, out), 'Game_GetNumCampGroups'); const numGroups = dv().getUint32(out, true);
  const rewardByCamp = new Map();
  for (let g = 0; g < numGroups; g++) {
    check(X.Game_GetCampGroupHandle(H, g, out), 'Game_GetCampGroupHandle'); const gh = u64();
    check(X.Game_GetCampGroup(H, gh, out), 'Game_GetCampGroup');
    const r = { gems: dv().getUint32(out, true), gold: dv().getUint32(out + 4, true), respawnDelay: dv().getUint32(out + 8, true) }, nc = dv().getUint32(out + 12, true);
    for (let j = 0; j < nc; j++) { check(X.Game_GetCampGroupCamp(H, gh, j, out), 'Game_GetCampGroupCamp'); const ci = handleToIndex.get(u64()); if (ci !== undefined) rewardByCamp.set(ci, r); }
  }
  X.Engine_Free(out);
  return { width, height, symmetry, numCamps, numGroups,
    spawn(e) { const c = camps[Math.floor(e / 2)]; if (!c) return null; if (e % 2 === 0) return { x: c.x, y: c.y };
      return { x: symmetry === 'VERTICAL' ? c.x : width - 1 - c.x, y: symmetry === 'HORIZONTAL' ? c.y : height - 1 - c.y }; },
    reward(e) { return rewardByCamp.get(Math.floor(e / 2)); } };
}

// --- statistics ----------------------------------------------------------------------------------
function readSummary(d, p) {
  const u = (o) => d.getUint32(p + o, true), i = (o) => d.getInt32(p + o, true);
  const picks = [[], []];
  for (let t = 0; t < 2; t++) for (let k = 0; k < 5; k++) picks[t].push(i(40 + t * 20 + k * 4));
  return { engineVersionPacked: u(0), outcome: u(4), round: u(8), numChampions: u(12),
    submittedGems: [Number(d.getBigUint64(p + 16, true)), Number(d.getBigUint64(p + 24, true))],
    draftCounts: [u(32), u(36)], draftPicks: picks };
}
let NITEMS = 42; // 84 with engine 2.0.0 (snapshot 189768), set in main
function readChampionStats(d, p) {
  const u = (o) => d.getUint32(p + o, true), U = (o) => Number(d.getBigUint64(p + o, true)), f = (o) => d.getFloat64(p + o, true);
  const arr = (o, n, w) => Array.from({ length: n }, (_, k) => (w === 8 ? U(o + k * 8) : u(o + k * 4)));
  return { index: u(0), team: u(4), type: u(8), typeName: CHAMPION_TYPES[u(8)] ?? String(u(8)),
    kills: u(12), deaths: u(16), assists: u(20),
    earnedGold: U(24), collectedGems: U(32), submittedGems: U(40), spentGold: U(48), gold: u(56), gems: u(60), // gold/gems are u32 (was read as u64 gold)
    ...(() => { const n = NITEMS, cb = 64 + n * 8, it = cb + 32, co = it + n * 4, fd = co + 16;
      return { itemsBought: arr(64, n, 8), consumablesBought: arr(cb, 4, 8), items: arr(it, n, 4), consumables: arr(co, 4, 4),
        monsterDamageDone: f(fd), monsterDamageTaken: f(fd + 8), championDamageDone: f(fd + 16), championDamageTaken: f(fd + 24), healingDone: f(fd + 32), shieldingDone: f(fd + 40) }; })() };
}

async function main() {
  const argv = process.argv.slice(2);
  const everyStep = argv.includes('--every-step');
  const includeDraft = argv.includes('--draft');
  const includeCamps = argv.includes('--camps');
  const file = argv.find((a) => !a.startsWith('--'));
  if (!file) { process.stderr.write('usage: node replaydump.js <replay.repl26a | bundle.zip> [--draft] [--every-step] [--camps]\n'); process.exit(2); }
  const replay = loadReplayBytes(file);
  const engineVersion = replayEngineVersion(replay), WASM = findWasm(engineVersion);
  process.stderr.write(`[replaydump] replay engine ${engineVersion}, wasm ${path.basename(WASM)}\n`);
  const E = await createEngine(WASM);
  const { X, rd, dv, check } = E;
  const SNAPSHOT_SIZE = X.Game_Visualiser_SnapshotSize();
  if (!SNAPSHOT_SIZES.includes(SNAPSHOT_SIZE)) throw new Error('Unsupported snapshot layout: ' + SNAPSHOT_SIZE);
  if (SNAPSHOT_SIZE === 189768) { // engine 2.0.0 (visualiser PanelChrome: offsets >=7436 +2688, >=133436 +4688; champion stride 624, group stride 24)
    NITEMS = 84; CHAMP.stride = 624; CAMPS.dataOffset = 7436 + 2688; GROUPS.dataOffset = 123436 + 2688; GROUPS.stride = 24;
  }

  const out = X.Engine_Malloc(64), args = X.Engine_Malloc(128);
  const snapA = X.Engine_Malloc(SNAPSHOT_SIZE), snapB = X.Engine_Malloc(SNAPSHOT_SIZE), snapC = X.Engine_Malloc(SNAPSHOT_SIZE);
  const includeVis = argv.includes('--vis');
  const fileBuf = X.Engine_Malloc(replay.length);
  new Uint8Array(E.memory.buffer, fileBuf, replay.length).set(replay);
  check(X.Game_FromReplayFileBytes(fileBuf, replay.length, out), 'Game_FromReplayFileBytes');
  const H = dv().getBigUint64(out, true);
  X.Engine_Free(fileBuf);

  const perspective = (p) => { const d = dv(); d.setUint32(args + 48, p.team, true); d.setUint32(args + 52, p.champion, true); return args + 48; };
  const readState = (snap) => { check(X.Game_Visualiser_ReadState(H, perspective(OMNISCIENT), snap), 'ReadState'); return readHeader(dv(), snap); };

  const map = includeCamps ? readMapCamps(E, H) : null;
  if (map) process.stderr.write(`[replaydump] map ${map.width}x${map.height} ${map.symmetry}, ${map.numCamps} map camps in ${map.numGroups} groups\n`);
  check(X.Game_Visualiser_Timeline_GetMain(H, out), 'Timeline_GetMain');
  const TL = dv().getBigUint64(out, true);
  check(X.Game_Visualiser_Timeline_Info(H, TL, args, args + 8, args + 16), 'Timeline_Info');
  const size = dv().getUint32(args, true);
  process.stderr.write(`[replaydump] ${path.basename(file)}: ${replay.length} bytes, main timeline ${TL} with ${size} input positions\n`);

  check(X.Game_Visualiser_Timeline_Seek(H, TL, 0, 0), 'Timeline_Seek');
  const emit = (snap, h) => {
    const draft = h.phase === 12;
    if (draft && !includeDraft) return false;
    const rec = { round: h.round, phase: h.phase, phaseName: PHASES[h.phase] ?? String(h.phase), position: h.inputPosition, substep: h.step.substep,
      outcome: h.outcome, submittedGems: h.submittedGems, champions: readChampions(dv(), snap) };
    if (draft) rec.draft = true;
    if (includeCamps) rec.camps = readCamps(dv(), snap, map);
    if (everyStep) rec.step = h.step;
    if (includeVis) { // enemy champions each team sees (perspective read of the same engine state)
      // vision is per champion: vis[i] = enemy champion indices that champion i sees (null if dead / unreadable)
      rec.vis = rec.champions.map((me) => { if (!me.alive) return null;
        if (X.Game_Visualiser_ReadState(H, perspective({ team: me.team, champion: me.index }), snapC) !== 0) return null;
        return readChampions(dv(), snapC).filter((c) => c.team !== me.team && c.x >= 0).map((c) => c.index); });
    }
    emitLine(JSON.stringify(rec) + '\n');
    return true;
  };

  // --deltas (top10 study): instead of full states, one compact line per step that changed a champion's or camp's health
  // or whose actor is a champion: {r, ak, ai, k, dc:[[champIdx, dHp]...], dk:[[campEntityIdx, dHp]...]}. Implies every step.
  const MAXR = +(process.env.MAXR || 1e9);
  const deltas = argv.includes('--deltas'), rawChamps = argv.includes('--raw');
  const lightHp = (snap) => {
    const d = dv(), nc = d.getUint32(snap + CHAMP.countOffset, true), nk = d.getUint32(snap + CAMPS.countOffset, true);
    const c = new Float64Array(nc), k = new Float64Array(nk);
    for (let i = 0; i < nc; i++) c[i] = d.getFloat32(snap + CHAMP.dataOffset + i * CHAMP.stride + 28, true);
    for (let i = 0; i < nk; i++) k[i] = d.getFloat32(snap + CAMPS.dataOffset + i * CAMPS.stride + 28, true);
    return { c, k };
  };
  if (deltas) {
    let s = readState(snapA), hp = lightHp(snapA), n = 0;
    for (;;) {
      const code = X.Game_Visualiser_Timeline_ReplayNext(H, 1);
      if (code !== 0) break;
      const h = readState(snapA), hp2 = lightHp(snapA), dc = [], dk = [];
      for (let i = 0; i < Math.min(hp.c.length, hp2.c.length); i++) if (hp2.c[i] !== hp.c[i]) dc.push([i, r2(hp2.c[i] - hp.c[i])]);
      for (let i = 0; i < Math.min(hp.k.length, hp2.k.length); i++) if (hp2.k[i] !== hp.k[i]) dk.push([i, r2(hp2.k[i] - hp.k[i])]);
      if (dc.length || dk.length || h.step.actorKind === 1) {
        const rec = { r: h.round, ak: h.step.actorKind, ai: h.step.actorIndex, k: h.step.kind };
        if (dc.length) rec.dc = dc; if (dk.length) rec.dk = dk;
        emitLine(JSON.stringify(rec) + '\n');
      }
      hp = hp2; s = h; n++;
      if (h.round > MAXR) break;
      if (n > 5_000_000) throw new Error('too many steps');
    }
    X.Game_Destroy(H); return;
  }
  if (rawChamps) {
    const emitRaw = (snap, h) => {
      const d = dv(), nc = d.getUint32(snap + CHAMP.countOffset, true), raw = [];
      for (let i = 0; i < nc; i++) { const b = snap + CHAMP.dataOffset + i * CHAMP.stride, w = [];
        for (let o = 0; o < CHAMP.stride; o += 4) w.push(d.getUint32(b + o, true)); raw.push(w); }
      emitLine(JSON.stringify({ round: h.round, phase: h.phase, raw }) + '\n');
    };
    let c = snapA, p = snapB, hc = readState(c), hp = null;
    for (;;) {
      if (hp && hp.round !== hc.round) emitRaw(p, hp);
      const code = X.Game_Visualiser_Timeline_ReplayNext(H, 1);
      if (code !== 0) break;
      [c, p] = [p, c]; hp = hc; hc = readState(c);
    }
    X.Game_Destroy(H); return;
  }

  let cur = snapA, prev = snapB;
  let hCur = readState(cur), hPrev = null, steps = 0, roundsEmitted = 0;
  for (;;) {
    if (everyStep) emit(cur, hCur);
    else if (hPrev && hPrev.round !== hCur.round && emit(prev, hPrev)) roundsEmitted++;
    const code = X.Game_Visualiser_Timeline_ReplayNext(H, 1);
    if (code !== 0) { if (code !== 18) process.stderr.write(`[replaydump] ReplayNext stopped: code ${code}: ${rd(X.GetLastErrorMsg())}\n`); break; }
    [cur, prev] = [prev, cur]; hPrev = hCur;
    hCur = readState(cur); steps++;
    if (hCur.round > MAXR + 1) break;
    if (hCur.inputPosition === hPrev.inputPosition && hCur.step.substep === hPrev.step.substep && hCur.round === hPrev.round) { process.stderr.write('[replaydump] timeline made no progress; stopping\n'); break; }
    if (steps > 5_000_000) throw new Error('too many steps');
  }
  if (!everyStep && emit(cur, hCur)) roundsEmitted++;
  process.stderr.write(`[replaydump] replayed ${steps} steps, emitted ${roundsEmitted} round lines\n`);

  // final summary from the statistics API plus the final state
  const summary = { summary: true, file: path.basename(file), finished: hCur.phase === 11 || hCur.outcome !== 0, finalRound: hCur.round,
    outcome: hCur.outcome, outcomeName: OUTCOMES[hCur.outcome] ?? `unknown(${hCur.outcome})`, submittedGems: hCur.submittedGems, timelineSize: size, steps };
  const SB = X.Engine_Malloc(4096); // 1168 bytes per champion with engine 2.0.0
  if (X.Game_Statistics_GetSummary(H, SB) === 0) {
    const s = readSummary(dv(), SB);
    summary.statistics = { engineVersionPacked: s.engineVersionPacked, outcome: s.outcome, outcomeName: OUTCOMES[s.outcome] ?? `unknown(${s.outcome})`, round: s.round,
      submittedGems: s.submittedGems, draftPicks: s.draftPicks, champions: [] };
    for (let i = 0; i < s.numChampions; i++) { if (X.Game_Statistics_GetChampion(H, i, SB) !== 0) break; summary.statistics.champions.push(readChampionStats(dv(), SB)); }
  } else summary.statisticsError = rd(X.GetLastErrorMsg());
  emitLine(JSON.stringify(summary) + '\n');
  X.Game_Destroy(H);
}
process.stdout.on('error', (e) => { if (e.code === 'EPIPE') process.exit(0); throw e; }); // tolerate `| head`
main().catch((e) => { process.stderr.write('replaydump: ' + (e.stack || e.message) + '\n'); process.exit(1); });
