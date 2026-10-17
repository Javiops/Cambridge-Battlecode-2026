#include "solo_routes.h"
#include <cstdio>
#include <cstdlib>
using namespace tactics;
// Quote outcomes are explicit inputs here: this fixture tests the exact
// production arbitration, not the SDK geometry/damage certificate again.
namespace bc {
inline unsigned remaining = 100000;
inline int round = 100;
inline unsigned fuel_remaining() { return remaining; }
inline int round_number() { return round; }
}
namespace tactics {
struct SoloFarmQuote {
    int group = -1;
    double rate = 0;
    bool known = false, feasible = false;
};
struct World {
    int round = 100;
    Actor self;
    struct Geometry { std::vector<Group> groups; } geo;
    std::vector<GroupView> groups;
    std::vector<SoloFarmQuote> quotes;
    std::vector<int> queried;
    unsigned quote_cost = 0;
};
namespace assembly_detail {
inline bool simple_sleeping(const World &w, int gi) {
    return !w.groups[gi].camps.front().awake;
}
}
inline SoloFarmQuote quote_solo_farm(World &w, int gi) {
    w.queried.push_back(gi);
    bc::remaining -= std::min(bc::remaining, w.quote_cost);
    return w.quotes[gi];
}
inline std::optional<Proposal> solo_farm_proposal(World &, Memory &, const SoloFarmQuote &q) {
    if (!q.known || !q.feasible) return std::nullopt;
    Proposal p; p.valid = true; p.mission.group = q.group;
    p.action.kind = Kind::BasicCamp; return p;
}
}
// EXACT_SOLO_ENTRY
static int checks=0;
static void yes(bool v,const char*s){++checks;if(!v){std::fprintf(stderr,"FAIL %s\n",s);std::exit(1);}}
int main(){
 Actor a;a.id=3;a.alive=true;a.hp=a.max_hp=900;a.can_move=a.can_attack=a.can_cast=true;Mission job;job.phase=Phase::Travel;job.expiry=0;
 yes(early_solo_eligible(a,job,100,false,false,false),"expired idle travel is eligible");
 for(auto phase:{Phase::Clear,Phase::Collect,Phase::Recover,Phase::Channel}){job.phase=phase;yes(!early_solo_eligible(a,job,100,false,false,false),"actual mandatory conversion/existingclear retained");}job.phase=Phase::Observe;
 yes(early_solo_eligible(a,job,100,false,false,false),"expired observation can select finite self route");
 yes(!early_solo_eligible(a,job,100,true,false,false),"actual holder retained");
 yes(!early_solo_eligible(a,job,100,false,true,false),"fresh or missing hostile retained");
 yes(!early_solo_eligible(a,job,100,false,false,true),"cash or install receipt retained");
 a.hp=674;yes(!early_solo_eligible(a,job,100,false,false,false),"unchanged healthy cutoff");a.hp=675;yes(early_solo_eligible(a,job,100,false,false,false),"healthy boundary inclusive");a.hp=900;
 a.gems=1;yes(!early_solo_eligible(a,job,100,false,false,false),"bag conversion cannot be preempted");a.gems=0;
 a.completed=true;yes(!early_solo_eligible(a,job,100,false,false,false),"completed owner cannot claim firsthit");a.completed=false;
 a.stunned=true;yes(!early_solo_eligible(a,job,100,false,false,false),"stun cannot enter");a.stunned=false;
 a.channel=Channel::Recall;yes(!early_solo_eligible(a,job,100,false,false,false),"live channel preserved");a.channel=Channel::None;
 job.assembly_pending=true;yes(!early_solo_eligible(a,job,100,false,false,false),"named crew preserved");job.assembly_pending=false;
 job.chain_used=true;yes(!early_solo_eligible(a,job,100,false,false,false),"named chain preserved");job.chain_used=false;
 job.bank_after_reward=true;yes(!early_solo_eligible(a,job,100,false,false,false),"bankafterreward preserved");job.bank_after_reward=false;
 job.sortie_length=1;yes(!early_solo_eligible(a,job,100,false,false,false),"sortie preserved");job.sortie_length=0;
 constexpr int n=11;std::vector<std::uint8_t> walls((n*n+7)/8),occ=walls,vis(walls.size(),255);
 auto bit=[](auto&v,int x,int y,bool value){int i=y*n+x;if(value)v[i/8]|=1<<(i%8);else v[i/8]&=~(1<<(i%8));};
 bit(occ,7,5,true);
 auto q=visible_solo_route(n,n,walls,occ,vis,{3,5},{7,5},1,1);
 yes(q.known&&q.arrival_steps==3&&q.capture_steps==1&&q.route_length==4,"three-turn local approach and exact postclear capture");
 yes(q.route[0]==Pos{3,5}&&distance(q.stage,{7,5})==1,"actual route endpoint in BASIC range");
 yes(q.visited<=128,"bounded total nodes");
 yes(q.capture_length==q.capture_steps+1&&q.capture_route[0]==q.stage&&q.capture_route[q.capture_length-1]==Pos{7,5},"exact postclear waypoints retained for awake-pressure veto");
 bit(walls,5,5,true);q=visible_solo_route(n,n,walls,occ,vis,{3,5},{7,5},1,1);yes(q.known,"visible wall detour is proved rather than straightline guessed");
 for(int y=0;y<n;++y)bit(walls,5,y,true);q=visible_solo_route(n,n,walls,occ,vis,{3,5},{7,5},1,1);yes(!q.known,"wall disconnect stays unknown");
 walls.assign(walls.size(),0);vis.assign(vis.size(),0);q=visible_solo_route(n,n,walls,occ,vis,{3,5},{7,5},1,1);yes(!q.known,"unseen route never certified");vis.assign(vis.size(),255);
 q=visible_solo_route(n,n,walls,occ,vis,{3,5},{7,5},1,1,1);yes(!q.known&&q.visited<=1,"workcap is unknown never infeasible");
 q=visible_solo_route(n,n,walls,occ,vis,{0,5},{7,5},1,1);yes(!q.known,"arrival beyond three owners unknown");
 q=visible_solo_route(n,n,walls,occ,vis,{6,5},{7,5},1,1);yes(q.known&&q.arrival_steps==0&&q.capture_steps==1,"living camp blocked only until actual clear");
 bit(occ,6,5,true);q=visible_solo_route(n,n,walls,occ,vis,{6,5},{7,5},1,1);yes(q.known,"self occupancy vacates only its own square");
 bit(walls,7,5,true);q=visible_solo_route(n,n,walls,occ,vis,{6,5},{7,5},1,1);yes(!q.known,"postclear cannot remove actual wall");bit(walls,7,5,false);
 q=visible_solo_route(n,n,walls,occ,vis,{-1,5},{7,5},1,1);yes(!q.known,"invalid origin rejected");
 q=visible_solo_route(n,n,walls,occ,vis,{6,5},{7,5},1,9);yes(!q.known,"unsupported speed no route fabrication");
 // Ring of other bodies cannot be promised to vacate for postclear capture.
 for(int y=4;y<=6;++y)for(int x=6;x<=8;++x)if(x!=7||y!=5)bit(occ,x,y,true);
 q=visible_solo_route(n,n,walls,occ,vis,{5,5},{7,5},3,1);yes(!q.known,"occupied capture approaches require known actual legal path");

 // Runtime work budgets are separate from the mathematical node horizon.
 occ.assign(occ.size(),0);walls.assign(walls.size(),0);vis.assign(vis.size(),255);bit(occ,7,5,true);
 int polls=0;
 q=visible_solo_route(n,n,walls,occ,vis,{3,5},{7,5},1,1,128,[&]{++polls;return false;});
 yes(!q.known&&q.visited==0&&polls==1,"unfunded route declines before scratch initialization/search");
 polls=0;q=visible_solo_route(n,n,walls,occ,vis,{3,5},{7,5},1,1,128,[&]{return ++polls<=3;});
 yes(!q.known&&q.visited<=128&&polls==4,"budget stop is bounded Unknown not readiness");
 q=visible_solo_route(n,n,walls,occ,vis,{3,5},{7,5},1,1,128,[]{return true;});
 yes(q.known&&q.arrival_steps==3&&q.capture_steps==1,"fresh funded retry preserves exact positive route");
 q=visible_solo_route(n,n,walls,occ,vis,{3,5},{7,5},4,1);
 yes(!q.known&&q.visited<=2,"admissible capture lower bound rejects beyond horizon before broad expansion");
 q=visible_solo_route(n,n,walls,occ,vis,{0,5},{7,5},1,1);
 yes(!q.known&&q.visited==1,"admissible approach lower bound prunes only impossible bounded branches");

 auto setup=[] {
  World w;w.self.id=3;w.self.pos={3,3};w.self.range=1;w.self.move_speed=1;
  for(int gi=0;gi<2;++gi){Group g;g.gems=22;g.spawns.push_back(Spawn{});w.geo.groups.push_back(g);
   GroupView v;v.state=Lifecycle::Alive;v.seen=100;Camp c;c.pos={5+gi,3};v.camps.push_back(c);w.groups.push_back(v);
   w.quotes.push_back({gi,0,false,false});}
  bc::remaining=100000;bc::round=100;return w;
 };
 auto mem=[] {Memory m;m.mission.group=0;m.mission.phase=Phase::Assemble;
  m.mission.expiry=106;m.mission.rate=1000;return m;};
 {auto w=setup();auto m=mem();w.quotes[1]={1,.2,true,true};auto p=early_solo_proposal(w,m);
  yes(p&&p->mission.group==1,"coarse unready1000 rate cannot veto fresh feasible .2 quote");
  yes(w.queried==std::vector<int>({0,1}),"incumbent and alternative both paid in existing two-slot pass");}
 {auto w=setup();auto m=mem();w.quotes[0]={0,900,true,false};w.quotes[1]={1,.2,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==1,"known failed incumbent has no feasible income receipt");}
 {auto w=setup();auto m=mem();w.quotes[0]={0,.2,true,true};w.quotes[1]={1,.24,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==0,"fresh feasible incumbent retains unchanged1.25 hysteresis");}
 {auto w=setup();auto m=mem();w.quotes[0]={0,.2,true,true};w.quotes[1]={1,.26,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==1,"real wholecycle improvement beats paid incumbent");}
 {auto w=setup();auto m=mem();m.mission.rate=0;w.quotes[0]={0,.2,true,true};w.quotes[1]={1,.24,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==0,"raw zero does not erase independently paid incumbent");}
 {auto w=setup();auto m=mem();m.mission.expiry=99;w.quotes[0]={0,.2,true,true};w.quotes[1]={1,.24,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==1,"expired intent does not renew switch margin");}
 {auto w=setup();auto m=mem();auto p=early_solo_proposal(w,m);
  yes(!p&&m.solo_probe_group==0&&m.solo_probe_round==100,"all Unknown remains no proposal never a fabricated zero value");}
 {auto w=setup();auto m=mem();w.quotes[0]={0,std::numeric_limits<double>::infinity(),true,true};w.quotes[1]={1,.2,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==1,"nonfinite incumbent quote cannot certify comparable income");}
 {auto w=setup();auto m=mem();w.quote_cost=57000;w.quotes[0]={0,.2,true,true};w.quotes[1]={1,.8,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==0&&w.queried.size()==1,"unfunded second quote is not fabricated or promoted");}
 {auto w=setup();auto m=mem();w.geo.groups[0].spawns.push_back(Spawn{});w.quotes[1]={1,.2,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==1,"unpriced multicamp Assemble cannot block certified singleton");}
 {auto w=setup();auto m=mem();w.quotes[0]={0,.2,true,true};w.quotes[1]={1,.25,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==0,"exact switch boundary retains paid incumbent");}
 {auto w=setup();auto m=mem();w.quotes[1]={1,0,true,true};
  yes(!early_solo_proposal(w,m),"zero quote cannot become an executable income alternative");}
 auto capture=[](Memory&m){m.mission.phase=Phase::Travel;m.mission.start=90;m.mission.target={5,3};
  m.moved_round=99;m.route_round=100;m.route_goal=m.mission.target;m.route_best=2;m.route_stall=0;};
 {auto w=setup();auto m=mem();capture(m);w.groups[0].state=Lifecycle::Reward;w.quotes[1]={1,.2,true,true};
  yes(!early_solo_proposal(w,m)&&w.queried.empty(),"fresh progressing actual reward approach retained before elective solo");}
 {auto w=setup();auto m=mem();capture(m);w.groups[0].state=Lifecycle::Reward;w.groups[0].seen=99;w.quotes[1]={1,.2,true,true};
  yes(!early_solo_proposal(w,m),"stale reward Travel remains Unknown under finite ordinary revalidation");}
 {auto w=setup();auto m=mem();capture(m);w.groups[0].state=Lifecycle::Reward;m.mission.expiry=100;w.quotes[1]={1,.2,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==1,"expired reward approach cannot renew itself forever");}
 {auto w=setup();auto m=mem();capture(m);w.groups[0].state=Lifecycle::Reward;m.route_stall=6;w.quotes[1]={1,.2,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==1,"stalled reward intent is revalidated rather than treated as progress");}
 auto crew=[](Memory&m){m.mission.assembly_count=2;m.mission.assembly_ids[0]=3;m.mission.assembly_ids[1]=4;
  m.mission.assembly_anchor=3;m.mission.last_camp_hp=1000;};
 {auto w=setup();auto m=mem();crew(m);w.quotes[1]={1,.2,true,true};
  yes(!early_solo_proposal(w,m),"actual named paid crew retained for ordinary fresh revalidation");}
 {auto w=setup();auto m=mem();crew(m);m.mission.assembly_ids[0]=2;w.quotes[1]={1,.2,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==1,"another crew's IDs cannot claim self readiness");}
 {auto w=setup();auto m=mem();crew(m);m.mission.last_camp_hp=-1;w.quotes[1]={1,.2,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==1,"unnamed stale IDs without actual prior camp state do not block solo");}
 {auto w=setup();auto m=mem();crew(m);m.mission.expiry=99;w.quotes[1]={1,.2,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==1,"expired paid crew intent requires ordinary proof before retention");}
 {auto w=setup();auto m=mem();m.mission.phase=Phase::Travel;w.quotes[1]={1,.2,true,true};
  yes(!early_solo_proposal(w,m),"unknown unexpired Travel cannot be treated as zero income by elective solo");}
 {auto w=setup();auto m=mem();m.mission.phase=Phase::Travel;w.quotes[0]={0,0,true,false};w.quotes[1]={1,.2,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==1,"fresh known infeasible Travel releases despite unexpired lease");}
 {auto w=setup();auto m=mem();m.mission.phase=Phase::Travel;m.mission.expiry=100;w.quotes[1]={1,.2,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==1,"expired unknown Travel cannot renew elective protection");}
 {auto w=setup();auto m=mem();m.mission.phase=Phase::Travel;w.groups[0].state=Lifecycle::Respawning;w.quotes[1]={1,.2,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==1,"actual known unavailable lifecycle releases old Travel");}
 {auto w=setup();auto m=mem();m.mission.phase=Phase::Observe;w.quotes[1]={1,.2,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==1,"unpriced Observe cannot veto a paid self itinerary");}
 {auto w=setup();auto m=mem();m.mission.phase=Phase::Travel;m.mission.rate=0;w.quotes[1]={1,.2,true,true};
  yes(!early_solo_proposal(w,m),"finite Travel continuity does not depend on raw positive rate");}
 {auto w=setup();auto m=mem();m.mission.group=-1;w.groups[1].state=Lifecycle::Respawning;
  w.groups[0].camps[0].awake=true;w.self.can_move=true;w.quotes[0]={0,.2,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==0,"one-move awake hypothesis still requires an explicit feasible quote");}
 {auto w=setup();auto m=mem();m.mission.group=-1;w.groups[1].state=Lifecycle::Respawning;
  w.groups[0].camps[0].awake=true;w.self.can_move=false;w.self.can_attack=true;w.quotes[0]={0,.2,true,true};
  yes(!early_solo_proposal(w,m)&&w.queried.empty(),"awake outside actual basic and spent movement is not a hypothesis");}
 {auto w=setup();auto m=mem();m.mission.group=-1;w.groups[1].state=Lifecycle::Respawning;
  w.groups[0].camps[0].awake=true;w.groups[0].camps[0].pos={4,3};w.self.can_attack=true;w.quotes[0]={0,.2,true,true};
  auto p=early_solo_proposal(w,m);yes(p&&p->mission.group==0,"actual awake in-basic-range body may request fresh proof");}
 {auto w=setup();auto m=mem();m.mission.group=-1;w.groups[1].state=Lifecycle::Respawning;
  w.groups[0].camps[0].awake=true;w.self.can_move=true;w.self.completed=true;w.quotes[0]={0,.2,true,true};
  yes(!early_solo_proposal(w,m)&&w.queried.empty(),"completed awake owner cannot fabricate useful entry");}
 std::printf("%d solo entry checks passed\n",checks);
}
