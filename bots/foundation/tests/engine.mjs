// Controlled official-engine mechanics. Sandbox setup is test-only knowledge.
// Snapshot ABI follows tools/replaydump.js; refuse a changed layout.
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';

const path = process.argv[2];
assert(path, 'Usage: node engine.mjs <official visualiser engine.wasm>');
let instance;
const view = () => new DataView(instance.exports.memory.buffer);
const bytes = (p, n) => new Uint8Array(instance.exports.memory.buffer, p, n);
const wasi = {
    environ_get: () => 0,
    environ_sizes_get: (p, n) => { view().setUint32(p, 0, true); view().setUint32(n, 0, true); return 0; },
    fd_close: () => 0, fd_fdstat_get: () => 0, fd_prestat_get: () => 8,
    fd_prestat_dir_name: () => 8, fd_seek: () => 70,
    fd_read: (_fd, _p, _n, out) => { view().setUint32(out, 0, true); return 0; },
    fd_write: (_fd, p, n, out) => {
        let size = 0;
        for (let i = 0; i < n; ++i) size += view().getUint32(p + i * 8 + 4, true);
        view().setUint32(out, size, true); return 0;
    },
    random_get: (p, n) => { bytes(p, n).fill(0); return 0; },
    proc_exit: code => { throw Error(`Engine exited ${code}`); },
};
const binary = fs.readFileSync(path);
instance = new WebAssembly.Instance(new WebAssembly.Module(binary), {wasi_snapshot_preview1: wasi});
const E = instance.exports;
E._initialize();
assert.equal(E.Game_Visualiser_SnapshotSize(), 184696, 'Unknown snapshot ABI');
assert.equal(E.Game_Visualiser_TimelineSnapshotSize(), 40152, 'Unknown timeline ABI');
const out = E.Engine_Malloc(256), scratch = E.Engine_Malloc(256), snap = E.Engine_Malloc(184696);
const u32 = p => view().getUint32(p, true);
function checked(name, ...args) { assert.equal(E[name](...args), 0, name); }
function entity(id) { view().setUint32(scratch, 1, true); view().setUint32(scratch+4, id, true); return scratch; }
function position(x, y) { view().setInt32(scratch+8, x, true); view().setInt32(scratch+12, y, true); return scratch+8; }
function state(g) {
    view().setUint32(scratch+16, 2, true); view().setUint32(scratch+20, 0xffffffff, true);
    checked('Game_Visualiser_ReadState', g, scratch+16, snap);
    return {
        round: u32(snap+8), current: u32(snap+60), phase: u32(snap+24), input: !!u32(snap+20),
        champions: Array.from({length: u32(snap+120)}, (_, i) => {
            const p = snap+140+i*456;
            return {id: u32(p+4), x: view().getInt32(p+20, true), y: view().getInt32(p+24, true),
                flags: u32(p+36), gems: u32(p+236)};
        }),
    };
}
function self(g) {
    // champion_info layout is public in sdk/cpp/imports.h; these are SDK flags,
    // not the differently packed visualiser flags at snapshot offset 36.
    state(g);
    checked('Game_API_Champion_Get',g,scratch+16,0,out);
    const result = {x:view().getInt32(out+8,true),y:view().getInt32(out+12,true),flags:u32(out+40)};
    result.gems = state(g).champions.find(c => c.id === 0).gems;
    return result;
}
function create(picks = [0, 1, 4, 5]) {
    checked('MapBuilder_Create', 32, 32, 0, out);
    const map = view().getBigUint64(out, true);
    checked('MapBuilder_SetNumChampsPerTeam', map, 2);
    [1,1,4,4].forEach((n, i) => view().setInt32(scratch+i*4, n, true));
    checked('MapBuilder_SetTeamASpawnArea', map, scratch);
    checked('MapBuilder_AddWall', map, 14, 15);
    checked('MapBuilder_AddAltar', map, 13, 15);
    checked('MapBuilder_AddCamp', map, 0, 13, 14, out);
    checked('MapBuilder_VerifyIntegrity', map);
    checked('MapBuilder_Encode', map, out, out+4);
    checked('Game_FromMapFileBytes', u32(out), u32(out+4), out, 0);
    const game = view().getBigUint64(out, true);
    checked('MapBuilder_Destroy', map);
    checked('Game_Runner_Init', game);
    let pick = 0;
    for (let i=0; i<1000; ++i) {
        const s = state(game);
        if (s.input && s.phase === 12) {
            checked('Game_Action_Draft', game, picks[pick++]);
            checked('Game_Runner_EndTurn', game, 0);
        }
        else if (s.input && s.phase === 10) return game;
        else checked('Game_Runner_Step', game);
    }
    throw Error('Draft exceeded bound');
}
function teleport(g, id, x, y) { checked('Game_Sandbox_Teleport', g, entity(id), position(x,y)); }
function nextOwn(g) {
    checked('Game_Runner_EndTurn', g, 0);
    for (let i=0; i<1000; ++i) {
        const s = state(g);
        if (s.input && s.phase === 10) {
            if (s.current === 0) return;
            checked('Game_Runner_EndTurn', g, 0);
        } else checked('Game_Runner_Step', g);
    }
    throw Error('Turn advance exceeded bound');
}
const cases = [];
function test(name, run, picks) {
    const game = create(picks);
    try { run(game); cases.push(name); }
    finally { checked('Game_Destroy', game); }
}
test('movement changes position without starting a channel', g => {
    teleport(g,0,10,10);
    checked('Game_Action_Move',g,10,11,out);
    assert.equal(u32(out),1); assert.equal(self(g).y,11); assert.equal(self(g).flags & 6,0);
});
test('known blocked movement is rejected without moving', g => {
    teleport(g,0,13,16);
    assert.notEqual(E.Game_Action_Move(g,14,15,out),0);
    assert.equal(self(g).x,13); assert.equal(self(g).y,16);
});
test('recall start is distinct from completion and cancellation', g => {
    teleport(g,0,10,10);
    checked('Game_Action_Recall',g);
    assert(self(g).flags & 2); assert.equal(self(g).x,10);
    checked('Game_Action_CancelChannel',g);
    assert.equal(self(g).flags & 2,0); assert.equal(self(g).x,10);
});
test('recall eventually completes on a later owner turn', g => {
    teleport(g,0,10,10); checked('Game_Action_Recall',g);
    for (let i=0; i<8 && (self(g).flags & 2); ++i) nextOwn(g);
    assert.equal(self(g).flags & 2,0);
    assert(self(g).x !== 10 || self(g).y !== 10);
});
test('empty-bag tribute is rejected without a channel', g => {
    teleport(g,0,12,15);
    assert.notEqual(E.Game_Action_SubmitGems(g,position(13,15)),0);
    assert.equal(self(g).flags & 4,0); assert.equal(self(g).gems,0);
});
test('tribute starts before gems are banked and later completes', g => {
    teleport(g,0,12,15); checked('Game_Sandbox_GiveGems',g,0,20);
    checked('Game_Action_SubmitGems',g,position(13,15));
    assert(self(g).flags & 4); assert.equal(self(g).gems,20);
    checked('Game_API_GetSubmittedGemCount',g,0,out);
    assert.equal(view().getBigUint64(out,true),0n);
    for (let i=0; i<8 && (self(g).flags & 4); ++i) nextOwn(g);
    assert.equal(self(g).flags & 4,0); assert.equal(self(g).gems,0);
    checked('Game_API_GetSubmittedGemCount',g,0,out);
    assert.equal(view().getBigUint64(out,true),20n);
});
test('ranged walk blocks ordinary attack; reset permits the attack', g => {
    teleport(g,0,10,10); teleport(g,2,12,10);
    checked('Game_Action_Move',g,10,11,out);
    assert.notEqual(E.Game_Action_Attack(g,entity(2)),0);
    view().setUint32(scratch+24,0,true); view().setUint32(scratch+28,0,true);
    checked('Game_Action_Cast',g,0,scratch+24,position(0,0),out);
    checked('Game_Action_Attack',g,entity(2));
    assert.notEqual(E.Game_Action_Move(g,10,12,out),0);
}, [1,0,0,4]);
console.log(JSON.stringify({engine_sha256: crypto.createHash('sha256').update(binary).digest('hex'),
    passed: true, cases, scope: 'Controlled official engine actions; guest fuel is checked separately.'}));
