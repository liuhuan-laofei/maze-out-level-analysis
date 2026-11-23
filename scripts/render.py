import json,sys,os,math
from PIL import Image,ImageDraw,ImageFont
SS=2
PAL={None:(52,58,72),1:(231,76,60),2:(243,156,18),3:(241,196,15),4:(46,204,113),5:(44,62,80),6:(26,188,156),7:(52,152,219),8:(155,89,182),9:(233,30,120)}
BG=(248,246,240);GRID=(228,225,216)
DIRV={1:(0,1),2:(0,-1),3:(1,0),4:(-1,0)}
FONT=None
def font(sz):
    sz=max(8,int(sz))
    for p in ('/System/Library/Fonts/Helvetica.ttc','/System/Library/Fonts/SFNS.ttf','/Library/Fonts/Arial.ttf'):
        if os.path.exists(p):
            try: return ImageFont.truetype(p,sz)
            except Exception: pass
    return ImageFont.load_default()
def render(x,path=None,long_side=760,margin=1):
    W,H=x['width'],x['height']
    S=max(8,min(34,long_side//max(W,H)))
    P=S*SS
    pad=P//2
    im=Image.new('RGB',(W*P+2*pad,H*P+2*pad),BG)
    d=ImageDraw.Draw(im,'RGBA')
    def C(c):  # cell center, y up
        return (pad+(c[0]+.5)*P, pad+(H-1-c[1]+.5)*P)
    def cellbox(c,inset=0):
        cx,cy=C(c);h=P/2-inset
        return [cx-h,cy-h,cx+h,cy+h]
    # board background + grid
    d.rectangle([pad,pad,pad+W*P,pad+H*P],fill=(255,255,255,255),outline=(200,196,185,255),width=SS)
    for i in range(1,W): d.line([pad+i*P,pad,pad+i*P,pad+H*P],fill=GRID+(255,),width=1)
    for j in range(1,H): d.line([pad,pad+j*P,pad+W*P,pad+j*P],fill=GRID+(255,),width=1)
    items=x['itemModels']
    f=font(max(10,int(P*0.55)))
    def txt(c,s,col=(255,255,255),sz=None):
        ff=f if sz is None else font(sz)
        d.text(C(c),str(s),fill=col,font=ff,anchor='mm')
    def arrow(it,alpha=255,wf=0.46,tint=None):
        dd=d
        if alpha<255:
            lay=Image.new('RGBA',im.size,(0,0,0,0));dd=ImageDraw.Draw(lay)
        p=it['occupiedPositions'];col=(tint or PAL.get(it.get('colorId'),PAL[None]))+(255,)
        pts=[C(c) for c in p]
        w=int(P*wf)
        if len(pts)>1:
            dd.line(pts,fill=col,width=w,joint='curve')
        for q in pts: dd.ellipse([q[0]-w/2,q[1]-w/2,q[0]+w/2,q[1]+w/2],fill=col)
        dv=DIRV.get(it.get('direction'))
        if dv:
            hx,hy=pts[-1];ux,uy=dv[0],-dv[1]
            L=P*(wf+0.0);B=P*(wf*0.87)
            tip=(hx+ux*L,hy+uy*L);bx,by=hx-ux*P*0.02,hy-uy*P*0.02
            px,py=-uy,ux
            dd.polygon([tip,(bx+px*B,by+py*B),(bx-px*B,by-py*B)],fill=col)
        if alpha<255:
            a=lay.getchannel('A').point(lambda v:v*alpha//255);lay.putalpha(a)
            im.paste(lay,(0,0),lay)
    def group_outline(cells,col,width):
        cs=set(map(tuple,cells))
        for c in cs:
            b=cellbox(c)
            for (dx,dy,seg) in ((0,1,(b[0],b[1],b[2],b[1])),(0,-1,(b[0],b[3],b[2],b[3])),(-1,0,(b[0],b[1],b[0],b[3])),(1,0,(b[2],b[1],b[2],b[3]))):
                if (c[0]+dx,c[1]+dy) not in cs: d.line(seg,fill=col,width=width)
    def center(cells):
        pts=[C(c) for c in cells];return (sum(p[0] for p in pts)/len(pts),sum(p[1] for p in pts)/len(pts))
    # --- layer 0: Box(2) Pipe(3) Corner(4)
    for it in items:
        k=it['kind'];cs=it['occupiedPositions']
        if k==2:
            for c in cs: d.rectangle(cellbox(c,P*0.04),fill=(176,124,72,255))
            group_outline(cs,(110,70,35,255),SS*2)
            if it.get('health') is not None:
                # label at the first-cell
                m=center(cs);d.text(m,str(it['health']),fill=(255,255,255,255),font=font(int(P*0.8)),anchor='mm',stroke_width=SS,stroke_fill=(90,55,25,255))
        elif k==3:
            pts=[C(c) for c in cs]
            d.line(pts,fill=(96,125,139,255),width=int(P*0.78),joint='curve')
            for q in pts: d.ellipse([q[0]-P*.39,q[1]-P*.39,q[0]+P*.39,q[1]+P*.39],fill=(96,125,139,255))
            d.line(pts,fill=(176,190,197,255),width=int(P*0.34),joint='curve')
            for p in it.get('passes',[]):
                q=C(p['position']);d.ellipse([q[0]-P*.3,q[1]-P*.3,q[0]+P*.3,q[1]+P*.3],fill=(255,193,7,255),outline=(120,90,0,255),width=SS)
            i=it.get('healthViewPathIndex',0)
            if it.get('health') is not None and 0<=i<len(cs): txt(cs[i],it['health'],(255,255,255,255),int(P*0.62))
        elif k==4:
            c=cs[0];d.rectangle(cellbox(c,P*0.04),fill=(171,71,188,255))
            q=C(c)
            for key in ('direction1','direction2'):
                v=it.get(key)
                if v:
                    ux,uy=v[0],-v[1];e=(q[0]+ux*P*.42,q[1]+uy*P*.42)
                    d.line([q,e],fill=(255,255,255,255),width=int(P*.16))
                    px,py=-uy,ux
                    d.polygon([(e[0]+ux*P*.1,e[1]+uy*P*.1),(e[0]-ux*P*.12+px*P*.14,e[1]-uy*P*.12+py*P*.14),(e[0]-ux*P*.12-px*P*.14,e[1]-uy*P*.12-py*P*.14)],fill=(255,255,255,255))
            if it.get('demand') is not None:
                d.ellipse([q[0]-P*.2,q[1]-P*.2,q[0]+P*.2,q[1]+P*.2],fill=(255,255,255,255));d.text(q,str(it['demand']),fill=(120,30,140,255),font=font(int(P*.36)),anchor='mm')
    # --- Curtain(12): hidden underlay layer (layer 1, below arrows)
    for it in items:
        if it['kind']==12:
            cs=it['occupiedPositions']
            for c in cs: d.rectangle(cellbox(c),fill=(124,77,255,38))
            group_outline(cs,(98,50,230,255),SS*2)
            for sub in it.get('items',[]):
                if sub['kind']==1: arrow(sub,215,0.30,(126,87,194))
    # --- layer 1: arrows (top level)
    for it in items:
        if it['kind']==1: arrow(it)
    # --- Band(8)
    for it in items:
        if it['kind']==8:
            pts=[C(c) for c in it['occupiedPositions']]
            d.line(pts,fill=(0,200,83,200),width=int(P*0.2),joint='curve')
            for q in pts: d.ellipse([q[0]-P*.17,q[1]-P*.17,q[0]+P*.17,q[1]+P*.17],fill=(0,200,83,255),outline=(255,255,255,255),width=SS)
    # --- Key(11)
    for it in items:
        if it['kind']==11:
            q=C(it['occupiedPositions'][0]);r=P*0.36
            d.ellipse([q[0]-r,q[1]-r,q[0]+r,q[1]+r],fill=(255,214,0,255),outline=(140,100,0,255),width=SS)
            d.text(q,'K',fill=(120,80,0,255),font=font(int(P*.48)),anchor='mm')
    # --- LockedCurtain(18)
    for it in items:
        if it['kind']==18:
            cs=it['occupiedPositions']
            for c in cs: d.rectangle(cellbox(c),fill=(211,47,47,34))
            group_outline(cs,(183,28,28,255),SS*2)
            m=center(cs);r=P*0.62
            d.ellipse([m[0]-r,m[1]-r,m[0]+r,m[1]+r],fill=(183,28,28,235),outline=(255,255,255,255),width=SS*2)
            d.text(m,str(it.get('health','')),fill=(255,255,255,255),font=font(int(P*0.85)),anchor='mm')
    out=im.resize((im.width//SS,im.height//SS),Image.LANCZOS)
    if path: out.save(path,'WEBP',quality=82,method=6)
    return out
if __name__=='__main__':
    L=json.load(open('data/levels.json'))
    for g in sys.argv[1:]:
        render(L[int(g)-1],f'/tmp/r_{g}.png')
