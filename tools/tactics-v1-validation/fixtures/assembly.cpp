#define TACTICS_ASSEMBLY_MODEL_ONLY
#include "assembly.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
int main() {
    int checks = 0;
    auto check = [&](bool ok, const char *name) {
        ++checks;
        if (!ok) { std::fprintf(stderr, "FAIL %s\n", name); std::exit(1); }
    };
    AssemblyFacts f;
    f.group=2; f.self_id=2; f.now=20; f.horizon=500;
    f.fresh_sleeping=f.safe_stage=f.hypothesis_affordable=f.minimal_crew=true;
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
    changed=f; changed.minimal_crew=false;
    check(!price_assembly(changed,crew).known,"unneeded surplus member never forced into group");
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
