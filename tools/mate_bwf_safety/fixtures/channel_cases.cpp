
int channel_regression() {
    fuel=100000;
#if P_DP_CHANNEL_FIX
    State s;bc::champion me;
    auto reset=[&]{ s={};me={};fuel=100000;bc::now=10;bc::vision::enemies.clear();bc::vision::monsters.clear();bc::vision::foes_fail=bc::vision::camps_fail=false; };
    assert(start_recall(s,me,10));
    reset();s.ch_camps.push_back({{6,5},1,true});
    assert(!start_recall(s,me,10) && me.calls==0); // concrete finish gap: actual awake fullHP camp
    me.hp=1;bc::camp::states=0;
    assert(start_submission(s,me,{5,6},10) && bc::camp::states==0); // no invented personal camp damage veto
    reset();s.ch_camps.push_back({{6,5},1,false});bc::camp::positions=0;
    assert(start_recall(s,me,10) && bc::camp::positions==0); // wounded-asleep/dead doesn't require HP/position
    reset();s.ch_camps.push_back({{100,100},1,true,true});
    assert(start_recall(s,me,10)); // no distant camp query / no global26k admission
    reset();fuel=3000;assert(start_recall(s,me,10)); // no optional camp/API observer needed
    reset();s.ch_camps.push_back({{6,5},1,true});fuel=4000;
    assert(!start_recall(s,me,10) && me.calls==0); // local optional query reserve
    reset();s.hit_round=10;
    assert(!start_recall(s,me,10));
    s.groups.push_back({10,{true}});s.target=0;
    assert(start_recall(s,me,10)); // preserve actually clear capture+recall overlap
    reset();s.ch_foes.push_back({11,5});s.thr.push_back({{11,5},6,30,-9});
    assert(!start_recall(s,me,10));
    me.hp=31;assert(start_submission(s,me,{5,6},10));
    me.hp=30;assert(!start_submission(s,me,{5,6},10)); // immediate champion exposure only
    reset();s.ch_foes.push_back({11,5});s.thr.push_back({{11,5},0,0,5});
    assert(!start_submission(s,me,{5,6},10)); // current ready pure-control envelope
    reset();s.ch_foes.push_back({14,5});s.thr.push_back({{14,5},6,30,-9});
    assert(start_recall(s,me,10)); // far future enemy approach does not block LIGHT
    reset();s.ch_foes.push_back({12,5});s.thr.push_back({{12,5},6,30,-9});me.p={6,5};
    bc::vision::enemies.push_back(bc::champion{});bc::vision::enemies.back().p={12,5};
    assert(!start_recall(s,me,10)); // same stored enemy, new actual tile is in ready range
    reset();s.ch_foes.push_back({11,5});s.thr.push_back({{11,5},6,10,-9});me.p={6,5};
    bc::vision::enemies.push_back(bc::champion{});bc::vision::enemies.back().p={11,5};
    assert(!start_submission(s,me,{6,6},10) && me.calls==0); // actual d5 veto, pre-move d6 was outside P_TRIBSAFE
    reset();me.p={6,5};bc::vision::enemies.push_back(bc::champion{});bc::vision::enemies.back().p={10,5};
    assert(!start_submission(s,me,{6,6},10)); // newly revealed unknown nearby foe after move
    reset();me.p={6,5};bc::vision::enemies.push_back(bc::champion{});bc::vision::enemies.back().p={100,100};
    assert(start_submission(s,me,{6,6},10));
    reset();me.p={6,5};bc::vision::foes_fail=true;
    assert(!start_submission(s,me,{6,6},10));
    reset();s.ch_complete=false;assert(!start_recall(s,me,10));
    reset();s.ch_camps_complete=false;
    assert(!start_recall(s,me,10) && start_submission(s,me,{5,6},10));
    reset();bc::now=11;assert(!start_recall(s,me,10) && me.calls==0);
    reset();me.no_op=true;assert(!start_recall(s,me,10));
    reset();me.fails=true;assert(!start_submission(s,me,{5,6},10));
    reset();me.instant=true;assert(start_recall(s,me,10));
    reset();me.instant=true;assert(start_submission(s,me,{5,6},10));
    std::puts("actual LIGHT channel eligibility/wrappers: passed");
#else
    State s;bc::champion me;s.ch_complete=false;fuel=0;bc::now=11;me.no_op=true;
    assert(channel_eligible(s,me,10,true));
    assert(start_recall(s,me,10));
    assert(start_submission(s,me,{5,6},10));
    me.fails=true;
    assert(!start_recall(s,me,10));
    assert(!start_submission(s,me,{5,6},10));
    std::puts("LIGHT flag0 baseline flow: passed");
#endif
    return 0;
}
