// Print metadata of .map26a files: size, symmetry, champs, spawn area, camps, altars/walls/bushes/holes counts.
const fs = require('fs');
const WASM = '/root/.cache/cambc/assets/a482d02100c0a35cf437a6d785dca78aabd98563e62ecb1864db62ad5df15424/mapeditor/assets/v0_0_1-ctH8uuEb.wasm';
const CAMPN = ['NONE','WOLF','ELK','GEM_CLUSTER','GOLD_CLUSTER','MONOLITH'];
async function main() {
  const bytes = fs.readFileSync(WASM); let mem; const td = new TextDecoder();
  const dv = () => new DataView(mem.buffer); const z = () => 0;
  const rd = (p) => { const u = new Uint8Array(mem.buffer); let e = p; while (u[e]) e++; return td.decode(u.subarray(p, e)); };
  const wasi = { random_get(p, n) { require('crypto').randomFillSync(new Uint8Array(mem.buffer, p, n)); return 0; },
    clock_time_get(i, pr, o) { dv().setBigUint64(o, BigInt(Date.now()) * 1000000n, true); return 0; },
    environ_sizes_get(a, b) { dv().setUint32(a, 0, true); dv().setUint32(b, 0, true); return 0; }, environ_get: z, args_sizes_get(a, b) { dv().setUint32(a, 0, true); dv().setUint32(b, 0, true); return 0; }, args_get: z,
    fd_close: z, fd_fdstat_get(fd, p) { const d = dv(); d.setUint8(p, 2); d.setUint16(p + 2, 0, true); d.setBigUint64(p + 8, 0n, true); d.setBigUint64(p + 16, 0n, true); return 0; },
    fd_prestat_get() { return 8; }, fd_prestat_dir_name() { return 8; }, fd_read(fd, i, n, o) { dv().setUint32(o, 0, true); return 0; }, fd_seek() { return 70; },
    fd_write(fd, iovs, n, out) { const d = dv(); let c = 0; for (let i = 0; i < n; i++) c += d.getUint32(iovs + i * 8 + 4, true); d.setUint32(out, c, true); return 0; }, proc_exit(c) { throw new Error('exit ' + c); } };
  const { instance } = await WebAssembly.instantiate(bytes, { wasi_snapshot_preview1: wasi, deep_wasm: { on_assert_fail_impl() { return 1; } } });
  const X = instance.exports; mem = X.memory; X._initialize(); const out = X.Engine_Malloc(64);
  const chk = (c, w) => { if (c !== 0) throw new Error(w + ': ' + c + ' ' + rd(X.GetLastErrorMsg())); };
  const f = process.argv[2];
  const m = fs.readFileSync(f); const buf = X.Engine_Malloc(m.length); new Uint8Array(mem.buffer, buf, m.length).set(m);
  chk(X.MapBuilder_FromFileBytes(buf, m.length, out), 'FromFileBytes'); const h = dv().getBigUint64(out, true);
  chk(X.MapBuilder_GetBitboardMetadata(h, out), 'meta'); const w = dv().getInt32(out, true), hh = dv().getInt32(out + 4, true);
  chk(X.MapBuilder_GetSymmetry(h, out), 'sym'); const sym = ['H','V','R180'][dv().getInt32(out, true)];
  chk(X.MapBuilder_GetNumChampsPerTeam(h, out), 'nch'); const nch = dv().getUint32(out, true);
  chk(X.MapBuilder_GetTeamASpawnArea(h, out), 'spawn'); const sa = [0, 4, 8, 12].map(o => dv().getInt32(out + o, true));
  const grid = [];
  for (let y = 0; y < hh; y++) { let row = ''; for (let x = 0; x < w; x++) {
    const g = (fn) => X[fn](h, x, y, out) === 0 && dv().getUint8(out);
    row += g('MapBuilder_GetWall') ? '#' : g('MapBuilder_GetHole') ? 'o' : g('MapBuilder_GetAltar') ? 'A' : g('MapBuilder_GetBush') ? '"' : '.'; } grid.push(row); }
  chk(X.MapBuilder_GetNumCamps(h, out), 'nc'); const nc = dv().getUint32(out, true);
  const camps = [], hidx = new Map();
  for (let i = 0; i < nc; i++) { chk(X.MapBuilder_GetCampHandle(h, i, out), 'ch'); const ch = dv().getBigUint64(out, true); hidx.set(ch, i);
    chk(X.MapBuilder_GetCamp(h, ch, out), 'gc'); camps.push({ type: CAMPN[dv().getInt32(out, true) + 1], x: dv().getInt32(out + 4, true), y: dv().getInt32(out + 8, true) }); }
  chk(X.MapBuilder_GetNumCampGroups(h, out), 'ng'); const ng = dv().getUint32(out, true);
  const groups = [];
  for (let g = 0; g < ng; g++) { chk(X.MapBuilder_GetCampGroupHandle(h, g, out), 'gh'); const gh = dv().getBigUint64(out, true);
    chk(X.MapBuilder_GetCampGroup(h, gh, out), 'gg'); const r = { gems: dv().getUint32(out, true), gold: dv().getUint32(out + 4, true), respawn: dv().getUint32(out + 8, true), n: dv().getUint32(out + 12, true), camps: [] };
    for (let j = 0; j < r.n; j++) { chk(X.MapBuilder_GetCampGroupCamp(h, gh, j, out), 'gc'); r.camps.push(hidx.get(dv().getBigUint64(out, true))); }
    groups.push(r); }
  console.log(JSON.stringify({ file: f, w, h: hh, sym, nch, spawnA: sa, grid, camps, groups }));
}
main().catch(e => { console.error(e.message); process.exit(1); });
