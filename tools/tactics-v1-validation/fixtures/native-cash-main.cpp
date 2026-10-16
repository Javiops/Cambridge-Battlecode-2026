// The tested Cassi executes unchanged actual Bot::turn, including production
// arbitration and all receipt/refresh/action gates. Other allied Issac bodies
// idle at spawn to isolate the explicitly solo finite itinerary.
#define main retained_production_main
#include "retained-main.h"
#undef main
int main(){tactics::Bot bot;bool marker=false;while(true){try{if(cambc::is_draft()||tactics::identity(cambc::self())==0||tactics::identity(cambc::self())==2){bot.turn();if(!cambc::is_draft()&&!marker){std::printf("CASH_MAIN_ACTUAL_CALLER %d\n",tactics::identity(cambc::self()));marker=true;}}}catch(const std::exception&e){std::printf("CASH_MAIN_ERROR %s\n",e.what());}cambc::end_turn();}}
