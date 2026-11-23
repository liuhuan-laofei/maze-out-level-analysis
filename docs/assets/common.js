const SETS=[
 {k:'main300',name:'A 主线 21.10_Levels_1-300_fix',short:'A',from:1,to:300,color:'#3b82f6'},
 {k:'ab200',name:'B 2205-arrows-main',short:'B',from:301,to:500,color:'#f59e0b'},
 {k:'loop200',name:'C 07.11_Loop_Fixes',short:'C',from:501,to:700,color:'#10b981'},
 {k:'loopv2',name:'D 2904-arrows-loop_v2',short:'D',from:701,to:730,color:'#a855f7'},
 {k:'oct',name:'E October_2026',short:'E',from:731,to:760,color:'#ef4444'}];
const SETMAP=Object.fromEntries(SETS.map(s=>[s.k,s]));
const ELEMS=[
 {k:'band',name:'连接箭头 Linked Arrows',kind:8,desc:'束带把 2–5 条箭头绑在一起，必须一起移动，只要有一条被挡就都走不了（游戏第 7 关引入，教程：Linked arrows move together）'},
 {k:'key',name:'钥匙 Key',kind:11,desc:'附着在某条箭头的一个格子上，该箭头离场时收集，用来打开幕布'},
 {k:'locked',name:'幕布 Curtain',kind:18,desc:'带锁的大幕布，盖住一片区域，收集足够数量的钥匙（health）后打开（第 20 关引入）'},
 {k:'pipe',name:'水管 Pipe',kind:3,desc:'箭头从一端穿入、从另一端按固定方向飞出，穿过 health 次后水管破碎（第 35 关引入）'},
 {k:'box',name:'盒子 Box',kind:2,desc:'占据矩形区域的障碍，数字是需要清除的箭头数量，达到后破碎、移除遮挡（第 50 关引入）'},
 {k:'corner',name:'拐角器 Corner',kind:4,desc:'单格转向块，箭头撞上后转向，考验路径预判（数据里首现第 70 关；见方法页对 75 的说明）'},
 {k:'curtain',name:'电梯 Elevator',kind:12,desc:'分层遮挡：先清掉电梯上的箭头，才会露出下层的嵌套箭头（第 100 关引入）'}];
async function loadStats(){const r=await fetch('data/stats.json');return r.json()}
function nav(cur){
 const p=[['index.html','总览'],['levels.html','关卡图墙'],['stats.html','数据统计'],['method.html','方法与说明']];
 document.body.insertAdjacentHTML('afterbegin','<header class="top"><div class="in"><b>Maze Out! 关卡解析</b>'+p.map(a=>`<a href="${a[0]}" class="${a[0]===cur?'on':''}">${a[1]}</a>`).join('')+'</div></header>');
}
const mean=a=>a.length?a.reduce((x,y)=>x+y,0)/a.length:0;
const median=a=>{if(!a.length)return 0;const s=[...a].sort((x,y)=>x-y),m=s.length>>1;return s.length%2?s[m]:(s[m-1]+s[m])/2};
const f1=x=>(Math.round(x*10)/10).toString();const f2=x=>(Math.round(x*100)/100).toString();
function pct(x){return (x*100).toFixed(1)+'%'}
