# fuelfit o11 (exact): a 12-buy shop visit cost up to 52k. Measured split: plan signature hash 15k (recomputed on every
# buy; the plan only changes at start-up: now once per visit), lshop_pick 21k (its [lshop] printf for the first 40
# picks, 2.5k each: now the first 4), item_count 3.4k, plan walk 3.3k, hp_pick 2.6k, buy 2.3k.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:70],s.count(a)); s=s.replace(a,b)
rep("""    for (int it = 0; it < 12 && fuel_ok(10000); ++it) {
        if (me.gold_count() < 30) return;
        auto counts = me.item_count();""","""    std::size_t sig = 0;  // fuelfit o11: the plan signature once per visit, not per buy
    for (auto& st : s.plan) sig = sig * 1000003u + std::hash<std::string_view>{}(std::string_view(st.family)) * 31u + static_cast<std::size_t>(st.stat) * 7u + static_cast<std::size_t>(st.want);
    for (int it = 0; it < 12 && fuel_ok(10000); ++it) {
        if (me.gold_count() < 30) return;
        auto counts = me.item_count();""")
rep("""            std::size_t sig = 0;
            for (auto& st : s.plan) sig = sig * 1000003u + std::hash<std::string_view>{}(std::string_view(st.family)) * 31u + static_cast<std::size_t>(st.stat) * 7u + static_cast<std::size_t>(st.want);
            if (plan_n != s.plan.size()""","""            if (plan_n != s.plan.size()""")
rep("    if (g_ls_log++ < 40) std::printf(\"[lshop]","    if (g_ls_log++ < 4) std::printf(\"[lshop]")  # fuelfit o11: log only
open(p,'w',newline='').write(s)
