# fuelfit o48 (farm section): the once-per-game farm precomputations out of the first playing turn.
# Measured by the integrator on b6 (unlimited fuel): the first choose_target_impl call cost 41-54k of its own C++ and the
# first refresh_groups 16-27k, all of it one-time work: the per-group tile index lists (o41 and o46 each built their own:
# one vector push_back is ~59 fuel, 100-300 tiles), the per-group scoring constants (o45) and the first resize of every
# snapshot buffer (std::vector zero-fills: ~10k for a 20KB distance snapshot on 100x100).
# Now: (1) `bool farm_warmup(State& s, int quota)` builds the shared tile index list and the scoring constants for up to
# `quota` groups per call and returns true when every group is done; the init steps call it with a fixed price per group,
# and any farm code that needs the tables before the warm-up finished completes it on the spot (same tables either way:
# the decision never depends on when they were built). (2) BitSnap/DistSnap keep their buffer in a heap array that is NOT
# zero-filled (new T[n]; the export overwrites every byte before any read), so the first load costs the export only.
# Exact: the same values are computed, only earlier. No fuel reads, fixed bounds, no new output. Over b6 (o41-o47).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)

rep("""struct State {""","""struct FarmGC { bool near_en, half; double cycle; };  // fuelfit o48: per-group scoring constants (o45)
struct State {""")
rep("""    std::size_t pd_rf_done = 0;             // fuelfit o45: groups whose field is computed (in index order)
""","""    std::size_t pd_rf_done = 0;             // fuelfit o45: groups whose field is computed (in index order)
    std::vector<std::vector<int>> fw_gidx;  // fuelfit o48: linear tile indices per group (o41 / o46)
    std::vector<FarmGC> fw_gc;              // fuelfit o48: scoring constants per group (o45)
    std::size_t fw_done = 0;                // fuelfit o48: groups warmed up (in index order)
""")

rep("""struct BitSnap {
    std::vector<std::uint8_t> b;
    int w = 0;
    void load(const bc::bitboard& bb) {
        w = bc::map::width();
        b.resize(bc::bitboard::linear_buffer_size());
        bb.export_linear_buffer(std::span<std::uint8_t>(b.data(), b.size()));
    }
    bool is_set(vec2 p) const { const int k = p.y * w + p.x; return (b[k >> 3] >> (k & 7)) & 1; }
};
struct DistSnap {
    std::vector<std::uint16_t> d;
    int w = 0;
    void load(const bc::distance_field& df) {
        w = bc::map::width();
        d.resize(bc::distance_field::linear_buffer_size() / sizeof(std::uint16_t));
        df.export_linear_buffer(std::span<std::uint16_t>(d.data(), d.size()));
    }
    int get(vec2 p) const { return d[p.y * w + p.x]; }
};
#include "mapplan_game.h"
""","""struct BitSnap {  // fuelfit o48: heap array without zero-fill (the export writes every byte before any read)
    std::unique_ptr<std::uint8_t[]> b;
    std::size_t n = 0;
    int w = 0;
    void load(const bc::bitboard& bb) {
        w = bc::map::width();
        if (!b) { n = bc::bitboard::linear_buffer_size(); b.reset(new std::uint8_t[n]); }
        bb.export_linear_buffer(std::span<std::uint8_t>(b.get(), n));
    }
    bool is_set(vec2 p) const { const int k = p.y * w + p.x; return (b[k >> 3] >> (k & 7)) & 1; }
};
struct DistSnap {
    std::unique_ptr<std::uint16_t[]> d;
    std::size_t n = 0;
    int w = 0;
    void load(const bc::distance_field& df) {
        w = bc::map::width();
        if (!d) { n = bc::distance_field::linear_buffer_size() / sizeof(std::uint16_t); d.reset(new std::uint16_t[n]); }
        df.export_linear_buffer(std::span<std::uint16_t>(d.get(), n));
    }
    int get(vec2 p) const { return d[p.y * w + p.x]; }
};
// fuelfit o48: once-per-game farm tables, up to `quota` groups per call; true when every group is done. Needs the groups,
// the centres (init_map/init_groups) and spawn_pd (init_paths), so it runs after init stage 3. Same tables whenever built.
bool farm_warmup(State& s, int quota) {
    if (s.fw_gidx.size() != s.groups.size()) {
        s.fw_gidx.assign(s.groups.size(), {});
        s.fw_gc.assign(s.groups.size(), FarmGC{});
        s.fw_done = 0;
    }
    const int w = bc::map::width();
    for (int k = 0; k < quota && s.fw_done < s.groups.size(); ++k, ++s.fw_done) {
        const std::size_t i = s.fw_done;
        const Group& g = s.groups[i];
        std::vector<int>& ix = s.fw_gidx[i];
        ix.reserve(g.tiles.size());
        for (auto t : g.tiles) ix.push_back(t.y * w + t.x);
        s.fw_gc[i].near_en = dist(g.center, s.en_center) < 8;
        s.fw_gc[i].half = dist(g.center, s.spawn_center) - dist(g.center, s.en_center) > 6;
        s.fw_gc[i].cycle = 8.0 + (P_PATHD && g.spawn_pd >= 0 ? g.spawn_pd : dist(s.spawn_center, g.center));
    }
    return s.fw_done == s.groups.size();
}
inline void farm_warmup_now(State& s) { if (s.fw_done != s.groups.size() || s.fw_gidx.size() != s.groups.size()) farm_warmup(s, 1 << 30); }
#include "mapplan_game.h"
""")

# o46 refresh_groups: shared tile indices
rep("""    static BitSnap vis_s;
    static std::vector<std::vector<int>> gtiles;
    if (gtiles.size() != s.groups.size()) {
        const int w = bc::map::width();
        gtiles.assign(s.groups.size(), {});
        for (std::size_t i = 0; i < s.groups.size(); ++i)
            for (auto t : s.groups[i].tiles) gtiles[i].push_back(t.y * w + t.x);
    }
    if (!attempt([&] { vis_s.load(s.vis); return true; })) return;""","""    static BitSnap vis_s;
    farm_warmup_now(s);  // fuelfit o48: the tile index lists come from the warm-up
    const std::vector<std::vector<int>>& gtiles = s.fw_gidx;
    if (!attempt([&] { vis_s.load(s.vis); return true; })) return;""")

# o41 block: shared indices, uninitialised export buffers
rep("""            const int w = bc::map::width();
            static std::vector<std::vector<int>> gidx;
            if (gidx.size() != s.groups.size()) {
                gidx.assign(s.groups.size(), {});
                for (std::size_t i = 0; i < s.groups.size(); ++i)
                    for (auto t : s.groups[i].tiles) gidx[i].push_back(t.y * w + t.x);
            }
            static std::vector<std::uint8_t> vb;
            static std::vector<std::uint16_t> db;
            vb.resize(bc::bitboard::linear_buffer_size());
            db.resize(bc::distance_field::linear_buffer_size() / sizeof(std::uint16_t));
            s.pdv.export_linear_buffer(std::span<std::uint8_t>(vb.data(), vb.size()));
            s.pdf.export_linear_buffer(std::span<std::uint16_t>(db.data(), db.size()));
            for (std::size_t i = 0; i < s.groups.size(); ++i) {
                int b = 1 << 20;
                for (int k : gidx[i])
                    if ((vb[k >> 3] >> (k & 7)) & 1) b = std::min(b, static_cast<int>(db[k]));""","""            farm_warmup_now(s);  // fuelfit o48: shared tile index lists, buffers without zero-fill
            const std::vector<std::vector<int>>& gidx = s.fw_gidx;
            static BitSnap vb;
            static DistSnap db;
            vb.load(s.pdv);
            db.load(s.pdf);
            for (std::size_t i = 0; i < s.groups.size(); ++i) {
                int b = 1 << 20;
                for (int k : gidx[i])
                    if ((vb.b[k >> 3] >> (k & 7)) & 1) b = std::min(b, static_cast<int>(db.d[k]));""")

# o45 constants
rep("""    struct GroupConst { bool near_en, half; double cycle; };
    static std::vector<GroupConst> gc;
    if (gc.size() != s.groups.size()) {
        gc.resize(s.groups.size());
        for (std::size_t i = 0; i < s.groups.size(); ++i) {
            const Group& g = s.groups[i];
            gc[i].near_en = dist(g.center, s.en_center) < 8;
            gc[i].half = dist(g.center, s.spawn_center) - dist(g.center, s.en_center) > 6;
            gc[i].cycle = 8.0 + (P_PATHD && g.spawn_pd >= 0 ? g.spawn_pd : dist(s.spawn_center, g.center));
        }
    }""","""    farm_warmup_now(s);  // fuelfit o48: per-group constants from the warm-up
    const std::vector<FarmGC>& gc = s.fw_gc;""")
if '#include <memory>' not in s:
    rep("#include <optional>\n","#include <optional>\n#include <memory>\n")
open(p,'w',newline='').write(s)
print("o48 ok")
