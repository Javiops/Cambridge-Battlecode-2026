#pragma once
#include "types.h"
#include <span>

namespace tactics {
// A small personal visible route proof, never a completed whole-map field.
// The first path cannot walk through the living camp. Only the second path,
// after its certified clear, may enter that selected camp's vacated tile.
struct SoloLocalRoute {
    Pos stage{};
    std::array<Pos, 25> route{}, capture_route{};
    int route_length = 0, capture_length = 0, arrival_steps = -1, capture_steps = -1, visited = 0;
    bool known = false;
};
struct SoloRouteAlwaysFunded {
    bool operator()() const {
        return true;
    }
};
template <class Funded = SoloRouteAlwaysFunded>
inline SoloLocalRoute
visible_solo_route(int width, int height, std::span<const std::uint8_t> terrain,
                   std::span<const std::uint8_t> occupied, std::span<const std::uint8_t> visible,
                   Pos origin, Pos camp, int basic_range, int speed, int max_nodes = 128,
                   Funded funded = {}) {
    SoloLocalRoute out;
    if (!funded())
        return out;
    if (width <= 0 || height <= 0 || width > 65535 / height || basic_range < 1 || speed < 1 ||
        speed > 8 || max_nodes < 1 || max_nodes > 128 ||
        terrain.size() < std::size_t((width * height + 7) / 8) ||
        occupied.size() < std::size_t((width * height + 7) / 8) ||
        visible.size() < std::size_t((width * height + 7) / 8))
        return out;
    const auto valid = [&](Pos p) { return p.x >= 0 && p.y >= 0 && p.x < width && p.y < height; };
    if (!valid(origin) || !valid(camp))
        return out;
    const auto index = [&](Pos p) { return p.y * width + p.x; };
    const auto bit = [](std::span<const std::uint8_t> bytes, int i) {
        return (bytes[std::size_t(i) >> 3] & (1u << (i & 7))) != 0;
    };
    const auto legal = [&](Pos p, bool after_clear) {
        if (!valid(p) || bit(terrain, index(p)) || !bit(visible, index(p)))
            return false;
        return p == origin || (after_clear && p == camp) || !bit(occupied, index(p));
    };
    struct Node {
        Pos at{};
        int parent = -1, depth = 0;
    };
    std::array<Node, 128> nodes;
    std::array<int, 256> seen;
    auto search = [&](Pos start, bool capture) -> int {
        if (!funded() || out.visited >= max_nodes)
            return -1;
        ++out.visited;
        seen.fill(-1);
        int size = 1, head = 0;
        nodes[0] = {start, -1, 0};
        auto insert = [&](Pos p, int node) {
            const int key = index(p);
            unsigned slot = (unsigned(key) * 2654435761u) & 255u;
            while (seen[slot] >= 0 && index(nodes[seen[slot]].at) != key)
                slot = (slot + 1) & 255u;
            if (seen[slot] >= 0)
                return false;
            seen[slot] = node;
            return true;
        };
        insert(start, 0);
        while (head < size) {
            if (!funded())
                return -1;
            const Node current = nodes[head];
            const int lower = capture ? distance(current.at, camp)
                                      : std::max(0, distance(current.at, camp) - basic_range);
            if (current.depth + lower > 3 * speed) {
                ++head;
                continue;
            }
            if ((capture && current.at == camp) ||
                (!capture && distance(current.at, camp) <= basic_range))
                return head;
            if (current.depth >= 3 * speed) {
                ++head;
                continue;
            }
            for (int dy = -1; dy <= 1; ++dy)
                for (int dx = -1; dx <= 1; ++dx) {
                    if (!dx && !dy)
                        continue;
                    Pos next{current.at.x + dx, current.at.y + dy};
                    if (!legal(next, capture))
                        continue;
                    const int lower = capture ? distance(next, camp)
                                              : std::max(0, distance(next, camp) - basic_range);
                    if (current.depth + 1 + lower > 3 * speed)
                        continue;
                    if (out.visited >= max_nodes || size >= 128)
                        return -1;
                    // Slot assignment precedes initialization only for a new
                    // key; no existing entry refers to this unused node.
                    if (!insert(next, size))
                        continue;
                    nodes[size++] = {next, head, current.depth + 1};
                    ++out.visited;
                }
            ++head;
        }
        return -1;
    };
    if (!legal(origin, false))
        return out;
    int found = search(origin, false);
    if (found < 0)
        return out;
    out.stage = nodes[found].at;
    out.arrival_steps = nodes[found].depth;
    out.route_length = out.arrival_steps + 1;
    for (int k = out.arrival_steps; k >= 0; --k) {
        out.route[k] = nodes[found].at;
        found = nodes[found].parent;
    }
    found = search(out.stage, true);
    if (found < 0)
        return out;
    out.capture_steps = nodes[found].depth;
    out.capture_length = out.capture_steps + 1;
    for (int k = out.capture_steps; k >= 0; --k) {
        out.capture_route[k] = nodes[found].at;
        found = nodes[found].parent;
    }
    out.known = true;
    return out;
}

// A bounded shortest visible approach to an OUTER casting annulus, followed
// by a separate post-clear capture path. A*'s Chebyshev lower bound avoids
// flooding the entire radius-four square for an already valid current tile.
// No occupancy other than self and the selected dead camp is wished away.
template <class Funded = decltype([] { return true; })>
inline SoloLocalRoute
visible_solo_annulus_route(int width, int height, std::span<const std::uint8_t> terrain,
                           std::span<const std::uint8_t> occupied,
                           std::span<const std::uint8_t> visible, Pos origin, Pos camp,
                           int minimum_range, int maximum_range, int speed, int max_nodes = 128,
                           Funded funded = {}) {
    SoloLocalRoute out;
    if (!funded() || width <= 0 || height <= 0 || width > 65535 / height || minimum_range < 1 ||
        maximum_range < minimum_range || maximum_range > 24 || speed < 1 || speed > 8 ||
        max_nodes < 2 || max_nodes > 128 ||
        terrain.size() < std::size_t((width * height + 7) / 8) ||
        occupied.size() < std::size_t((width * height + 7) / 8) ||
        visible.size() < std::size_t((width * height + 7) / 8))
        return out;
    const auto valid = [&](Pos p) { return p.x >= 0 && p.y >= 0 && p.x < width && p.y < height; };
    if (!valid(origin) || !valid(camp))
        return out;
    const auto index = [&](Pos p) { return p.y * width + p.x; };
    const auto bit = [](auto bytes, int i) {
        return (bytes[std::size_t(i) >> 3] & (1u << (i & 7))) != 0;
    };
    const auto legal = [&](Pos p, bool capture) {
        return valid(p) && !bit(terrain, index(p)) && bit(visible, index(p)) &&
               (p == origin || (capture && p == camp) || !bit(occupied, index(p)));
    };
    if (!legal(origin, false))
        return out;
    struct Node {
        Pos at{};
        int parent = -1, depth = 0;
        bool closed = false;
    };
    struct Entry {
        int total = 0, lower = 0, node = -1, depth = 0;
    };
    std::array<Node, 128> nodes;
    std::array<int, 256> seen;
    std::array<Entry, 256> heap;
    const auto later = [](const Entry &a, const Entry &b) {
        if (a.total != b.total)
            return a.total > b.total;
        if (a.lower != b.lower)
            return a.lower > b.lower;
        return a.node > b.node;
    };
    auto search = [&](Pos start, bool capture) -> int {
        if (!funded() || out.visited >= max_nodes)
            return -1;
        seen.fill(-1);
        int count = 1, queued = 0;
        nodes[0] = {start, -1, 0, false};
        ++out.visited;
        const int limit = capture ? std::min(24, std::max(maximum_range, 3 * speed)) : 3 * speed;
        const auto lower = [&](Pos p) {
            const int d = distance(p, camp);
            return capture ? d : std::max({0, minimum_range - d, d - maximum_range});
        };
        const auto lookup = [&](Pos p) {
            unsigned slot = (unsigned(index(p)) * 2654435761u) & 255u;
            while (seen[slot] >= 0 && nodes[seen[slot]].at != p)
                slot = (slot + 1) & 255u;
            return slot;
        };
        seen[lookup(start)] = 0;
        auto push = [&](int node) {
            if (queued == int(heap.size()))
                return false;
            const int h = lower(nodes[node].at);
            heap[queued++] = {nodes[node].depth + h, h, node, nodes[node].depth};
            std::push_heap(heap.begin(), heap.begin() + queued, later);
            return true;
        };
        push(0);
        while (queued) {
            if (!funded())
                return -1;
            std::pop_heap(heap.begin(), heap.begin() + queued, later);
            const auto entry = heap[--queued];
            auto &current = nodes[entry.node];
            if (current.closed || current.depth != entry.depth)
                continue;
            current.closed = true;
            if (lower(current.at) == 0)
                return entry.node;
            if (current.depth >= limit)
                continue;
            const Pos at = current.at;
            const int depth = current.depth + 1;
            for (int dy = -1; dy <= 1; ++dy)
                for (int dx = -1; dx <= 1; ++dx) {
                    const Pos next{at.x + dx, at.y + dy};
                    if ((!dx && !dy) || !legal(next, capture) || depth + lower(next) > limit)
                        continue;
                    const auto slot = lookup(next);
                    int node = seen[slot];
                    if (node >= 0) {
                        if (nodes[node].closed || nodes[node].depth <= depth)
                            continue;
                        nodes[node].depth = depth;
                        nodes[node].parent = entry.node;
                    } else {
                        if (out.visited >= max_nodes || count == int(nodes.size()))
                            return -1;
                        seen[slot] = node = count++;
                        nodes[node] = {next, entry.node, depth, false};
                        ++out.visited;
                    }
                    if (!push(node))
                        return -1;
                }
        }
        return -1;
    };
    int found = search(origin, false);
    if (found < 0)
        return out;
    out.stage = nodes[found].at;
    out.arrival_steps = nodes[found].depth;
    out.route_length = out.arrival_steps + 1;
    for (int k = out.arrival_steps; k >= 0; --k) {
        out.route[k] = nodes[found].at;
        found = nodes[found].parent;
    }
    found = search(out.stage, true);
    if (found < 0)
        return out;
    out.capture_steps = nodes[found].depth;
    out.capture_length = out.capture_steps + 1;
    for (int k = out.capture_steps; k >= 0; --k) {
        out.capture_route[k] = nodes[found].at;
        found = nodes[found].parent;
    }
    out.known = true;
    if (!funded())
        out.known = false;
    return out;
}
} // namespace tactics
