# fuelfit o23 (recall/altares/campamentos): the awake-camp test reads each camp with one raw sdk_camp call and no
# exception. Measured: sdk_camp costs ~60 fuel, but a thrown engine error (camp not in vision any more, error 97)
# costs ~5.5k to unwind; gold_rush's monolith turns threw 8-13 times in this loop (76k in one turn). A failed read
# counts in g_errors as the throw did (only the first 8 "[err]" log lines go). Decisions are the same: the flag was
# never set on a throw. position/health/max_health were three reads of the same record.
import sys
d=sys.argv[1]; p=d+'/main.cpp'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""std::vector<bc::camp> near_camps(State& s, vec2 pos) {""","""// fuelfit o23: one sdk_camp read without a throw (a thrown engine error costs ~5.5k fuel to unwind)
bool camp_snap(const bc::camp& c, bc::detail::camp_state& v) {
    const std::int32_t code = bc::detail::sdk_camp(static_cast<std::uint32_t>(static_cast<bc::handle_camp_t>(c)), &v);
    if (code == 0) return true;
    ++g_errors;  // counted as attempt() counted the throw; no message (the text is only a log line)
    return false;
}

std::vector<bc::camp> near_camps(State& s, vec2 pos) {""")
rep("""            if (dist(c.position(), pos) <= camp_range(c) + 1 && c.health() < c.max_health()) awake_camp_near = true;
#else""","""            bc::detail::camp_state cv{};  // fuelfit o23
            if (!camp_snap(c, cv)) return false;
            if (dist(vec2(cv.x, cv.y), pos) <= camp_range(c) + 1 && cv.health < cv.max_health) awake_camp_near = true;
#else""")
open(p,'w',newline='').write(s)
