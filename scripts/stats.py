import json,csv,collections,math,sys
sys.path.insert(0,'scripts')
from solver2 import solve as solve2
BEST={}
L=json.load(open('data/levels.json'))
DV={1:(0,1),2:(0,-1),3:(1,0),4:(-1,0)}
KN={1:'arrow',2:'box',3:'pipe',4:'corner',8:'band',11:'key',12:'elevator',18:'curtain'}
def solve(arrows,W,H):
    """arrows: list of items. returns (depth, stuck, free0, blockers_mean, longest_ray, order_levels)"""
    owner={}
    for i,a in enumerate(arrows):
        for c in a['occupiedPositions']: owner[tuple(c)]=i
    deps=[]
    for i,a in enumerate(arrows):
        hx,hy=a['occupiedPositions'][-1];dx,dy=DV[a['direction']]
        b=set();x,y=hx+dx,hy+dy
        while 0<=x<W and 0<=y<H:
            o=owner.get((x,y))
            if o is not None and o!=i: b.add(o)
            x+=dx;y+=dy
        deps.append(b)
    n=len(arrows);lvl=[0]*n;rem=set(range(n));rounds=0
    free0=sum(1 for b in deps if not b)
    while rem:
        ready=[i for i in rem if not (deps[i]&rem)]
        if not ready: break
        rounds+=1
        for i in ready: lvl[i]=rounds
        rem-=set(ready)
    return dict(depth=rounds,stuck=len(rem),free0=free0,dep_mean=(sum(len(b) for b in deps)/n if n else 0),dep_max=max((len(b) for b in deps),default=0),n=n)
def turns(p):
    t=0
    for i in range(2,len(p)):
        if (p[i][0]-p[i-1][0],p[i][1]-p[i-1][1])!=(p[i-1][0]-p[i-2][0],p[i-1][1]-p[i-2][1]): t+=1
    return t
rows=[]
for x in L:
    W,H=x['width'],x['height'];its=x['itemModels']
    ar=[i for i in its if i['kind']==1]
    nested=[s for i in its if i['kind']==12 for s in i.get('items',[]) if s['kind']==1]
    kc=collections.Counter(KN[i['kind']] for i in its)
    for i in its:
        if i['kind']==12:
            for sub_ in i.get('items',[]):
                if sub_['kind']!=1: kc[KN[sub_['kind']]]+=1
    lens=[len(a['occupiedPositions']) for a in ar] or [0]
    s1=solve(ar,W,H) if ar else dict(depth=0,stuck=0,free0=0,dep_mean=0,dep_max=0,n=0)
    s2=solve(nested,W,H) if nested else dict(depth=0,stuck=0,free0=0,dep_mean=0,dep_max=0,n=0)
    cells=sum(lens)
    dirs=collections.Counter(a['direction'] for a in ar)
    cols=set(a.get('colorId') for a in ar)|set(a.get('colorId') for a in nested)
    tr=[turns(a['occupiedPositions']) for a in ar] or [0]
    allits=its+[q for i in its if i['kind']==12 for q in i.get('items',[])]
    box_hp=sum(i.get('health',0) for i in allits if i['kind']==2)
    pipe_hp=sum(i.get('health',0) for i in allits if i['kind']==3)
    elevator_cells=sum(len(i['occupiedPositions']) for i in its if i['kind']==12)
    curtain_keys=sum(i.get('health',0) for i in its if i['kind']==18)
    r2=solve2(x,**BEST)
    rows.append(dict(
        global_id=x['global_id'],set=x['set'],set_index=x['set_index'],levelId=x['levelId'],
        width=W,height=H,area=W*H,
        cfg_difficulty=x['cfg_difficulty'],cfg_duration=x['cfg_duration'],levelKind=x.get('levelKind'),
        arrows=len(ar),nested_arrows=len(nested),arrow_cells=cells,density=round(cells/(W*H),4),
        len_mean=round(sum(lens)/len(lens),2),len_max=max(lens),len_min=min(lens),turns_mean=round(sum(tr)/len(tr),2),turns_max=max(tr),
        dir_up=dirs[1],dir_down=dirs[2],dir_right=dirs[3],dir_left=dirs[4],
        colors=len(cols-{None})+(1 if None in cols else 0),
        box=kc['box'],pipe=kc['pipe'],corner=kc['corner'],band=kc['band'],key=kc['key'],elevator=kc['elevator'],curtain=kc['curtain'],
        box_hp=box_hp,pipe_hp=pipe_hp,curtain_keys=curtain_keys,elevator_cells=elevator_cells,
        special_kinds=sum(1 for k in ('box','pipe','corner','band','key','elevator','curtain') if kc[k]),
        depth_basic=s1['depth'],solved2=int(r2['solved']),rounds2=r2['rounds'],left2=r2['left'],
        depth=r2['rounds'],stuck=r2['left'],free0=s1['free0'],free0_ratio=round(s1['free0']/s1['n'],4) if s1['n'] else 0,
        dep_mean=round(s1['dep_mean'],2),dep_max=s1['dep_max'],
                total_stuck=r2['left'],
        total_items=len(its)+len(nested)))
json.dump(rows,open('data/stats.json','w'),separators=(',',':'))
with open('data/stats.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(len(rows))
import statistics as st
for s in ('main300','ab200','loop200','loopv2','oct'):
    r=[x for x in rows if x['set']==s]
    print(s,len(r),'arrows',st.mean(x['arrows'] for x in r),'area',st.mean(x['area'] for x in r),'depth',st.mean(x['depth'] for x in r),'stuck>0',sum(1 for x in r if x['total_stuck']>0),'free0',round(st.mean(x['free0_ratio'] for x in r),3))
