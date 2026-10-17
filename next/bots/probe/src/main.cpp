// probe-v1: not a player. On its first turn it prints the game's constants and every champion's base
// stats, so mechanics/ is written from what the engine says, not from memory (python3 -m lab probe).
#include <algorithm>
#include <cambc.h>
#include <cstdint>
#include <iostream>
#include <span>

static void print_once() {
    namespace k = cambc::constants;
    std::cout << "CONST capture_time " << k::capture_time << "\nCONST camp_sleep_time " << k::camp_sleep_time
              << "\nCONST respawn_time " << k::respawn_time << "\nCONST recall_time " << k::recall_time
              << "\nCONST submit_gem_duration_multiplier " << k::submit_gem_duration_multiplier
              << "\nCONST submit_gem_base_duration " << k::submit_gem_base_duration
              << "\nCONST submit_gem_minimum_duration " << k::submit_gem_minimum_duration
              << "\nCONST submit_gems_range " << k::submit_gems_range << "\nCONST max_rounds " << k::max_rounds
              << "\nCONST winning_gems " << k::winning_gems << "\nCONST kill_gold " << k::kill_gold
              << "\nCONST assist_gold " << k::assist_gold << "\nCONST passive_gold " << k::passive_gold
              << "\nCONST spawn_healing " << k::spawn_healing << "\nCONST active_wards " << k::active_wards
              << "\nCONST shared_memory_bytes " << k::shared_memory_bytes
              << "\nCONST draft_memory_bytes " << k::draft_memory_bytes
              << "\nCONST tile_reveal_rounds " << k::tile_reveal_rounds << "\nCONST ward_cooldown " << k::ward_cooldown
              << "\nCONST ward_lifetime " << k::ward_lifetime << "\nCONST ward_vision_radius " << k::ward_vision_radius
              << "\nCONST ward_placement_radius " << k::ward_placement_radius
              << "\nCONST altar_lock_hits " << k::altar_lock_hits << "\nCONST tp_crystal_time " << k::tp_crystal_time << "\n";
    const char* names[] = {"Ryth", "Vesper Vale", "Vendetta", "Cassi", "Issac", "Stellar",
                           "Prism", "Marcella", "Willow", "Ren", "Varg", "Tavi"};
    for (int t = 0; t < 12; ++t) {
        cambc::detail::champion_design d{};
        if (cambc::detail::sdk_champion_design(t, &d) != 0) continue;
        const auto& s = d.base_stats;
        std::cout << "CHAMP " << names[t] << " | " << s.vision_radius << " | " << s.base_move_speed << " | "
                  << s.base_attack_range << " | " << s.base_health << " | " << s.health_growth << " | "
                  << s.base_strength << " | " << s.strength_growth << " | " << s.base_focus << " | "
                  << s.focus_growth << " | " << s.camp_damage_multiplier << "\n";
    }
    std::cout << "MAP " << cambc::map::width() << "x" << cambc::map::height() << "\n" << std::flush;
}

int main() {
    bool printed = false;
    while (true) {
        if (cambc::is_draft()) {
            const auto chosen = cambc::draft::current_draft(cambc::team::ally);
            for (int i = 0; i < 11; ++i) {
                auto pick = static_cast<cambc::champion_draft>(i);
                if (std::find(chosen.begin(), chosen.end(), pick) == chosen.end()) { cambc::draft::pick(pick); break; }
            }
        } else if (!printed) {
            // Every champion runs this bot; only the first to get here prints (flag in shared memory byte 7).
            printed = true;
            std::uint8_t done = 0;
            cambc::shared_memory.read(7, std::span{&done, 1});
            if (!done) {
                done = 1;
                cambc::shared_memory.write(7, std::span{&done, 1});
                print_once();
            }
        }
        cambc::end_turn();
    }
}
