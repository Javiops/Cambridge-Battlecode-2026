#include "../src/actions.h"
#include <cassert>
#include <cstdio>
#include <stdexcept>
#include <type_traits>
using namespace foundation;

struct Port {
    Observation state{3, true, true, {2, 2}, Channel::none};
    std::uint64_t budget = 100000;
    int calls{}, reads{}, error{};
    bool accept = true, mutate = true, suspend{}, broken_read{}, stale_on_check{};
    Observation read() {
        ++reads;
        if (broken_read) throw std::runtime_error("read failed");
        return state;
    }
    std::uint64_t fuel() const { return budget; }
    std::uint32_t round() { return state.round + (stale_on_check ? 1 : 0); }
    void action() {
        ++calls;
        if (error) throw EngineError{error};
        if (suspend) ++state.round;
    }
    bool move(Tile p) { action(); if (accept && mutate) state.position = p; return accept; }
    void recall() { action(); if (mutate) state.channel = Channel::recall; }
    void tribute(Tile) { action(); if (mutate) state.channel = Channel::tribute; }
};

int main() {
    static_assert(!std::is_convertible_v<Result, bool>);
    int checks = 0;
    auto check = [&](bool ok) { ++checks; assert(ok); };
    { Port p; Executor e; auto s=e.observe(p);
      auto r=e.execute(p,{Action::move,s.epoch,{3,2}});
      check(r.outcome==Outcome::moved && r.after->state.channel==Channel::none);
      check(e.execute(p,{Action::recall,s.epoch}).outcome==Outcome::stale && p.calls==1); }
    { Port p; Executor e; auto s=e.observe(p); p.error=48;
      auto r=e.execute(p,{Action::tribute,s.epoch,{10,10}});
      check(r.outcome==Outcome::rejected && r.engine_error==48 && r.after.has_value());
      check(e.execute(p,{Action::move,s.epoch,{3,2}}).outcome==Outcome::stale); }
    { Port p; Executor e; auto s=e.observe(p); p.accept=false;
      check(e.execute(p,{Action::move,s.epoch,{3,2}}).outcome==Outcome::rejected);
      check(p.state.position==Tile{2,2}); }
    { Port p; Executor e; auto s=e.observe(p); p.mutate=false;
      check(e.execute(p,{Action::recall,s.epoch}).outcome==Outcome::unconfirmed); }
    { Port p; Executor e; auto s=e.observe(p);
      check(e.execute(p,{Action::recall,s.epoch}).outcome==Outcome::recall_started);
      auto fresh=e.observe(p);
      check(e.execute(p,{Action::move,fresh.epoch,{3,2}}).outcome==Outcome::channel_active && p.calls==1); }
    { Port p; Executor e; auto s=e.observe(p);
      check(e.execute(p,{Action::tribute,s.epoch,{2,3}}).outcome==Outcome::tribute_started); }
    { Port p; Executor e; auto s=e.observe(p); p.state.round++;
      check(e.execute(p,{Action::recall,s.epoch}).outcome==Outcome::stale && p.calls==0); }
    { Port p; Executor e; auto s=e.observe(p); p.suspend=true;
      check(e.execute(p,{Action::recall,s.epoch}).outcome==Outcome::unconfirmed); }
    { Port p; Executor e; auto s=e.observe(p); p.budget=Executor::reserve-1;
      check(e.execute(p,{Action::move,s.epoch,{3,2}}).outcome==Outcome::deferred && p.calls==0); }
    { Port p; Executor e; auto s=e.observe(p); p.broken_read=true;
      check(e.execute(p,{Action::recall,s.epoch}).outcome==Outcome::fault && p.calls==0); }
    { Port p; Executor e; auto s=e.observe(p); p.state.consistent=false;
      check(e.execute(p,{Action::recall,s.epoch}).outcome==Outcome::stale && p.calls==0); }
    { Port p; Executor e; auto s=e.observe(p); p.stale_on_check=true;
      check(e.execute(p,{Action::recall,s.epoch}).outcome==Outcome::stale && p.calls==0); }
    { Port p; Executor e; auto s=e.observe(p); p.state.alive=false;
      check(e.execute(p,{Action::recall,s.epoch}).outcome==Outcome::rejected && p.calls==0); }
    { Port p; Executor e; auto s=e.observe(p);
      check(e.execute(p,{Action::wait,s.epoch}).outcome==Outcome::waited && p.calls==0); }
    std::printf("PASS %d executor checks\n",checks);
}
