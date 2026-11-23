const SETS=[
 {k:'main300',name:'A 主线 21.10_Levels_1-300_fix',short:'A',from:1,to:300,color:'#3b82f6'},
 {k:'ab200',name:'B 2205-arrows-main',short:'B',from:301,to:500,color:'#f59e0b'},
 {k:'loop200',name:'C 07.11_Loop_Fixes',short:'C',from:501,to:700,color:'#10b981'},
 {k:'loopv2',name:'D 2904-arrows-loop_v2',short:'D',from:701,to:730,color:'#a855f7'},
 {k:'oct',name:'E October_2026',short:'E',from:731,to:760,color:'#ef4444'}];
const SETMAP=Object.fromEntries(SETS.map(s=>[s.k,s]));
const ELEMS=[
 {k:'box',name:'箱子 Box',kind:2,desc:'占据矩形区域的障碍，带血量(health)'},
 {k:'pipe',name:'管道 Pipe',kind:3,desc:'带血量的管道路径，含通过点(passes)'},
 {k:'corner',name:'拐角 Corner',kind:4,desc:'单格转向块，带两个方向和 demand 数字'},
 {k:'band',name:'束带 Band',kind:8,desc:'覆盖在 2~5 条箭头上的束带，把它们绑在一起'},
 {k:'key',name:'钥匙 Key',kind:11,desc:'附着在某条箭头一个格子上，箭头离场后收集'},
 {k:'curtain',name:'幕布 Curtain',kind:12,desc:'垫在箭头下方的隐藏层，内含嵌套箭头'},
 {k:'locked',name:'锁定幕布 Locked',kind:18,desc:'覆盖大块区域，health=所需钥匙数'}];
async function loadStats(){const r=await fetch('data/stats.json');return r.json()}
function nav(cur){
 const p=[['index.html','总览'],['levels.html','关卡图墙'],['stats.html','数据统计'],['method.html','方法与说明']];
 document.body.insertAdjacentHTML('afterbegin','<header class="top"><div class="in"><b>Maze Out! 关卡解析</b>'+p.map(a=>`<a href="${a[0]}" class="${a[0]===cur?'on':''}">${a[1]}</a>`).join('')+'</div></header>');
}
const mean=a=>a.length?a.reduce((x,y)=>x+y,0)/a.length:0;
const median=a=>{if(!a.length)return 0;const s=[...a].sort((x,y)=>x-y),m=s.length>>1;return s.length%2?s[m]:(s[m-1]+s[m])/2};
const f1=x=>(Math.round(x*10)/10).toString();const f2=x=>(Math.round(x*100)/100).toString();
function pct(x){return (x*100).toFixed(1)+'%'}
