# fuelfit o41 (farm section): choose_target's walking distance to every camp group read from ONE export of the
# reached mask (bitboard, packed bits LSB-first, index y*w+x, ~190 fuel) and ONE export of the distance field
# (uint16 per tile, row-major, ~460 fuel on 41x41 .. ~2500 on 100x100) instead of bitboard.is_set (~47) +
# distance_field.get (~41) per group tile (~180 tiles on a normal map = ~16k of choose_target's ~26k).
# Exact: both exports are verified tile-by-tile copies of is_set/get (bench on big_world: 0 mismatches of 10000),
# group tiles never change after init_groups, so their linear indices are computed once per game, and the min
# over the same tiles in the same order gives the same pd_gd. No fuel_ok, fixed loop bounds, no new output.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""    if (have_pd && !cached) {  // the walking distance to each group, read once per tile
        s.pd_gd.assign(s.groups.size(), -1);
        attempt([&] {
            for (std::size_t i = 0; i < s.groups.size(); ++i) {
                int b = 1 << 20;
                for (auto t : s.groups[i].tiles)
                    if (s.pdv.is_set(t)) b = std::min(b, static_cast<int>(s.pdf.get(t)));
                s.pd_gd[i] = b < (1 << 20) ? b : -1;
            }
            s.pd_pos = pos;
            return true;
        });
    }""","""    if (have_pd && !cached) {  // the walking distance to each group, read once per tile
        s.pd_gd.assign(s.groups.size(), -1);
        attempt([&] {
            // fuelfit o41: one export of the reached mask and one of the distances, then plain C++ over the
            // groups' tile indices (fixed after init_groups, computed once) instead of is_set + get per tile.
            const int w = bc::map::width();
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
                    if ((vb[k >> 3] >> (k & 7)) & 1) b = std::min(b, static_cast<int>(db[k]));
                s.pd_gd[i] = b < (1 << 20) ? b : -1;
            }
            s.pd_pos = pos;
            return true;
        });
    }""")
open(p,'w',newline='').write(s)
print("o41 ok")
