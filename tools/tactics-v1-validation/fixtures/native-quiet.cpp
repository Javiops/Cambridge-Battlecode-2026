#include <cambc.h>
#include <algorithm>
int main(){namespace bc=cambc;while(true){if(bc::is_draft()){auto old=bc::draft::current_draft(bc::team::ally);for(auto pick:{bc::champion_draft::vendetta,bc::champion_draft::varg,bc::champion_draft::cassi_and_issac,bc::champion_draft::ryth,bc::champion_draft::tavi})if(std::find(old.begin(),old.end(),pick)==old.end()){bc::draft::pick(pick);break;}}bc::end_turn();}}
