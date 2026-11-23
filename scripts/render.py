import json,sys,os,math
from PIL import Image,ImageDraw,ImageFont
SS=2
BG=(248,246,240);GRID=(228,225,216)
INK=(24,26,32)
BOX=(176,124,72);BOXD=(110,70,35)
PIPE=(96,125,139);PIPEL=(176,190,197)
CORN=(171,71,188)
BAND=(0,200,83)
KEY=(255,200,0);KEYD=(140,100,0)
CURT=(198,40,40)
ELEV=(124,77,255)
DIRV={1:(0,1),2:(0,-1),3:(1,0),4:(-1,0)}
_fc={}
def font(sz):
    sz=max(6,int(sz))
    if sz in _fc: return _fc[sz]
    f=None
    for p in ('/System/Library/Fonts/Helvetica.ttc','/System/Library/Fonts/SFNS.ttf','/Library/Fonts/Arial.ttf'):
        if os.path.exists(p):
            try: f=ImageFont.truetype(p,sz);break
            except Exception: pass
    _fc[sz]=f or ImageFont.load_default();return _fc[sz]
def auto_long_side(x): return min(1100,max(760,18*max(x['width'],x['height'])))
def render(x,path=None,long_side=None,thumb=False):
    W,H=x['width'],x['height']
    if long_side is None: long_side=auto_long_side(x)
    S=max(6,min(34,long_side//max(W,H)));P=S*SS;pad=P//2
    im=Image.new('RGB',(W*P+2*pad,H*P+2*pad),BG);d=ImageDraw.Draw(im,'RGBA')
    minD=0.05*max(W,H)*P if not thumb else 0.05*max(W,H)*P
    minD=max(P*0.8,0.045*max(im.width,im.height))   # badge diameter never below 4.5% of the long side
    def C(c): return (pad+(c[0]+.5)*P,pad+(H-1-c[1]+.5)*P)
    def cellbox(c,ins=0):
        cx,cy=C(c);h=P/2-ins;return [cx-h,cy-h,cx+h,cy+h]
    d.rectangle([pad,pad,pad+W*P,pad+H*P],fill=(255,255,255),outline=(200,196,185),width=SS)
    for i in range(1,W): d.line([pad+i*P,pad,pad+i*P,pad+H*P],fill=GRID,width=1)
    for j in range(1,H): d.line([pad,pad+j*P,pad+W*P,pad+j*P],fill=GRID,width=1)
    def outline(cells,col,w):
        cs=set(map(tuple,cells))
        for c in cs:
            b=cellbox(c)
            for dx,dy,seg in ((0,1,(b[0],b[1],b[2],b[1])),(0,-1,(b[0],b[3],b[2],b[3])),(-1,0,(b[0],b[1],b[0],b[3])),(1,0,(b[2],b[1],b[2],b[3]))):
                if (c[0]+dx,c[1]+dy) not in cs: d.line(seg,fill=col,width=w)
    labels=[];keys=[]
    def arrow(it,col=INK,wf=0.46):
        pts=[C(c) for c in it['occupiedPositions']];w=int(P*wf)
        if len(pts)>1: d.line(pts,fill=col,width=w,joint='curve')
        for q in pts: d.ellipse([q[0]-w/2,q[1]-w/2,q[0]+w/2,q[1]+w/2],fill=col)
        dv=DIRV.get(it.get('direction'))
        if dv:
            hx,hy=pts[-1];ux,uy=dv[0],-dv[1];L=P*wf;B=P*wf*0.87;px,py=-uy,ux
            d.polygon([(hx+ux*L,hy+uy*L),(hx-ux*P*.02+px*B,hy-uy*P*.02+py*B),(hx-ux*P*.02-px*B,hy-uy*P*.02-py*B)],fill=col)
    def body(it):
        k=it['kind'];cs=it['occupiedPositions']
        if k==1: arrow(it)
        elif k==2:
            for c in cs: d.rectangle(cellbox(c,P*0.04),fill=BOX)
            outline(cs,BOXD,SS*2)
            if it.get('health') is not None: labels.append(dict(cands=sorted(cs,key=lambda c:(c[0]-sum(a[0] for a in cs)/len(cs))**2+(c[1]-sum(a[1] for a in cs)/len(cs))**2),text=it['health'],fill=BOXD,D=1.0))
        elif k==3:
            pts=[C(c) for c in cs]
            d.line(pts,fill=PIPE,width=int(P*0.78),joint='curve')
            for q in pts: d.ellipse([q[0]-P*.39,q[1]-P*.39,q[0]+P*.39,q[1]+P*.39],fill=PIPE)
            d.line(pts,fill=PIPEL,width=int(P*0.34),joint='curve')
            for p in it.get('passes',[]):
                q=C(p['position']);r=P*.3;d.ellipse([q[0]-r,q[1]-r,q[0]+r,q[1]+r],fill=(255,193,7),outline=(120,90,0),width=SS)
            i=it.get('healthViewPathIndex',0)
            if it.get('health') is not None:
                order=sorted(range(len(cs)),key=lambda j:abs(j-i))
                labels.append(dict(cands=[cs[j] for j in order],text=it['health'],fill=(55,80,95),D=1.0))
        elif k==4:
            c=cs[0];d.rectangle(cellbox(c,P*0.04),fill=CORN);q=C(c)
            for key in ('direction1','direction2'):
                v=it.get(key)
                if v:
                    ux,uy=v[0],-v[1];e=(q[0]+ux*P*.42,q[1]+uy*P*.42)
                    d.line([q,e],fill=(255,255,255),width=int(P*.16));px,py=-uy,ux
                    d.polygon([(e[0]+ux*P*.1,e[1]+uy*P*.1),(e[0]-ux*P*.12+px*P*.14,e[1]-uy*P*.12+py*P*.14),(e[0]-ux*P*.12-px*P*.14,e[1]-uy*P*.12-py*P*.14)],fill=(255,255,255))
        elif k==8:
            pts=[C(c) for c in cs];d.line(pts,fill=BAND+(210,),width=int(max(P*0.2,SS*2)),joint='curve')
            r=max(P*.17,SS*3)
            for q in pts: d.ellipse([q[0]-r,q[1]-r,q[0]+r,q[1]+r],fill=BAND,outline=(255,255,255),width=SS)
        elif k==11: keys.append(cs[0])
    items=x['itemModels']
    elevs=[i for i in items if i['kind']==12]
    # 1 nested (under elevator)
    for e in elevs:
        for s in e.get('items',[]):
            if s['kind']==1: arrow(s,INK)
            else: body(s)
    # 2 elevator panel (translucent) over nested
    for e in elevs:
        cs=e['occupiedPositions']
        for c in cs: d.rectangle(cellbox(c),fill=ELEV+(46,))
        outline(cs,ELEV+(255,),SS*2)
    # 3 top-level
    for k in (2,3,4): [body(i) for i in items if i['kind']==k]
    [body(i) for i in items if i['kind']==1]
    [body(i) for i in items if i['kind']==8]
    [body(i) for i in items if i['kind']==11]
    # 4 curtain overlay
    curts=[i for i in items if i['kind']==18]
    for cu in curts:
        cs=cu['occupiedPositions']
        for c in cs: d.rectangle(cellbox(c),fill=CURT+(40,))
        outline(cs,CURT+(255,),SS*2)
        cx=sum(c[0] for c in cs)/len(cs);cy=sum(c[1] for c in cs)/len(cs)
        labels.append(dict(cands=sorted(cs,key=lambda c:(c[0]-cx)**2+(c[1]-cy)**2),text=cu.get('health',''),fill=CURT,D=1.25))
    # 5 keys (fixed markers, always large enough)
    placed=[]
    kd=max(P*0.78,minD*0.95)
    for c in keys:
        q=C(c);r=kd/2
        d.ellipse([q[0]-r,q[1]-r,q[0]+r,q[1]+r],fill=KEY,outline=KEYD,width=SS*2)
        d.text(q,'K',fill=KEYD,font=font(kd*0.62),anchor='mm');placed.append((q[0],q[1],r))
    # 6 numeric badges, placed without overlapping each other or keys
    def free_at(q,r): return all((q[0]-a)**2+(q[1]-b)**2>=((r+rr)*0.96)**2 for a,b,rr in placed)
    for lb in sorted(labels,key=lambda l:-l['D']):
        r=max(P*0.42,minD*0.5)*lb['D'];pos=None
        cand=[C(c) for c in lb['cands']]
        for q in cand:
            if free_at(q,r): pos=q;break
        if pos is None:   # try shifted spots around candidates
            for q in cand:
                for ang in range(0,360,30):
                    for mult in (1.0,1.6):
                        qq=(q[0]+math.cos(math.radians(ang))*r*mult,q[1]+math.sin(math.radians(ang))*r*mult)
                        if free_at(qq,r): pos=qq;break
                    if pos: break
                if pos: break
        if pos is None: pos=cand[0]
        placed.append((pos[0],pos[1],r))
        d.ellipse([pos[0]-r,pos[1]-r,pos[0]+r,pos[1]+r],fill=lb['fill'],outline=(255,255,255),width=max(SS*2,int(r*0.1)))
        d.text(pos,str(lb['text']),fill=(255,255,255),font=font(r*1.15 if len(str(lb['text']))<2 else r*0.95),anchor='mm')
    out=im.resize((im.width//SS,im.height//SS),Image.LANCZOS)
    if path: out.save(path,'WEBP',quality=84,method=6)
    return out
if __name__=='__main__':
    L=json.load(open('data/levels.json'))
    for g in sys.argv[1:]: render(L[int(g)-1],f'/tmp/r_{g}.png')
