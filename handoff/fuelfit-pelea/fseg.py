# fseg.py MAIN THR: segment costs inside the fight section, accumulated over turns whose fight section > THR
import sys
p,thr=sys.argv[1],sys.argv[2]; s=open(p).read()
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(a,s.count(a)); s=s.replace(a,b)
hdr='''double g_fsT[40], g_fsA[40], g_fsB[40]; int g_fsN = 0, g_fsBN = 0; int g_fsLast = -1; std::uint64_t g_fsF = 0;
inline void fseg(int i) { const std::uint64_t f = bc::fuel_remaining(); if (g_fsLast >= 0) g_fsT[g_fsLast] += double(g_fsF) - double(f); g_fsLast = i; g_fsF = bc::fuel_remaining(); }
'''
rep("inline void pp_point();\n", "inline void pp_point();\n"+hdr)
rep("inline void dm_mark(int i) {\n    pp_point();\n", "inline void dm_mark(int i) {\n    pp_point();\n    if (g_fsLast >= 0) { fseg(-1); g_fsLast = -1; }\n")
rep("    const double fsec_ = g_tsec[9];\n", "    const double fsec_ = g_tsec[9];\n    if (g_dm_turn > 1) { ++g_fsN; if (fsec_ > %s) ++g_fsBN; for (int k = 0; k < 40; ++k) { g_fsA[k] += g_fsT[k]; if (fsec_ > %s) g_fsB[k] += g_fsT[k]; } }\n    for (int k = 0; k < 40; ++k) g_fsT[k] = 0;\n" % (thr,thr))
rep('std::printf("[prf] r%d %d %d", rr, g_prAllN, g_prBigN);', 'std::printf("[fsg] r%d %d %d", rr, g_fsN, g_fsBN); for (int k = 0; k < 40; ++k) if (g_fsA[k] != 0) std::printf(" %d:%.0f:%.0f", k, g_fsA[k], g_fsB[k]); std::printf("\\n"); std::printf("[prf] r%d %d %d", rr, g_prAllN, g_prBigN);')
marks=[('    g_mode = "fight";\n',1,'after'),
 ('#if P_BCF\n    // P_BCF: the engage decision',2,'before'),
 ('    std::vector<vec2> allies;\n    for (auto& a : vis_champions(*s.my))',3,'before'),
 ('    bool pv_fight = false;',4,'before'),
 ('    if (s.casters && !foes.empty() && !on_spawn && (!s.melee || s.renkite) && fight::kite',5,'before'),
 ('    if (!foes.empty()) {\n        if (false) fight::call_help',6,'before'),
 ('        fight_fav = favourable;\n',7,'before'),
 ('        if (!on_spawn && fight::front_line(s, me, foes, round)) {',8,'before'),
 ('        if (tgt && carrying && !killable && !tgt->channeling) tgt = nullptr;',9,'before'),
 ('        bool acted = engage(s, me, tgt->c, tgt->p, true, true);\n            if (!acted',10,'before'),
 ('    if (P_TEAM_FIGHT && hpr >= 0.5f && cassi_issac::pair_ok(s, me) && !on_spawn && !awake_camp_near && !foes.empty()',11,'before'),
 ('        if (k) {\n            if (!s.chase || !(*s.chase == k->c))',12,'before'),
 ('        if (dec == bcf::ENGAGE) {',13,'before'),
 ('            if (engage(s, me, tgt->c, tgt->p, true, true)) return;\n        } else if (P_BCF >= 2',14,'before'),
 ('            if (engage(s, me, tgt->c, tgt->p, true, true)) return;\n        } else if (P_BCF >= 2',15,'afterline'),
 ('        if (!killable && !on_spawn && !pot_hold && ((low_pct',16,'before'),
 ('        if (PR.outnum && !on_spawn && !(killable && reachable) && nearest_foe <= PR.outnum) {',17,'before'),
 ('        if (!favourable && !killable && (hpr * 100 < P_GA_AVOID_HP',18,'before'),
]
for a,i,w in marks:
    assert s.count(a)==1,(a,s.count(a))
    if w=='after': s=s.replace(a,a+f'fseg({i});\n')
    elif w=='before': s=s.replace(a,f'fseg({i});\n'+a)
    else:
        first=a.split('\n')[0]+'\n'; s=s.replace(a,first+f'fseg({i});\n'+a[len(first):])
open(p,'w').write(s)
