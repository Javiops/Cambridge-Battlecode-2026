// probe-week2-v1: print the patched engine's settings, all designs and dash effects.
#include <algorithm>
#include <array>
#include <cambc.h>
#include <cstdint>
#include <iostream>
#include <span>

static void print_once() {
    namespace bc = cambc;
    namespace k = bc::constants;
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
    namespace p = k::passive_abilities;
    std::cout << "CONST prism_focus_per_gem " << p::prism_focus_per_gem
              << "\nCONST vesper_vale_bonus_gold_percent " << p::vesper_vale_bonus_gold_percent
              << "\nCONST marcella_tribute_gold_per_gem " << p::marcella_tribute_gold_per_gem
              << "\nCONST heart_of_ruin_missing_health_damage_max_bonus " << p::heart_of_ruin_missing_health_damage_max_bonus << "\n";
    constexpr std::array champions{
        bc::champion_type::ryth, bc::champion_type::vesper_vale, bc::champion_type::vendetta,
        bc::champion_type::cassi, bc::champion_type::issac, bc::champion_type::stellar,
        bc::champion_type::prism, bc::champion_type::marcella, bc::champion_type::willow,
        bc::champion_type::ren, bc::champion_type::varg, bc::champion_type::tavi,
        bc::champion_type::heart_of_ruin};
    for (const auto type : champions) {
        const bc::champion design{type};
        const auto s = design.base_stats();
        std::cout << "CHAMP " << bc::to_string(type) << " | " << s.vision_radius << " | " << s.base_move_speed << " | "
                  << s.base_attack_range << " | " << s.base_health << " | " << s.health_growth << " | "
                  << s.base_strength << " | " << s.strength_growth << " | " << s.base_focus << " | "
                  << s.focus_growth << " | " << s.camp_damage_multiplier << "\n";
        for (const auto ability : design.abilities()) {
            if (ability.is_dash()) {
                const auto dash = ability.get<bc::ability_dash>();
                std::cout << "DASH " << bc::to_string(type) << " | " << ability.slot() << " | "
                          << dash.range << " | " << dash.radius << " | " << dash.modifier << " | " << dash.duration << "\n";
            } else if (ability.is_cc()) {
                const auto cc = ability.get<bc::ability_cc>();
                std::cout << "CC " << bc::to_string(type) << " | " << ability.slot() << " | "
                          << cc.range << " | " << cc.modifier << " | " << cc.duration << "\n";
            }
        }
    }
    constexpr std::array camps{bc::camp_type::wolf, bc::camp_type::elk, bc::camp_type::gem_cluster,
                              bc::camp_type::gold_cluster, bc::camp_type::monolith, bc::camp_type::golem};
    for (const auto type : camps) {
        bc::detail::camp_design design{};
        bc::detail::check(bc::detail::sdk_camp_design(static_cast<std::int32_t>(type), &design));
        const auto s = design.base_stats;
        std::cout << "CAMP " << bc::to_string(type) << " | " << s.base_health << " | "
                  << s.base_strength << " | " << s.base_attack_range << "\n";
    }
    std::cout << "MAP " << bc::map::width() << "x" << bc::map::height() << "\n" << std::flush;
}

int main() {
    bool printed = false;
    constexpr std::array picks{cambc::champion_draft::ryth, cambc::champion_draft::vesper_vale,
        cambc::champion_draft::vendetta, cambc::champion_draft::cassi_and_issac, cambc::champion_draft::stellar,
        cambc::champion_draft::prism, cambc::champion_draft::marcella, cambc::champion_draft::willow,
        cambc::champion_draft::ren, cambc::champion_draft::varg, cambc::champion_draft::tavi,
        cambc::champion_draft::heart_of_ruin};
    while (true) {
        if (cambc::is_draft()) {
            const auto chosen = cambc::draft::current_draft(cambc::team::ally);
            for (const auto pick : picks) {
                if (std::find(chosen.begin(), chosen.end(), pick) == chosen.end()) {
                    cambc::draft::pick(pick);
                    break;
                }
            }
        } else if (!printed) {
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
