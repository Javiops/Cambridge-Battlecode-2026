#include "actions.h"
#include "coordinator.h"
#include "shopping.h"
#include <cstdio>
#include <memory>
#include <stdexcept>
using namespace tactics;
static void burn_to(unsigned n) {
    volatile unsigned x = 1;
    while (bc::fuel_remaining() > n)
        x = x * 1664525u + 1013904223u;
}
static void check(bool ok, const char *name) {
    if (!ok) {
        std::printf("SHOP_GEM_FAIL %s\n", name);
        std::fflush(stdout);
        throw std::runtime_error(name);
    }
}
static const Camp *view_camp(const World &w, int id) {
    for (const auto &g : w.groups)
        for (const auto &c : g.camps)
            if (c.id == id)
                return &c;
    return nullptr;
}
int main() {
    Geometry geo;
    Memory m;
    ShoppingState shop;
    std::unique_ptr<World> world;
    int phase = 0, gold = -1, gem = -1, warmups = 0;
    Actor predicted;
    int initial_gold = 0;
    while (true) {
        if (bc::is_draft()) {
            bc::draft::pick(bc::champion_draft::ryth);
            bc::end_turn();
            continue;
        }
        geo.initialize();
        if (!geo.initialized) {
            bc::end_turn();
            continue;
        }
        if (phase >= 10) {
            bc::end_turn();
            continue;
        }
        if (gold < 0) {
            int best = unreachable;
            for (const auto &g : geo.groups)
                if (g.gold > 0 && g.gems == 0 && g.spawns.size() == 1) {
                    int d = geo.at(geo.home, g.spawns[0].pos);
                    if (d < best) {
                        best = d;
                        gold = g.index;
                    }
                }
            best = unreachable;
            for (const auto &g : geo.groups)
                if (g.gems > 0 && g.initial_hp == 2400 && g.spawns.size() == 1) {
                    int d = geo.at(geo.home, g.spawns[0].pos);
                    if (d < best) {
                        best = d;
                        gem = g.index;
                    }
                }
            check(gold >= 0 && gem >= 0, "real gold and2400HP gem singleton");
        }
        const Pos goldpos = geo.groups[gold].spawns.front().pos;
        geo.goal_field(goldpos, 0);
        if (world)
            if (auto hint = shopping_gem_route_hint(*world, shop))
                geo.goal_field(*hint, 0);
        if (!world)
            world = std::make_unique<World>(geo, m);
        world->refresh();
        auto &w = *world;
        check(w.self.alive, "fixture remains alive");
        Action act;
        if (phase == 0) {
            if (w.gold >= 300) {
                phase = 1;
                act.kind = Kind::Recall;
            } else {
                const Camp *camp = nullptr;
                for (const auto &c : w.groups[gold].camps)
                    if (c.hp > 0)
                        camp = &c;
                if (camp) {
                    if (distance(w.self.pos, camp->pos) <= w.self.range && w.self.can_attack) {
                        act.kind = Kind::BasicCamp;
                        act.target = camp->id;
                    } else if (auto step = w.toward(camp->pos, w.self.range)) {
                        act.kind = Kind::Move;
                        act.at = *step;
                    }
                } else if (w.groups[gold].state == Lifecycle::Reward) {
                    if (w.self.pos != goldpos)
                        if (auto step = w.toward(goldpos, 0)) {
                            act.kind = Kind::Move;
                            act.at = *step;
                        }
                } else if (w.self.pos == goldpos) {
                    Pos leave{goldpos.x - 1, goldpos.y - 1};
                    if (w.geo.blocked(leave) || w.in_spawn(leave))
                        leave = {goldpos.x + 1, goldpos.y + 1};
                    if (w.free(leave)) {
                        act.kind = Kind::Move;
                        act.at = leave;
                    }
                }
            }
        } else if (phase == 1) {
            if (w.in_spawn(w.self.pos) && w.self.channel == Channel::None) {
                act.kind = Kind::Buy;
                act.item = 10;
                act.count = 5;
                phase = 2;
            }
        } else if (phase == 2) {
            check(w.self.max_hp == 1800 && w.gold >= 150, "actual preload/private wallet");
            if (w.in_spawn(w.self.pos)) {
                if (auto step = w.toward(goldpos, 1)) {
                    act.kind = Kind::Move;
                    act.at = *step;
                }
            } else {
                m.mission = {};
                m.mission.phase = Phase::Travel;
                m.mission.group = gold;
                m.mission.target = goldpos;
                m.mission.rate = .2;
                m.mission.start = m.mission.last_progress = w.round;
                m.mission.expiry = w.round + 6;
                if (auto hint = shopping_gem_route_hint(w, shop)) {
                    geo.goal_field(*hint, 0);
                    bc::end_turn();
                    continue;
                }
                if (!assembly_detail::simple_sleeping(w, gem)) {
                    if (auto step = w.toward(goldpos, 1)) {
                        act.kind = Kind::Move;
                        act.at = *step;
                    }
                } else {
                    burn_to(65000);
                    const unsigned start = bc::fuel_remaining();
                    plan_upgrade_return(w, m, shop);
                    std::printf("SHOP_GEM_PLAN %d %u %u %d %d %d %d\n", w.self.id, start,
                                unsigned(bc::fuel_remaining()), shop.investment_item,
                                shop.investment_mission.group, shop.investment_origin.group,
                                m.upgrade_gem_unlock);
                    if (shop.investment_item < 0) {
                        check(++warmups < 6, "bounded immutable warmup eventually activates");
                        bc::end_turn();
                        continue;
                    }
                    check(m.upgrade_gem_unlock, "actual wallet activates proven unlock");
                    check(shop.investment_origin.group == gold &&
                              shop.investment_mission.group == gem && m.mission.group == gold,
                          "origin retained before actual install");
                    const auto inv = shop_inventory(w.me.item_count());
                    predicted = project_bundle_actor(w.self, upgrade_delta(shop.investment_item,
                                                                           inv, w.me.base_stats(),
                                                                           shop.investment_count));
                    initial_gold = w.gold;
                    phase = 3;
                    act.kind = Kind::Recall;
                }
            }
        } else if (phase == 3) {
            if (w.in_spawn(w.self.pos) && w.self.channel == Channel::None) {
                auto buy = shopping_proposal(w, m.mission, shop);
                check(buy && buy->kind == Kind::Buy, "named bundle proposal after real recall");
                act = *buy;
                phase = 4;
            }
        } else if (phase == 5) {
            check(w.self.hp == w.self.max_hp && w.self.max_hp == predicted.max_hp &&
                      std::abs(w.self.strength - predicted.strength) < .001 &&
                      std::abs(w.self.focus - predicted.focus) < .001 &&
                      std::abs(w.self.camp_mitigation - predicted.camp_mitigation) < .001,
                  "actual postinstall stats equal projected power");
            check(w.gold == initial_gold - 150, "exact real private wallet payment");
            check(m.mission.group == gem && m.mission.phase == Phase::Reenter &&
                      !m.upgrade_gem_unlock && shop.investment_item < 0,
                  "new gem job only restored after verified install and unlock flag clears");
            std::printf("SHOP_GEM_INSTALL %d %d %d %d %u\n", w.self.id, w.round, w.gold,
                        m.mission.group, unsigned(bc::fuel_remaining()));
            phase = 6;
        }

        if (phase == 6) {
            const Camp *camp = nullptr;
            for (const auto &c : w.groups[gem].camps)
                if (c.hp > 0)
                    camp = &c;
            if (!camp) {
                if (w.groups[gem].state == Lifecycle::Reward)
                    phase = 7;
                else if (auto step = w.toward(geo.groups[gem].spawns[0].pos, w.self.range)) {
                    act.kind = Kind::Move;
                    act.at = *step;
                }
            } else if (distance(w.self.pos, camp->pos) <= w.self.range) {
                if (w.self.can_attack) {
                    act.kind = Kind::BasicCamp;
                    act.target = camp->id;
                }
            } else if (auto step = w.toward(camp->pos, w.self.range)) {
                act.kind = Kind::Move;
                act.at = *step;
            }
        }
        if (phase == 7) {
            if (w.self.gems > 0)
                phase = 8;
            else {
                const Pos at = geo.groups[gem].spawns[0].pos;
                if (w.self.pos != at)
                    if (auto step = w.toward(at, 0)) {
                        act.kind = Kind::Move;
                        act.at = *step;
                    }
            }
        }
        if (phase == 8 && w.self.channel == Channel::None) {
            if (w.self.gems == 0 && w.own_score > 0)
                phase = 9;
            else {
                int best = unreachable;
                Pos altar{};
                for (auto q : geo.altars) {
                    int d = geo.at(geo.home, q);
                    for (int dy = -1; dy <= 1; ++dy)
                        for (int dx = -1; dx <= 1; ++dx)
                            d = std::min(d, geo.at(geo.home, {q.x + dx, q.y + dy}));
                    if (d < best) {
                        best = d;
                        altar = q;
                    }
                }
                if (distance(w.self.pos, altar) <= 1) {
                    act.kind = Kind::Tribute;
                    act.at = altar;
                } else if (auto step = w.toward(altar, 1)) {
                    act.kind = Kind::Move;
                    act.at = *step;
                }
            }
        }
        if (phase == 9 && w.self.channel == Channel::None) {
            if (w.in_spawn(w.self.pos)) {
                if (w.self.hp == w.self.max_hp) {
                    check(w.own_score == geo.groups[gem].gems && w.self.gems == 0,
                          "actual newly affordable gem cycle banked and recovered");
                    std::printf("SHOP_GEM_PASS %d %d %d %d %d %u\n", w.self.id, w.round, w.gold,
                                w.own_score, int(w.self.hp), unsigned(bc::fuel_remaining()));
                    phase = 10;
                }
            } else
                act.kind = Kind::Recall;
        }
        if (act.kind != Kind::None) {
            act.reason = phase == 4 ? "install-priced-return-bundle" : "native-gold-unlock-script";
            const auto result = execute(w, act);
            check(result.outcome == Outcome::Applied || result.outcome == Outcome::Started,
                  "actual scripted SDK action succeeds");
            if (phase == 4) {
                w.refresh(true);
                shopping_after_action(w, act, true, shop);
                phase = 5;
            }
            if (phase == 6 && act.kind == Kind::BasicCamp) {
                w.refresh_local_effects(act);
                const Camp *camp = view_camp(w, act.target);
                if (camp && camp->hp > 0) {
                    int chosen = -1;
                    double amount = 0;
                    for (int k = 0; k < 2; ++k) {
                        const auto &sp = w.spells[k];
                        if (sp.ready && sp.camps &&
                            (sp.kind == 2 || sp.kind == 3 || sp.kind == 4) &&
                            distance(w.self.pos, camp->pos) <= sp.range && sp.amount > amount) {
                            chosen = k;
                            amount = sp.amount;
                        }
                    }
                    if (chosen < 0)
                        for (int k = 0; k < 2; ++k)
                            if (w.spells[k].ready && w.spells[k].kind == 1 && w.spells[k].self)
                                chosen = k;
                    if (chosen >= 0) {
                        Action cast;
                        cast.slot = chosen;
                        const bool reset = w.spells[chosen].kind == 1;
                        cast.kind = reset ? Kind::CastSelf : Kind::CastCamp;
                        cast.target = camp->id;
                        auto result = execute(w, cast);
                        check(result.outcome == Outcome::Applied,
                              "actual priced farm cast sequence");
                        w.refresh_local_effects(cast);
                        if (reset) {
                            const auto *live = view_camp(w, act.target);
                            if (live && live->hp > 0 && w.self.can_attack) {
                                auto extra = execute(w, act);
                                check(extra.outcome == Outcome::Applied,
                                      "actual priced reset second basic");
                            }
                        }
                    }
                }
            }
        }

        bc::end_turn();
    }
}
