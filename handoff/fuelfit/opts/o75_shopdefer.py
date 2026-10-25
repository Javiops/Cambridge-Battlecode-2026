# o75_shopdefer.py SRCDIR (NOT EXACT: start-up timing; judge by strength). Over b35 (o74). The item list (build_shop:
# every item type's result/passive, 24.5k on every map, measured with k35dbg) leaves the start-up turn: the list is read
# in thirds from round 2 on (a count quota, no fuel read; the loop was already resumable by s.shop_next) and the emblem
# plan is built once the list is complete. Gold is 0 at the start, so nothing shops before ~r30. With 24.5k less in
# turn 1, these maps play from round 2 (start-up <= 160k): collision, broken_curve, swirl, shortcut, great_wall,
# gem_fields, rushbait_v2 (o74 had them at r3). monolith (160k) and quadrants (168k) stay at r3. v2: maps > 2500 tiles
# keep the list in turn 1 (b36 deferred it everywhere: far 44/56 vs 48, the first playing turns there are 77-168k).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:70],s.count(a)); s=s.replace(a,b)
rep("""void build_shop(State& s, bc::champion& me) {
    std::size_t n = 0;
    attempt([&] {
        n = me.item_count().size();
        return true;
    });
    std::size_t i0 = s.shop_next;
    for (std::size_t i = i0; i < n && fuel_ok(20000); ++i) {
        s.shop_next = i + 1;
        if (s.shop_next >= n) s.shop_done = true;
""","""void build_shop(State& s, bc::champion& me, int parts = 1) {  // o75: read 1/parts of the item list per call
    std::size_t n = 0;
    attempt([&] {
        n = me.item_count().size();
        return true;
    });
    std::size_t i0 = s.shop_next;
    const std::size_t quota = parts <= 1 ? n : (n + parts - 1) / parts;
    for (std::size_t i = i0; i < n && i - i0 < quota; ++i) {
        s.shop_next = i + 1;
        if (s.shop_next >= n) s.shop_done = true;
""")
rep("""            s.shards.push_back({t, *r, stat, fam});
            return true;
        });
    }
    // Emblem build per champion. Families are matched by name prefix.
""","""            s.shards.push_back({t, *r, stat, fam});
            return true;
        });
    }
    if (!s.shop_done) return;  // o75: the plan waits for the whole list
    // Emblem build per champion. Families are matched by name prefix.
""")
rep("""    FP(23, "init-shop");
    attempt([&] {
        build_shop(s, me);
        return true;
    });
""","""    FP(23, "init-shop");
    // o75: on maps <= 2500 tiles the item list (24.5k) is read from round 2 on, in thirds (play_turn): nothing shops
    // before gold >= 30. Big maps overflow turn 1 anyway and their first playing turns are the heavy ones: list here.
    if (static_cast<long>(bc::map::width()) * static_cast<long>(bc::map::height()) > 2500)
        attempt([&] {
            build_shop(s, me);
            return true;
        });
""")
rep("""    if (!s.shop_done && fuel_ok(40000)) build_shop(s, me);  // init ran out of fuel before the item list was done
""","""    if (!s.shop_done && round >= 2) build_shop(s, me, P_SHOP_PARTS);  // o75: the item list in P_SHOP_PARTS turns from round 2 (no fuel read)
""")
rep("""            else if ((ng <= 16 && tiles <= 2500) || (ng <= 19 && tiles <= 1000)) s.play_from = 2;  // start-up <= 160k (turn 1 <= 190k measured): ends inside round 1
""","""            else if (tiles <= 2500 && (ng <= 19 || (ng <= 22 && tiles < 2000))) s.play_from = 2;  // o75: start-up without the shop list <= 160k (monolith 160k / quadrants 168k at 20-21 groups on 2000+ tiles stay r3)
""")
open(p,'w',newline='').write(s)
p=d+'/params.h'; s=open(p,newline='').read()
rep("""#ifndef P_DH_ROUND
""","""#ifndef P_SHOP_PARTS
#define P_SHOP_PARTS 3  // o75: the shop item list is read in this many turns from round 2 (~8k each)
#endif
#ifndef P_DH_ROUND
""")
open(p,'w',newline='').write(s)
