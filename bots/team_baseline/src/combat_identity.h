#pragma once
#ifndef P_FUEL_IDENTITY
#define P_FUEL_IDENTITY 1
#endif
// Runtime handle identity is immutable, including while hidden or dead. Design
// objects share the sentinel handle, so they deliberately bypass this cache.
inline bc::champion_type combat_identity_type(const bc::champion& c) {
#if P_FUEL_IDENTITY
    struct Entry { bc::handle_champion_t handle; bc::champion_type type; };
    static std::vector<Entry> identities;
    const auto handle=static_cast<bc::handle_champion_t>(c);
    if (static_cast<std::uint32_t>(handle)==std::numeric_limits<std::uint32_t>::max()) return c.champion_name();
    for(const auto& entry:identities) if(entry.handle==handle) return entry.type;
    const auto type=c.champion_name(); // An exception must never create an entry.
    identities.push_back({handle,type});
    return type;
#else
    return c.champion_name();
#endif
}
