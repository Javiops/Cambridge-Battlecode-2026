#pragma once
#include <array>
#include <cstddef>

namespace tactics {
struct CampRank {
    int gi = -1;
    double score = 0;
};
inline bool camp_rank_before(CampRank a, CampRank b) {
    return a.score > b.score || (a.score == b.score && a.gi < b.gi);
}

template <class T, std::size_t Capacity> struct BoundedRanks {
    std::array<T, Capacity> values{};
    std::size_t count = 0;
    const T *begin() const {
        return values.data();
    }
    const T *end() const {
        return values.data() + count;
    }
    std::size_t size() const {
        return count;
    }
};

// Offer each eligible group once. The old full ordering is needed only for
// its top three entries and its first fresh reward/solo-affordable entry.
// Keep precisely those sufficient statistics in one pass, without a heap.
class CampRanking {
    std::array<CampRank, 3> top_{};
    std::size_t count_ = 0;
    CampRank reward_{}, affordable_{};

  public:
    void offer(CampRank candidate, bool fresh_reward, bool affordable) {
        if (candidate.gi < 0)
            return;
        if (fresh_reward && (reward_.gi < 0 || camp_rank_before(candidate, reward_)))
            reward_ = candidate;
        if (affordable && (affordable_.gi < 0 || camp_rank_before(candidate, affordable_)))
            affordable_ = candidate;
        std::size_t at = 0;
        while (at < count_ && !camp_rank_before(candidate, top_[at]))
            ++at;
        if (at >= top_.size())
            return;
        const auto last = count_ < top_.size() ? count_++ : top_.size() - 1;
        for (auto i = last; i > at; --i)
            top_[i] = top_[i - 1];
        top_[at] = candidate;
    }

    BoundedRanks<int, 3> shortlist(int incumbent = -1) const {
        BoundedRanks<int, 3> out;
        auto add = [&](int gi) {
            if (gi < 0 || out.count == out.values.size())
                return;
            for (auto old : out)
                if (old == gi)
                    return;
            out.values[out.count++] = gi;
        };
        add(incumbent);
        add(reward_.gi);
        add(affordable_.gi);
        for (std::size_t i = 0; i < count_; ++i)
            add(top_[i].gi);
        return out;
    }

    // Holder handoff needs the first alternative in full order. Its first
    // distinct entry is always among the top three. Include the two special
    // entries for callers inspecting the same bounded shortlist, deduplicated.
    BoundedRanks<CampRank, 5> candidates() const {
        BoundedRanks<CampRank, 5> out;
        auto add = [&](CampRank candidate) {
            if (candidate.gi < 0)
                return;
            for (auto old : out)
                if (old.gi == candidate.gi)
                    return;
            std::size_t at = out.count++;
            while (at > 0 && camp_rank_before(candidate, out.values[at - 1])) {
                out.values[at] = out.values[at - 1];
                --at;
            }
            out.values[at] = candidate;
        };
        for (std::size_t i = 0; i < count_; ++i)
            add(top_[i]);
        add(reward_);
        add(affordable_);
        return out;
    }
};
} // namespace tactics
