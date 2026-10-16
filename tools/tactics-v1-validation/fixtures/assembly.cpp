#define TACTICS_ASSEMBLY_MODEL_ONLY
#include "assembly.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
template<class F, class Check> void observed_group_contract(Check check) {
    if constexpr (requires(F f) { f.fresh_observed; }) {
        F f; f.group=2; f.self_id=0; f.now=20; f.horizon=500;
        f.fresh_observed=f.safe_stage=f.hypothesis_affordable=f.priced_crew=true;
        f.alternative_known=true; f.alternative_rate=.1; f.reward_once=90; f.cycle_ticks=20;
        std::array<AssemblyMember,3> crew{{
            {0,1,true,true,true,true,false,true,true,.1},
            {1,2,true,true,true,true,false,true,true,.1},
            {2,3,true,true,true,true,false,true,true,.1}}};
        const auto quote=price_assembly(f,crew);
        check(quote.known,"observed multi-member group can price three-body staging without sleeping label");
        check(!quote.clear_ready,"observed awake quote grants no actual current attack permission");
        auto changed=f;changed.hypothesis_affordable=false;
        check(!price_assembly(changed,crew).known,"awake observation does not bypass movement/clear affordability");
        auto bodies=crew;bodies[2].arrival=4;
        check(!price_assembly(f,bodies).known,"essential third participant misses bounded arrival");
        bodies=crew;bodies[2].route_known=false;
        check(!price_assembly(f,bodies).known,"third-body headcount cannot substitute known useful route");
        bodies=crew;bodies[2].alternative_known=false;
        check(!price_assembly(f,bodies).known,"new third helper's unknown task is not free zero");
        changed=f;changed.fresh_observed=false;
        check(!price_assembly(changed,crew).known,"partial/unobserved group cannot receive an entry certificate");
        check(price_assembly(f,std::span(crew.data(),1)).known,"certified observed solo approach does not require fictional partner");
    }
}
int main() {
    int checks = 0;
    auto check = [&](bool ok, const char *name) {
        ++checks;
        if (!ok) { std::fprintf(stderr, "FAIL %s\n", name); std::exit(1); }
    };
    observed_group_contract<AssemblyFacts>(check);
    AssemblyPathHint hint;
    hint.actor=7;hint.origin=hint.start={1,1};hint.goal={5,5};hint.range=2;hint.speed=1;hint.kind=0;hint.seen=10;hint.length=3;
    hint.route[0]={1,1};hint.route[1]={2,2};hint.route[2]={3,3};
    check(assembly_hint_matches(hint,7,{1,1},{5,5},{1,1},2,1,0,42),"geometry lifetime is bounded and inclusive");
    check(!assembly_hint_matches(hint,7,{1,1},{5,5},{1,1},2,1,0,43),"expired route cannot promise current movement");
    check(!assembly_hint_matches(hint,7,{2,1},{5,5},{1,1},2,1,0,12),"changed actual body position invalidates geometry key");
    check(!assembly_hint_matches(hint,7,{1,1},{5,5},{1,1},3,1,0,12),"changed true action range requires a different stance");
    check(!assembly_hint_matches(hint,7,{1,1},{5,5},{1,1},2,2,0,12),"changed actual speed invalidates geometry key");
    check(!assembly_hint_matches(hint,7,{1,1},{5,5},{1,1},2,1,1,12),"exit path cannot be reused as entry");
    check(assembly_hint_legal(hint,[](Pos){return true;}),"validated unit-step cached path is reusable geometry");
    check(!assembly_hint_legal(hint,[](Pos p){return p!=Pos{2,2};}),"new current wall occupancy reservation or missing vision vetoes path");
    auto broken=hint;broken.route[1]={8,8};
    check(!assembly_hint_legal(broken,[](Pos){return true;}),"cached path cannot skip legal adjacency");
    broken=hint;broken.route[0]={0,0};
    check(!assembly_hint_legal(broken,[](Pos){return true;}),"cached route start must match actual keyed start");
    {
        std::array<Camp,3> threats;
        for(auto &c:threats){c.hp=20;c.strength=5;c.range=3;}
        threats[0].pos={24,24};threats[1].pos={24,25};threats[2].pos={23,24};
        Pos at{22,25};int steps=0;
        auto home=[](Pos p){return distance(p,{29,29});};
        const auto outside=[&](Pos p){return std::all_of(threats.begin(),threats.end(),[&](const Camp&c){return distance(p,c.pos)>c.range;});};
        while(!outside(at)&&steps<3){auto next=assembly_exit_step(at,threats,[](Pos){return true;},home);if(!next)break;at=*next;++steps;}
        check(outside(at)&&steps<=3,"far-side helper exits actual camp pressure even when home gradient crosses camp");
        check(!assembly_exit_step(Pos{22,25},threats,[](Pos){return false;},home),"no exit through walls missing vision occupancy or reservation");
        auto next=assembly_exit_step(Pos{22,25},threats,[](Pos p){return p.x!=21;},home);
        check(next&&next->x!=21,"currently reserved preferred exit uses another actual legal reducing step");
        threats[0].hp=threats[1].hp=threats[2].hp=0;
        check(!assembly_exit_step(Pos{22,25},threats,[](Pos){return true;},home),"cleared camps do not invent exit movement");
    }
    {
        std::array<AssemblyPathHint,12> hints;
        for(unsigned k=0;k<hints.size();++k){hints[k].borrowed_generation=9;hints[k].touched=k;}
        check(assembly_unborrowed_slot(hints,9)<0,"twelve active spans cannot be silently evicted");
        hints[7].borrowed_generation=8;hints[10].borrowed_generation=8;
        check(assembly_unborrowed_slot(hints,9)==7,"deterministic eviction considers only unborrowed geometry");
    }
    {
        Actor enemy;enemy.alive=true;enemy.pos={0,0};enemy.range=1;enemy.move_speed=1;
        for(auto &spell:enemy.spells){spell.kind=6;spell.range=3;spell.cooldown=0;spell.recharge=2;}
        std::array<Pos,1> near{{{20,0}}},far{{{32,0}}};
        check(!assembly_quiet_path(near,enemy,6),"two distinct future dash slots can threaten a real approach tile");
        check(assembly_quiet_path(far,enemy,6),"bounded full-window contact preserves a genuinely distant route");
        for(auto &spell:enemy.spells)spell.cooldown=7;
        check(assembly_quiet_path(near,enemy,6),"known dash cooldown beyond actual approach window is not invented ready");
        check(!assembly_quiet_path(near,enemy,9),"missing sighting age enlarges the complete approach contact window");
        std::array<Pos,3> route{{{2,2},{3,3},{4,4}}};
        std::array<Pos,2> stages{{{2,2},{3,3}}};
        check(!assembly_exit_unreserved(route,{2,2},stages),"earlier body's exit cannot cross later helper's future stage");
        stages[1]={5,5};check(assembly_exit_unreserved(route,{2,2},stages),"known exit outside all other future stage slots remains valid");
        check(!assembly_exit_unreserved({},Pos{2,2},stages),"missing abort path is not a certified exit");
    }
    {
        Mission clear;clear.phase=Phase::Clear;clear.group=1;clear.assembly_count=3;
        clear.expiry=6;clear.last_camp_hp=1000;clear.last_progress=0;
        bool leased=true;
        for(int now=1;now<=17;++now){renew_crew_clear_lease(clear,now,now,true,1000-10*now);leased&=now<clear.expiry;}
        check(leased&&clear.last_progress==17&&clear.expiry==23,"seventeen-tick real clear retains finite renewed lease before expiry gate");
        auto still=clear;still.expiry=6;still.last_progress=0;still.last_camp_hp=1000;
        for(int now=1;now<=17;++now)renew_crew_clear_lease(still,now,now,true,1000);
        check(still.expiry==6&&still.last_progress==0,"movement forecasts claims and unchanged HP cannot renew clear indefinitely");
        auto test=still;check(!renew_crew_clear_lease(test,6,5,true,900)&&test.expiry==6,"stale observed damage cannot resurrect expired clear lease");
        test=still;check(!renew_crew_clear_lease(test,6,6,false,900),"partial missing group HP is not real clear progress");
        test=still;test.phase=Phase::Observe;check(!renew_crew_clear_lease(test,6,6,true,900),"prospective assembly cannot renew from a quote");
        test=still;test.last_camp_hp=-1;check(!renew_crew_clear_lease(test,6,6,true,900),"first unobserved HP reference is not accepted work");
        test=still;test.assembly_count=0;check(!renew_crew_clear_lease(test,6,6,true,900),"unnamed bodies cannot create a paid crew lease");
        test=still;check(renew_crew_clear_lease(test,6,6,true,900)&&test.expiry==12,"actual observed progress at first expired owner renews before gate");
    }
    {
        Actor actor;actor.id=1;actor.type=2;actor.alive=true;actor.hp=actor.max_hp=700;actor.strength=40;actor.range=3;actor.pos={3,4};
        Camp camp;camp.id=8;camp.pos={5,5};camp.hp=camp.max_hp=500;camp.strength=20;
        std::array<const Actor*,1> one{{&actor}};std::array<Camp,1> target{{camp}};
        const auto base=assembly_group_signature(2,one,target);
        check(base==assembly_group_signature(2,one,target),"unchanged single-body failed signature remains excluded without round-only retry");
        actor.hp+=1;check(base!=assembly_group_signature(2,one,target),"single-body actual healing invalidates old failed signature");actor.hp-=1;
        actor.strength+=1;check(base!=assembly_group_signature(2,one,target),"single-body actual upgrade invalidates old failed signature");actor.strength-=1;
        actor.pos.x+=1;check(base!=assembly_group_signature(2,one,target),"single-body actual reposition invalidates old failed signature");actor.pos.x-=1;
        actor.can_attack=true;check(base!=assembly_group_signature(2,one,target),"real current permission change is part of single-body proof");actor.can_attack=false;
        target[0].hp-=1;check(base!=assembly_group_signature(2,one,target),"actual monster damage invalidates old single-body failure");target[0].hp+=1;
        actor.spells[0].cooldown=2;check(base!=assembly_group_signature(2,one,target),"known actual cooldown changes alter failed opportunity");
    }
    AssemblyFacts f;
    f.group=2; f.self_id=2; f.now=20; f.horizon=500;
    f.fresh_sleeping=f.safe_stage=f.hypothesis_affordable=f.priced_crew=true;
    f.alternative_known=true; f.alternative_rate=.36;
    f.reward_once=80; f.cycle_ticks=35;
    AssemblyMember leader{1,0,true,true,true,true,true,true,true,.20};
    AssemblyMember self{2,2,true,true,true,true,false,true,true,.36};
    std::array crew{leader,self};
    const auto base=price_assembly(f,crew);
    check(base.known,"short profitable cooperative quote can compete with ready solo job");
    check(!base.clear_ready,"pending quote never grants actual clear readiness");
    check(base.anchor_id==1&&base.helper_id==1,"lower-ID claimed anchor retained");
    check(base.expiry==26&&base.start==20,"absolute finite first lease");
    auto bodies=crew; bodies[0].claim=false;
    check(!price_assembly(f,bodies).known,"follower requires an existing visible intention");
    auto changed=f; changed.self_id=1;
    check(price_assembly(changed,bodies).known,"minimum visible ID may invite finite local crew");
    bodies=crew; bodies[0].visible=false;
    check(!price_assembly(f,bodies).known,"remote claim cannot guarantee helper");
    bodies=crew; bodies[0].alive=false;
    check(!price_assembly(f,bodies).known,"observed dead helper cancels");
    bodies=crew; bodies[0].available=false;
    check(!price_assembly(f,bodies).known,"channelled or stunned helper cancels");
    bodies=crew; bodies[0].current_kit=false;
    check(!price_assembly(f,bodies).known,"no invented future damage ability");
    bodies=crew; bodies[0].route_known=false;
    check(!price_assembly(f,bodies).known,"unknown cached path declines");
    bodies=crew; bodies[0].alternative_known=false;
    check(!price_assembly(f,bodies).known,"unknown helper opportunity is not free");
    bodies=crew; bodies[0].alternative_rate=2;
    check(!price_assembly(f,bodies).known,"productive helper alternative defeats gathering");
    bodies=crew; bodies[1].arrival=4;
    check(!price_assembly(f,bodies).known,"distant rendezvous exceeds finite bound");
    bodies=crew; bodies[0].id=2;
    check(!price_assembly(f,bodies).known,"same body cannot supply two shares of damage");
    changed=f; changed.fresh_sleeping=false;
    check(!price_assembly(changed,crew).known,"no waiting under awake or stale monster");
    changed=f; changed.safe_stage=false;
    check(!price_assembly(changed,crew).known,"unsafe stage declines");
    changed=f; changed.warning=true;
    check(!price_assembly(changed,crew).known,"new warning invalidates pending plan");
    changed=f; changed.actual_ready=true;
    check(!price_assembly(changed,crew).known,"actual ready crew uses real clear policy");
    changed=f; changed.hypothesis_affordable=false;
    check(!price_assembly(changed,crew).known,"unaffordable hypothetical pair declines");
    changed=f; changed.priced_crew=false;
    check(!price_assembly(changed,crew).known,"an unpriced crew cannot manufacture a profitable entry");
    changed=f; changed.existing_group=2; changed.existing_start=14; changed.last_progress=20;
    check(!price_assembly(changed,crew).known,"absolute expiry cannot renew via motion");
    changed.existing_start=18; changed.last_progress=17;
    check(!price_assembly(changed,crew).known,"genuine movable stall exits");
    changed.can_move=false;
    check(price_assembly(changed,crew).known,"same-owner spent move retains accepted intention");
    changed=f; changed.unchanged_failure=true;
    check(!price_assembly(changed,crew).known,"unchanged failed signature cannot invite again");
    changed=f; changed.horizon=50;
    check(!price_assembly(changed,crew).known,"completed conversion must fit remaining time");
    changed=f; changed.reward_once=5;
    check(!price_assembly(changed,crew).known,"low reward fails actual opportunity comparison");
    changed=f; changed.alternative_known=false;
    check(!price_assembly(changed,crew).known,"unknown own cycle trade declines");
    const auto slower=price_assembly(f,crew,3,4,6);
    check(slower.known&&slower.total_ticks>base.total_ticks&&slower.rate<base.rate,
          "arrival and handshake are charged to cycle rate");
    Actor a;a.id=2;a.type=2;a.alive=true;a.pos={4,5};a.hp=a.max_hp=150;a.strength=30;a.range=1;
    a.spells[0].kind=1;a.spells[0].self=true;a.spells[0].slot=0;
    a.spells[1].kind=6;a.spells[1].ground=true;a.spells[1].slot=1;a.spells[1].range=2;
    Camp c;c.pos={5,5};c.hp=c.max_hp=240;c.strength=60;c.range=1;
    const auto bound=optimistic_solo_impossibility(a,c);
    check(bound.impossible&&bound.earliest_kill==4&&bound.volley_upper==60,"even free reset every round cannot save weak stationary solo");
    check(bound.unavoidable_damage==180,"sleeping camp lower bound charges Kminus1 responses rather than invented pre-wake damage");
    auto body=a;body.hp=180;check(optimistic_solo_impossibility(body,c).impossible,"exact lethal lower-bound response still excludes solo");
    body.hp=181;check(!optimistic_solo_impossibility(body,c).impossible,"one HP beyond lower bound remains unknown rather than fabricated infeasible");
    check(!optimistic_solo_impossibility(a,c,31).impossible,"observed possibly enduring shield is granted optimistically");
    body=a;body.shield=31;check(!optimistic_solo_impossibility(body,c).impossible,"current body shield cannot be silently discarded by lower-bound proof");
    body=a;body.monster=true;auto small=c;small.hp=190;check(!optimistic_solo_impossibility(body,small).impossible,"actual Monster1.1 can reduce earliest kill below lethal boundary");
    body=a;body.camp_mitigation=.7;check(!optimistic_solo_impossibility(body,c).impossible,"actual Jungle mitigation affects unavoidable pressure");
    auto one=c;one.hp=30;check(!optimistic_solo_impossibility(a,one).impossible,"instant kill needs no invented monster reply");
    auto far=c;far.range=0;check(!optimistic_solo_impossibility(a,far).impossible,"out-of-range stage has no unavoidable camp damage");
    auto awake=c;awake.awake=true;check(!optimistic_solo_impossibility(a,awake).impossible,"sleeping-stage lower bound does not price an awake approach");
    body=a;body.type=9;check(!optimistic_solo_impossibility(body,c).impossible,"Ren retaliation is outside narrow primitive proof");
    body=a;body.type=11;check(!optimistic_solo_impossibility(body,c).impossible,"field-shopping Tavi is not assumed unable to improve");
    body=a;body.type=7;check(!optimistic_solo_impossibility(body,c).impossible,"enhanced-control Marcella remains unsupported");
    body=a;body.type=77;check(!optimistic_solo_impossibility(body,c).impossible,"unknown passive semantics cannot prove infeasibility");
    body=a;body.spells[1].kind=0;check(!optimistic_solo_impossibility(body,c).impossible,"missing ability metadata remains unknown");
    for(int kind:{4,5,7}){body=a;body.spells[0].kind=kind;check(!optimistic_solo_impossibility(body,c).impossible,"control/heal/shield remains a funded generic fallback");}
    body=a;body.spells[0].kind=2;body.spells[0].camps=true;body.spells[0].range=1;body.spells[0].amount=210;
    check(!optimistic_solo_impossibility(body,c).impossible,"generous direct cast upper bound protects a possible burst kill");
    body.spells[0].cooldown=100;check(!optimistic_solo_impossibility(body,c).impossible,"proof ignores cooldown in favor of solo rather than manufacturing failure");
    body=a;body.strength=std::numeric_limits<double>::quiet_NaN();check(!optimistic_solo_impossibility(body,c).impossible,"nonfinite kit rejects lower-bound certificate");
    std::printf("%d assembly checks passed\n",checks);
}
