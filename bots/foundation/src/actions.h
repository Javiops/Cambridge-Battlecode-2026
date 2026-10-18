#pragma once
#include <cstdint>
#include <optional>

namespace foundation {
struct Tile {
    int x{}, y{};
    bool operator==(const Tile&) const = default;
};
enum class Channel { none, recall, tribute, teleport };
struct Epoch {
    std::uint32_t round{}, sequence{};
    bool operator==(const Epoch&) const = default;
};
struct Observation {
    std::uint32_t round{};
    bool consistent{}, alive{};
    Tile position{};
    Channel channel{Channel::none};
};
struct Snapshot {
    Observation state;
    Epoch epoch;
};
enum class Action { wait, move, recall, tribute };
struct Request {
    Action action;
    Epoch epoch;
    Tile target{}; // Absolute movement destination, or altar tile.
};
enum class Outcome {
    waited, moved, recall_started, tribute_started, channel_active,
    rejected, stale, deferred, unconfirmed, fault
};
struct EngineError { int code; };
struct Result {
    Outcome outcome;
    std::optional<Snapshot> after;
    int engine_error{};
    // Deliberately no bool conversion: movement and channel start differ.
};

class Executor {
    std::uint32_t sequence_{};
public:
    static constexpr std::uint64_t reserve = 12000; // Initial bound; measure in guest tests.

    template<class Port> Snapshot observe(Port& port) const {
        auto state = port.read();
        return {state, {state.round, sequence_}};
    }

    template<class Port> Result execute(Port& port, const Request& request) {
        try {
            if (port.fuel() < reserve) return {Outcome::deferred, std::nullopt};
            const auto before = observe(port);
            if (!before.state.consistent || before.epoch != request.epoch)
                return {Outcome::stale, before};
            if (request.action == Action::wait) return {Outcome::waited, before};
            if (!before.state.alive) return {Outcome::rejected, before};
            if (before.state.channel != Channel::none)
                return {Outcome::channel_active, before};
            if (port.round() != request.epoch.round)
                return {Outcome::stale, std::nullopt};

            // Invalidate every sibling proposal, including after a rejected attempt.
            ++sequence_;
            int error = 0;
            bool accepted = true;
            try {
                switch (request.action) {
                    case Action::move: accepted = port.move(request.target); break;
                    case Action::recall: port.recall(); break;
                    case Action::tribute: port.tribute(request.target); break;
                    default: return {Outcome::fault, std::nullopt};
                }
            } catch (const EngineError& e) { error = e.code; }
            const auto after = observe(port);
            if (!after.state.consistent || after.state.round != before.state.round)
                return {Outcome::unconfirmed, after, error};
            if (error || !accepted) return {Outcome::rejected, after, error};
            if (request.action == Action::move && after.state.position == request.target)
                return {Outcome::moved, after};
            if (request.action == Action::recall && after.state.channel == Channel::recall)
                return {Outcome::recall_started, after};
            if (request.action == Action::tribute && after.state.channel == Channel::tribute)
                return {Outcome::tribute_started, after};
            return {Outcome::unconfirmed, after};
        } catch (...) {
            // A read/adapter failure is not an ordinary engine rejection.
            return {Outcome::fault, std::nullopt};
        }
    }
};
} // namespace foundation
