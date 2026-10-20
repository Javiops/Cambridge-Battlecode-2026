// Centralized critic only. Input actor tensors use the original, frozen BC encoder.
import {forward} from './ppo-actor.mjs';
const f=Math.fround;
export function criticState(o,units,terrain,encoded,backbone){
  const {hidden}=forward(backbone,encoded),count=encoded.mask.filter(Boolean).length,mean=[],maximum=[];
  for(let h=0;h<8;h++){let sum=0,m=-Infinity;for(let k=0;k<16;k++)if(encoded.mask[k]){sum=f(sum+hidden[k][h]);m=Math.max(m,hidden[k][h]);}mean.push(f(sum/count));maximum.push(m);}
  const x=encoded.features,margin=f(x[22]-x[23]),elapsed=x[7],team=o.actor.team;
  const local=[margin,elapsed,team*2-1,f(margin*elapsed),...x,...mean,...maximum];
  const totals=[],wealth=[];
  for(const side of [0,1]){const selected=units.filter(u=>u.team===side),out=Array(8).fill(0);let assets=0,cash=0;
    if(!selected.length)throw Error('Missing critic team');
    for(const u of selected){const alive=!!(u.state&1),d=Math.min(...terrain.altars.map(p=>Math.max(Math.abs(u.x-p[0]),Math.abs(u.y-p[1]))));
      const values=[u.gems/1000,u.gold/5000,+alive/selected.length,alive?Math.max(0,u.health)/Math.max(1,u.max_health)/selected.length:0,
        u.strength/1000,u.focus/1000,u.gems/1000/(1+d),(u.state&4)?u.gems/1000:0];
      values.forEach((v,j)=>out[j]+=v);cash+=u.gold;u.items.forEach((n,j)=>assets+=n*(j%2?150:30));}
    totals.push(out);wealth.push([assets/5000,(assets+cash)/5000]);
  }
  const difference=totals[team].map((v,j)=>v-totals[1-team][j]),economic=wealth[team].map((v,j)=>v-wealth[1-team][j]),t=o.actor.round/2000;
  const transform=a=>[...a,...a.map(v=>v*t),...a.map(v=>Math.sign(v)*Math.log1p(Math.abs(v)))];
  return [...local,...transform(difference),...transform(economic)].map(f);
}
