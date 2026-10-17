// Fixture opponent only. Allied candidate owners use unchanged production main.
#include <cambc.h>
#include <algorithm>
#include <array>
int main(){
 while(true){
  if(cambc::is_draft()){
   const auto accepted=cambc::draft::current_draft(cambc::team::ally);
   constexpr std::array<int,10> choices{0,2,4,5,6,7,8,9,10,1};
   for(int choice:choices){
    if(std::find(accepted.begin(),accepted.end(),static_cast<cambc::champion_draft>(choice))!=accepted.end())continue;
    try{cambc::draft::pick(static_cast<cambc::champion_draft>(choice));break;}
    catch(const cambc::error&){}
   }
  }
  cambc::end_turn();
 }
}
