# fuelfit o18 (pelea, logs): the [fin] line (every finish hit, ~50 a game) and the [bcf] line (each bcf engage streak,
# ~56 a game) used printf (~2.5k each) on the heaviest fight turns. They now go through o09's LineOut (a few dozen
# instructions a number), moved above play_turn. Same bytes on stdout, no decision reads it: exact.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,a; s=s.replace(a,b)
i=s.index("// fuelfit o09: a cheap line writer (no format parsing)."); j=s.index("void log_status(State& s) {")
lo=s[i:j]; s=s[:i]+s[j:]
rep("void play_turn(State& s) {\n", lo+"void play_turn(State& s) {\n")
rep('                    if (fuel_ok(30000)) std::printf("[fin] r%d %d/%d/%d\\n", round, g_fin_trig, g_fin_hurt, g_fin_hit);',
'''                    if (fuel_ok(30000)) {  // fuelfit o18: LineOut, same text as the printf
                        static LineOut o;
                        o.n = 0;
                        o.s("[fin] r"); o.i(round); o.s(" "); o.i(g_fin_trig); o.s("/"); o.i(g_fin_hurt); o.s("/"); o.i(g_fin_hit);
                        o.end();
                    }''')
rep('                std::printf("[bcf] r%d %s d=%d hp=%d fhp=%d lr=%d\\n", round, s.name.c_str(), ft.d, ft.hp, ft.fhp, ft.lr);',
'''            {  // fuelfit o18: LineOut, same text as the printf
                static LineOut o;
                o.n = 0;
                o.s("[bcf] r"); o.i(round); o.s(" "); o.s(s.name.c_str()); o.s(" d="); o.i(ft.d); o.s(" hp="); o.i(ft.hp);
                o.s(" fhp="); o.i(ft.fhp); o.s(" lr="); o.i(ft.lr);
                o.end();
            }''')
open(p,'w',newline='').write(s)
