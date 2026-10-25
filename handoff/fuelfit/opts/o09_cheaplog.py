# fuelfit o09 (log only, no decision changes): the status line is written with a tiny formatter and one fwrite instead
# of a 24-argument printf (19k fuel: the fuel counts instructions, and vfprintf is long). Same text, so every parser
# (vstat, emerg, a14) keeps working; %.0f of hp is replaced by rounding half up (log text only).
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:70],s.count(a)); s=s.replace(a,b)
rep("void log_status(State& s) {\n","""// fuelfit o09: a cheap line writer (no format parsing). Each number costs a few dozen instructions.
struct LineOut {
    char b[640];
    int n = 0;
    void s(const char* t) { while (*t && n < 600) b[n++] = *t++; }
    void u(unsigned long long v) {
        char t[24]; int k = 0;
        do { t[k++] = static_cast<char>('0' + v % 10); v /= 10; } while (v);
        while (k && n < 600) b[n++] = t[--k];
    }
    void i(long long v) { if (v < 0) { if (n < 600) b[n++] = '-'; u(static_cast<unsigned long long>(-v)); } else u(static_cast<unsigned long long>(v)); }
    void f0(float x) { i(x >= 0 ? static_cast<long long>(x + 0.5f) : -static_cast<long long>(-x + 0.5f)); }
    void end() { if (n < 639) b[n++] = '\\n'; std::fwrite(b, 1, static_cast<std::size_t>(n), stdout); std::fflush(stdout); }
};

void log_status(State& s) {
""")
rep("""        std::printf("[r%d] %s pos=(%d,%d) hp=%.0f/%.0f gems=%u gold=%u mode=%s farm=%s target=%d errs=%d fuel=%llu tpc=%d/%d wd=%d unreach=%d holdto=%d gskip=%d trip=%d isle=%d bcf=%d rc=%d/%d\\n",
                    round, s.name.c_str(), X(p), Y(p), me.health(), me.max_health(), me.gem_count(),
                    me.gold_count(), g_mode, g_farm, s.target, g_errors,
                    static_cast<unsigned long long>(bc::fuel_remaining()), g_tpc_buys, g_tpc_uses, g_wd_drops, g_cap_unreach, g_hold_to, g_guard_skip, g_trip_keep, g_isle, g_bcf, g_rc_big, g_rc_tiny);
        std::fflush(stdout);""","""        static LineOut o;  // fuelfit o09
        o.n = 0;
        o.s("[r"); o.i(round); o.s("] "); o.s(s.name.c_str()); o.s(" pos=("); o.i(X(p)); o.s(","); o.i(Y(p));
        o.s(") hp="); o.f0(me.health()); o.s("/"); o.f0(me.max_health()); o.s(" gems="); o.u(me.gem_count());
        o.s(" gold="); o.u(me.gold_count()); o.s(" mode="); o.s(g_mode); o.s(" farm="); o.s(g_farm);
        o.s(" target="); o.i(s.target); o.s(" errs="); o.i(g_errors); o.s(" fuel="); o.u(bc::fuel_remaining());
        o.s(" tpc="); o.i(g_tpc_buys); o.s("/"); o.i(g_tpc_uses); o.s(" wd="); o.i(g_wd_drops); o.s(" unreach="); o.i(g_cap_unreach);
        o.s(" holdto="); o.i(g_hold_to); o.s(" gskip="); o.i(g_guard_skip); o.s(" trip="); o.i(g_trip_keep); o.s(" isle="); o.i(g_isle);
        o.s(" bcf="); o.i(g_bcf); o.s(" rc="); o.i(g_rc_big); o.s("/"); o.i(g_rc_tiny);
        o.end();""")
open(p,'w',newline='').write(s)
