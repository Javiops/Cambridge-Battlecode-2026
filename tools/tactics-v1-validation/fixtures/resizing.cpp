#define TACTICS_COORDINATION_MODEL_ONLY
#define TACTICS_SOLO_MODEL_ONLY
#include "coordination.h"
#include "resizing_policy.h"
#include "solo.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
static int checks = 0;
static void require(bool value, const char *why) {
    ++checks;
    if (!value) {
        std::printf("FAIL%d %s\n", checks, why);
        std::exit(1);
    }
}
static Actor actor(int id, int type, double hp, double strength, int range, Pos at) {
    Actor a;
    a.id = id;
    a.type = type;
    a.alive = true;
    a.hp = a.max_hp = hp;
    a.strength = strength;
    a.range = range;
    a.move_speed = 1;
    a.pos = at;
    a.can_attack = a.can_cast = a.can_move = true;
    return a;
}
static CurrentResizeCycle cycle(const CampRollout &r, int owner, int collector) {
    CurrentResizeCycle c;
    c.owner = owner;
    c.group = 0;
    c.round = 100;
    c.serial = 7;
    c.collector = collector;
    c.count = int(r.selected_ids.size());
    for (int k = 0; k < c.count; ++k)
        c.ids[k] = r.selected_ids[k];
    c.capture = {9, 8};
    c.bank = {7, 7};
    c.reward_once = c.collector_reward = 24;
    c.recipients = 1;
    c.collector_conversion_priced = true;
    c.clear_ticks = r.ticks;
    c.capture_ticks = 8;
    c.bank_ticks = 6;
    c.known = r.complete;
    c.sufficient = r.ready;
    c.complete = true;
    return c;
}
int main() {
    auto cassi = actor(2, 3, 700, 30, 3, {8, 10});
    cassi.focus = 70;
    cassi.spells[0].kind = 2;
    cassi.spells[0].slot = 0;
    cassi.spells[0].amount = 140;
    cassi.spells[0].range = 4;
    cassi.spells[0].camps = true;
    cassi.spells[0].ready = true;
    cassi.spells[0].cooldown = 0;
    cassi.spells[0].recharge = 8;
    auto issac = actor(0, 4, 900, 40, 1, {8, 8});
    Camp target;
    target.id = 10;
    target.pos = {9, 8};
    target.hp = target.max_hp = 20;
    target.range = 3;
    target.awake = true;
    std::vector<CampClearMonster> monsters{{target, true}};
    CampClearBody ca;
    ca.actor = cassi;
    CampClearBody ia;
    ia.actor = issac;
    auto both = basic_clear_rollout(std::vector{ca, ia}, monsters, cassi.id);
    auto remaining = basic_clear_rollout(std::vector{ia}, monsters, issac.id);
    require(both && remaining && both->ready && remaining->ready,
            "actual shared sufficient kernel certifies both fixed crews");
    require(both->ticks == 1 && remaining->ticks == 1,
            "extra member does not accelerate final20HP basic window");
    require(resize_current_basic_lethal(cassi, target) &&
                resize_current_basic_lethal(issac, target),
            "exact current harmless lethal proof agrees with shared one-tick kernel");
    {
        auto a = issac;
        a.completed = true;
        require(!resize_current_basic_lethal(a, target),
                "completed remaining owner cannot promise same-round completion");
    }
    {
        auto a = issac;
        a.can_attack = false;
        require(!resize_current_basic_lethal(a, target),
                "spent remaining attack cannot promise same-round completion");
    }
    {
        auto a = issac;
        a.stunned = true;
        require(!resize_current_basic_lethal(a, target),
                "stunned remaining participant is unavailable");
    }
    {
        auto c = target;
        c.strength = 1;
        require(!resize_current_basic_lethal(issac, c),
                "O1 certificate never substitutes for damaging-camp survival");
    }
    {
        auto a = issac;
        a.strength = 55.55555725097656;
        auto c = target;
        c.hp = 500;
        const auto lower = resize_basic_hit_lower(a, c);
        require(lower && std::ceil(c.hp / *lower) == 10,
                "f32 subtraction boundary cannot underprice nine ideal hits");
    }
    require(resize_collector_current_basic(issac, target),
            "healthy actual collector can recertify retained job");
    {
        auto a = issac;
        a.hp = Settings::ordinary_heal * a.max_hp - 1;
        require(!resize_collector_current_basic(a, target),
                "mandatory-heal collector cannot promise no-delay retention");
    }
    {
        auto a = issac;
        a.hp = Settings::ordinary_heal * a.max_hp;
        require(resize_collector_current_basic(a, target),
                "existing ordinary-heal boundary is retained exactly");
    }
    require(resize_bank_certificate(true, false, false),
            "current visible warning-free unlocked bank remains valid");
    require(!resize_bank_certificate(false, false, false),
            "unseen bank is no completed endpoint certificate");
    require(!resize_bank_certificate(true, true, false),
            "known bank warning vetoes the completed itinerary");
    require(!resize_bank_certificate(true, false, true),
            "known enemy lock work cannot be omitted from completed itinerary");
    {
        Mission job;
        job.start = 99;
        job.expiry = 101;
        require(resize_retained_job_active(job, 100),
                "live finite current commitment passes before expiry");
        job.expiry = 100;
        require(!resize_retained_job_active(job, 100),
                "expiry boundary returns to ordinary current repricing");
        job.expiry = 99;
        require(!resize_retained_job_active(job, 100),
                "old crew metadata cannot survive expired lease");
        job.expiry = 102;
        job.start = 101;
        require(!resize_retained_job_active(job, 100),
                "future commitment start is no active retained baseline");
        job.start = -1;
        require(!resize_retained_job_active(job, 100),
                "unset current commitment cannot become resizing baseline");
    }
    auto base = cycle(*both, 2, 0), split = cycle(*remaining, 2, 0);
    Camp other;
    other.id = 11;
    other.pos = {9, 11};
    other.hp = other.max_hp = 500;
    other.range = 3;
    const auto alternative = certify_solo_clear(cassi, other, cassi.pos, 0, true, 0, 64, false);
    require(alternative.known && alternative.feasible,
            "shared actual solo kernel proves a different current fixed-tile job");
    base.group_gems = split.group_gems = 24;
    base.recipient_bound = split.recipient_bound = 1;
    CurrentResizeAlternative alt;
    alt.owner = 2;
    alt.body = 2;
    alt.group = 1;
    alt.round = 100;
    alt.serial = 7;
    alt.reward_once = 24;
    alt.group_gems = 24;
    alt.recipient_bound = 1;
    alt.complete_ticks = alternative.clear_ticks + 8 + 6;
    alt.known = alt.sufficient = alt.complete = true;
    CurrentResizeOption option{CurrentResizeKind::ReleaseSelf, split, alt};
    auto decide = [&](CurrentResizeOption o) {
        return compare_current_resize(base, std::span(&o, 1));
    };
    auto d = decide(option);
    require(d.baseline_known && d.kind == CurrentResizeKind::ReleaseSelf && d.option == 0,
            "marginal self release admits independently priced different gem itinerary");
    require(d.changed_value > d.keep_value,
            "team reward counted once plus distinct alternative improves model value");
    {
        auto o = option;
        o.alternative.known = false;
        require(decide(o).kind == CurrentResizeKind::Keep,
                "unknown alternative never becomes free zero");
    }
    {
        auto o = option;
        o.alternative.sufficient = false;
        require(decide(o).option == -1, "unaffordable alternative retains productive job");
    }
    {
        auto o = option;
        o.alternative.complete = false;
        require(decide(o).option == -1, "missing bank/return itinerary retains productive job");
    }
    {
        auto o = option;
        o.alternative.group = 0;
        require(decide(o).option == -1, "same reward is not a distinct alternative");
    }
    {
        auto o = option;
        o.alternative.round = 99;
        require(decide(o).option == -1, "stale counterpart owner round declines");
    }
    {
        auto o = option;
        o.alternative.serial = 6;
        require(decide(o).option == -1, "same-round changed snapshot declines");
    }
    {
        auto o = option;
        o.alternative.body = 0;
        require(decide(o).option == -1, "another body's alternative cannot authorize self split");
    }
    {
        auto o = option;
        o.cycle.collector = 2;
        require(decide(o).option == -1, "no fictional collector handoff");
    }
    {
        auto o = option;
        o.cycle.capture = {10, 8};
        require(decide(o).option == -1, "different collection endpoint is not a paired comparison");
    }
    {
        auto o = option;
        o.cycle.bank = {8, 7};
        require(decide(o).option == -1, "specific bank endpoint consistency required");
    }
    {
        auto o = option;
        o.cycle.reward_once = 48;
        require(decide(o).option == -1, "no duplicated team reward in changed crew");
    }
    {
        auto o = option;
        o.cycle.known = false;
        require(decide(o).option == -1, "unknown remaining crew retains incumbent");
    }
    {
        auto o = option;
        o.cycle.sufficient = false;
        require(decide(o).option == -1, "missing remaining survival certificate retains incumbent");
    }
    {
        auto o = option;
        o.cycle.complete = false;
        require(decide(o).option == -1, "remaining clear alone does not prove conversion");
    }
    {
        auto o = option;
        o.cycle.recipients = 2;
        require(decide(o).option == -1,
                "two possible payout recipients cannot use one bank itinerary");
    }
    {
        auto o = option;
        o.cycle.collector_conversion_priced = false;
        require(decide(o).option == -1,
                "one nominated collector alone does not prove all reward conversion");
    }
    {
        auto o = option;
        o.cycle.collector_reward = 12;
        require(decide(o).option == -1,
                "personal12 share cannot be priced as whole24 secured score");
    }
    {
        auto o = option;
        o.cycle.clear_ticks = 2;
        require(decide(o).option == -1, "release cannot delay the incumbent actual clear window");
    }
    {
        auto o = option;
        o.cycle.capture_ticks += 1;
        require(decide(o).option == -1, "release preserves actual collector capture window");
    }
    {
        auto o = option;
        o.cycle.bank_ticks += 1;
        require(decide(o).option == -1, "release preserves existing bank obligation");
    }
    {
        auto o = option;
        o.alternative.reward_once = 0;
        require(decide(o).option == -1,
                "no unpriced zero-value wait masquerading as independent work");
    }
    {
        auto o = option;
        o.alternative.complete_ticks = 0;
        require(decide(o).option == -1, "no divide by zero opportunity");
    }
    {
        auto o = option;
        o.alternative.complete_ticks = std::numeric_limits<double>::infinity();
        require(decide(o).option == -1, "nonfinite alternative remains unknown");
    }
    {
        auto o = option;
        o.cycle.clear_ticks = 1000;
        require(decide(o).option == -1,
                "a slower remaining crew must justify its lost completion value");
    }
    {
        auto old = base;
        base.collector = 2;
        auto o = option;
        o.cycle.collector = 2;
        require(decide(o).option == -1, "actual collector cannot self release");
        base = old;
    }
    {
        auto old = base;
        base.known = false;
        require(!decide(option).baseline_known, "no comparison without valid actual incumbent");
        base = old;
    }
    {
        auto old = base;
        base.ids[1] = base.ids[0];
        require(!decide(option).baseline_known, "duplicate bodies do not produce headcount");
        base = old;
    }
    {
        auto old = base;
        base.owner = 0;
        auto o = option;
        o.cycle.owner = 0;
        o.cycle.ids[0] = 2;
        o.cycle.collector = 2;
        o.alternative.owner = 0;
        o.alternative.body = 0;
        require(decide(o).option == -1, "lowest-ID member cannot mutually yield to higher-ID crew");
        base = old;
    }
    {
        auto a = cassi;
        a.can_attack = a.can_cast = false;
        auto current = certify_solo_clear(a, other, a.pos, 0, true, 0, 64, false);
        require(!current.known && !current.feasible,
                "spent current permissions do not gain a free present hit");
    }
    // Addition is compared against the added actor's actual lost-work rate,
    // rather than treating every visible extra body as a free improvement.
    auto alone = base;
    alone.count = 1;
    alone.ids[0] = 2;
    alone.collector = 2;
    alone.clear_ticks = 50;
    auto joined = base;
    joined.collector = 2;
    joined.clear_ticks = 5;
    CurrentResizeAlternative added = alt;
    added.body = 0;
    added.complete_ticks = 500;
    CurrentResizeOption add{CurrentResizeKind::AddOne, joined, added};
    require(compare_current_resize(alone, std::span(&add, 1)).kind == CurrentResizeKind::AddOne,
            "large secured-time gain can beat a known slow different job");
    added.complete_ticks = 5;
    add.alternative = added;
    require(compare_current_resize(alone, std::span(&add, 1)).kind == CurrentResizeKind::Keep,
            "a highly productive added actor remains on its better alternative");
    add.alternative.known = false;
    require(compare_current_resize(alone, std::span(&add, 1)).kind == CurrentResizeKind::Keep,
            "unknown new helper cost retains valid solo");
    {
        auto o = option;
        const auto x = compare_current_resize(base, std::span(&o, 1),
                                              std::numeric_limits<double>::quiet_NaN());
        require(!x.baseline_known, "invalid margin cannot authorize changes");
    }
    {
        auto b = base;
        auto o = option;
        b.reward_scope = o.cycle.reward_scope = ResizeRewardScope::PersonalShareLowerBound;
        b.recipient_bound = o.cycle.recipient_bound = 6;
        b.reward_once = b.collector_reward = o.cycle.reward_once = o.cycle.collector_reward = 4;
        o.alternative.reward_scope = ResizeRewardScope::PersonalShareLowerBound;
        o.alternative.recipient_bound = 6;
        o.alternative.reward_once = 4;
        o.alternative.complete_ticks = 500;
        require(compare_current_resize(b, std::span(&o, 1)).kind == CurrentResizeKind::Keep,
                "small secured personal share cannot borrow entire alternate team reward to "
                "justify release");
        o.alternative.reward_once = 24;
        require(compare_current_resize(b, std::span(&o, 1)).kind == CurrentResizeKind::Keep,
                "optimistic full payout with six possible recipients is invalid");
        o.alternative.reward_once = 4;
        o.alternative.recipient_bound = 0;
        require(compare_current_resize(b, std::span(&o, 1)).kind == CurrentResizeKind::Keep,
                "unknown participant bound stays unknown");
    }
    std::printf("%d current-resizing checks passed; shared release witness clear=%.0f/%.0f "
                "alternate=%.0f\n",
                checks, both->ticks, remaining->ticks, alternative.clear_ticks);
}
