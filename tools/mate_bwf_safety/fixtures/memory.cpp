#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <span>
#include <stdexcept>
#include <string>
#include <vector>
#include <queue>
struct vec2 {
    int x=0,y=0;
    vec2()=default; vec2(int a,int b):x(a),y(b){}
    vec2 operator+(vec2 b) const { return {x+b.x,y+b.y}; }
    bool operator==(const vec2&) const=default;
};
int dist(vec2 a,vec2 b) { return std::max(std::abs(a.x-b.x),std::abs(a.y-b.y)); }
std::uint64_t fuel=1000000;
int errors=0,queries=0,fields=0,fail_field=0;
bool fuel_drop=false;
std::string fail_query;
bool fuel_ok(std::uint64_t n) { return fuel>n+6000; }
template<class F> bool attempt(F&& f) { try { return f(); } catch (...) { ++errors; return false; } }
void query(const char* name) { ++queries; if (fail_query==name) throw std::runtime_error(name); }
namespace bc {
enum class team { ally,enemy };
struct bitboard {
    std::vector<vec2> tiles;
    std::string tag;
    bool is_set(vec2 p) const { return std::find(tiles.begin(),tiles.end(),p)!=tiles.end(); }
    std::vector<vec2> positions() const { if (!tag.empty()) query(tag.c_str()); return tiles; }
    void set(vec2 p) { if (!is_set(p)) tiles.push_back(p); }
    bitboard operator|(const bitboard& b) const { auto v=*this; v.tag.clear(); for(auto p:b.tiles) v.set(p); return v; }
};
namespace map {
inline int W=20,H=20;
inline bitboard walls_v,holes_v,altars_v,bushes_v,ally_v,enemy_v;
int width() { query("width"); return W; }
int height() { query("height"); return H; }
bool is_in_bounds(vec2 p) { return p.x>=0 && p.y>=0 && p.x<W && p.y<H; }
const bitboard& walls() { query("walls"); return walls_v; }
const bitboard& holes() { query("holes"); return holes_v; }
const bitboard& altars() { query("altars"); return altars_v; }
const bitboard& bushes() { query("bushes"); return bushes_v; }
const bitboard& spawn_region(team t) { query("spawn"); return t==team::ally ? ally_v : enemy_v; }
}
namespace draft { inline int TS=5; int team_size() { query("team_size"); return TS; } }
struct distance_field {
    std::array<int,65536> d{};
    void compute(const bitboard& block,const bitboard& roots,bitboard& seen) {
        ++fields;
        if (fields==fail_field) throw std::runtime_error("field");
        d.fill(-1); seen={}; std::queue<vec2> q;
        for(auto p:roots.tiles) if (!block.is_set(p)) { d[p.y*256+p.x]=0; seen.set(p); q.push(p); }
        while(!q.empty()) {
            auto p=q.front(); q.pop();
            for(int dx=-1;dx<=1;++dx) for(int dy=-1;dy<=1;++dy) {
                auto n=p+vec2(dx,dy);
                if ((!dx&&!dy)||!map::is_in_bounds(n)||block.is_set(n)||d[n.y*256+n.x]>=0) continue;
                d[n.y*256+n.x]=d[p.y*256+p.x]+1; seen.set(n); q.push(n);
            }
        }
        if (fuel_drop && fields==1) fuel=25000;
    }
    int get(vec2 p) const { return d.at(p.y*256+p.x); }
};
inline std::vector<std::byte> memory(256);
inline int writes=0,fail_writes=0,fail_index=-1;
struct draft_memory_buffer {
    std::vector<std::byte> bytes;
    draft_memory_buffer():bytes(memory){}
    explicit draft_memory_buffer(std::vector<std::byte> b):bytes(std::move(b)){}
    std::size_t size() const { return bytes.size(); }
    const std::byte& operator[](std::size_t i) const {
        if (static_cast<int>(i)==fail_index) throw std::out_of_range("injected read");
        return bytes.at(i);
    }
    draft_memory_buffer& operator=(std::span<const std::byte> s) {
        ++writes;
        if (fail_writes>0) { --fail_writes; throw std::runtime_error("submit"); }
        for(std::size_t i=0;i<std::min(s.size(),memory.size());++i) memory[i]=s[i];
        return *this;
    }
};
}
#define P_DP_BANK 1
#define P_DP_WARDS 1
#define P_UNI_PATH 45
#include "draft_plan.h"
int checks=0;
void check(bool yes,const char* why) { ++checks; if(!yes) { std::fprintf(stderr,"FAIL %s\n",why); std::exit(1); } }
void reset() {
    fuel=1000000; errors=queries=fields=fail_field=0; fuel_drop=false; fail_query.clear();
    bc::map::W=bc::map::H=20; bc::draft::TS=5;
    bc::map::walls_v={}; bc::map::holes_v={};
    bc::map::altars_v={{{10,10}},"altar_positions"};
    bc::map::bushes_v={{{7,7},{13,13},{8,7}},"bush_positions"};
    bc::map::ally_v={{{0,0}},"ally_positions"}; bc::map::enemy_v={{{19,19}},"enemy_positions"};
    bc::memory.assign(256,std::byte{0}); bc::writes=bc::fail_writes=0; bc::fail_index=-1;
    draftplan::packet.fill(std::byte{0}); draftplan::R={}; draftplan::prepared=false;
#if P_DP_MEMORY_FIX
    draftplan::preparation=draftplan::Preparation::fresh;
#endif
}
std::array<std::byte,256> make_packet() {
    std::array<std::byte,256> p{};
    p[0]=std::byte{'C'}; p[1]=std::byte{'M'}; p[2]=std::byte{'B'}; p[3]=std::byte{'1'};
    p[24]=std::byte{12}; p[25]=std::byte{54}; p[26]=std::byte{29}; p[27]=std::byte{90}; p[28]=std::byte{4};
    draftplan::copy_to(p); return p;
}
bc::draft_memory_buffer dm_of(const std::array<std::byte,256>& p,std::size_t n=256) {
    std::vector<std::byte> b(p.begin(),p.end()); b.resize(n); return bc::draft_memory_buffer(b);
}
int memory_regression() {
    reset(); auto good=make_packet();
    draftplan::load(dm_of(good)); check(draftplan::R.valid,"normal round trip");
    check(draftplan::R.ward[0]==vec2(8,7),"original first anchor score retained");
#if P_DP_ANCHOR_FIX
    check(draftplan::R.ward[1]==vec2(13,13)&&dist(draftplan::R.ward[0],draftplan::R.ward[1])>=6,"enabled fix spaces second anchor");
#else
    check(draftplan::R.ward[1]==vec2(7,7)&&dist(draftplan::R.ward[0],draftplan::R.ward[1])<6,"disabled fix retains original promotion behavior");
#endif
    std::printf("GEOMETRY path=%d open=%d flags=%d altar=%d,%d,%d,%d ward=%d:%d,%d:%d,%d quiet=%d penalty=%d\n",
        draftplan::R.path,draftplan::R.open,draftplan::R.flags,draftplan::R.altar[0].x,draftplan::R.altar[0].y,
        draftplan::R.altar[0].da,draftplan::R.altar[0].db,draftplan::R.ward_n,draftplan::R.ward[0].x,
        draftplan::R.ward[0].y,draftplan::R.ward[1].x,draftplan::R.ward[1].y,draftplan::quiet_bag(),draftplan::altar_penalty({10,10}));
    for(int i=0;i<32;++i) check(good[i]==(i==0?std::byte{'C'}:i==1?std::byte{'M'}:i==2?std::byte{'B'}:
        i==3?std::byte{'1'}:i==24?std::byte{12}:i==25?std::byte{54}:i==26?std::byte{29}:i==27?std::byte{90}:
        i==28?std::byte{4}:std::byte{0}),"legacy prefix preserved");
#if P_DP_MEMORY_FIX
    check(good[35]==std::byte{2} && good[55]==std::byte{3},"version and complete ready markers");
    const auto legacy=draftplan::read_legacy_settings(dm_of(good));
    check(legacy.tribute==12&&legacy.recall==54&&legacy.flee==29&&legacy.late==900&&legacy.family==4,"legacy settings actual helper");
    for (auto n : {0,32,80,81,223,255}) {
        draftplan::R.valid=true; draftplan::load(dm_of(good,n)); check(!draftplan::R.valid,"short packet resets runtime");
    }
    for(auto n : {256,300}) { draftplan::load(dm_of(good,n)); check(draftplan::R.valid,"supported larger capacity"); }
    for (auto [o,v] : std::vector<std::pair<int,int>>{{32,0},{35,1},{35,3},{55,0},{55,7},{36,21},{38,4},
        {39,2},{45,25},{54,3},{50,250},{80,9},{84,99},{85,1},{46,9},{44,128}}) {
        auto bad=good; bad[o]=static_cast<std::byte>(v); draftplan::R.valid=true;
        draftplan::load(dm_of(bad)); check(!draftplan::R.valid,"invalid packet resets all runtime");
        const auto l=draftplan::read_legacy_settings(dm_of(bad)); check(l.tribute==12&&l.late==900,"bad planner preserves legacy");
    }
    draftplan::Runtime untouched; untouched.w=77;
    auto bad=good; bad[35]=std::byte{1}; check(!draftplan::decode(dm_of(bad),untouched)&&untouched.w==77,"decode output atomic");
    bc::fail_index=80; draftplan::R.valid=true; draftplan::load(dm_of(good));
    check(!draftplan::R.valid,"thrown decode resets runtime");
    check(draftplan::read_legacy_settings(dm_of(good)).tribute==12,"thrown planner read cannot suppress legacy"); bc::fail_index=-1;
    for(const char* stage : {"width","spawn","altar_positions","bush_positions"}) {
        reset(); fail_query=stage; auto p=make_packet(); check(p[32]==std::byte{0},"query failure no packet magic");
        check(draftplan::preparation==draftplan::Preparation::unavailable,"failure status is not ready");
        const int q=queries; make_packet(); check(queries==q,"failed expensive preparation does not repeat");
    }
    reset(); fail_field=2; check(make_packet()[32]==std::byte{0},"second field failure atomic");
    reset(); fuel=65999; auto p=make_packet(); check(queries==0&&p[32]==std::byte{0},"low fuel refuses before geometry");
    check(draftplan::preparation==draftplan::Preparation::deferred,"low fuel status deferred");
    fuel=1000000; p=make_packet(); check(p[32]==std::byte{'D'},"recovered budget may prepare");
    reset(); fuel_drop=true; check(make_packet()[32]==std::byte{0}&&fields==1,"stage budget stops before second field");
    reset(); bc::map::bushes_v.tiles.clear(); p=make_packet(); draftplan::load(dm_of(p));
    check(draftplan::R.valid&&draftplan::R.ward_n==0&&!draftplan::use_ward_plan(),"completed empty anchors use original ward fallback");
    reset(); bc::map::W=256; check(make_packet()[32]==std::byte{0},"unsupported width no truncation");
    reset(); for(int i=0;i<25;++i) bc::map::altars_v.set({i%20,i/20});
    check(make_packet()[32]==std::byte{0},"too many altars no partial ranking");
    reset(); bc::memory.assign(good.begin(),good.end()); bc::fail_writes=1;
    p=good; p[24]=std::byte{22};
    check(draftplan::submit_plan(p)&&bc::writes==2,"full submission failure retries legacy prefix");
    check(bc::memory[24]==std::byte{22}&&bc::memory[32]==std::byte{0}&&bc::memory[35]==std::byte{0},"fallback clears retained magic");
    check(bc::memory[80]==good[80],"fallback mock preserves unwritten tail");
    draftplan::load(bc::draft_memory_buffer()); check(!draftplan::R.valid,"retained payload cannot reactivate");
    check(draftplan::read_legacy_settings(bc::draft_memory_buffer()).tribute==22,"fallback still loads updated legacy");
    reset(); bc::memory.assign(good.begin(),good.end()); bc::fail_writes=2;
    check(!draftplan::submit_plan(p)&&bc::writes==2&&bc::memory[32]==std::byte{'D'},"double failure reports failure without claiming invalidation");
    for(auto cap : {28,32,35,36,81,255}) {
        reset(); bc::memory.assign(cap,std::byte{99}); check(draftplan::submit_plan(good),"short capacity legacy write");
        check(bc::memory[24]==std::byte{12},"short capacity preserves legacy");
        draftplan::load(bc::draft_memory_buffer()); check(!draftplan::R.valid,"short capacity never planner");
    }
#else
    check(good[35]==std::byte{1}&&good[55]==std::byte{0},"disabled memory fix retains original packet format");
#endif
    // Exact promotion-bug witness: best arrives last adjacent to the former first.
    std::vector<vec2> bushes{{3,3},{12,12},{4,3}};
    auto score=[](vec2 p) { return p==vec2(4,3)?1:p==vec2(3,3)?2:3; };
    vec2 wp[2]; check(draftplan::spaced_anchors(bushes,score,wp)==2&&wp[0]==vec2(4,3)&&wp[1]==vec2(12,12),"late adjacent best keeps distant second");
    std::reverse(bushes.begin(),bushes.end()); draftplan::spaced_anchors(bushes,score,wp);
    check(wp[0]==vec2(4,3)&&wp[1]==vec2(12,12),"anchor iteration order independent");
    bushes={{3,3},{4,3}}; check(draftplan::spaced_anchors(bushes,score,wp)==1&&wp[1].x==-1,"one separated anchor only");
    bushes.clear(); check(draftplan::spaced_anchors(bushes,score,wp)==0,"no anchors");
    bushes={{12,12},{2,2},{2,1}}; draftplan::spaced_anchors(bushes,[](vec2){return 1;},wp);
    check(wp[0]==vec2(12,12)&&wp[1]==vec2(2,2),"equal scores preserve first SDK enumeration for both anchors");
    std::reverse(bushes.begin(),bushes.end()); draftplan::spaced_anchors(bushes,[](vec2){return 1;},wp);
    check(wp[0]==vec2(2,1)&&wp[1]==vec2(12,12),"reversed enumeration follows original first-equal-score rule");
    reset(); bc::map::bushes_v.tiles={{8,7},{7,8},{14,13},{13,14}};
    auto tied=make_packet(); draftplan::load(dm_of(tied));
    check(draftplan::R.valid&&draftplan::R.ward[0]==vec2(8,7),"actual prepare first tied anchor matches baseline enumeration");
    check(draftplan::R.ward[1]==vec2(14,13),"actual prepare second tied eligible anchor stable");
    reset(); bc::map::bushes_v.tiles={{7,8},{8,7},{13,14},{14,13}};
    tied=make_packet(); draftplan::load(dm_of(tied));
    check(draftplan::R.valid&&draftplan::R.ward[0]==vec2(7,8),"actual prepare honors first SDK tile instead of lexical coordinate");
    check(draftplan::R.ward[1]==vec2(13,14),"actual prepare reverses eligible tie with SDK enumeration");
    bushes={{0,0},{7,7}}; draftplan::spaced_anchors(bushes,[](vec2){return 1;},wp);
    check(wp[0]==vec2(0,0)&&wp[1]==vec2(7,7),"legitimate zero coordinate retained");
    std::printf("PASS checks=%d memory=%d anchor=%d\n",checks,P_DP_MEMORY_FIX,P_DP_ANCHOR_FIX);
    return 0;
}
