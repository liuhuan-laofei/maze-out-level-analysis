import json,collections,statistics as st
L=json.load(open('data/levels.json'))
def bbox(cs):
    xs=[c[0] for c in cs];ys=[c[1] for c in cs];return min(xs),min(ys),max(xs),max(ys)
def turns(p):
    return sum(1 for i in range(2,len(p)) if (p[i][0]-p[i-1][0],p[i][1]-p[i-1][1])!=(p[i-1][0]-p[i-2][0],p[i-1][1]-p[i-2][1]))
rows=[]
for x in L:
    W,H=x['width'],x['height']
    def visit(it,under):
        k=it['kind'];cs=it['occupiedPositions']
        if k not in(2,3,12): return
        x0,y0,x1,y1=bbox(cs);w,h=x1-x0+1,y1-y0+1
        r=dict(gid=x['global_id'],set=x['set'],kind={2:'box',3:'pipe',12:'elevator'}[k],under_elevator=under,cells=len(cs),w=w,h=h,
               rect=int(len(cs)==w*h),health=it.get('health'),board_area=W*H,W=W,H=H,
               cx=round(((x0+x1)/2+.5)/W,3),cy=round(((y0+y1)/2+.5)/H,3),
               edge=int(x0==0 or y0==0 or x1==W-1 or y1==H-1),share=round(len(cs)/(W*H),4))
        if k==3: r['turns']=turns(cs);r['shape']='straight' if turns(cs)==0 else f'{turns(cs)}-turn'
        if k==12:
            sub=it.get('items',[]);r['nested_arrows']=sum(1 for s in sub if s['kind']==1)
            r['nested_other']=dict(collections.Counter({2:'box',3:'pipe',4:'corner',8:'band',11:'key'}[s['kind']] for s in sub if s['kind']!=1))
        rows.append(r)
        if k==12:
            for s in it.get('items',[]): visit(s,True)
    for it in x['itemModels']: visit(it,False)
json.dump(rows,open('data/obstacles.json','w'),separators=(',',':'))
def summ(v):
    return dict(n=len(v),min=min(v),med=st.median(v),mean=round(st.mean(v),2),max=max(v)) if v else None
for kind in('box','pipe','elevator'):
    R=[r for r in rows if r['kind']==kind]
    print('==',kind,'instances',len(R),'levels',len({r['gid'] for r in R}),'under elevator',sum(r['under_elevator'] for r in R))
    print(' cells',summ([r['cells'] for r in R]))
    print(' w',summ([r['w'] for r in R]),'h',summ([r['h'] for r in R]),'rect',sum(r['rect'] for r in R))
    if kind!='elevator': print(' health',summ([r['health'] for r in R if r['health'] is not None]))
    print(' share of board',summ([r['share'] for r in R]),'edge',sum(r['edge'] for r in R))
    print(' per level',collections.Counter(collections.Counter(r['gid'] for r in R).values()))
    print(' by set',collections.Counter(r['set'] for r in R))
    print(' top sizes',collections.Counter((r['w'],r['h']) for r in R).most_common(8))
    if kind=='pipe': print(' shape',collections.Counter(r['shape'] for r in R),'len',collections.Counter(r['cells'] for r in R).most_common(6))
    if kind=='elevator':
        print(' nested arrows',summ([r['nested_arrows'] for r in R]))
        print(' nested other',collections.Counter(k for r in R for k in r['nested_other']))
        print(' first',min(r['gid'] for r in R),' ratio to board', summ([r['share'] for r in R]))
