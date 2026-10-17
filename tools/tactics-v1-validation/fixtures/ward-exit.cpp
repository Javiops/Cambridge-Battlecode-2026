#define TACTICS_STRATEGIC_MODEL_ONLY
#include "strategic.h"
#include <bit>
// INSERT_PRODUCTION_WARD_HELPERS
// Frozen integration07 anchor-ranking reference SHA256: dbc5c25863045ea733292d582ae659981bea8d115cf6cf4a1da0ab5911776b0d
namespace tactics {
inline std::vector<Pos> reference_ward_candidate_positions(const std::vector<Pos> &legal, Pos self,
                                                 Pos ahead) {
    int dx = (ahead.x > self.x) - (ahead.x < self.x), dy = (ahead.y > self.y) - (ahead.y < self.y);
    if (dx == 0 && dy == 0)
        dx = 1;
    const std::array<Pos, 4> offsets{{{dx, dy}, {-dy, dx}, {dy, -dx}, {-dx, -dy}}};
    std::vector<Pos> selected;
    for (auto offset : offsets) {
        const Pos desired{self.x + 2 * offset.x, self.y + 2 * offset.y};
        std::optional<Pos> best;
        int best_distance = 100000, best_axis = 100000;
        for (auto p : legal) {
            if (std::find(selected.begin(), selected.end(), p) != selected.end())
                continue;
            const int d = distance(p, desired),
                      axis = std::abs(p.x - desired.x) + std::abs(p.y - desired.y);
            if (!best || d < best_distance ||
                (d == best_distance &&
                 (axis < best_axis ||
                  (axis == best_axis && (p.y < best->y || (p.y == best->y && p.x < best->x)))))) {
                best = p;
                best_distance = d;
                best_axis = axis;
            }
        }
        if (best)
            selected.push_back(*best);
    }
    return selected;
}
}

#include <cstdio>
#include <cstdlib>
using namespace tactics;
static unsigned checks = 0;
static void check(bool value, const char *why) {
    ++checks;
    if (!value) {
        std::printf("FAIL ward/exit %u %s\n", checks, why);
        std::exit(1);
    }
}
int main() {
    unsigned seed = 213517;
    auto random = [&](unsigned n) { seed = seed * 1664525u + 1013904223u; return seed % n; };
    for (int trial = 0; trial < 1600; ++trial) {
        const int width = 3 + random(62), height = 3 + random(48);
        std::vector<std::uint8_t> mask((width * height + 7) / 8), now(mask.size()),
            future(mask.size()), blocked(mask.size());
        for (unsigned i = 0; i < mask.size(); ++i) {
            mask[i] = random(256); now[i] = random(256);
            future[i] = random(256); blocked[i] = random(256);
        }
        const Pos self{int(random(width)), int(random(height))};
        const Pos anchor{std::clamp(self.x + int(random(13)) - 6, 0, width - 1),
                         std::clamp(self.y + int(random(13)) - 6, 0, height - 1)};
        const auto stencil = ward_score_stencil(width, height, self, anchor, blocked);
        const int expected = ward_buffer_score(mask, now, future, blocked, width, height, self, anchor);
        check(ward_stencil_score(stencil, mask, now, future) == expected,
              "packed interval/popcount score equals exact per-tile policy");
        std::vector<Pos> legal;
        const int dx = (anchor.x > self.x) - (anchor.x < self.x);
        const int dy = (anchor.y > self.y) - (anchor.y < self.y);
        for (int y = std::max(0, self.y - 2); y <= std::min(height - 1, self.y + 2); ++y)
            for (int x = std::max(0, self.x - 2); x <= std::min(width - 1, self.x + 2); ++x) {
                Pos p{x, y};
                const bool blocked_anchor = trial % 3 == 0 &&
                    (p == Pos{self.x + 2 * dx, self.y + 2 * dy} ||
                     p == Pos{self.x - 2 * dy, self.y + 2 * dx} ||
                     p == Pos{self.x + 2 * dy, self.y - 2 * dx});
                if (!blocked_anchor && random(3) != 0)
                    legal.push_back(p);
            }
        check(ward_candidate_positions(legal, self, anchor) ==
                  reference_ward_candidate_positions(legal, self, anchor),
              "exact-anchor fastpath preserves ranking with blocked desired tiles and map edges");
    }
    auto home = [](Pos p) { return p.x < 0 || p.y < 0 || p.x >= 20 || p.y >= 20 ? unreachable : p.x; };
    auto available = [](Pos p) { return p.x >= 0 && p.y >= 0 && p.x < 20 && p.y < 20; };
    auto observed = [](Pos) { return true; };
    auto quiet = [](Pos) { return unreachable; };
    const auto ready = trace_exit_gradient({10, 10}, 1, true, home, available, observed, quiet);
    check(ready.known && ready.viable && ready.length == 6 && ready.owner_eta == 5,
          "six-tile bounded prefix prices current ready movement");
    const auto spent = trace_exit_gradient({10, 10}, 1, false, home, available, observed, quiet);
    check(spent.known && spent.owner_eta == 6, "spent movement adds actual next-owner delay");
    const auto cut = trace_exit_gradient({10, 10}, 1, false, home, available, observed,
                                         [](Pos) { return 4; });
    check(cut.known && !cut.viable && cut.earliest_contact == 4,
          "enemy cutoff before owner exit rejects safe-walkout claim");
    const auto unknown = trace_exit_gradient({10, 10}, 1, true, home, available,
                                             [](Pos p) { return p.x >= 8; }, quiet);
    check(!unknown.known && !unknown.viable && unknown.length == 2,
          "occluded continuation retains reversible prefix without false safe exit");
    const auto blocked = trace_exit_gradient({10, 10}, 1, true, home,
                                             [](Pos p) { return p.x != 9; }, observed, quiet);
    check(!blocked.known && blocked.length == 0, "occupied single retreat front is not an exit");
    Actor enemy; enemy.alive = true; enemy.pos = {5, 5}; enemy.range = 3; enemy.move_speed = 1;
    enemy.spells[0].kind = 4; enemy.spells[0].range = 4; enemy.spells[0].cooldown = 0;
    enemy.spells[1].kind = 6; enemy.spells[1].range = 2; enemy.spells[1].cooldown = 0;
    check(enemy_contact_eta(enemy, {12, 5}) == 1, "dash plus control changes plausible cutoff");
    check(enemy_contact_eta(enemy, {12, 5}, 1) == 0, "recent missing movement shortens warning");
    enemy.spells[0].cooldown = enemy.spells[1].cooldown = 10;
    check(enemy_contact_eta(enemy, {12, 5}) == 4, "known cooldown outside window is not ready power");
    std::printf("%u ward/exit checks passed\n", checks);
}
