"""Rule-aware solver using rules confirmed by in-game tutorials (xlsx):
 band(8)=linked arrows move together; key(11)+locked curtain(18)=collect keys to open (hides arrows);
 pipe(3)=arrows pass through to exit at other end, breaks after `health` passes;
 box(2)=breaks after `health` arrows cleared; corner(4)=turns arrows; curtain(12)=Elevator: clear arrows on it to reveal nested arrows."""
import json,collections
DV={1:(0,1),2:(0,-1),3:(1,0),4:(-1,0)}
def solve(x,hidden_blocks=True,hidden_tappable=False,corner_side=True,pipe_side=True,box_mode='count',delay=False):
    W,H=x['width'],x['height'];its=x['itemModels']
    arrows={};nested={};boxes={};pipes={};corners={};bands=[];keys={};elev=[];locked=[]
    for it in its:
        k=it['kind'];i=it['instanceId']
        if k==1: arrows[i]=it
        elif k==2: boxes[i]=it
        elif k==3: pipes[i]=it
        elif k==4: corners[i]=it
        elif k==8: bands.append(it)
        elif k==11: keys[tuple(it['occupiedPositions'][0])]=i
        elif k==12:
            elev.append(it)
            for s in it.get('items',[]):
                if s['kind']==1: nested[s['instanceId']]=s
        elif k==18: locked.append(it)
    # band groups
    cellowner={}
    for i,a in arrows.items():
        for c in a['occupiedPositions']: cellowner[tuple(c)]=i
    parent={i:i for i in arrows}
    def find(a):
        while parent[a]!=a: parent[a]=parent[parent[a]];a=parent[a]
        return a
    for b in bands:
        ids=[cellowner[tuple(c)] for c in b['occupiedPositions'] if tuple(c) in cellowner]
        for j in ids[1:]: parent[find(j)]=find(ids[0])
    # key -> arrow
    keyarrow={}
    for c,ki in keys.items():
        if c in cellowner: keyarrow[cellowner[c]]=keyarrow.get(cellowner[c],0)+1
    # locked curtains: need cumulative keys in order
    locked.sort(key=lambda l:l.get('order',0))
    need=[];cum=0
    for l in locked: cum+=l.get('health',1);need.append(cum)
    hidden={}  # arrow -> curtain idx
    for ci,l in enumerate(locked):
        cs={tuple(c) for c in l['occupiedPositions']}
        for i,a in arrows.items():
            if any(tuple(c) in cs for c in a['occupiedPositions']): hidden.setdefault(i,ci)
    # elevator top sets
    etop=[]
    for e in elev:
        cs={tuple(c) for c in e['occupiedPositions']}
        etop.append({i for i,a in arrows.items() if any(tuple(c) in cs for c in a['occupiedPositions'])})
    # static cell maps
    pipecell={};pipeend={}
    for pid,p in pipes.items():
        cs=[tuple(c) for c in p['occupiedPositions']]
        for c in cs: pipecell[c]=pid
        def sub(a,b): return (a[0]-b[0],a[1]-b[1])
        # end0 inward = cs[1]-cs[0]; exits outward = cs[0]-cs[1]
        pipeend[cs[0]]=(pid,sub(cs[1],cs[0]),sub(cs[-1],cs[-2]),cs[-1])
        pipeend[cs[-1]]=(pid,sub(cs[-2],cs[-1]),sub(cs[0],cs[1]),cs[0])
    boxcell={}
    for bid,b in boxes.items():
        for c in b['occupiedPositions']: boxcell[tuple(c)]=bid
    cornercell={tuple(c['occupiedPositions'][0]):c for c in corners.values()}
    active=set(arrows);nactive_nested=set();revealed=[False]*len(elev)
    pipe_passes=collections.Counter();broken_pipe=set();broken_box=set();opened=0
    cleared=0;keys_got=0
    def occ(cell,exclude_group):
        # return blocker id or None
        o=cellowner.get(cell)
        if o is not None and o in active and find(o) not in exclude_group:
            if o in hidden and hidden_blocks is False and hidden[o]>=opened: pass
            else: return ('a',o)
        for n in nested_cells.get(cell,()):
            if n in nactive_nested: return ('n',n)
        return None
    nested_cells=collections.defaultdict(list)
    for i,a in nested.items():
        for c in a['occupiedPositions']: nested_cells[tuple(c)].append(i)
    def free(i,group):
        a=arrows[i] if i in arrows else nested[i]
        own={tuple(c) for c in a['occupiedPositions']}
        pos=tuple(a['occupiedPositions'][-1]);d=DV[a['direction']];steps=0;passed=[]
        while True:
            pos=(pos[0]+d[0],pos[1]+d[1]);steps+=1
            if steps>4*W*H+10: return False,passed
            if not(0<=pos[0]<W and 0<=pos[1]<H): return True,passed
            if pos in own: continue
            b=occ(pos,group)
            if b and not (b[0]=='n' and b[1]==i): return False,passed
            if pos in boxcell and boxcell[pos] not in broken_box: return False,passed
            if pos in pipecell and pipecell[pos] not in broken_pipe:
                pe=pipeend.get(pos)
                if pe and pe[1]==d:
                    passed.append(pe[0]);pos=pe[3];d=pe[2]
                    # the exit end cell itself: continue from there
                    continue
                if pipe_side: return False,passed
            if pos in cornercell:
                c=cornercell[pos];d1=tuple(c['direction1']);d2=tuple(c['direction2'])
                if d==(-d1[0],-d1[1]): d=d2
                elif d==(-d2[0],-d2[1]): d=d1
                elif corner_side: return False,passed
    rounds=0;total=len(arrows)+len(nested)
    removed=0
    def tappable(i):
        if i in arrows and i in hidden and hidden[i]>=opened and not hidden_tappable: return False
        if i in arrows: return i in active
        return i in nactive_nested
    while True:
        cand=[i for i in list(active)+list(nactive_nested) if tappable(i)]
        groups=collections.defaultdict(list)
        for i in cand: groups[find(i) if i in arrows else ('n',i)].append(i)
        ok=[]
        for g,mem in groups.items():
            full=[j for j in arrows if find(j)==g and j in active] if g in parent else mem
            gs={g} if g in parent else set()
            res=[free(j,gs) if tappable(j) else (False,[]) for j in full]
            if all(r[0] for r in res): ok.append((g,full,[p for r in res for p in r[1]]))
        if not ok: break
        if delay:
            nonc=[]
            for g,full,_p in ok:
                comp=False
                for ei,top in enumerate(etop):
                    if not revealed[ei] and top and top<= (set(arrows)-active)|set(full): comp=True
                if not comp: nonc.append((g,full,_p))
            if nonc: ok=nonc
        rounds+=1
        for g,full,ps in ok:
            for p in ps: pipe_passes[p]+=1
            for j in full:
                if j in arrows: active.discard(j)
                else: nactive_nested.discard(j)
                removed+=1;cleared+=1
                keys_got+=keyarrow.get(j,0)
        # side effects after round: pipe passes (recompute passes before removal is complicated; approximate by re-trace on removed set)
        # box / curtains / elevator
        for pid,p in pipes.items():
            if pipe_passes[pid]>=p.get('health',1): broken_pipe.add(pid)
        for bid,b in boxes.items():
            if bid not in broken_box and cleared>=b.get('health',0): broken_box.add(bid)
        while opened<len(need) and keys_got>=need[opened]: opened+=1
        for ei,top in enumerate(etop):
            if not revealed[ei] and not (top&active):
                revealed[ei]=True
                for s in elev[ei].get('items',[]):
                    if s['kind']==1: nactive_nested.add(s['instanceId'])
        if rounds>5000: break
    return dict(solved=(not active and not nactive_nested),left=len(active)+len(nactive_nested),rounds=rounds,total=total)
