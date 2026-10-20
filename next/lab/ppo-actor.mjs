// Actor-only port of lab/policy.py. No critic, world state, or terminal inputs.
const f=Math.fround;
export function encode(o,terrain){
  const m=o.self,x=m.x,y=m.y,w=o.width,h=o.height,team=o.actor.team,state=m.state;
  const distance=p=>Math.max(Math.abs(p[0]-x),Math.abs(p[1]-y));
  const altars=[...terrain.altars].sort((a,b)=>a[1]-b[1]||a[0]-b[0]);
  const altar=altars.reduce((best,p)=>distance(p)<distance(best)?p:best);
  const features=[m.health/Math.max(1,m.max_health),m.strength/200,m.focus/200,m.gems/100,m.gold/1000,x/w,y/h,o.actor.round/2000,
    !!(state&8),!!(state&16),!!(state&2048),m.attack_range/8,m.move_speed/3,
    o.champions.filter(c=>c.team!==team).length/10,o.champions.filter(c=>c.team===team).length/10,o.camps.length/20,
    m.type/12,!!(state&(2|4|4096)),!!(state&1),o.vision.length/512,(altar[0]-x)/w,(altar[1]-y)/h,o.banks[team]/1000,o.banks[1-team]/1000].map(v=>f(Math.max(-4,Math.min(4,v))));
  const rows=[[1,0,0,0,0,0,0,0,0,0,0,1]],actions=[{kind:'wait'}];
  if(state&2048)for(const a of o.abilities)if(a.cooldown===0&&((a.kind===1&&!(state&16))||(a.kind===7&&(a.targets&8)))){
    rows.push([0,0,0,1,0,0,0,m.health/2000,0,0,a.slot/2,1]);const action={kind:'cast',slot:a.slot};
    if(a.kind!==1)action.target={kind:1,id:m.id};actions.push(action);
  }
  if(state&16){
    const targets=[...o.champions].sort((a,b)=>a.id-b.id).filter(c=>c.team!==team).map(c=>[c,1])
      .concat([...o.camps].sort((a,b)=>a.id-b.id).map(c=>[c,2]));let count=0;
    for(const [t,kind] of targets){if(count>=4)break;const dx=t.x-x,dy=t.y-y,d=Math.max(Math.abs(dx),Math.abs(dy));
      if(d<=m.attack_range&&t.health>0){rows.push([0,0,1,0,dx/8,dy/8,d/8,t.health/2000,+(kind===1),+(kind===2),0,1]);count++;actions.push({kind:'attack',target:{kind,id:t.id}});}
    }
  }
  if(state&8)for(const [px,py] of [...o.moves].sort((a,b)=>a[1]-b[1]||a[0]-b[0])){
    const dx=px-x,dy=py-y;if(Math.max(Math.abs(dx),Math.abs(dy))===1){rows.push([0,1,0,0,dx/8,dy/8,1/8,0,0,0,0,1]);actions.push({kind:'move',x:px,y:py});if(rows.length===16)break;}
  }
  const mask=Array(16).fill(false);rows.forEach((_,i)=>mask[i]=true);
  while(rows.length<16){rows.push(Array(12).fill(0));actions.push(null);}
  return {features,candidates:rows.map(row=>row.map(f)),mask,actions};
}

export function forward(w,input){
  const context=Array.from({length:8},(_,h)=>w[288+h]);
  for(let h=0;h<8;h++)for(let g=0;g<24;g++)context[h]=f(context[h]+f(w[g*8+h]*input.features[g]));
  const hidden=[],scores=[];
  for(const c of input.candidates){const lanes=[0,0,0,0],row=[];
    for(let h=0;h<8;h++){let v=context[h];for(let j=0;j<12;j++)v=f(v+f(w[192+j*8+h]*c[j]));
      v=Math.max(0,v);row.push(v);lanes[h%4]=f(lanes[h%4]+f(w[296+h]*v));}
    hidden.push(row);scores.push(f(f(f(f(lanes[0]+lanes[1])+lanes[2])+lanes[3])+w[304]));
  }
  return {scores,hidden};
}

export function sample(scores,mask,rng,temperature=1){
  const maximum=Math.max(...scores.filter((_,i)=>mask[i]))/temperature;
  const p=scores.map((s,i)=>mask[i]?Math.exp(s/temperature-maximum):0),sum=p.reduce((a,b)=>a+b,0);
  let u=rng()*sum,index=-1;for(let i=0;i<p.length;i++)if(mask[i]){index=i;u-=p[i];if(u<=0)break;}
  return {index,logp:Math.log(p[index]/sum),logits:scores.map(v=>v/temperature)};
}

// Shared, deterministic controller. It cannot read opponent inventories or labels.
export function banking(o,terrain,cfg){
  const m=o.self;if(!(m.state&1)||m.state&(2|4|4096))return {kind:'wait'};
  const returning=m.gems>=cfg.bank_threshold||(o.actor.round>=cfg.bank_late_round&&m.gems>0);
  let goals;
  if(returning){
    const adjacent=terrain.altars.find(p=>Math.max(Math.abs(p[0]-m.x),Math.abs(p[1]-m.y))<=1);
    if(adjacent&&!(m.state&(64|128)))return {kind:'submit',x:adjacent[0],y:adjacent[1]};
    if(!(m.state&8))return {kind:'wait'};
    goals=terrain.altars.map(p=>[...p,1]);
  }else{
    if(!cfg.farm_navigation)return null;
    const distance=t=>Math.max(Math.abs(t.x-m.x),Math.abs(t.y-m.y));
    if(o.champions.some(c=>c.team!==o.actor.team&&c.health>0&&distance(c)<=cfg.enemy_attention_radius)||
       o.camps.some(c=>c.health>0&&distance(c)<=m.attack_range)||!(m.state&8))return null;
    const camps=o.camps.filter(c=>c.health>0);goals=camps.map(c=>[c.x,c.y,m.attack_range]);
    if(!goals.length){
      const corners=[[.25,.25],[.75,.75],[.25,.75],[.75,.25]],phase=(Math.floor(o.actor.round/cfg.exploration_period)+m.id)%corners.length;
      const [x,y]=corners[phase];goals=[[Math.floor(x*o.width),Math.floor(y*o.height),2]];
    }
  }
  const w=o.width,h=o.height,key=(x,y)=>y*w+x,blocked=new Set([...terrain.walls,...terrain.holes,...terrain.altars].map(p=>key(...p)));
  for(const c of [...o.camps,...o.champions])if(c.health>0&&!(c.x===m.x&&c.y===m.y))blocked.add(key(c.x,c.y));
  const distance=new Int32Array(w*h).fill(-1),queue=[];
  for(const [ax,ay,radius] of goals)for(let dy=-radius;dy<=radius;dy++)for(let dx=-radius;dx<=radius;dx++){
    const x=ax+dx,y=ay+dy,k=key(x,y);if(x>=0&&x<w&&y>=0&&y<h&&!blocked.has(k)&&distance[k]<0){distance[k]=0;queue.push(k);}
  }
  for(let j=0;j<queue.length;j++){const k=queue[j],x=k%w,y=Math.floor(k/w);
    for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){const nx=x+dx,ny=y+dy,n=key(nx,ny);
      if(nx>=0&&nx<w&&ny>=0&&ny<h&&!blocked.has(n)&&distance[n]<0){distance[n]=distance[k]+1;queue.push(n);}}
  }
  const moves=o.moves.filter(p=>Math.max(Math.abs(p[0]-m.x),Math.abs(p[1]-m.y))===1&&distance[key(...p)]>=0)
    .sort((a,b)=>distance[key(...a)]-distance[key(...b)]||a[1]-b[1]||a[0]-b[0]);
  return moves.length?{kind:'move',x:moves[0][0],y:moves[0][1]}:{kind:'wait'};
}
