#include "ranking.h"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <vector>

using namespace tactics;
struct Entry { CampRank rank; bool reward, affordable; };
static unsigned checks = 0;
static void require(bool value, const char *message) {
    ++checks;
    if (!value) { std::fprintf(stderr, "ranking failure: %s at check %u\n", message, checks); std::exit(1); }
}
static void compare(std::vector<Entry> entries, int incumbent) {
    CampRanking bounded;
    for (auto row : entries) bounded.offer(row.rank, row.reward, row.affordable);
    // Independent reference preserves the exact removed full-sort algorithm.
    std::sort(entries.begin(), entries.end(), [](auto a, auto b) {
        return a.rank.score > b.rank.score ||
            (a.rank.score == b.rank.score && a.rank.gi < b.rank.gi);
    });
    std::vector<int> reference;
    auto add = [&](int gi) {
        if (gi >= 0 && std::find(reference.begin(), reference.end(), gi) == reference.end())
            reference.push_back(gi);
    };
    add(incumbent);
    for (auto row : entries) if (row.reward) { add(row.rank.gi); break; }
    for (auto row : entries) if (row.affordable) { add(row.rank.gi); break; }
    for (auto row : entries) if (reference.size() < 3) add(row.rank.gi);
    const auto shortlist = bounded.shortlist(incumbent);
    require(reference.size() == shortlist.size(), "shortlist length");
    require(std::equal(reference.begin(), reference.end(), shortlist.begin()), "exact shortlist order");
    const auto candidates = bounded.candidates();
    require(candidates.size() <= 5, "bounded candidate storage");
    for (std::size_t i = 0; i < candidates.size(); ++i) {
        if (i) require(!camp_rank_before(candidates.values[i], candidates.values[i - 1]), "sorted candidates");
        for (std::size_t j = 0; j < i; ++j)
            require(candidates.values[i].gi != candidates.values[j].gi, "unique candidates");
    }
    for (int selected : {-1, incumbent, entries.empty() ? -1 : entries.front().rank.gi}) {
        int old_next = -1, next = -1;
        for (auto row : entries) if (row.rank.gi != selected) { old_next = row.rank.gi; break; }
        for (auto row : candidates) if (row.gi != selected) { next = row.gi; break; }
        require(old_next == next, "exact first holder-handoff alternative");
    }
}
static unsigned random_state = 0x91d653b7u;
static unsigned random_value() { random_state ^= random_state << 13; random_state ^= random_state >> 17; random_state ^= random_state << 5; return random_state; }
int main() {
    compare({}, -1); compare({}, 12);
    compare({{{7, 0}, false, false}}, -1);
    compare({{{7, 0}, true, true}}, 7);
    compare({{{0, 10}, false, false}, {{1, 9}, false, false}, {{2, 8}, false, false},
             {{3, 1}, true, false}, {{4, 0}, false, true}}, 99);
    compare({{{9, 4}, true, true}, {{3, 4}, false, true}, {{6, 4}, true, false},
             {{1, 4}, false, false}, {{2, 4}, false, false}}, -1);
    for (int iteration = 0; iteration < 20000; ++iteration) {
        const unsigned count = random_value() % (iteration % 7 == 0 ? 513 : 65);
        std::vector<Entry> entries;
        for (unsigned i = 0; i < count; ++i) {
            const int integer_score = static_cast<int>(random_value() % 31) - 3;
            const double score = iteration % 3 == 0 ? integer_score : integer_score / 7.0;
            entries.push_back({{static_cast<int>(i * 3 + 1), score},
                               random_value() % 7 == 0, random_value() % 3 == 0});
        }
        // Every group is offered once, in an order independent of its score/ID.
        for (unsigned i = count; i > 1; --i) std::swap(entries[i - 1], entries[random_value() % i]);
        const int incumbent = iteration % 3 == 0 || entries.empty() ? -1 :
            iteration % 4 == 0 ? 100000 : entries[random_value() % count].rank.gi;
        compare(entries, incumbent);
    }
    std::printf("%u ranking checks passed\n", checks);
}
