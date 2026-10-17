#pragma once
// draft_plan.h - proven bank + ward static planner.
// Uses draft-memory bytes 32..255. No hunt/idle/mid/items logic is enabled here.

#ifndef P_DP_BANK
#define P_DP_BANK 0
#endif
#ifndef P_DP_WARDS
#define P_DP_WARDS 0
#endif
#ifndef P_DP_FINISH
#define P_DP_FINISH 0
#endif
#ifndef P_DP_FINISH_NEAR
#define P_DP_FINISH_NEAR 60
#endif
#ifndef P_DP_FINISH_RECALL_HP
#define P_DP_FINISH_RECALL_HP 35
#endif
#ifndef P_DP_BANK_QUIET
#define P_DP_BANK_QUIET 35
#endif
#ifndef P_DP_BANK_LONG
#define P_DP_BANK_LONG 60
#endif
#ifndef P_DP_BANK_MID
#define P_DP_BANK_MID 40
#endif
#ifndef P_DP_WARDERS
#define P_DP_WARDERS 2
#endif

namespace draftplan {
constexpr int SIZE = 256;
constexpr int OFF = 32;
constexpr std::uint8_t F_LONG = 1u << 0;
constexpr std::uint8_t F_FEW_ALTARS = 1u << 1;
constexpr std::uint8_t F_FAR_FIGHT = 1u << 2;
constexpr std::uint8_t F_OPEN = 1u << 3;
constexpr std::uint8_t F_CENTRAL_ALTAR = 1u << 4;

struct Runtime {
    bool valid = false;
    int w = 0, h = 0, team_size = 0, altars = 0, path = -1, open = 0;
    std::uint8_t flags = 0;
    vec2 central{-1,-1}, safe{-1,-1}, ward[2]{{-1,-1},{-1,-1}};
    int ward_n = 0;
    struct A { int x=-1,y=-1,da=255,db=255; } altar[24];
    int altar_n = 0;
};
inline Runtime R;
inline std::array<std::byte, SIZE> packet{};
inline bool prepared = false;

inline int clamp8(int x) { return std::max(0, std::min(255, x)); }
inline void put8(int o, int v) { packet[o] = static_cast<std::byte>(clamp8(v)); }
inline void put16(int o, int v) {
    v = std::max(0, std::min(65535, v));
    packet[o] = static_cast<std::byte>(v & 255);
    packet[o+1] = static_cast<std::byte>((v >> 8) & 255);
}
inline int b8(const bc::draft_memory_buffer& dm, int o) { return std::to_integer<unsigned char>(dm[o]); }
inline int b16(const bc::draft_memory_buffer& dm, int o) { return b8(dm,o) | (b8(dm,o+1) << 8); }
inline bool any_enabled() { return P_DP_BANK || P_DP_WARDS; }

inline int ring_distance(const bc::distance_field& f, const bc::bitboard& seen,
                         const bc::bitboard& block, vec2 a) {
    int best = 1 << 20;
    for (int dx=-1; dx<=1; ++dx) for (int dy=-1; dy<=1; ++dy) {
        if (!dx && !dy) continue;
        vec2 p = a + vec2(dx,dy);
        if (!bc::map::is_in_bounds(p) || block.is_set(p) || !seen.is_set(p)) continue;
        best = std::min(best, static_cast<int>(f.get(p)) + 1);
    }
    return best < (1<<20) ? best : 255;
}

inline void prepare() {
    if (prepared || !any_enabled()) return;
    prepared = true;
    packet.fill(std::byte{0});
    packet[32]=std::byte{'D'}; packet[33]=std::byte{'P'};
    packet[34]=std::byte{'1'}; packet[35]=std::byte{1};
    attempt([&] {
        const int w = static_cast<int>(bc::map::width());
        const int h = static_cast<int>(bc::map::height());
        const int ts = static_cast<int>(bc::draft::team_size());
        const auto alts = bc::map::altars().positions();
        bc::bitboard block = bc::map::walls() | bc::map::holes() | bc::map::altars();
        const auto& sa = bc::map::spawn_region(bc::team::ally);
        const auto& sb = bc::map::spawn_region(bc::team::enemy);
        bc::distance_field da, db;
        bc::bitboard va, vb;
        da.compute(block, sa, va);
        db.compute(block, sb, vb);
        int path = 1 << 20;
        for (auto p : sb.positions())
            if (va.is_set(p)) path = std::min(path, static_cast<int>(da.get(p)));
        if (path >= (1<<20)) path = 65535;
        const int open = static_cast<int>(va.positions().size());
        std::uint8_t flags=0;
        if (path > P_UNI_PATH) flags |= F_LONG;
        if (static_cast<int>(alts.size()) <= 4) flags |= F_FEW_ALTARS;
        if (ts >= 5 && path > P_UNI_PATH && static_cast<int>(alts.size()) <= 4) flags |= F_FAR_FIGHT;
        if (w*h > 0 && open * 100 >= w*h*70) flags |= F_OPEN;
        put8(36,w); put8(37,h); put8(38,ts); put8(39,static_cast<int>(alts.size()));
        put16(40,path); put16(42,open); put8(44,flags);

        int ci=-1, cs=1<<20, si=-1, ss=-(1<<20);
        const int an = std::min<int>(24, static_cast<int>(alts.size()));
        put8(45,an);
        for (int i=0;i<an;++i) {
            int ad=ring_distance(da,va,block,alts[i]);
            int bd=ring_distance(db,vb,block,alts[i]);
            int o=80+i*6;
            put8(o+0,alts[i].x); put8(o+1,alts[i].y);
            put8(o+2,ad); put8(o+3,bd);
            put8(o+4,std::abs(ad-bd)); put8(o+5,0);
            if (ad<255 && bd<255) {
                int bal=std::abs(ad-bd)*4 + ad + bd;
                if (bal<cs) { cs=bal; ci=i; }
                int safety=bd-ad;
                if (safety>ss) { ss=safety; si=i; }
            }
        }
        if (ci>=0) {
            flags |= F_CENTRAL_ALTAR;
            packet[44]=static_cast<std::byte>(flags);
            put8(46,alts[ci].x); put8(47,alts[ci].y);
        }
        if (si>=0) { put8(48,alts[si].x); put8(49,alts[si].y); }

        // Same proven ward-anchor rule: two balanced bushes around the contested route.
        std::vector<vec2> bushes;
        attempt([&] { bushes = bc::map::bushes().positions(); return true; });
        vec2 mid = ci>=0 ? alts[ci] : vec2(w/2,h/2);
        int picked=0;
        vec2 wp[2]{{-1,-1},{-1,-1}};
        int ws[2]{1<<20,1<<20};
        for (auto p : bushes) {
            if (!va.is_set(p) || !vb.is_set(p)) continue;
            int ad=static_cast<int>(da.get(p)), bd=static_cast<int>(db.get(p));
            int sc=std::abs(ad-bd)*8 + dist(p,mid)*3 + std::min(ad,bd);
            if (sc < ws[0]) {
                ws[1]=ws[0]; wp[1]=wp[0]; ws[0]=sc; wp[0]=p;
            } else if (dist(p,wp[0]) >= 6 && sc < ws[1]) {
                ws[1]=sc; wp[1]=p;
            }
        }
        for (int k=0;k<2;++k)
            if (wp[k].x>=0) {
                put8(50+k*2,wp[k].x); put8(51+k*2,wp[k].y); ++picked;
            }
        put8(54,picked);
        return true;
    });
}

template <std::size_t N> inline void copy_to(std::array<std::byte,N>& buf) {
    if (!any_enabled()) return;
    prepare();
    const std::size_t n=std::min<std::size_t>(N,packet.size());
    for (std::size_t i=OFF;i<n;++i) buf[i]=packet[i];
}

inline void load(const bc::draft_memory_buffer& dm) {
    if (!any_enabled() || dm.size() <= 80) return;
    if (dm[32]!=std::byte{'D'} || dm[33]!=std::byte{'P'} || dm[34]!=std::byte{'1'}) return;
    R.valid=true;
    R.w=b8(dm,36); R.h=b8(dm,37); R.team_size=b8(dm,38); R.altars=b8(dm,39);
    R.path=b16(dm,40); R.open=b16(dm,42);
    R.flags=static_cast<std::uint8_t>(b8(dm,44));
    R.altar_n=std::min(24,b8(dm,45));
    R.central=vec2(b8(dm,46),b8(dm,47));
    R.safe=vec2(b8(dm,48),b8(dm,49));
    R.ward_n=std::min(2,b8(dm,54));
    for (int k=0;k<2;++k)
        R.ward[k]=vec2(b8(dm,50+k*2),b8(dm,51+k*2));
    for (int i=0;i<R.altar_n;++i) {
        int o=80+i*6;
        R.altar[i]={b8(dm,o),b8(dm,o+1),b8(dm,o+2),b8(dm,o+3)};
    }
}

inline bool long_map() { return R.valid && (R.flags & F_LONG); }
inline bool few_altars() { return R.valid && (R.flags & F_FEW_ALTARS); }

inline int altar_penalty(vec2 a) {
    if (!P_DP_BANK || !R.valid) return 0;
    for (int i=0;i<R.altar_n;++i)
        if (R.altar[i].x==a.x && R.altar[i].y==a.y) {
            int enemy_adv = R.altar[i].da - R.altar[i].db;
            if (enemy_adv <= 0) return 0;
            return std::min(80, enemy_adv*4);
        }
    return 0;
}

inline int quiet_bag() {
    if (!P_DP_BANK || !R.valid) return 0;
    if (long_map()) return P_DP_BANK_LONG;
    if (!few_altars()) return P_DP_BANK_MID;
    return 0;
}
} // namespace draftplan
