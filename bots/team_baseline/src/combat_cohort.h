#pragma once
#ifndef P_FUEL_COHORT
#define P_FUEL_COHORT 1
#endif
// Only handles/immutable constructor metadata are shared. All live properties
// are still read through the SDK. Immutable ownership keeps an outstanding
// range safe if a nested scope invalidates the cache or its Scope is destroyed.
namespace combatcohort {
using List=std::vector<bc::champion>;
class View {
    List owned_;
    std::shared_ptr<const List> borrowed_;
    const List& list() const { return borrowed_ ? *borrowed_ : owned_; }
public:
    explicit View(List&& list):owned_(std::move(list)){}
    explicit View(std::shared_ptr<const List> list):borrowed_(std::move(list)){}
    View(View&&)=default;
    View& operator=(View&&)=default;
    View(const View&)=delete;
    View& operator=(const View&)=delete;
    List::const_iterator begin() const { return list().begin(); }
    List::const_iterator end() const { return list().end(); }
    const bc::champion& operator[](std::size_t i) const { return list()[i]; }
    std::size_t size() const { return list().size(); }
    bool empty() const { return list().empty(); }
};
struct Frame {
    Frame* previous=nullptr;
    int round=-1;
    bool valid=true,loaded=false;
    std::shared_ptr<const List> allies;
};
inline Frame* active=nullptr;
struct Scope {
    Frame frame;
    Frame* previous=active;
    explicit Scope(int round) { frame.round=round;frame.previous=active;active=&frame; }
    ~Scope() { active=previous; }
    Scope(const Scope&)=delete;
    Scope& operator=(const Scope&)=delete;
};
inline void invalidate() {
#if P_FUEL_COHORT
    for(auto* frame=active;frame;frame=frame->previous) frame->valid=false;
#endif
}
} // namespace combatcohort

inline combatcohort::View combat_allies(const State& s) {
#if P_FUEL_COHORT
    auto* frame=combatcohort::active;
    if(frame && frame->valid) {
        if(frame->round!=static_cast<int>(bc::round_number())) frame->valid=false;
        else if(frame->loaded) return combatcohort::View(frame->allies);
        else {
            auto list=bc::vision::champions(*s.my);
            if(frame->round==static_cast<int>(bc::round_number())) {
                // Moving the vector transfers its buffer, without copying any
                // champion handle. Views retain ownership of this exact list.
                frame->allies=std::make_shared<const combatcohort::List>(std::move(list));
                frame->loaded=true;
                return combatcohort::View(frame->allies);
            }
            frame->valid=false;
            return combatcohort::View(std::move(list));
        }
    }
#endif
    return combatcohort::View(bc::vision::champions(*s.my));
}
