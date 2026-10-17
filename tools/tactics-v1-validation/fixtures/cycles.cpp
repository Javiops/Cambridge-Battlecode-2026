#include "cycles.h"
#include <cstdio>
#include <cstdlib>
#include <limits>
using namespace tactics;
int main() {
    int checks=0;
    auto check=[&](bool ok){++checks;if(!ok){std::fprintf(stderr,"cycle check %d failed\n",checks);std::exit(1);}};
    ChainSchedule s{13, 5, 12, 10, 10, 3, 6, 0};
    auto c=compare_chain(s,1.25);
    check(c.known);check(c.bank_then_job==48);check(c.job_then_bank==31);check(c.prefer_job);
    // The direct bank's 22/13 versus the larger bag's 44/31 cannot
    // decide this: both schedules must finish the same second reward.
    s.self_to_job=25;c=compare_chain(s,1.25);
    check(c.bank_then_job==48);check(c.job_then_bank==51);check(!c.prefer_job);
    // A shared recovery leg is included in both endpoints, with the same
    // conservative margin. No bonus reward or free return is invented.
    s={4,1,1,1,1,1,2,30};c=compare_chain(s,1.25);
    check(c.bank_then_job==38);check(c.job_then_bank==35);check(!c.prefer_job);
    s={20,1,15,2,1,1,2,0};check(compare_chain(s,1.25).prefer_job);
    s.direct_bank=-1;check(!compare_chain(s,1.25).known);
    s.direct_bank=std::numeric_limits<double>::infinity();check(!compare_chain(s,1.25).known);
    s.direct_bank=std::numeric_limits<double>::quiet_NaN();check(!compare_chain(s,1.25).known);
    check(!compare_chain({},1.25).known);
    std::printf("%d cycle checks passed\n",checks);
}
