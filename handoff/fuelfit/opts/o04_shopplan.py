# fuelfit o04: shop's plan walk (every plan step x every shard, string compares: 7.4k per buy) resolved once per plan;
# map::bushes() read once (static).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""        bool fill = false;
        if (!pick) for (auto& st : s.plan) {
            const Shard* sh = nullptr;
            for (auto& x : s.shards)
                if (x.stat == st.stat && starts_with(x.family, st.family)) { sh = &x; break; }
            if (!sh) continue;
            if (static_cast<int>(counts[sh->emblem]) >= st.want) continue;
            pick = sh;
            fill = st.want >= 99;
            break;
        }""","""        bool fill = false;
        if (!pick) {
            // fuelfit o04: the shard of each plan step, resolved once per plan (plan and shards only change at init)
            static std::vector<const Shard*> plan_sh;
            static std::size_t plan_n = ~std::size_t(0), shards_n = 0, plan_sig = 0;
            std::size_t sig = 0;
            for (auto& st : s.plan) sig = sig * 1000003u + std::hash<std::string_view>{}(std::string_view(st.family)) * 31u + static_cast<std::size_t>(st.stat) * 7u + static_cast<std::size_t>(st.want);
            if (plan_n != s.plan.size() || shards_n != s.shards.size() || plan_sig != sig) {
                plan_sh.clear();
                for (auto& st : s.plan) {
                    const Shard* sh = nullptr;
                    for (auto& x : s.shards)
                        if (x.stat == st.stat && starts_with(x.family, st.family)) { sh = &x; break; }
                    plan_sh.push_back(sh);
                }
                plan_n = s.plan.size(); shards_n = s.shards.size(); plan_sig = sig;
            }
            for (std::size_t k = 0; k < s.plan.size(); ++k) {
                const Shard* sh = plan_sh[k];
                if (!sh) continue;
                if (static_cast<int>(counts[sh->emblem]) >= s.plan[k].want) continue;
                pick = sh;
                fill = s.plan[k].want >= 99;
                break;
            }
        }""")
rep("""    bc::bitboard dark;
    dark.draw_chebyshev(pos, static_cast<float>(P_WARD_R));
    dark &= bc::map::bushes();""","""    static const bc::bitboard bushes = bc::map::bushes();  // fuelfit o04: static map data
    bc::bitboard dark;
    dark.draw_chebyshev(pos, static_cast<float>(P_WARD_R));
    dark &= bushes;""")
if '#include <string_view>' not in s: s=s.replace('#include <string>','#include <string>\n#include <string_view>',1)
open(p,'w',newline='').write(s)
