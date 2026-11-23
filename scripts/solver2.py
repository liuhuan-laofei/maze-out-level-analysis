"""Rule-aware solver. Rules (from in-game tutorials + designer notes):
 kind 1 arrow; 8 linked-arrows band (group moves together); 11 key (on an arrow cell) ; 18 curtain (locked until
 cumulative keys >= sum of health in `order`; while locked it BLOCKS arrows and covered arrows cannot be tapped);
 3 pipe (arrow enters one end, exits other end; breaks after `health` passes); 2 box (blocks, breaks after cumulative
 cleared arrows >= health); 4 corner (spring at 45deg: arrow moving -direction1 turns to direction2, moving -direction2
 turns to direction1; arrow moving along direction1/direction2 hits the metal base -> blocked);
 12 elevator (layer: top-level arrows may pass/stand on it; when NO top arrow occupies its cells it opens and reveals its
 nested items; unrelated to keys). Nested items (arrows, keys, boxes, pipes, corners, bands) only exist after reveal.
"""
import collections
DV={1:(0,1),2:(0,-1),3:(1,0),4:(-1,0)}
def solve(x,**_):
    W,H=x['width'],x['height'];top=x['itemModels']
    elevs=[i for i in top if i['kind']==12]
    items=[];     # (layer, item); layer -1 = top-level
    for i in top:
        if i['kind']!=12: items.append((-1,i))
    for ei,e in enumerate(elevs):
        for s in e.get('items',[]): items.append((ei,s))
    uid=lambda j:j
    A={};BOXS={};PIPES={};CORN={};BANDS=[];KEYS=[];CURT=[]
    for j,(ly,it) in enumerate(items):
        k=it['kind']
        if k==1:A[j]=(ly,it)
        elif k==2:BOXS[j]=(ly,it)
        elif k==3:PIPES[j]=(ly,it)
        elif k==4:CORN[j]=(ly,it)
        elif k==8:BANDS.append((ly,it))
        elif k==11:KEYS.append((ly,it))
        elif k==18:CURT.append((ly,it))
    # cell -> arrows (per layer)
    cellarrows=collections.defaultdict(list)
    for j,(ly,it) in A.items():
        for c in it['occupiedPositions']: cellarrows[tuple(c)].append(j)
    parent={j:j for j in A}
    def find(a):
        while parent[a]!=a: parent[a]=parent[parent[a]];a=parent[a]
        return a
    for ly,b in BANDS:
        ids=[j for c in b['occupiedPositions'] for j in cellarrows.get(tuple(c),[]) if A[j][0]==ly]
        for j in ids[1:]: parent[find(j)]=find(ids[0])
    keyof=collections.Counter()
    for ly,k in KEYS:
        c=tuple(k['occupiedPositions'][0])
        for j in cellarrows.get(c,[]):
            if A[j][0]==ly: keyof[j]+=1;break
    CURT.sort(key=lambda t:t[1].get('order',0))
    need=[];cum=0
    for ly,c in CURT: cum+=c.get('health',1);need.append(cum)
    curtcells=[{tuple(c) for c in c_[1]['occupiedPositions']} for c_ in CURT]
    covered={j for j,(ly,it) in A.items() for ci,cs in enumerate(curtcells) if any(tuple(c) in cs for c in it['occupiedPositions'])}
    covered_by={}
    for j in covered:
        covered_by[j]=[ci for ci,cs in enumerate(curtcells) if any(tuple(c) in cs for c in A[j][1]['occupiedPositions'])]
    # static cell maps for pipes / boxes / corners (+layer)
    pipecell={};pipeend={}
    sub=lambda a,b:(a[0]-b[0],a[1]-b[1])
    for j,(ly,p) in PIPES.items():
        cs=[tuple(c) for c in p['occupiedPositions']]
        for c in cs: pipecell[c]=j
        pipeend[cs[0]]=(j,sub(cs[1],cs[0]),sub(cs[-1],cs[-2]),cs[-1])
        pipeend[cs[-1]]=(j,sub(cs[-2],cs[-1]),sub(cs[0],cs[1]),cs[0])
    boxcell={}
    for j,(ly,b) in BOXS.items():
        for c in b['occupiedPositions']: boxcell[tuple(c)]=j
    cornercell={tuple(c['occupiedPositions'][0]):j for j,(ly,c) in CORN.items()}
    curtcellmap=collections.defaultdict(list)
    for ci,cs in enumerate(curtcells):
        for c in cs: curtcellmap[c].append(ci)
    revealed=[False]*len(elevs)
    live=lambda ly: ly<0 or revealed[ly]
    active={j for j,(ly,_) in A.items() if ly<0}
    pipe_passes=collections.Counter();broken_pipe=set();broken_box=set();opened=0;cleared=0;keys_got=0
    def tappable(j):
        if j not in active: return False
        return all(ci<opened for ci in covered_by.get(j,[]))
    def free(j,grp):
        a=A[j][1];own={tuple(c) for c in a['occupiedPositions']}
        pos=tuple(a['occupiedPositions'][-1]);d=DV[a['direction']];steps=0;passed=[]
        while True:
            pos=(pos[0]+d[0],pos[1]+d[1]);steps+=1
            if steps>4*W*H+10: return False,passed
            if not(0<=pos[0]<W and 0<=pos[1]<H): return True,passed
            if pos in own: continue
            for o in cellarrows.get(pos,()):
                if o in active and find(o) not in grp: return False,passed
            for ci in curtcellmap.get(pos,()):
                if ci>=opened: return False,passed
            b=boxcell.get(pos)
            if b is not None and live(BOXS[b][0]) and b not in broken_box: return False,passed
            p=pipecell.get(pos)
            if p is not None and live(PIPES[p][0]) and p not in broken_pipe:
                pe=pipeend.get(pos)
                if pe and pe[1]==d:
                    passed.append(pe[0]);pos=pe[3];d=pe[2];continue
                return False,passed
            c=cornercell.get(pos)
            if c is not None and live(CORN[c][0]):
                cc=CORN[c][1];d1=tuple(cc['direction1']);d2=tuple(cc['direction2'])
                if d==(-d1[0],-d1[1]): d=d2
                elif d==(-d2[0],-d2[1]): d=d1
                else: return False,passed
    rounds=0;total=len(A)
    while True:
        groups=collections.defaultdict(list)
        for j in active: groups[find(j)].append(j)
        ok=[]
        for g,mem in groups.items():
            if not all(tappable(m) for m in mem): continue
            res=[free(m,{g}) for m in mem]
            if all(r[0] for r in res): ok.append((mem,[p for r in res for p in r[1]]))
        if not ok: break
        rounds+=1
        for mem,ps in ok:
            for p in ps: pipe_passes[p]+=1
            for m in mem:
                active.discard(m);cleared+=1;keys_got+=keyof.get(m,0)
        for p,(ly,pp) in PIPES.items():
            if live(ly) and pipe_passes[p]>=pp.get('health',1): broken_pipe.add(p)
        for b,(ly,bb) in BOXS.items():
            if live(ly) and cleared>=bb.get('health',0): broken_box.add(b)
        while opened<len(need) and keys_got>=need[opened]: opened+=1
        for ei,e in enumerate(elevs):
            if revealed[ei]: continue
            cs={tuple(c) for c in e['occupiedPositions']}
            if not any(A[j][0]<0 and any(tuple(c) in cs for c in A[j][1]['occupiedPositions']) for j in active):
                revealed[ei]=True
                for j,(ly,_) in A.items():
                    if ly==ei: active.add(j)
        if rounds>5000: break
    return dict(solved=not active,left=len(active),rounds=rounds,total=total)
