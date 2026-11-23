import json,sys
from PIL import Image,ImageDraw
L=json.load(open('data/levels.json'))
KC={1:(60,60,60),2:(200,120,40),3:(60,120,200),4:(200,40,200),8:(40,180,80),11:(230,200,0),12:(150,150,230),18:(220,60,60)}
def render(x,path,S=22):
    W,H=x['width'],x['height']
    im=Image.new('RGB',(W*S,H*S),(245,245,245));d=ImageDraw.Draw(im)
    for it in sorted(x['itemModels'],key=lambda i:-i['layer']):
        its=[it]
        for it in its:
            c=KC[it['kind']]
            for (px,py) in it['occupiedPositions']:
                Y=(H-1-py)
                d.rectangle([px*S+1,Y*S+1,px*S+S-2,Y*S+S-2],fill=c if it['kind']!=12 else (210,210,245),outline=(255,255,255) if it['kind']!=12 else (150,150,230))
            if it['kind']==1:
                p=it['occupiedPositions'];hx,hy=p[-1]
                d.ellipse([hx*S+5,(H-1-hy)*S+5,hx*S+S-5,(H-1-hy)*S+S-5],fill=(255,255,255))
    im.save(path)
ids=[int(a) for a in sys.argv[1:]]
for g in ids:
    render(L[g-1],f'/tmp/dbg_{g}.png')
