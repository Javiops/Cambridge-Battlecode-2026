#include "resource.h"
#include <cstdio>
#include <initializer_list>
#include <cstdlib>
using namespace tactics;
static int checks=0;
static void yes(bool value,const char*why){++checks;if(!value){std::fprintf(stderr,"FAIL %s\n",why);std::exit(1);}}
int main(){
 for(int gems:{0,22})for(int bag:{0,12})for(bool mono:{false,true})for(bool holder:{false,true})for(bool priced:{false,true}){
  const auto purpose=resource_job_purpose(gems,bag,mono,holder,priced);
  yes(resource_job_eligible(gems,bag,mono,holder,priced)==(gems>0||bag>0||mono||holder||priced),"eligibility requires actual score endpoint, holder or explicit exception");
  const auto expected=gems>0?ResourcePurpose::Score:bag>0?ResourcePurpose::CarryBank:holder?ResourcePurpose::HeldReward:priced?ResourcePurpose::Investment:mono?ResourcePurpose::MonolithFallback:ResourcePurpose::Ineligible;
  yes(purpose==expected,"purpose separates score, actual bag, continuity, named investment and unpriced fallback");
 }
 yes(!resource_job_eligible(0,0,false),"ordinary endless gold loop is not a score cycle");
 yes(resource_job_eligible(0,0,false,true),"existing physical reward holder remains eligible");
 yes(resource_job_eligible(0,0,true),"monolith-only growth fallback remains available");
 yes(resource_has_bank(0,12)&&!resource_has_bank(0,0),"real carried bag supplies a bank endpoint");
 yes(score_resource_gold(0,1000000)==0,"pure gold cannot invent gem-equivalent score");
 yes(score_resource_gold(22,90)==90,"gem camp retains inherited supporting gold fallback");
 yes(resource_candidate_before(true,false,.01,true,true,1000000),"ready score beats unpriced gold of any numeric rate");
 yes(!resource_candidate_before(true,true,1000000,true,false,.01),"large gold currency cannot displace equal-readiness score");
 yes(resource_candidate_before(true,true,1,false,false,100),"ready monolith growth may replace infeasible score staging");
 yes(resource_candidate_before(true,true,3,true,true,2),"fallback rates compare only within own purpose");
 yes(resource_candidate_before(true,false,3,true,false,2),"same-purpose score rates retain ordinary order");
 yes(!resource_new_job_eligible(0,12,false),"existing bag does not justify a new gold-only capture detour");
 yes(resource_new_job_eligible(0,12,false,false,true),"existing cash commitment may be revalidated");
 yes(resource_new_job_eligible(0,12,false,true),"physical cash holder preserved even with a bag");
 yes(resource_new_job_eligible(22,12,false),"one actual extra gem reward remains a candidate");
 yes(resource_new_job_eligible(0,0,true),"scoreless monolith growth keeps separate fallback");
 std::printf("%d resource eligibility checks passed\n",checks);
}
