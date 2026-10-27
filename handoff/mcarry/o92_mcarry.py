# o92 mcarry (marcella.h + vesper.h carry_rank + vcarry_on): Marcella takes shared rewards first. Why (10-27, top 10 vs
# top 10 25-10 r0-150, 40 games, both sides; vs e85 base local): gems gained per champion in r0-150 for the top 10 are
# Marcella 31.8, HoR 26.8, Vesper 23.6, Vendetta 21.6, Ryth 15.1; ours (b35) Vesper 17.9, HoR 10.6, Marcella 6.1, Ryth
# 4.5, Vendetta 2.8. Marcella's passive pays 2 gold per gem tributed, so the gems she carries become shards; our
# P_VCARRY gives every shared reward to Vesper. P_MCARRY 1: carry order Marcella, Vesper, rest (also with no Vesper
# drafted). 2: also Marcella's no-leave on a waiting reward within P_VCARRY_NL (vcarry's rule (b)).
import sys
d=sys.argv[1]; v=int(sys.argv[2]) if len(sys.argv)>2 else 1
def edit(fn, pairs):
    p=d+'/'+fn; s=open(p,newline='').read()
    for a,b in pairs:
        assert s.count(a)==1,(fn,a[:60],s.count(a)); s=s.replace(a,b)
    open(p,'w',newline='').write(s)
p=d+'/params.h'; s=open(p,newline='').read(); nl='\r\n' if '\r\n' in s else '\n'
s=s.rstrip('\r\n')+nl+nl.join(["","// o92 mcarry: 0 = Vesper carries (vcarry); 1 = Marcella first, then Vesper; 2 = 1 + Marcella's no-leave",
"#ifndef P_MCARRY","#define P_MCARRY %d"%v,"#endif"])+nl
open(p,'w',newline='').write(s)
edit('champions.h',[("""namespace marcella {
CHAMP_HOOK bool is(const std::string& n);
""","""namespace marcella {
CHAMP_HOOK bool is(const std::string& n);
CHAMP_HOOK bool carries(const std::string& n);
""")])
edit('marcella.h',[("""CHAMP_HOOK bool is(const std::string& n) { return starts_with(n, "marcella"); }
""","""CHAMP_HOOK bool is(const std::string& n) { return starts_with(n, "marcella"); }
// o92 mcarry: Marcella is the first carry on shared rewards (2 gold per gem tributed; top-10 Marcella 31.8 gems by r150)
CHAMP_HOOK bool carries(const std::string& n) { return P_MCARRY && is(n); }
""")])
edit('vesper.h',[("""CHAMP_HOOK int carry_rank(const std::string& n) { return is(n) ? 0 : 1; }""",
"""CHAMP_HOOK int carry_rank(const std::string& n) { return P_MCARRY ? (marcella::carries(n) ? 0 : is(n) ? 1 : 2) : (is(n) ? 0 : 1); }""")])
edit('main.cpp',[("""                if (starts_with(norm(bc::to_string(a.champion_name())), "vesper")) v = 1;""",
"""                if (starts_with(norm(bc::to_string(a.champion_name())), "vesper") ||
                    (P_MCARRY && marcella::carries(norm(bc::to_string(a.champion_name()))))) v = 1;"""),
("""vcarry_on(s) && vesper::is(s.name) && nearest_foe > P_VCARRY_FOE;""",
"""vcarry_on(s) && (vesper::is(s.name) || (P_MCARRY >= 2 && marcella::carries(s.name))) && nearest_foe > P_VCARRY_FOE;""")])
