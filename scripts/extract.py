import zipfile,io,re,json,struct,subprocess,os
X=os.path.expanduser('~/Downloads/Maze+Out!+-+Tap+Puzzle_909_APKPure.xapk')
zx=zipfile.ZipFile(X)
z=zipfile.ZipFile(io.BytesIO(zx.read('com.grandgames.arrowjam.apk')))
def js(d,key):
    j=d.find(key)
    if j<0: return None
    ln=struct.unpack('<I',d[j-4:j])[0]
    return json.loads(d[j:j+ln])
levels={};cfg={}
for i in z.infolist():
    n=i.filename
    if not n.startswith('assets/bin/Data/') or i.file_size>200000 or '.' in n.split('/')[-1]: continue
    d=z.read(i)
    o=js(d,b'{"itemModels')
    if o:
        nm=re.findall(rb'[ -~]{6,}',d[max(0,d.find(b'{"itemModels')-120):d.find(b'{"itemModels')-4])[-1].decode()
        levels[nm]=o
    c=js(d,b'{"levelConfigModels')
    if c:
        for m in c['levelConfigModels']:
            if 'levelId' in m: cfg[m['levelId']]=m
print(len(levels),len(cfg))
sets=[('21.10_Levels_1-300_fix',300,'main300'),('2205-arrows-main',200,'ab200'),('07.11_Loop_Fixes',200,'loop200'),('2904-arrows-loop_v2',30,'loopv2'),('October_2026',30,'oct')]
out=[];g=0
for s,cnt,tag in sets:
    for k in range(1,cnt+1):
        lid=f'{s}-level-{k}-seed-1'
        o=levels[lid]; g+=1
        c=cfg.get(lid,{})
        out.append(dict(global_id=g,set=tag,set_index=k,levelId=lid,cfg_difficulty=c.get('difficulty'),cfg_duration=c.get('durationInSeconds'),**o))
json.dump(out,open('data/levels.json','w'),separators=(',',':'))
print(len(out),sum(1 for x in out if x['cfg_difficulty'] is None))
