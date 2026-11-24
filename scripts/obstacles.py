"""Per-instance stats for box(2) / pipe(3) / elevator(12) / curtain(18), incl. items nested under elevators."""
import json,collections,statistics as st
L=json.load(open('data/levels.json'))
NAME={2:'box',3:'pipe',12:'elevator',18:'curtain'}
def bbox(cs):
    xs=[c[0] for c in cs];ys=[c[1] for c in cs];return min(xs),min(ys),max(xs),max(ys)
def turns(p):
    return sum(1 for i in range(2,len(p)) if (p[i][0]-p[i-1][0],p[i][1]-p[i-1][1])!=(p[i-1][0]-p[i-2][0],p[i-1][1]-p[i-2][1]))
rows=[]
for x in L:
    W,H=x['width'],x['height'];top=x['itemModels']
    top_arrows=[a for a in top if a['kind']==1]
    curts=sorted([i for i in top if i['kind']==18],key=lambda i:i.get('order',0))
    cum={};s=0
    for c in curts: s+=c.get('health',1);cum[c['instanceId']]=s
    keys_total=sum(1 for i in top if i['kind']==11)+sum(1 for e in top if e['kind']==12 for q in e.get('items',[]) if q['kind']==11)
    def touch(cs,arrows):
        S={tuple(p) for p in cs}
        t=[a for a in arrows if any(tuple(p) in S for p in a['occupiedPositions'])]
        return len(t),sum(1 for a in t if all(tuple(p) in S for p in a['occupiedPositions']))
    def visit(it,layer_arrows,under):
        k=it['kind']
        if k not in NAME: return
        cs=it['occupiedPositions'];x0,y0,x1,y1=bbox(cs);w,h=x1-x0+1,y1-y0+1
        r=dict(gid=x['global_id'],set=x['set'],kind=NAME[k],under_elevator=under,cells=len(cs),w=w,h=h,rect=int(len(cs)==w*h),
               health=it.get('health'),W=W,H=H,share=round(len(cs)/(W*H),4),
               edge=int(x0==0 or y0==0 or x1==W-1 or y1==H-1),level_arrows=len(top_arrows))
        if k==3:
            r['turns']=turns(cs)
        if k in(2,18):
            n,f=touch(cs,layer_arrows);r['below']=n;r['below_full']=f
            r['cond']=it.get('health');r['cond_ratio']=round(it.get('health',0)/max(1,len(top_arrows)),3)
            if k==2 and not under:
                r['below_nested']=sum(touch(cs,[q for q in e.get('items',[]) if q['kind']==1])[0] for e in top if e['kind']==12)
        if k==3: r['cond']=it.get('health')
        if k==18:
            r['order']=it.get('order');r['cum_keys']=cum[it['instanceId']];r['level_keys']=keys_total
            nn=0
            for e in top:
                if e['kind']==12: nn+=touch(cs,[q for q in e.get('items',[]) if q['kind']==1])[0]
            r['below_nested']=nn
        if k==12:
            sub=it.get('items',[]);r['below']=sum(1 for q in sub if q['kind']==1)
            r['below_other']=dict(collections.Counter({2:'box',3:'pipe',4:'corner',8:'band',11:'key'}[q['kind']] for q in sub if q['kind']!=1))
            n,f=touch(cs,top_arrows);r['cond']=n;r['cond_full']=f   # top-level arrows still standing on it
            r['cond_ratio']=round(n/max(1,len(top_arrows)),3)
        rows.append(r)
        if k==12:
            subarrows=[q for q in it.get('items',[]) if q['kind']==1]
            for q in it.get('items',[]): visit(q,subarrows,True)
    for it in top: visit(it,top_arrows,False)
json.dump(rows,open('data/obstacles.json','w'),separators=(',',':'))
def summ(v): return (min(v),st.median(v),round(st.mean(v),1),max(v)) if v else None
for kind in NAME.values():
    R=[r for r in rows if r['kind']==kind]
    print('==',kind,len(R),'unique sizes',len({(r['w'],r['h']) for r in R}))
    for f in ('cells','below','cond','below_nested','cum_keys'):
        v=[r[f] for r in R if r.get(f) is not None]
        if v: print(' ',f,summ(v))
    if kind=='box': print('  box below>0',sum(1 for r in R if r['below']>0),'nested>0',sum(1 for r in R if r.get('below_nested',0)>0),'under_elev',sum(r['under_elevator'] for r in R))
    if kind=='curtain': print('  full-cover',sum(1 for r in R if r['below']==r['below_full']),'partial',sum(1 for r in R if r['below']!=r['below_full']),'zero',sum(1 for r in R if r['below']==0),'by set',collections.Counter(r['set'] for r in R),'per level',collections.Counter(collections.Counter(r['gid'] for r in R).values()))
    if kind=='elevator': print('  cond==0',sum(1 for r in R if r['cond']==0),'cond_full==cond',sum(1 for r in R if r['cond']==r['cond_full']))
