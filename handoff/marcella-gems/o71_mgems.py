# o71 mgems (marcella.h gem_w): Marcella values the gems of a camp group by what they pay HER.
# Why (10-25, top 10 online near maps vs b27 local, before r150): her camp damage 2327 vs 1551 because she earns half the
# gold (202 vs 93) and buys half the shards (4.8 vs 2.0; r400 21 vs 11; hit r150-400 70 vs 52). The gold comes from
# gems: top-10 Marcella collects 25.6 gems by r150 (0.45 captures of elk+gem groups, 13 gems) against our 6.4 (0.06,
# 2 gems). Her passive pays 2 gold per gem tributed, so for her a gem is worth 1 + 2 x gold_w in choose_target's units.
# P_MGEM % of that extra (100 = the passive's exact worth); P_MGEM_CO 1: no "still needs company" x0.7 for her on
# groups with gems. Decision change; no fuel read, no loop, no printf.
import sys
d=sys.argv[1]; mgem=int(sys.argv[2]) if len(sys.argv)>2 else 100; mco=int(sys.argv[3]) if len(sys.argv)>3 else 0
def edit(fn, pairs):
    p=d+'/'+fn; s=open(p,newline='').read()
    for a,b in pairs:
        assert s.count(a)==1,(fn,a[:60],s.count(a)); s=s.replace(a,b)
    open(p,'w',newline='').write(s)
p=d+'/params.h'; s=open(p,newline='').read(); nl='\r\n' if '\r\n' in s else '\n'
s=s.rstrip('\r\n')+nl+nl.join(["","// o71 mgems (marcella.h gem_w): Marcella's gems are worth 1 + P_MGEM% x 2 x gold_w (her passive: 2 gold a gem)",
"#ifndef P_MGEM","#define P_MGEM %d"%mgem,"#endif","#ifndef P_MGEM_CO","#define P_MGEM_CO %d     // 1: no company x0.7 for her on gem groups"%mco,"#endif"])+nl
open(p,'w',newline='').write(s)
edit('champions.h',[("""CHAMP_HOOK bool shop_plan(State& s);
}
namespace ryth {""","""CHAMP_HOOK bool shop_plan(State& s);
CHAMP_HOOK double gem_w(const State& s, double gold_w);
CHAMP_HOOK bool solo_gems(const State& s);
}
namespace ryth {""")])
edit('marcella.h',[("""}  // namespace marcella""","""// o71 mgems (choose_target): her passive pays 2 gold per gem tributed (bc::constants::passive_abilities::marcella_tribute_gold_per_gem),
// so a gem is worth 1 + 2 x gold_w to her. Top-10 Marcella collects 25.6 gems by r150 (elk + gem groups), ours 6.4.
CHAMP_HOOK double gem_w(const State& s, double gold_w) {
    if (!P_MGEM || !is(s.name)) return 1.0;
    return 1.0 + P_MGEM / 100.0 * bc::constants::passive_abilities::marcella_tribute_gold_per_gem * gold_w;
}
CHAMP_HOOK bool solo_gems(const State& s) { return P_MGEM_CO && is(s.name); }

}  // namespace marcella""")])
edit('main.cpp',[("""    double best_score = 0;""","""    const double mgem_w = marcella::gem_w(s, gold_w);  // o71: once per choice
    const bool mgem_solo = marcella::solo_gems(s);
    double best_score = 0;"""),
("""        double value = (g.gems + gold_w * g.gold) / (pack""","""        double value = (g.gems * mgem_w + gold_w * g.gold) / (pack"""),
("""        if (needed > 1 + claimers) score *= (false && P_MP_COMPANY)""","""        if (needed > 1 + claimers && !(mgem_solo && g.gems > 0)) score *= (false && P_MP_COMPANY)""")])
