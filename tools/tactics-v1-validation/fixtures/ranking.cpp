#define TACTICS_SOLO_MODEL_ONLY
#define TACTICS_COORDINATION_MODEL_ONLY
#include "solo.h"
#include "ranking.h"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <vector>

using namespace tactics;
struct Entry { CampRank rank; bool reward, singleton; };
static unsigned checks = 0;
static void require(bool value, const char *message) {
    ++checks;
    if (!value) { std::fprintf(stderr, "ranking failure: %s at check %u\n", message, checks); std::exit(1); }
}
static void compare(std::vector<Entry> entries, int incumbent) {
    CampRanking bounded;
    for (auto row : entries) bounded.offer(row.rank, row.reward, row.singleton);
    // Independent full-sort reference implements the bounded hypothesis policy.
    std::sort(entries.begin(), entries.end(), [](auto a, auto b) {
        return a.rank.score > b.rank.score ||
            (a.rank.score == b.rank.score && a.rank.gi < b.rank.gi);
    });
    std::vector<int> reference;
    auto add = [&](int gi) {
        if (gi >= 0 && std::find(reference.begin(), reference.end(), gi) == reference.end())
            reference.push_back(gi);
    };
    add(incumbent);
    for (auto row : entries) if (row.reward) { add(row.rank.gi); break; }
    for (auto row : entries) if (row.singleton) { add(row.rank.gi); break; }
    for (auto row : entries) if (reference.size() < 3) add(row.rank.gi);
    const auto shortlist = bounded.shortlist(incumbent);
    require(reference.size() == shortlist.size(), "shortlist length");
    require(std::equal(reference.begin(), reference.end(), shortlist.begin()), "exact shortlist order");
    const auto candidates = bounded.candidates();
    require(candidates.size() <= 5, "bounded candidate storage");
    for (std::size_t i = 0; i < candidates.size(); ++i) {
        if (i) require(!camp_rank_before(candidates.values[i], candidates.values[i - 1]), "sorted candidates");
        for (std::size_t j = 0; j < i; ++j)
            require(candidates.values[i].gi != candidates.values[j].gi, "unique candidates");
    }
    for (int selected : {-1, incumbent, entries.empty() ? -1 : entries.front().rank.gi}) {
        int old_next = -1, next = -1;
        for (auto row : entries) if (row.rank.gi != selected) { old_next = row.rank.gi; break; }
        for (auto row : candidates) if (row.gi != selected) { next = row.gi; break; }
        require(old_next == next, "exact first holder-handoff alternative");
    }
}
static unsigned random_state = 0x91d653b7u;
static unsigned random_value() { random_state ^= random_state << 13; random_state ^= random_state >> 17; random_state ^= random_state << 5; return random_state; }
int main() {
    compare({}, -1); compare({}, 12);
    compare({{{7, 0}, false, false}}, -1);
    compare({{{7, 0}, true, true}}, 7);
    compare({{{0, 10}, false, false}, {{1, 9}, false, false}, {{2, 8}, false, false},
             {{3, 1}, true, false}, {{4, 0}, false, true}}, 99);
    compare({{{9, 4}, true, true}, {{3, 4}, false, true}, {{6, 4}, true, false},
             {{1, 4}, false, false}, {{2, 4}, false, false}}, -1);
    // The observed normal22 Issac had900HP/40STR. Basic-only damage681
    // mislabeled every Wolf unsafe against675, though his reset kit is safe.
    Actor a; a.id=3; a.type=4; a.alive=true; a.pos={16,34}; a.hp=a.max_hp=900;
    a.strength=40; a.range=1; a.can_attack=a.can_cast=true;
    auto& reset=a.spells[0]; reset.kind=1; reset.self=reset.ready=true;
    reset.cooldown=0; reset.recharge=8; reset.slot=0;
    Camp wolf; wolf.id=6; wolf.pos={17,34}; wolf.hp=1350; wolf.strength=20; wolf.range=3;
    const auto proof=certify_solo_clear(a,wolf,a.pos,0,true);
    require(std::ceil(wolf.hp/a.strength)*wolf.strength+1>=.75*a.hp&&
            proof.known&&proof.feasible&&proof.clear_ticks==30&&proof.remaining_hp==320,
            "false basic-only affordability does not represent actual reset kit");
    CampRanking hypotheses;
    for(auto row:{CampRank{5,1.282051},CampRank{9,1.282051},CampRank{1,1.219512}})
        hypotheses.offer(row,false,false);
    hypotheses.offer({6,.656827},false,true);
    auto selected=hypotheses.shortlist();
    require(selected.size()==3&&selected.values[0]==6&&selected.values[1]==5&&selected.values[2]==9,
            "lower coarse singleton receives one hypothesis slot without ready or safety credit");
    require(hypotheses.shortlist(9).values[0]==9,
            "actual incumbent continuity remains ahead of singleton hypothesis");
    for (int iteration = 0; iteration < 20000; ++iteration) {
        const unsigned count = random_value() % (iteration % 7 == 0 ? 513 : 65);
        std::vector<Entry> entries;
        for (unsigned i = 0; i < count; ++i) {
            const int integer_score = static_cast<int>(random_value() % 31) - 3;
            const double score = iteration % 3 == 0 ? integer_score : integer_score / 7.0;
            entries.push_back({{static_cast<int>(i * 3 + 1), score},
                               random_value() % 7 == 0, random_value() % 3 == 0});
        }
        // Every group is offered once, in an order independent of its score/ID.
        for (unsigned i = count; i > 1; --i) std::swap(entries[i - 1], entries[random_value() % i]);
        const int incumbent = iteration % 3 == 0 || entries.empty() ? -1 :
            iteration % 4 == 0 ? 100000 : entries[random_value() % count].rank.gi;
        compare(entries, incumbent);
    }
    // A bounded quote cutoff may give the next hypothesis another owner's
    // budget. No outcome, income or readiness is inferred from the cursor.
    for(int n=0;n<=3;++n){
        BoundedRanks<int,3>s;s.count=n;for(int k=0;k<n;++k)s.values[k]=10+k;
        for(int last=-1;last<=13;++last){
            auto out=rotate_candidates_after(s,last);
            require(out.count==s.count,"rotation preserves bounded slot count");
            auto a=s.values,b=out.values;std::sort(a.begin(),a.begin()+n);std::sort(b.begin(),b.begin()+n);
            require(a==b,"rotation preserves exact candidate membership");
            if(n>1&&last>=10&&last<10+n)
                require(out.values[0]==10+(last-10+1)%n,"last attempted slot yields first budget to successor");
        }
        if(n){int last=-1;bool visited[3]={};
            for(int owner=0;owner<n;++owner){auto out=rotate_candidates_after(s,last);last=out.values[0];visited[last-10]=true;}
            for(int k=0;k<n;++k)require(visited[k],"every fixed bounded hypothesis gets a funded first position");
        }
    }
    BoundedRanks<int,3> witness;witness.count=3;witness.values={3,1,5};
    require(rotate_candidates_after(witness,3).values==std::array<int,3>{1,5,3},"actual R60 first-slot monopoly can advance");
    require(rotate_candidates_after(witness,1).values==std::array<int,3>{5,3,1},"next bounded hypothesis is not silently dropped");
    std::printf("%u ranking checks passed\n", checks);
}
