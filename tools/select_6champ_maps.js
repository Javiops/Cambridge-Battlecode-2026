#!/usr/bin/env node
// Read the exact champion count from .map26a files and make lists for tools/ab.py.
// Run from the repository root: node tools/select_6champ_maps.js
// Uses the same CAMBC map-editor WASM API as tools/mapjson.js.
'use strict';
const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');

function locateWasm() {
  if (process.env.CAMBC_MAPEDITOR_WASM) return process.env.CAMBC_MAPEDITOR_WASM;
  const roots = [path.join(os.homedir(), '.cache', 'cambc', 'assets')];
  if (process.env.LOCALAPPDATA) roots.push(path.join(process.env.LOCALAPPDATA, 'cambc', 'assets'));
  let best = null;
  for (const root of roots) {
    let dirs = [];
    try { dirs = fs.readdirSync(root); } catch { continue; }
    for (const d of dirs) {
      const dir = path.join(root, d, 'mapeditor', 'assets');
      let names = [];
      try { names = fs.readdirSync(dir); } catch { continue; }
      for (const name of names) {
        if (!name.endsWith('.wasm')) continue;
        const candidate = path.join(dir, name);
        const mtime = fs.statSync(candidate).mtimeMs;
        if (!best || mtime > best.mtime) best = { path: candidate, mtime };
      }
    }
  }
  if (!best) throw Error('Map editor WASM not found. Run cambc init, or set CAMBC_MAPEDITOR_WASM.');
  return best.path;
}

async function main() {
  const wasmPath = locateWasm();
  const source = fs.readFileSync(wasmPath);
  let memory;
  const dv = () => new DataView(memory.buffer);
  const zero = () => 0;
  const wasi = {
    random_get(p, n) { crypto.randomFillSync(new Uint8Array(memory.buffer, p, n)); return 0; },
    clock_time_get(i, precision, out) { dv().setBigUint64(out, BigInt(Date.now()) * 1000000n, true); return 0; },
    environ_sizes_get(a, b) { dv().setUint32(a, 0, true); dv().setUint32(b, 0, true); return 0; },
    environ_get: zero,
    args_sizes_get(a, b) { dv().setUint32(a, 0, true); dv().setUint32(b, 0, true); return 0; },
    args_get: zero,
    fd_close: zero,
    fd_fdstat_get(fd, p) {
      const d = dv(); d.setUint8(p, 2); d.setUint16(p + 2, 0, true);
      d.setBigUint64(p + 8, 0n, true); d.setBigUint64(p + 16, 0n, true);
      return 0;
    },
    fd_prestat_get() { return 8; }, fd_prestat_dir_name() { return 8; },
    fd_read(fd, i, n, out) { dv().setUint32(out, 0, true); return 0; },
    fd_seek() { return 70; },
    fd_write(fd, iovs, n, out) {
      let size = 0;
      for (let i = 0; i < n; i++) size += dv().getUint32(iovs + i * 8 + 4, true);
      dv().setUint32(out, size, true);
      return 0;
    },
    proc_exit(code) { throw Error(`WASM exited: ${code}`); }
  };
  const { instance } = await WebAssembly.instantiate(source, {
    wasi_snapshot_preview1: wasi,
    deep_wasm: { on_assert_fail_impl() { return 1; } }
  });
  const X = instance.exports;
  memory = X.memory;
  X._initialize();
  const out = X.Engine_Malloc(64);

  function readTeamSize(file) {
    const bytes = fs.readFileSync(file);
    const buf = X.Engine_Malloc(bytes.length);
    new Uint8Array(memory.buffer, buf, bytes.length).set(bytes);
    const err = X.MapBuilder_FromFileBytes(buf, bytes.length, out);
    if (err !== 0) throw Error(`MapBuilder_FromFileBytes returned ${err}`);
    const handle = dv().getBigUint64(out, true);
    const status = X.MapBuilder_GetNumChampsPerTeam(handle, out);
    if (status !== 0) throw Error(`MapBuilder_GetNumChampsPerTeam returned ${status}`);
    return dv().getUint32(out, true);
  }

  const outputDir = path.join('out', 'six_champ_maps');
  fs.mkdirSync(outputDir, { recursive: true });
  let total = 0;
  const allSix = [];
  for (const [set, folder] of [
    ['official', 'maps'], ['hold', 'maps_hold60'], ['dev', 'maps_dev200']
  ]) {
    if (!fs.existsSync(folder)) {
      console.log(`${set}: folder ${folder} not found; skipped`);
      continue;
    }
    const maps = fs.readdirSync(folder).filter(f => f.endsWith('.map26a')).sort();
    const six = [];
    const errors = [];
    for (const m of maps) {
      const f = path.join(folder, m).replaceAll('\\', '/');
      try {
        if (readTeamSize(f) === 6) six.push(f);
      } catch (err) {
        errors.push(`${f}: ${err.message}`);
      }
    }
    const dest = path.join(outputDir, `${set}.txt`);
    fs.writeFileSync(dest, six.join(',') + (six.length ? '\n' : ''));
    allSix.push(...six);
    total += six.length;
    console.log(`${set}: ${six.length} six-champion maps / ${maps.length} total -> ${dest}`);
    if (errors.length) {
      console.error(`${errors.length} map(s) could not be classified in ${folder}:`);
      for (const msg of errors.slice(0, 12)) console.error(`  ${msg}`);
      process.exitCode = 1;
    }
  }
  fs.writeFileSync(path.join(outputDir, 'all.txt'), allSix.join(',') + (allSix.length ? '\n' : ''));
  console.log(`TOTAL: ${total} six-champion maps. Pass the contents of each .txt to tools/ab.py --sets.`);
}

main().catch(err => { console.error(err.stack || String(err)); process.exitCode = 1; });
