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
#ifndef P_DP_MEMORY_FIX
#define P_DP_MEMORY_FIX 1
#endif
#ifndef P_DP_ANCHOR_FIX
#define P_DP_ANCHOR_FIX 1
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

// Two scans retain the original first-equal-score enumeration rule and space the second.
template<class Score> inline int spaced_anchors(const std::vector<vec2>& bushes,
                                                Score score, vec2 (&wp)[2]) {
    wp[0] = wp[1] = vec2(-1,-1);
    int best = 1 << 20;
    for (auto p : bushes) {
        const int sc = score(p);
        if (sc == -2) return -1;
        if (sc >= 0 && sc < best) { best=sc; wp[0]=p; }
    }
    if (wp[0].x < 0) return 0;
    best = 1 << 20;
    for (auto p : bushes) {
        if (dist(p,wp[0]) < 6) continue;
        const int sc = score(p);
        if (sc == -2) return -1;
        if (sc >= 0 && sc < best) { best=sc; wp[1]=p; }
    }
    return wp[1].x < 0 ? 1 : 2;
}

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

inline void prepare_legacy() {
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
#if P_DP_ANCHOR_FIX
        spaced_anchors(bushes, [&](vec2 p) {
            if (!va.is_set(p) || !vb.is_set(p)) return -1;
            const int ad=static_cast<int>(da.get(p)), bd=static_cast<int>(db.get(p));
            return std::abs(ad-bd)*8 + dist(p,mid)*3 + std::min(ad,bd);
        }, wp);
#else
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
#endif
        for (int k=0;k<2;++k)
            if (wp[k].x>=0) {
                put8(50+k*2,wp[k].x); put8(51+k*2,wp[k].y); ++picked;
            }
        put8(54,picked);
        return true;
    });
}

template <std::size_t N> inline void copy_to_legacy(std::array<std::byte,N>& buf) {
    if (!any_enabled()) return;
    prepare_legacy();
    const std::size_t n=std::min<std::size_t>(N,packet.size());
    for (std::size_t i=OFF;i<n;++i) buf[i]=packet[i];
}

inline void load_legacy(const bc::draft_memory_buffer& dm) {
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

#if P_DP_MEMORY_FIX
constexpr int VERSION = 2;
constexpr int READY = 3;  // Both bank and ward sections completed; no partial packet is admitted.
enum class Preparation { fresh, deferred, unavailable, ready };
inline Preparation preparation = Preparation::fresh;

inline void store8(std::array<std::byte,SIZE>& p, int o, int v) { p[o]=static_cast<std::byte>(v); }
inline void store16(std::array<std::byte,SIZE>& p, int o, int v) {
    store8(p,o,v & 255); store8(p,o+1,(v >> 8) & 255);
}

inline void prepare() {
    if (!any_enabled() || preparation == Preparation::ready || preparation == Preparation::unavailable) return;
    // Admission only; this conservative reserve is not a calibrated bound on native query cost.
    if (!fuel_ok(60000)) { preparation=Preparation::deferred; return; }
    preparation=Preparation::unavailable;  // At most one expensive attempt, including failures.
    std::array<std::byte,SIZE> next{};
    const bool ok=attempt([&] {
        const int w=static_cast<int>(bc::map::width()), h=static_cast<int>(bc::map::height());
        const int ts=static_cast<int>(bc::draft::team_size());
        const auto alts=bc::map::altars().positions();
        if (w<=0 || h<=0 || w>255 || h>255 || ts<=0 || ts>255 || alts.size()>24) return false;
        const auto block=bc::map::walls() | bc::map::holes() | bc::map::altars();
        const auto& sa=bc::map::spawn_region(bc::team::ally);
        const auto& sb=bc::map::spawn_region(bc::team::enemy);
        bc::distance_field da,db;
        bc::bitboard va,vb;
        da.compute(block,sa,va);
        if (!fuel_ok(35000)) return false;
        db.compute(block,sb,vb);
        if (!fuel_ok(18000)) return false;
        int path=65535;
        for (auto p : sb.positions()) if (va.is_set(p)) path=std::min(path,static_cast<int>(da.get(p)));
        const int open=static_cast<int>(va.positions().size());
        if (open>w*h || open>65535 || (path!=65535 && path>=w*h)) return false;
        std::uint8_t flags=0;
        if (path>P_UNI_PATH) flags|=F_LONG;
        if (alts.size()<=4) flags|=F_FEW_ALTARS;
        if (ts>=5 && path>P_UNI_PATH && alts.size()<=4) flags|=F_FAR_FIGHT;
        if (open*100>=w*h*70) flags|=F_OPEN;
        store8(next,36,w); store8(next,37,h); store8(next,38,ts); store8(next,39,alts.size());
        store16(next,40,path); store16(next,42,open); store8(next,45,alts.size());
        for (int o=46;o<=53;++o) store8(next,o,255);  // Absent coordinates cannot become tile(0,0).
        auto exact_ring = [&](const bc::distance_field& f, const bc::bitboard& seen, vec2 a) {
            int best=1<<20;
            for (int dx=-1;dx<=1;++dx) for (int dy=-1;dy<=1;++dy) {
                if (!dx && !dy) continue;
                const vec2 p=a+vec2(dx,dy);
                if (p.x<0 || p.y<0 || p.x>=w || p.y>=h || block.is_set(p) || !seen.is_set(p)) continue;
                best=std::min(best,static_cast<int>(f.get(p))+1);
            }
            return best==(1<<20) ? -1 : best;
        };
        int ci=-1,cs=1<<20,si=-1,ss=-(1<<20);
        for (std::size_t i=0;i<alts.size();++i) {
            if (!fuel_ok(12000)) return false;
            const vec2 a=alts[i];
            if (a.x<0 || a.y<0 || a.x>=w || a.y>=h) return false;
            int ad=exact_ring(da,va,a),bd=exact_ring(db,vb,a);
            if (ad>=255 || bd>=255) return false;  // Finite saturated distances are unsupported.
            if (ad<0) ad=255;
            if (bd<0) bd=255;
            const int o=80+static_cast<int>(i)*6;
            store8(next,o,a.x); store8(next,o+1,a.y); store8(next,o+2,ad); store8(next,o+3,bd);
            store8(next,o+4,std::abs(ad-bd));
            if (ad<255 && bd<255) {
                const int bal=std::abs(ad-bd)*4+ad+bd,safety=bd-ad;
                if (bal<cs) { cs=bal; ci=static_cast<int>(i); }
                if (safety>ss) { ss=safety; si=static_cast<int>(i); }
            }
        }
        if (ci>=0) { flags|=F_CENTRAL_ALTAR; store8(next,46,alts[ci].x); store8(next,47,alts[ci].y); }
        if (si>=0) { store8(next,48,alts[si].x); store8(next,49,alts[si].y); }
        // A failed bush read aborts the transaction; it is not a completed empty search.
        const auto bushes=bc::map::bushes().positions();
        const vec2 mid=ci>=0 ? alts[ci] : vec2(w/2,h/2);
        vec2 wp[2]{{-1,-1},{-1,-1}};
        auto score = [&](vec2 p) {
            if (!fuel_ok(10000)) return -2;
            if (!va.is_set(p) || !vb.is_set(p)) return -1;
            const int ad=static_cast<int>(da.get(p)),bd=static_cast<int>(db.get(p));
            return std::abs(ad-bd)*8+dist(p,mid)*3+std::min(ad,bd);
        };
#if P_DP_ANCHOR_FIX
        if (spaced_anchors(bushes,score,wp)<0) return false;
#else
        int ws[2]{1<<20,1<<20};
        for (auto p : bushes) {
            const int sc=score(p);
            if (sc==-2) return false;
            if (sc<0) continue;
            if (sc<ws[0]) { ws[1]=ws[0]; wp[1]=wp[0]; ws[0]=sc; wp[0]=p; }
            else if (dist(p,wp[0])>=6 && sc<ws[1]) { ws[1]=sc; wp[1]=p; }
        }
#endif
        if (!fuel_ok(10000)) return false;  // Never publish a loop interrupted by the budget guard.
        int picked=0;
        for (int k=0;k<2;++k) if (wp[k].x>=0) {
            store8(next,50+2*k,wp[k].x); store8(next,51+2*k,wp[k].y); ++picked;
        }
        store8(next,44,flags); store8(next,54,picked); store8(next,55,READY);
        next[32]=std::byte{'D'}; next[33]=std::byte{'P'}; next[34]=std::byte{'1'};
        store8(next,35,VERSION);  // Commit markers are written only after all payload work succeeds.
        return true;
    });
    if (ok) { packet=next; preparation=Preparation::ready; }
}

template<std::size_t N> inline void copy_to(std::array<std::byte,N>& buf) {
    for (std::size_t i=OFF;i<std::min<std::size_t>(N,SIZE);++i) buf[i]=std::byte{0};
    if (!any_enabled()) return;
    prepare();
    if (preparation!=Preparation::ready || N<SIZE) return;
    for (std::size_t i=OFF;i<SIZE;++i) buf[i]=packet[i];
}

// A shorter SDK write retains the previous tail. Clear magic in the fallback prefix.
inline bool submit_plan(const std::array<std::byte,SIZE>& buf) {
    if (attempt([&] {
        bc::draft_memory_buffer dm;
        const std::size_t n=dm.size()>=SIZE ? SIZE : std::min<std::size_t>(dm.size(),36);
        auto out=buf;
        if (n<SIZE) for (int i=32;i<36;++i) out[i]=std::byte{0};
        dm=std::span<const std::byte>(out.data(),n);
        return true;
    })) return true;
    return attempt([&] {
        bc::draft_memory_buffer dm;
        auto fallback=buf;
        for (int i=32;i<36;++i) fallback[i]=std::byte{0};
        dm=std::span<const std::byte>(fallback.data(),std::min<std::size_t>(dm.size(),36));
        return true;
    });
}

inline bool decode(const bc::draft_memory_buffer& dm, Runtime& out) {
    if (dm.size()<SIZE || dm[32]!=std::byte{'D'} || dm[33]!=std::byte{'P'} || dm[34]!=std::byte{'1'} ||
        b8(dm,35)!=VERSION || b8(dm,55)!=READY) return false;
    Runtime next;
    next.w=b8(dm,36); next.h=b8(dm,37); next.team_size=b8(dm,38); next.altars=b8(dm,39);
    next.path=b16(dm,40); next.open=b16(dm,42); next.flags=static_cast<std::uint8_t>(b8(dm,44));
    next.altar_n=b8(dm,45); next.ward_n=b8(dm,54);
    const auto& alts=bc::map::altars();
    if (next.w<=0 || next.h<=0 || next.w!=static_cast<int>(bc::map::width()) ||
        next.h!=static_cast<int>(bc::map::height()) || next.team_size<=0 ||
        next.team_size!=static_cast<int>(bc::draft::team_size()) || next.altar_n>24 ||
        next.altars!=next.altar_n || next.altars!=static_cast<int>(alts.positions().size()) ||
        next.ward_n>2 || next.open>next.w*next.h || (next.path!=65535 && next.path>=next.w*next.h)) return false;
    auto in_bounds = [&](vec2 p) { return p.x>=0 && p.y>=0 && p.x<next.w && p.y<next.h; };
    int ci=-1,cs=1<<20,si=-1,ss=-(1<<20);
    for (int i=0;i<next.altar_n;++i) {
        const int o=80+i*6;
        const vec2 a(b8(dm,o),b8(dm,o+1));
        const int ad=b8(dm,o+2),bd=b8(dm,o+3);
        if (!in_bounds(a) || !alts.is_set(a) || b8(dm,o+4)!=std::abs(ad-bd) || b8(dm,o+5)!=0) return false;
        for (int j=0;j<i;++j) if (next.altar[j].x==a.x && next.altar[j].y==a.y) return false;
        next.altar[i]={a.x,a.y,ad,bd};
        if (ad<255 && bd<255) {
            const int bal=std::abs(ad-bd)*4+ad+bd,safety=bd-ad;
            if (bal<cs) { cs=bal; ci=i; }
            if (safety>ss) { ss=safety; si=i; }
        }
    }
    const vec2 central(b8(dm,46),b8(dm,47)),safe(b8(dm,48),b8(dm,49));
    auto matches = [&](vec2 p,int i) {
        return i<0 ? (p.x==255 && p.y==255) : (p.x==next.altar[i].x && p.y==next.altar[i].y);
    };
    if (!matches(central,ci) || !matches(safe,si)) return false;
    next.central=ci<0 ? vec2(-1,-1) : central;
    next.safe=si<0 ? vec2(-1,-1) : safe;
    int flags=0;
    if (next.path>P_UNI_PATH) flags|=F_LONG;
    if (next.altars<=4) flags|=F_FEW_ALTARS;
    if (next.team_size>=5 && next.path>P_UNI_PATH && next.altars<=4) flags|=F_FAR_FIGHT;
    if (next.open*100>=next.w*next.h*70) flags|=F_OPEN;
    if (ci>=0) flags|=F_CENTRAL_ALTAR;
    if (next.flags!=flags) return false;
    for (int k=0;k<2;++k) {
        const vec2 p(b8(dm,50+k*2),b8(dm,51+k*2));
        if (k>=next.ward_n) { if (p.x!=255 || p.y!=255) return false; continue; }
        if (!in_bounds(p) || !bc::map::bushes().is_set(p) || bc::map::walls().is_set(p) ||
            bc::map::holes().is_set(p) || alts.is_set(p) || (k && p==next.ward[0])) return false;
        next.ward[k]=p;
    }
#if P_DP_ANCHOR_FIX
    if (next.ward_n==2 && dist(next.ward[0],next.ward[1])<6) return false;
#endif
    next.valid=true;
    out=next;  // Output is untouched until the complete packet validates.
    return true;
}

inline void load(const bc::draft_memory_buffer& dm) {
    R=Runtime{};
    if (!any_enabled()) return;
    Runtime next;
    if (attempt([&] { return decode(dm,next); })) R=next;
}

struct LegacySettings { int tribute=-1, recall=-1, flee=-1, late=-1, family=-1; };
inline LegacySettings read_legacy_settings(const bc::draft_memory_buffer& dm) {
    LegacySettings s;
    if (dm.size()<28 || dm[0]!=std::byte{'C'} || dm[1]!=std::byte{'M'} ||
        dm[2]!=std::byte{'B'} || dm[3]!=std::byte{'1'}) return s;
    const int tg=b8(dm,24),rc=b8(dm,25),fl=b8(dm,26),lr=b8(dm,27)*10;
    if (tg>=5 && tg<=200) s.tribute=tg;
    if (rc>=10 && rc<=90) s.recall=rc;
    if (fl>=5 && fl<=80) s.flee=fl;
    if (lr>=500 && lr<=2000) s.late=lr;
    if (dm.size()>28) s.family=b8(dm,28);
    return s;
}
#else
inline void prepare() { prepare_legacy(); }
template<std::size_t N> inline void copy_to(std::array<std::byte,N>& buf) { copy_to_legacy(buf); }
inline void load(const bc::draft_memory_buffer& dm) { load_legacy(dm); }
#endif

inline bool use_ward_plan() {
#if P_DP_MEMORY_FIX
    return P_DP_WARDS && R.valid && R.ward_n>0;
#else
    return P_DP_WARDS && R.valid;
#endif
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
