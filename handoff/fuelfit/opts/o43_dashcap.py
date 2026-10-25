# fuelfit o43 (farm section): mp_dash_hole_step's hole-route search bounded by max_distance = here - P_MP_DASHHOLE.
# The unbounded compute_to(vblock & ~dashholes, goals, {pos}, mp_hvis) is exhaustive (a full-map BFS, ~30k fuel on
# 100x100) whenever we cannot be reached through the holes either, which is the common case on hole maps.
# Exact: (1) if pos is reached within the bound, hh = mp_hdf.get(pos) <= bound and the original search reached pos with
# the same BFS distance (bound includes distance == bound: verified, bench var3); (2) if not, the original had
# hh > here - P_MP_DASHHOLE and returned 0 with no side effect, exactly what `!ok -> return 0` does now; (3) every later
# read of the field is at a tile with distance < hh (ring scan: d < bestd <= hh-1; next_moves_from(pos) and
# next_moves_from(*best): neighbours at distance d-1), and every BFS layer below hh is complete whatever the stop point,
# so those reads see the same values; tiles at distance >= hh are never read (a tile the original search had visited at
# d >= hh fails d < bestd exactly as an unreached one does). mp_hvis / mp_hdf are read nowhere else (grep).
# No fuel_ok, fixed bounds, no new output.
import sys
d=sys.argv[1]; p=d+'/mapplan_game.h'; s=open(p,newline='').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a)); s=s.replace(a,b)
rep("""    if (here - P_MP_DASHHOLE <= cd) return 0;  // the walk is as fast as waiting for the dash
    bool ok = attempt([&] {
        s.mp_hdf.compute_to(vblock & ~s.mp_dashholes, goals, s.dest, s.mp_hvis);
        return s.mp_hvis.is_set(pos);
    });
    if (!ok) return 0;
    int hh = s.mp_hdf.get(pos);
    if (hh > here - P_MP_DASHHOLE || hh <= cd) return 0;  // no crossing on the way, or it does not pay""","""    if (here - P_MP_DASHHOLE <= cd) return 0;  // the walk is as fast as waiting for the dash
    // fuelfit o43: the search stops at here - P_MP_DASHHOLE steps; farther means "no crossing on the way" below anyway
    const std::uint16_t hole_bound = static_cast<std::uint16_t>(here - P_MP_DASHHOLE);
    bool ok = attempt([&] {
        s.mp_hdf.compute_to(vblock & ~s.mp_dashholes, goals, s.dest, s.mp_hvis, hole_bound);
        return s.mp_hvis.is_set(pos);
    });
    if (!ok) return 0;
    int hh = s.mp_hdf.get(pos);
    if (hh > here - P_MP_DASHHOLE || hh <= cd) return 0;  // no crossing on the way, or it does not pay""")
open(p,'w',newline='').write(s)
print("o43 ok")
