#pragma once

// A bound on repeated exploration *near* a camp with no visible living monster,
// no capture reward and no active respawn.  The count of near turns is not
// increased while travelling across the map toward that camp.
constexpr bool camp_probe_exhausted(bool no_unvisited_reachable_tile,
                                    int near_rounds, int failed_moves) noexcept {
    return no_unvisited_reachable_tile || near_rounds > 12 || failed_moves >= 3;
}
